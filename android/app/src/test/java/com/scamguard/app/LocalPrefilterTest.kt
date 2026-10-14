package com.scamguard.app

import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

/**
 * Unit tests for Android LocalPrefilter logic.
 */
class LocalPrefilterTest {

    private lateinit var prefilter: LocalPrefilter

    @Before
    fun setUp() {
        prefilter = LocalPrefilter()
    }

    @Test
    fun testEmptyMessageFiltered() {
        val res = prefilter.evaluate("", userRequested = false)
        assertFalse(res.shouldRouteToBackend)
        assertEquals("Likely Safe", res.localRiskTier)
    }

    @Test
    fun testBenignChatFilteredOnDevice() {
        val text = "Hey, are you free for lunch today at 1pm?"
        val res = prefilter.evaluate(text, userRequested = false)
        assertFalse(res.shouldRouteToBackend)
        assertEquals("Likely Safe", res.localRiskTier)
    }

    @Test
    fun testPhishingWithUrlRoutedToBackend() {
        val text = "URGENT: Verify your account at https://bank-secure.xyz to avoid suspension."
        val res = prefilter.evaluate(text, userRequested = false)
        assertTrue(res.shouldRouteToBackend)
        assertEquals("Candidate", res.localRiskTier)
        assertTrue(res.triggersDetected.isNotEmpty())
    }

    @Test
    fun testUserRequestedAnalysisBypassesFilter() {
        val text = "Hey, are you free for lunch?"
        val res = prefilter.evaluate(text, userRequested = true)
        assertTrue(res.shouldRouteToBackend)
        assertTrue(res.triggersDetected.contains("USER_EXPLICIT_REQUEST"))
    }
}
