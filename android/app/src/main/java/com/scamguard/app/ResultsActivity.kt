package com.scamguard.app

import android.graphics.Color
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

/**
 * Detection Results Screen.
 * Displays 4-tier classification, risk score, explanations, and safety recommendations.
 */
class ResultsActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_results)

        val classification = intent.getStringExtra("EXTRA_CLASSIFICATION") ?: "Unable to Determine"
        val riskScore = intent.getDoubleExtra("EXTRA_RISK_SCORE", 0.0)
        val confidence = intent.getDoubleExtra("EXTRA_CONFIDENCE", 0.0)
        val reasons = intent.getStringArrayListExtra("EXTRA_REASONS") ?: arrayListOf()
        val actions = intent.getStringArrayListExtra("EXTRA_ACTIONS") ?: arrayListOf()

        val textClassification = findViewById<TextView>(R.id.textClassification)
        val textRiskScore = findViewById<TextView>(R.id.textRiskScore)
        val textConfidence = findViewById<TextView>(R.id.textConfidence)
        val textReasons = findViewById<TextView>(R.id.textReasons)
        val textActions = findViewById<TextView>(R.id.textActions)
        val btnDone = findViewById<Button>(R.id.btnDone)
        val btnFeedbackAccurate = findViewById<Button>(R.id.btnFeedbackAccurate)
        val btnFeedbackFalse = findViewById<Button>(R.id.btnFeedbackFalse)

        textClassification.text = classification
        textRiskScore.text = "Risk Index: ${riskScore.toInt()} / 100"
        textConfidence.text = "Confidence Certainty: ${(confidence * 100).toInt()}%"

        // Color coding by tier
        when (classification) {
            "Likely Scam" -> {
                textClassification.setTextColor(Color.parseColor("#DC2626")) // Red
            }
            "Suspicious" -> {
                textClassification.setTextColor(Color.parseColor("#D97706")) // Amber
            }
            "Unable to Determine" -> {
                textClassification.setTextColor(Color.parseColor("#4B5563")) // Gray
            }
            else -> {
                textClassification.setTextColor(Color.parseColor("#16A34A")) // Green
            }
        }

        // Explanations
        val reasonsFormatted = if (reasons.isNotEmpty()) {
            reasons.joinToString("\n\n") { "• $it" }
        } else {
            "No prominent threat indicators detected."
        }
        textReasons.text = reasonsFormatted

        // Recommended Actions
        val actionsFormatted = if (actions.isNotEmpty()) {
            actions.joinToString("\n\n") { "✓ $it" }
        } else {
            "Standard vigilance advised."
        }
        textActions.text = actionsFormatted

        btnDone.setOnClickListener { finish() }

        btnFeedbackAccurate.setOnClickListener {
            Toast.makeText(this, "Feedback recorded: Marked as accurate detection.", Toast.LENGTH_SHORT).show()
            btnFeedbackAccurate.isEnabled = false
            btnFeedbackFalse.isEnabled = false
        }

        btnFeedbackFalse.setOnClickListener {
            Toast.makeText(this, "Feedback recorded: Marked for model review.", Toast.LENGTH_SHORT).show()
            btnFeedbackAccurate.isEnabled = false
            btnFeedbackFalse.isEnabled = false
        }
    }
}
