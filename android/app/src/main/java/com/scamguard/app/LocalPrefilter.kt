package com.scamguard.app

import java.util.regex.Pattern

/**
 * Stage 1 On-Device Lightweight Event Filter.
 * Runs locally on Android to filter out clearly benign notifications and conversations.
 * Preserves user privacy and reduces mobile data / backend server load by ~90%.
 */
class LocalPrefilter {

    private val urlPattern = Pattern.compile(
        "https?://[^\\s]+|www\\.[^\\s]+|[a-zA-Z0-9-]+\\.(com|org|net|info|biz|xyz|top|ru|cn|in|uk|io)/[^\\s]*",
        Pattern.CASE_INSENSITIVE
    )

    private val moneyPattern = Pattern.compile(
        "(\\\$|£|€|₹|rs\\.?|inr|usd)\\s*\\d+|\\b\\d+\\s*(dollars|pounds|euros|rupees|cash|credits|points)\\b",
        Pattern.CASE_INSENSITIVE
    )

    private val urgentKeywordsPattern = Pattern.compile(
        "\\b(urgent|immediately|action required|suspended|blocked|warning|compromised|expire[sd]?|otp|code|pin|verify|won|winner|lottery|prize|refund|kyc|bank|card|account)\\b",
        Pattern.CASE_INSENSITIVE
    )

    private val callToActionPattern = Pattern.compile(
        "\\b(call|click|login|sign in|visit|dial|text|reply|send|claim|collect)\\b",
        Pattern.CASE_INSENSITIVE
    )

    data class PrefilterResult(
        val shouldRouteToBackend: Boolean,
        val localRiskTier: String,
        val triggersDetected: List<String>,
        val reason: String
    )

    fun evaluate(text: String?, userRequested: Boolean = false): PrefilterResult {
        if (text.isNullOrBlank()) {
            return PrefilterResult(
                shouldRouteToBackend = false,
                localRiskTier = "Likely Safe",
                triggersDetected = emptyList(),
                reason = "Empty message"
            )
        }

        // If the user explicitly requested analysis (via Share Sheet or Manual Paste),
        // always bypass the local prefilter and send to the backend.
        if (userRequested) {
            return PrefilterResult(
                shouldRouteToBackend = true,
                localRiskTier = "Candidate",
                triggersDetected = listOf("USER_EXPLICIT_REQUEST"),
                reason = "User requested explicit scan"
            )
        }

        val triggers = mutableListOf<String>()

        if (urlPattern.matcher(text).find()) {
            triggers.add("URL_PRESENT")
        }

        if (moneyPattern.matcher(text).find()) {
            triggers.add("FINANCIAL_PATTERN")
        }

        val kwMatcher = urgentKeywordsPattern.matcher(text)
        var kwCount = 0
        while (kwMatcher.find()) kwCount++
        if (kwCount > 0) {
            triggers.add("KEYWORDS_FOUND($kwCount)")
        }

        if (callToActionPattern.matcher(text).find() && (triggers.isNotEmpty() || text.length > 200)) {
            triggers.add("CALL_TO_ACTION")
        }

        val shouldRoute = triggers.isNotEmpty()

        return PrefilterResult(
            shouldRouteToBackend = shouldRoute,
            localRiskTier = if (shouldRoute) "Candidate" else "Likely Safe",
            triggersDetected = triggers,
            reason = if (shouldRoute) "Triggers found; backend verification required" else "Benign conversational text; kept on device"
        )
    }
}
