package com.scamguard.app

import java.util.LinkedHashMap

/**
 * Thread-safe deduplication processor shared between SmsReceiver and NotificationListener.
 * Ensures the exact same message isn't processed twice within a short window.
 */
object ScanProcessor {

    private val processedHashCache = object : LinkedHashMap<String, Long>(100, 0.75f, true) {
        override fun removeEldestEntry(eldest: MutableMap.MutableEntry<String, Long>?): Boolean {
            return size > 100
        }
    }

    @Synchronized
    fun isDuplicate(contentKey: String): Boolean {
        val hash = PrivacyRedactor.sha256(contentKey)
        val lastSeen = processedHashCache[hash]
        val now = System.currentTimeMillis()
        if (lastSeen != null && (now - lastSeen) < 180_000) { // 3 minutes
            return true
        }
        processedHashCache[hash] = now
        return false
    }
}
