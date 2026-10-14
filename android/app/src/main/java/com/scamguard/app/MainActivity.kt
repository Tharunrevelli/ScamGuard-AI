package com.scamguard.app

import android.app.AlertDialog
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import java.util.concurrent.Executors

/**
 * Main Activity for ScamGuard Android Application.
 * Supports manual message paste, Share-to-App receiver, history list, and privacy settings.
 */
class MainActivity : AppCompatActivity() {

    private lateinit var editMessageInput: EditText
    private lateinit var btnAnalyze: Button
    private lateinit var progressBar: ProgressBar
    private lateinit var textStatus: TextView
    private lateinit var switchRedactPii: Switch
    private lateinit var switchPrefilter: Switch
    private lateinit var switchNotificationListener: Switch
    private lateinit var btnNotificationPermission: Button
    private lateinit var listHistory: ListView
    private lateinit var btnClearHistory: Button
    private lateinit var editBackendUrl: EditText

    private val localPrefilter = LocalPrefilter()
    private val privacyRedactor = PrivacyRedactor()
    private val executor = Executors.newSingleThreadExecutor()
    private lateinit var historyStorage: HistoryStorage

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        historyStorage = HistoryStorage(this)
        initViews()
        handleIncomingShareIntent(intent)
        loadSettings()
        refreshHistoryList()
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handleIncomingShareIntent(intent)
    }

    private fun initViews() {
        editMessageInput = findViewById(R.id.editMessageInput)
        btnAnalyze = findViewById(R.id.btnAnalyze)
        progressBar = findViewById(R.id.progressBar)
        textStatus = findViewById(R.id.textStatus)
        switchRedactPii = findViewById(R.id.switchRedactPii)
        switchPrefilter = findViewById(R.id.switchPrefilter)
        switchNotificationListener = findViewById(R.id.switchNotificationListener)
        btnNotificationPermission = findViewById(R.id.btnNotificationPermission)
        listHistory = findViewById(R.id.listHistory)
        btnClearHistory = findViewById(R.id.btnClearHistory)
        editBackendUrl = findViewById(R.id.editBackendUrl)

        btnAnalyze.setOnClickListener {
            val text = editMessageInput.text.toString().trim()
            if (text.isEmpty()) {
                Toast.makeText(this, "Please paste or enter a message to analyze.", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            performAnalysis(text, source = "MANUAL")
        }

        btnNotificationPermission.setOnClickListener {
            promptNotificationAccess()
        }

        btnClearHistory.setOnClickListener {
            AlertDialog.Builder(this)
                .setTitle("Clear History")
                .setMessage("Are you sure you want to delete all local scan history?")
                .setPositiveButton("Clear") { _, _ ->
                    historyStorage.clear()
                    refreshHistoryList()
                    Toast.makeText(this, "History cleared.", Toast.LENGTH_SHORT).show()
                }
                .setNegativeButton("Cancel", null)
                .show()
        }

        // Test Presets
        findViewById<Button>(R.id.btnPresetPhishing)?.setOnClickListener {
            editMessageInput.setText("URGENT: Chase Bank alert! Account suspended. Verify at https://chase-security-verify.xyz immediately.")
        }
        findViewById<Button>(R.id.btnPresetSafe)?.setOnClickListener {
            editMessageInput.setText("Hey! Are you still free to grab lunch around 1pm today?")
        }
    }

    private fun handleIncomingShareIntent(intent: Intent?) {
        if (intent == null) return
        if (intent.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            val sharedText = intent.getStringExtra(Intent.EXTRA_TEXT) ?: ""
            if (sharedText.isNotBlank()) {
                editMessageInput.setText(sharedText)
                performAnalysis(sharedText, source = "SHARE_SHEET")
            }
        }
    }

    private fun performAnalysis(rawText: String, source: String) {
        val prefs = getSharedPreferences("scamguard_settings", Context.MODE_PRIVATE)
        val serverUrl = editBackendUrl.text.toString().trim().ifEmpty { "http://10.0.2.2:8000/api/v1" }
        prefs.edit().putString("backend_url", serverUrl).apply()

        val shouldRedact = switchRedactPii.isChecked
        val usePrefilter = switchPrefilter.isChecked

        // Stage 1: Optional Local Prefilter
        if (usePrefilter && source != "SHARE_SHEET") {
            val preCheck = localPrefilter.evaluate(rawText, userRequested = false)
            if (!preCheck.shouldRouteToBackend) {
                // Kept on device!
                Toast.makeText(this, "Stage 1 Local Prefilter: Evaluated as Likely Safe on device.", Toast.LENGTH_LONG).show()
                return
            }
        }

        // UI Loading State
        progressBar.visibility = View.VISIBLE
        btnAnalyze.isEnabled = false
        textStatus.text = "Contacting ScamGuard detection engine..."

        executor.execute {
            val client = ApiClient(serverUrl)
            val textToSend = if (shouldRedact) privacyRedactor.redact(rawText).redactedText else rawText

            val result = client.detect(
                text = textToSend,
                source = source,
                sessionId = "android_device",
                bypassPrefilter = true, // User triggered
                redactPii = false
            )

            runOnUiThread {
                progressBar.visibility = View.GONE
                btnAnalyze.isEnabled = true
                textStatus.text = ""

                when (result) {
                    is ApiClient.Result.Success -> {
                        val detection = result.data
                        historyStorage.record(detection, source, rawText)
                        refreshHistoryList()

                        // Open Results Screen
                        val intent = Intent(this@MainActivity, ResultsActivity::class.java).apply {
                            putExtra("EXTRA_REQUEST_ID", detection.requestId)
                            putExtra("EXTRA_CLASSIFICATION", detection.classification)
                            putExtra("EXTRA_RISK_SCORE", detection.riskScore)
                            putExtra("EXTRA_CONFIDENCE", detection.confidence)
                            putExtra("EXTRA_SOURCE", source)
                            putExtra("EXTRA_MODEL_VERSION", detection.modelVersion)
                            putExtra("EXTRA_PROCESSING_MS", detection.processingTimeMs)
                            putExtra("EXTRA_REASONS", ArrayList(detection.reasons))
                            putExtra("EXTRA_ACTIONS", ArrayList(detection.suggestedActions))
                        }
                        startActivity(intent)
                    }
                    is ApiClient.Result.Error -> {
                        val msg = if (result.isOffline) {
                            "Offline Error: Cannot reach backend server at $serverUrl. Please ensure the backend is started."
                        } else {
                            result.message
                        }
                        AlertDialog.Builder(this@MainActivity)
                            .setTitle("Connection Error")
                            .setMessage(msg)
                            .setPositiveButton("OK", null)
                            .show()
                    }
                }
            }
        }
    }

    private fun promptNotificationAccess() {
        AlertDialog.Builder(this)
            .setTitle("Notification Access Authorization")
            .setMessage("ScamGuard requires Notification Listener permission to inspect incoming previews from WhatsApp, SMS, and Gmail locally. Personal chat databases are never read.\n\nWould you like to open System Settings to authorize?")
            .setPositiveButton("Open Settings") { _, _ ->
                startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS))
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun refreshHistoryList() {
        val history = historyStorage.getHistory()
        val summaries = history.map { "[${it.classification} - ${it.riskScore.toInt()}%] ${it.source}\n${it.summary}" }
        val adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, summaries)
        listHistory.adapter = adapter
    }

    private fun loadSettings() {
        val prefs = getSharedPreferences("scamguard_settings", Context.MODE_PRIVATE)
        editBackendUrl.setText(prefs.getString("backend_url", "http://10.0.2.2:8000/api/v1"))
        switchNotificationListener.isChecked = prefs.getBoolean("enable_notification_monitoring", true)
        switchNotificationListener.setOnCheckedChangeListener { _, isChecked ->
            prefs.edit().putBoolean("enable_notification_monitoring", isChecked).apply()
        }
    }
}
