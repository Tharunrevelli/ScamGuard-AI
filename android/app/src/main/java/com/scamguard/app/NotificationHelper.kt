package com.scamguard.app

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import java.util.ArrayList

/**
 * Helper to display high-priority heads-up threat warnings.
 * Handles both regular threat alerts and truncation warnings for clipped notification previews.
 */
object NotificationHelper {

    const val CHANNEL_ID = "scamguard_alerts"

    fun createAlertChannel(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Scam Threat Warnings",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "High-priority notifications for intercepted smishing, phishing, or financial scam threats"
                enableVibration(true)
                enableLights(true)
            }
            val manager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            manager.createNotificationChannel(channel)
        }
    }

    fun showWarning(
        context: Context,
        sourcePkg: String,
        sender: String,
        result: DetectionResult,
        isTruncated: Boolean = false
    ) {
        createAlertChannel(context)

        val intent = Intent(context, ResultsActivity::class.java).apply {
            putExtra("EXTRA_REQUEST_ID", result.requestId)
            putExtra("EXTRA_CLASSIFICATION", result.classification)
            putExtra("EXTRA_RISK_SCORE", result.riskScore)
            putExtra("EXTRA_CONFIDENCE", result.confidence)
            putExtra("EXTRA_SOURCE", sourcePkg)
            putExtra("EXTRA_MODEL_VERSION", result.modelVersion)
            putExtra("EXTRA_PROCESSING_MS", result.processingTimeMs)
            putExtra("EXTRA_REASONS", ArrayList(result.reasons))
            putExtra("EXTRA_ACTIONS", ArrayList(result.suggestedActions))
            putExtra("EXTRA_IS_TRUNCATED", isTruncated)
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }

        val pendingIntent = PendingIntent.getActivity(
            context,
            (System.currentTimeMillis() % 10000).toInt(),
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or (if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) PendingIntent.FLAG_IMMUTABLE else 0)
        )

        val appName = when {
            sourcePkg.contains("whatsapp", ignoreCase = true) -> "WhatsApp"
            sourcePkg.contains("gmail", ignoreCase = true) -> "Gmail"
            sourcePkg.contains("telegram", ignoreCase = true) -> "Telegram"
            sourcePkg.contains("signal", ignoreCase = true) -> "Signal"
            else -> "SMS"
        }

        val title = if (isTruncated) {
            "⚠️ ScamGuard Alert: $appName Threat [Preview Clipped]"
        } else {
            "⚠️ ScamGuard Alert: $appName Threat Detected"
        }

        val summaryReason = result.reasons.firstOrNull() ?: "Exercise caution before clicking links or sharing credentials."
        val bigTextContent = buildString {
            append("Risk: ${result.classification} (${result.riskScore.toInt()}/100)\n")
            append("Sender: $sender\n")
            if (isTruncated) {
                append("⚠️ Preview Clipped: Notification was truncated by Android. Tap to verify full text via Share Sheet.\n")
            }
            append("Analysis: $summaryReason")
        }

        // Action button to open ScamGuard for full paste / share sheet check
        val openAppIntent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        val openAppPendingIntent = PendingIntent.getActivity(
            context,
            (System.currentTimeMillis() % 10000 + 1).toInt(),
            openAppIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or (if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) PendingIntent.FLAG_IMMUTABLE else 0)
        )

        val builder = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.stat_sys_warning)
            .setContentTitle(title)
            .setContentText("Potential ${result.classification} from $sender (Risk: ${result.riskScore.toInt()}/100)")
            .setStyle(NotificationCompat.BigTextStyle().bigText(bigTextContent))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setDefaults(Notification.DEFAULT_ALL)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .addAction(android.R.drawable.ic_menu_search, "Verify Full Message", openAppPendingIntent)

        val manager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        manager.notify((System.currentTimeMillis() % 100000).toInt(), builder.build())
    }
}
