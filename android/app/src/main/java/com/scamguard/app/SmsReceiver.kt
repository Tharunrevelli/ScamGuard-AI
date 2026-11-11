package com.scamguard.app

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Telephony
import android.util.Log
import java.util.concurrent.Executors

/**
 * Direct SMS BroadcastReceiver (v2.0 - Privacy Shield Architecture).
 *
 * Implements 100% on-device SMS inspection via OnDeviceScamEngine under the Local Privacy Shield.
 * Private SMS messages from personal contacts remain on the device and are never sent over the network.
 */
class SmsReceiver : BroadcastReceiver() {

    private val executor = Executors.newSingleThreadExecutor()
    private val onDeviceEngine = OnDeviceScamEngine()
    private val privacyRedactor = PrivacyRedactor()

    override fun onReceive(context: Context, intent: Intent?) {
        if (intent == null) return
        val isTest = intent.action == "com.scamguard.app.TEST_SMS"
        val isReal = intent.action == Telephony.Sms.Intents.SMS_RECEIVED_ACTION
        if (!isTest && !isReal) return

        Log.i("ScamGuard", "SmsReceiver triggered by ${intent.action}")

        val sender: String
        val fullText: String

        if (isTest) {
            sender = intent.getStringExtra("sender") ?: "TEST-BANK"
            fullText = intent.getStringExtra("text") ?: "URGENT: Chase Bank alert! Account suspended. Verify at https://chase-security-verify.xyz immediately."
        } else {
            val messages = Telephony.Sms.Intents.getMessagesFromIntent(intent)
            if (messages.isNullOrEmpty()) {
                Log.w("ScamGuard", "SmsReceiver: Empty messages array from intent")
                return
            }
            sender = messages[0].displayOriginatingAddress ?: "Unknown Sender"
            val bodyBuilder = StringBuilder()
            for (msg in messages) {
                bodyBuilder.append(msg.displayMessageBody ?: "")
            }
            fullText = bodyBuilder.toString().trim()
        }

        if (fullText.isBlank()) {
            Log.w("ScamGuard", "SmsReceiver: Blank message body")
            return
        }

        val combinedMessage = if (sender.isNotBlank()) "$sender: $fullText" else fullText

        if (ScanProcessor.isDuplicate("SMS|$sender|$fullText")) {
            return
        }

        val historyStorage = HistoryStorage(context.applicationContext)
        val prefs = context.getSharedPreferences("scamguard_settings", Context.MODE_PRIVATE)
        val monitoringEnabled = prefs.getBoolean("enable_notification_monitoring", true)
        val monitorSms = prefs.getBoolean("monitor_sms", true)
        if (!monitoringEnabled || !monitorSms) {
            return
        }

        val localPrivacyShield = prefs.getBoolean("enable_local_privacy_shield", true)

        // 1. PRIVACY SHIELD: 100% Local On-Device Analysis (Zero Network Transmission)
        if (localPrivacyShield) {
            val assessment = onDeviceEngine.evaluate(combinedMessage)
            val detectionResult = onDeviceEngine.toDetectionResult(combinedMessage, assessment)

            Log.i("ScamGuard", "SmsReceiver On-Device Privacy Shield: ${assessment.classification} (Score: ${assessment.riskScore}) in ${assessment.processingTimeMs}ms [0 Network Calls]")

            historyStorage.record(detectionResult, "SMS ($sender)", combinedMessage)
            context.sendBroadcast(Intent("com.scamguard.app.REFRESH_HISTORY"))

            if (assessment.classification == "Likely Scam" || assessment.classification == "Suspicious") {
                NotificationHelper.showWarning(
                    context = context.applicationContext,
                    sourcePkg = "SMS",
                    sender = sender,
                    result = detectionResult,
                    isTruncated = assessment.isTruncated
                )
            }
            return
        }

        // Optional Cloud Hybrid Fallback (if user explicitly turned off Privacy Shield)
        val pendingResult = goAsync()
        executor.execute {
            try {
                val serverUrl = prefs.getString("backend_url", "http://172.22.107.83:8000/api/v1") ?: "http://172.22.107.83:8000/api/v1"
                val client = ApiClient(serverUrl)

                val redaction = privacyRedactor.redact(combinedMessage)
                val detectionResult = client.detect(
                    text = redaction.redactedText,
                    source = "SMS",
                    sessionId = "android_device",
                    bypassPrefilter = false,
                    redactPii = false
                )

                if (detectionResult is ApiClient.Result.Success) {
                    val data = detectionResult.data
                    val (isTruncated, _) = onDeviceEngine.checkTruncation(combinedMessage)
                    historyStorage.record(data, "SMS ($sender)", combinedMessage)
                    context.sendBroadcast(Intent("com.scamguard.app.REFRESH_HISTORY"))

                    if (data.classification == "Likely Scam" || data.classification == "Suspicious") {
                        NotificationHelper.showWarning(
                            context = context.applicationContext,
                            sourcePkg = "SMS",
                            sender = sender,
                            result = data,
                            isTruncated = isTruncated
                        )
                    }
                }
            } catch (e: Exception) {
                Log.e("ScamGuard", "SmsReceiver error: ${e.message}", e)
            } finally {
                pendingResult.finish()
            }
        }
    }
}
