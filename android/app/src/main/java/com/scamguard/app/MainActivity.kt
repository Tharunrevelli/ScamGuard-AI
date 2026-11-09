package com.scamguard.app

import android.app.AlertDialog
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import java.util.concurrent.Executors

/**
 * Main Activity for ScamGuard Android Application (v2.0).
 * Supports on-device Privacy Shield, direct clipboard paste & scan, Share-to-App,
 * noise package rejection, truncation detection, and deep cloud forensic verification.
 */
class MainActivity : AppCompatActivity() {

    private lateinit var editMessageInput: EditText
    private lateinit var btnAnalyze: Button
    private lateinit var btnScanClipboard: Button
    private lateinit var progressBar: ProgressBar
    private lateinit var textStatus: TextView
    private lateinit var switchPrivacyShield: Switch
    private lateinit var switchRedactPii: Switch
    private lateinit var switchNotificationListener: Switch
    private lateinit var checkWhatsApp: CheckBox
    private lateinit var checkSms: CheckBox
    private lateinit var checkTelegram: CheckBox
    private lateinit var checkEmail: CheckBox
    private lateinit var btnNotificationPermission: Button
    private lateinit var listHistory: ListView
    private lateinit var btnClearHistory: Button
    private lateinit var editBackendUrl: EditText

    private val onDeviceEngine = OnDeviceScamEngine()
    private val privacyRedactor = PrivacyRedactor()
    private val executor = Executors.newSingleThreadExecutor()
    private lateinit var historyStorage: HistoryStorage

