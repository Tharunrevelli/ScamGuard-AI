package com.scamguard.app

import android.accessibilityservice.AccessibilityService
import android.content.Context
import android.content.Intent
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo

/**
 * On-Screen Chat Threat Inspector (Accessibility Service).
 *
 * Solves Professor Critique #2:
 * "What if notifications are switched OFF on the mobile? How can ScamGuard detect scams?"
 *
 * Capabilities:
 * 1. Passively inspects on-screen chat view hierarchies inside messaging apps (WhatsApp, Telegram, Messages).
 * 2. Operates 100% on-device even when system status-bar notifications are disabled, muted, or silenced.
 * 3. Evaluates displayed text via OnDeviceScamEngine with 0 network calls (zero data exposure).
 * 4. Displays real-time warning if a phishing link, OTP lure, or account threat is rendered on screen.
 */
class ScamGuardAccessibilityService : AccessibilityService() {

    private val onDeviceEngine = OnDeviceScamEngine()
    private lateinit var historyStorage: HistoryStorage

    override fun onServiceConnected() {
        super.onServiceConnected()
        Log.i("ScamGuard", "ScamGuardAccessibilityService active (Protection active even when notifications are OFF)")
        historyStorage = HistoryStorage(this)
        NotificationHelper.createAlertChannel(this)
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event == null) return

        val pkgName = event.packageName?.toString() ?: return
        val lowerPkg = pkgName.lowercase()

        // Only monitor approved messaging and email applications on-screen
        val isTargetApp = lowerPkg.contains("whatsapp") ||
                lowerPkg.contains("telegram") ||
                lowerPkg.contains("messaging") ||
                lowerPkg.contains(".mms") ||
                lowerPkg.contains("sms") ||
                lowerPkg.contains("gmail") ||
                lowerPkg.contains("android.gm") ||
                lowerPkg.contains("outlook") ||
                lowerPkg.contains("mail")

        if (!isTargetApp) return

        val prefs = getSharedPreferences("scamguard_settings", Context.MODE_PRIVATE)
        val enabled = prefs.getBoolean("enable_accessibility_protection", true)
        if (!enabled) return

        val rootNode = rootInActiveWindow ?: return
        try {
            inspectNodeHierarchy(rootNode, pkgName)
        } finally {
            rootNode.recycle()
        }
    }

    private fun inspectNodeHierarchy(node: AccessibilityNodeInfo?, pkgName: String) {
        if (node == null) return

        val text = node.text?.toString()?.trim()
        if (!text.isNullOrBlank() && text.length > 20) {
            // Check if this snippet looks suspicious or contains a link/lure
            if (text.contains("http", ignoreCase = true) ||
                text.contains("www.", ignoreCase = true) ||
                text.contains("verify", ignoreCase = true) ||
                text.contains("suspended", ignoreCase = true) ||
                text.contains("blocked", ignoreCase = true) ||
                text.contains("otp", ignoreCase = true) ||
                text.contains("won", ignoreCase = true) ||
                text.contains("urgent", ignoreCase = true) ||
                text.contains("bill", ignoreCase = true) ||
                text.contains("power", ignoreCase = true) ||
                text.contains("electricity", ignoreCase = true) ||
                text.contains("parcel", ignoreCase = true) ||
                text.contains("delivery", ignoreCase = true) ||
                text.contains("kyc", ignoreCase = true) ||
                text.contains("pan", ignoreCase = true) ||
                text.contains("job", ignoreCase = true) ||
                text.contains("earn", ignoreCase = true) ||
                text.contains("bank", ignoreCase = true)
            ) {
                // Avoid redundant evaluation of the same text
                if (!ScanProcessor.isDuplicate("ACCESSIBILITY|$pkgName|$text")) {
                    val assessment = onDeviceEngine.evaluate(text)
                    if (assessment.classification == "Likely Scam" || assessment.classification == "Suspicious") {
                        Log.w("ScamGuard", "On-Screen threat detected via Accessibility [Notifications OFF scenario]: ${assessment.classification} ($pkgName)")
                        val detection = onDeviceEngine.toDetectionResult(text, assessment)
                        historyStorage.record(detection, "ON-SCREEN ($pkgName)", text)
                        sendBroadcast(Intent("com.scamguard.app.REFRESH_HISTORY"))

                        NotificationHelper.showWarning(
                            context = applicationContext,
                            sourcePkg = pkgName,
                            sender = "On-Screen Chat",
                            result = detection,
                            isTruncated = assessment.isTruncated
                        )
                    }
                }
            }
        }

        for (i in 0 until node.childCount) {
            val child = node.getChild(i)
            if (child != null) {
                inspectNodeHierarchy(child, pkgName)
                child.recycle()
            }
        }
    }

    override fun onInterrupt() {
        Log.i("ScamGuard", "ScamGuardAccessibilityService interrupted")
    }
}
