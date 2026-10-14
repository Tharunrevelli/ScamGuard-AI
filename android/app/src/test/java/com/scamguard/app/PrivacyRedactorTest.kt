package com.scamguard.app

import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

/**
 * Unit tests for Android PrivacyRedactor.
 */
class PrivacyRedactorTest {

    private lateinit var redactor: PrivacyRedactor

    @Before
    fun setUp() {
        redactor = PrivacyRedactor()
    }

    @Test
    fun testRedactsPhoneNumber() {
        val input = "Call me at +1-555-234-5678 immediately."
        val res = redactor.redact(input)
        assertTrue(res.wasRedacted)
        assertTrue(res.redactedText.contains("[PHONE_REDACTED]"))
        assertFalse(res.redactedText.contains("555-234-5678"))
    }

    @Test
    fun testRedactsCardNumber() {
        val input = "Pay to card 4111222233334444 now."
        val res = redactor.redact(input)
        assertTrue(res.wasRedacted)
        assertTrue(res.redactedText.contains("[CARD_NUMBER_REDACTED]"))
    }

    @Test
    fun testSha256Determinism() {
        val hash1 = PrivacyRedactor.sha256("test_message_123")
        val hash2 = PrivacyRedactor.sha256("test_message_123")
        assertEquals(hash1, hash2)
        assertEquals(64, hash1.length)
    }
}