    private val historyRefreshReceiver = object : android.content.BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            runOnUiThread {
                refreshHistoryList()
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        historyStorage = HistoryStorage(this)
        NotificationHelper.createAlertChannel(this)
        initViews()
        handleIncomingShareIntent(intent)
        loadSettings()
        refreshHistoryList()

        // Request POST_NOTIFICATIONS and RECEIVE_SMS permissions
        val permissions = mutableListOf<String>()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, android.Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                permissions.add(android.Manifest.permission.POST_NOTIFICATIONS)
            }
        }
        if (ContextCompat.checkSelfPermission(this, android.Manifest.permission.RECEIVE_SMS) != PackageManager.PERMISSION_GRANTED) {
            permissions.add(android.Manifest.permission.RECEIVE_SMS)
        }
        if (permissions.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, permissions.toTypedArray(), 101)
        }
    }

    override fun onStart() {
        super.onStart()
        val filter = android.content.IntentFilter("com.scamguard.app.REFRESH_HISTORY")
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            registerReceiver(historyRefreshReceiver, filter, Context.RECEIVER_NOT_EXPORTED)
        } else {
            registerReceiver(historyRefreshReceiver, filter)
        }
    }

    override fun onStop() {
        super.onStop()
        try {
            unregisterReceiver(historyRefreshReceiver)
        } catch (e: Exception) {
            // Ignored
        }
    }

    override fun onResume() {
        super.onResume()
        refreshHistoryList()
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handleIncomingShareIntent(intent)
    }

    private fun initViews() {
        editMessageInput = findViewById(R.id.editMessageInput)
        btnAnalyze = findViewById(R.id.btnAnalyze)
        btnScanClipboard = findViewById(R.id.btnScanClipboard)
        progressBar = findViewById(R.id.progressBar)
        textStatus = findViewById(R.id.textStatus)
        switchPrivacyShield = findViewById(R.id.switchPrivacyShield)
        switchRedactPii = findViewById(R.id.switchRedactPii)
        switchNotificationListener = findViewById(R.id.switchNotificationListener)
        checkWhatsApp = findViewById(R.id.checkWhatsApp)
        checkSms = findViewById(R.id.checkSms)
        checkTelegram = findViewById(R.id.checkTelegram)
        checkEmail = findViewById(R.id.checkEmail)
        btnNotificationPermission = findViewById(R.id.btnNotificationPermission)
        listHistory = findViewById(R.id.listHistory)
        btnClearHistory = findViewById(R.id.btnClearHistory)
        editBackendUrl = findViewById(R.id.editBackendUrl)

        // Manual Threat Analysis
        btnAnalyze.setOnClickListener {
            val text = editMessageInput.text.toString().trim()
            if (text.isEmpty()) {
                Toast.makeText(this, "Please paste or enter a message to analyze.", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            performAnalysis(text, source = "MANUAL")
        }

        // Quick Scan Clipboard Button
        btnScanClipboard.setOnClickListener {
            val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as? ClipboardManager
            val clipData = clipboard?.primaryClip
            if (clipData != null && clipData.itemCount > 0) {
                val clipText = clipData.getItemAt(0)?.text?.toString()?.trim() ?: ""
                if (clipText.isNotBlank()) {
                    editMessageInput.setText(clipText)
                    Toast.makeText(this, "Clipboard content imported (${clipText.length} chars)", Toast.LENGTH_SHORT).show()
                    performAnalysis(clipText, source = "CLIPBOARD")
                } else {
                    Toast.makeText(this, "Clipboard is empty or contains non-text content.", Toast.LENGTH_SHORT).show()
                }
            } else {
                Toast.makeText(this, "Clipboard is empty.", Toast.LENGTH_SHORT).show()
            }
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
        findViewById<Button>(R.id.btnPresetTruncated)?.setOnClickListener {
            // Demonstrates Truncation Detection critique from Professor
            editMessageInput.setText("Chase Bank: Unauthorized login from unfamiliar device. To safeguard your account, click http://chase-login-resolve.xyz/ver...")
        }
        findViewById<Button>(R.id.btnPresetEcommerce)?.setOnClickListener {
            // Demonstrates Scalability & Noise Filtering critique from Professor
            editMessageInput.setText("Meesho Deal: 70% OFF Kurtis & Sarees starting at Rs. 149! Free delivery on your first order. Open app now.")
        }

        // Channel Toggles Sync with SharedPreferences
        val prefs = getSharedPreferences("scamguard_settings", Context.MODE_PRIVATE)
        checkWhatsApp.setOnCheckedChangeListener { _, isChecked ->
            prefs.edit().putBoolean("monitor_whatsapp", isChecked).apply()
        }
        checkSms.setOnCheckedChangeListener { _, isChecked ->
            prefs.edit().putBoolean("monitor_sms", isChecked).apply()
        }
        checkTelegram.setOnCheckedChangeListener { _, isChecked ->
            prefs.edit().putBoolean("monitor_telegram", isChecked).apply()
        }
        checkEmail.setOnCheckedChangeListener { _, isChecked ->
            prefs.edit().putBoolean("monitor_email", isChecked).apply()
        }
        switchPrivacyShield.setOnCheckedChangeListener { _, isChecked ->
            prefs.edit().putBoolean("enable_local_privacy_shield", isChecked).apply()
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
        val serverUrl = editBackendUrl.text.toString().trim().ifEmpty { "http://172.22.107.154:8000/api/v1" }
        prefs.edit().putString("backend_url", serverUrl).apply()

        val usePrivacyShield = switchPrivacyShield.isChecked
        val shouldRedact = switchRedactPii.isChecked

        // OPTION 1: 100% On-Device Privacy Shield (Zero Network Calls)
        if (usePrivacyShield) {
            val assessment = onDeviceEngine.evaluate(rawText)
            val detection = onDeviceEngine.toDetectionResult(rawText, assessment)

            historyStorage.record(detection, source, rawText)
            refreshHistoryList()

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
                putExtra("EXTRA_IS_TRUNCATED", assessment.isTruncated)
            }
            startActivity(intent)
            return
        }

        // OPTION 2: Cloud Hybrid Inference (Deep Cloud Forensic Scan)
        progressBar.visibility = View.VISIBLE
        btnAnalyze.isEnabled = false
        btnScanClipboard.isEnabled = false
        textStatus.text = "Contacting ScamGuard Cloud Ensemble..."

        executor.execute {
            val client = ApiClient(serverUrl)
            val textToSend = if (shouldRedact) privacyRedactor.redact(rawText).redactedText else rawText

            val result = client.detect(
                text = textToSend,
                source = source,
                sessionId = "android_device",
                bypassPrefilter = true,
                redactPii = false
            )

            runOnUiThread {
                progressBar.visibility = View.GONE
                btnAnalyze.isEnabled = true
                btnScanClipboard.isEnabled = true
                textStatus.text = ""

                when (result) {
                    is ApiClient.Result.Success -> {
                        val detection = result.data
                        val (isTruncated, _) = onDeviceEngine.checkTruncation(rawText)
                        historyStorage.record(detection, source, rawText)
                        refreshHistoryList()

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
                            putExtra("EXTRA_IS_TRUNCATED", isTruncated)
                        }
                        startActivity(intent)
                    }
                    is ApiClient.Result.Error -> {
                        val msg = if (result.isOffline) {
                            "Offline Error: Cannot reach cloud backend at $serverUrl. You can enable 'Local Privacy Shield' to perform 100% offline scam detection."
                        } else {
                            result.message
                        }
                        AlertDialog.Builder(this@MainActivity)
                            .setTitle("Connection Error")
                            .setMessage(msg)
                            .setPositiveButton("Use Local Shield Instead") { _, _ ->
                                switchPrivacyShield.isChecked = true
                                performAnalysis(rawText, source)
                            }
                            .setNegativeButton("Cancel", null)
                            .show()
                    }
                }
            }
        }
    }

    private fun promptNotificationAccess() {
        AlertDialog.Builder(this)
            .setTitle("Notification Access Authorization")
            .setMessage("ScamGuard inspects incoming message previews from approved communication channels (WhatsApp, SMS, Telegram, Gmail) 100% on-device.\n\nE-commerce ads (Amazon, Meesho, Flipkart) and non-messaging notifications are automatically dropped. Personal chats are never sent to external servers.")
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
        editBackendUrl.setText(prefs.getString("backend_url", "http://172.22.107.154:8000/api/v1"))
        switchPrivacyShield.isChecked = prefs.getBoolean("enable_local_privacy_shield", true)
        switchNotificationListener.isChecked = prefs.getBoolean("enable_notification_monitoring", true)
        checkWhatsApp.isChecked = prefs.getBoolean("monitor_whatsapp", true)
        checkSms.isChecked = prefs.getBoolean("monitor_sms", true)
        checkTelegram.isChecked = prefs.getBoolean("monitor_telegram", true)
        checkEmail.isChecked = prefs.getBoolean("monitor_email", true)

        switchNotificationListener.setOnCheckedChangeListener { _, isChecked ->
            prefs.edit().putBoolean("enable_notification_monitoring", isChecked).apply()
        }
    }
}
