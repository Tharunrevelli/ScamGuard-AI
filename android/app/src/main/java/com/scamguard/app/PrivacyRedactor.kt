package com.scamguard.app

import java.security.MessageDigest
import java.util.regex.Pattern

/**
 * Client-Side PII Redactor and Fingerprint Generator.
 * Sanitizes phone numbers, credit card numbers, and email usernames
 * while preserving URL hostnames, payment requests, and scam indicators.
 */
class PrivacyRedactor {

    private val emailPattern = Pattern.compile("\\b([a-zA-Z0-9_.+-])[a-zA-Z0-9_.+-]*@([a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+)\\b")
    private val phonePattern = Pattern.compile("(\\+?\\d{1,3}[\\s-]?)?(\\(?\\d{3}\\)?[\\s-]?)(\\d{3}[\\s-]?\\d{4})")
    private val cardPattern = Pattern.compile("\\b(?:\\d[ -]*?){13,16}\\b")

    data class RedactionResult(
        val redactedText: String,
        val wasRedacted: Boolean
    )

    fun redact(text: String): RedactionResult {
        if (text.isBlank()) return RedactionResult(text, false)

        var result = text
        var modified = false

        // Mask emails
        val emailMatcher = emailPattern.matcher(result)
        if (emailMatcher.find()) {
            modified = true
            result = emailMatcher.replaceAll("$1***@$2")
        }

        // Mask credit cards
        val cardMatcher = cardPattern.matcher(result)
        if (cardMatcher.find()) {
            modified = true
            result = cardMatcher.replaceAll("[CARD_NUMBER_REDACTED]")
        }

        // Mask phone numbers
        val phoneMatcher = phonePattern.matcher(result)
        if (phoneMatcher.find()) {
            modified = true
            result = phoneMatcher.replaceAll("[PHONE_REDACTED]")
        }

        return RedactionResult(result, modified)
    }

    companion object {
        fun sha256(input: String): String {
            val bytes = MessageDigest.getInstance("SHA-256").digest(input.toByteArray(Charsets.UTF_8))
            return bytes.joinToString("") { "%02x".format(it) }
        }
    }
}
