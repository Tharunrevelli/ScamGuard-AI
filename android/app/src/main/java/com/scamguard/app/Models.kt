package com.scamguard.app

import org.json.JSONArray
import org.json.JSONObject

/**
 * Data models for ScamGuard Android client.
 */

data class RiskIndicator(
    val category: String,
    val severity: String,
    val description: String,
    val matchedSnippets: List<String>
) {
    companion object {
        fun fromJson(obj: JSONObject): RiskIndicator {
            val snippets = mutableListOf<String>()
            val arr = obj.optJSONArray("matched_snippets")
            if (arr != null) {
                for (i in 0 until arr.length()) {
                    snippets.add(arr.getString(i))
                }
            }
            return RiskIndicator(
                category = obj.optString("category", "UNKNOWN"),
                severity = obj.optString("severity", "MEDIUM"),
                description = obj.optString("description", ""),
                matchedSnippets = snippets
            )
        }
    }
}

data class DetectionResult(
    val requestId: String,
    val classification: String,
    val riskScore: Double,
    val confidence: Double,
    val reasons: List<String>,
    val suggestedActions: List<String>,
    val indicators: List<RiskIndicator>,
    val modelVersion: String,
    val processingTimeMs: Double,
    val stageApplied: String,
    val piiRedacted: Boolean,
    val redactedPreview: String?
) {
    companion object {
        fun fromJson(obj: JSONObject): DetectionResult {
            val reasons = mutableListOf<String>()
            val rArr = obj.optJSONArray("reasons")
            if (rArr != null) {
                for (i in 0 until rArr.length()) reasons.add(rArr.getString(i))
            }

            val actions = mutableListOf<String>()
            val aArr = obj.optJSONArray("suggested_actions")
            if (aArr != null) {
                for (i in 0 until aArr.length()) actions.add(aArr.getString(i))
            }

            val indicators = mutableListOf<RiskIndicator>()
            val indArr = obj.optJSONArray("indicators")
            if (indArr != null) {
                for (i in 0 until indArr.length()) {
                    indicators.add(RiskIndicator.fromJson(indArr.getJSONObject(i)))
                }
            }

            return DetectionResult(
                requestId = obj.optString("request_id", ""),
                classification = obj.optString("classification", "Unable to Determine"),
                riskScore = obj.optDouble("risk_score", 0.0),
                confidence = obj.optDouble("confidence", 0.0),
                reasons = reasons,
                suggestedActions = actions,
                indicators = indicators,
                modelVersion = obj.optString("model_version", "unknown"),
                processingTimeMs = obj.optDouble("processing_time_ms", 0.0),
                stageApplied = obj.optString("stage_applied", "HYBRID_REMOTE"),
                piiRedacted = obj.optBoolean("pii_redacted", false),
                redactedPreview = if (obj.has("redacted_preview") && !obj.isNull("redacted_preview")) obj.getString("redacted_preview") else null
            )
        }
    }
}

data class LocalAuditRecord(
    val requestId: String,
    val timestamp: String,
    val source: String,
    val classification: String,
    val riskScore: Double,
    val summary: String
)
