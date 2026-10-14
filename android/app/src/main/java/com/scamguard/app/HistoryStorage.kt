package com.scamguard.app

import android.content.Context
import android.content.SharedPreferences
import org.json.JSONArray
import org.json.JSONObject

/**
 * Manages privacy-conscious local detection history on the Android device.
 * Stores only metadata (timestamp, risk score, classification, brief preview) - NEVER full private chats.
 */
class HistoryStorage(context: Context) {

    private val prefs: SharedPreferences = context.getSharedPreferences("scamguard_local_history", Context.MODE_PRIVATE)

    fun record(result: DetectionResult, source: String, rawSnippet: String) {
        val list = getHistory().toMutableList()
        val snippetPreview = if (rawSnippet.length > 60) rawSnippet.substring(0, 60) + "..." else rawSnippet

        val record = LocalAuditRecord(
            requestId = result.requestId,
            timestamp = java.text.SimpleDateFormat("yyyy-MM-dd HH:mm", java.util.Locale.getDefault()).format(java.util.Date()),
            source = source,
            classification = result.classification,
            riskScore = result.riskScore,
            summary = snippetPreview
        )

        list.add(0, record) // Most recent first
        // Retain max 50 recent records
        val trimmed = if (list.size > 50) list.subList(0, 50) else list
        saveList(trimmed)
    }

    fun getHistory(): List<LocalAuditRecord> {
        val jsonStr = prefs.getString("history_records", "[]") ?: "[]"
        val list = mutableListOf<LocalAuditRecord>()
        try {
            val arr = JSONArray(jsonStr)
            for (i in 0 until arr.length()) {
                val obj = arr.getJSONObject(i)
                list.add(
                    LocalAuditRecord(
                        requestId = obj.optString("requestId"),
                        timestamp = obj.optString("timestamp"),
                        source = obj.optString("source"),
                        classification = obj.optString("classification"),
                        riskScore = obj.optDouble("riskScore"),
                        summary = obj.optString("summary")
                    )
                )
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return list
    }

    fun clear() {
        prefs.edit().remove("history_records").apply()
    }

    private fun saveList(list: List<LocalAuditRecord>) {
        val arr = JSONArray()
        for (item in list) {
            val obj = JSONObject().apply {
                put("requestId", item.requestId)
                put("timestamp", item.timestamp)
                put("source", item.source)
                put("classification", item.classification)
                put("riskScore", item.riskScore)
                put("summary", item.summary)
            }
            arr.put(obj)
        }
        prefs.edit().putString("history_records", arr.toString()).apply()
    }
}
