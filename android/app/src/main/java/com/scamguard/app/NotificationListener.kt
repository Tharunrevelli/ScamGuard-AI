package com.scamguard.app

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import androidx.core.app.NotificationCompat
import java.util.concurrent.Executors
import java.util.LinkedHashMap

/**
 * Native Android NotificationListenerService.
 * Listens for incoming notification events from supported messaging apps (WhatsApp, SMS, Gmail).
 * Implements Stage 1 on-device prefiltering, deduplication, and zero-leakage selective analysis.
 */
class NotificationListener : NotificationListenerService() {

    private val localPrefilter = LocalPrefilter()
    private val privacyRedactor = PrivacyRedactor()
    private val executor = Executors.newSingleThreadExecutor()
    private lateinit var apiClient: ApiClient
    private lateinit var historyStorage: HistoryStorage

    // Supported target apps whitelist (messaging & email only)
    private val supportedPackages = setOf(
        "com.whatsapp",                         // WhatsApp
        "com.google.android.apps.messaging",    // Google Messages / SMS
        "com.android.mms",                      // AOSP SMS
        "com.google.android.gm",                 // Gmail
        "org.telegram.messenger"               // Telegram
    )

    // Deduplication cache to prevent re-processing identical notification ticks (max 50 recent hashes)
    private val processedHashCache = object : LinkedHashMap<String, Long>(50, 0.75f, true) {
        override fun removeEldestEntry(eldest: MutableMap.MutableEntry<String, Long>?): Boolean {
            return size > 50
        }
    }

    override fun onCreate() {
        super.onCreate()
        apiClient = ApiClient()
        historyStorage = HistoryStorage(this)
        createAlertNotificationChannel()
    }

    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        super.onNotificationPosted(sbn)
        if (sbn == null) return

        val pkgName = sbn.packageName ?: return

        // 1. Whitelist filtering: ignore system apps, games, media players, social feeds
        if (!supportedPackages.contains(pkgName)) return

        // 2. Check user preference: is background monitoring enabled?
        val prefs = getSharedPreferences("scamguard_settings", Context.MODE_PRIVATE)
        val monitoringEnabled = prefs.getBoolean("enable_notification_monitoring", true)
        if (!monitoringEnabled) return

        val notification = sbn.notification ?: return
        val extras = notification.extras ?: return

        // 3. Extract notification payload (title and text preview)
        val title = extras.getCharSequence(Notification.EXTRA_TITLE)?.toString() ?: ""
        val text = extras.getCharSequence(Notification.EXTRA_BIG_TEXT)?.toString()
            ?: extras.getCharSequence(Notification.EXTRA_TEXT)?.toString()
            ?: ""

        // Fallback: If notification text is missing or blank, safely skip
        if (text.isBlank()) return

        val combinedMessage = if (title.isNotBlank()) "$title: $text" else text

        // 4. Deduplication check using SHA-256 fingerprint
        val hash = PrivacyRedactor.sha256("$pkgName|$title|$text")
        synchronized(processedHashCache) {
            val lastSeen = processedHashCache[hash]
            val now = System.currentTimeMillis()
            // Ignore if processed within last 5 minutes
            if (lastSeen != null && (now - lastSeen) < 300_000) {
                return
            }
            processedHashCache[hash] = now
        }

        // 5. STAGE 1: On-Device Local Prefilter
        val prefilterResult = localPrefilter.evaluate(combinedMessage, userRequested = false)
        if (!prefilterResult.shouldRouteToBackend) {
            // FILTERED ON DEVICE: Benign conversational notification
            // Save local audit stat without sending any data over the network!
            return
        }

        // 6. STAGE 2: Candidate detected -> Execute selective backend analysis in background
        executor.execute {
            val serverUrl = prefs.getString("backend_url", "http://10.0.2.2:8000/api/v1") ?: "http://10.0.2.2:8000/api/v1"
            val client = ApiClient(serverUrl)

            val redaction = privacyRedactor.redact(combinedMessage)
            val detectionResult = client.detect(
                text = redaction.redactedText,
                source = "NOTIFICATION",
                sessionId = "android_device",
                bypassPrefilter = false,
                redactPii = false // Already redacted locally on device
            )

            if (detectionResult is ApiClient.Result.Success) {
                val data = detectionResult.data
                // Record in local history
                historyStorage.record(data, "NOTIFICATION ($pkgName)", combinedMessage)

                // If flagged as Scam or Suspicious, present immediate user warning
                if (data.classification == "Likely Scam" || (data.classification == "Suspicious" && data.riskScore >= 45.0)) {
                    showWarningNotification(pkgName, title, data)
                }
            }
        }
    }

    private fun showWarningNotification(pkgName: String, sender: String, result: DetectionResult) {
        val intent = Intent(this, ResultsActivity::class.java).apply {
            putExtra("EXTRA_REQUEST_ID", result.requestId)
            putExtra("EXTRA_CLASSIFICATION", result.classification)
            putExtra("EXTRA_RISK_SCORE", result.riskScore)
            putExtra("EXTRA_CONFIDENCE", result.confidence)
            putExtra("EXTRA_SOURCE", "NOTIFICATION")
            putExtra("EXTRA_SUMMARY", if (result.reasons.isNotEmpty()) result.reasons[0] else "Potential scam detected")
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }

        val pendingIntent = PendingIntent.getActivity(
            this,
            (System.currentTimeMillis() % 10000).toInt(),
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or (if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) PendingIntent.FLAG_IMMUTABLE else 0)
        )

        val channelId = "scamguard_alerts"
        val appName = when {
            pkgName.contains("whatsapp") -> "WhatsApp"
            pkgName.contains("gmail") -> "Gmail"
            else -> "SMS"
        }

        val notification = NotificationCompat.Builder(this, channelId)
            .setSmallIcon(android.R.drawable.stat_sys_warning)
            .setContentTitle("⚠️ ScamGuard Alert: $appName Message")
            .setContentText("Potential ${result.classification} detected from $sender (Risk: ${result.riskScore.toInt()}/100)")
            .setStyle(NotificationCompat.BigTextStyle().bigText("Risk: ${result.classification}\n${result.reasons.firstOrNull() ?: "Exercise caution before clicking links or sharing credentials."}"))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .build()

        val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        manager.notify((System.currentTimeMillis() % 100000).toInt(), notification)
    }

    private fun createAlertNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                "scamguard_alerts",
                "Scam Threat Warnings",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "High-priority notifications for intercepted smishing, phishing, or financial scam threats"
            }
            val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            manager.createNotificationChannel(channel)
        }
    }
}
