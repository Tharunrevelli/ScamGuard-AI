# Thesis Demonstration & Evaluation Guide
**Project:** AI-Powered Selective Scam Detection System
**Target Audience:** Thesis Examination Committee / Academic Advisor

---

## 1. Quick Demonstration Workflow (3-Minute Walkthrough)

### Step 1: Start the Backend API & Web Application
Open a terminal in `D:\Project-1` and run:
```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
- Web Application Dashboard: **`http://localhost:8000`**
- Interactive OpenAPI / Swagger Documentation: **`http://localhost:8000/docs`**

---

## 2. Live Demonstration Scenarios

### Scenario A: Urgent Bank Phishing (Likely Scam)
1. On the Web Dashboard, click the **"Bank Phishing"** quick test preset:
   > *"URGENT: Chase Bank alert! Your online access has been temporarily suspended due to 3 suspicious login attempts. Verify immediately at https://chase-security-verify.xyz/login within 24 hours to prevent permanent closure."*
2. Ensure **"Redact PII Locally"** is toggled **ON**.
3. Click **"Inspect for Scam Indicators"**.
4. **Observe:**
   - Classification: **`Likely Scam`** (Risk Index: ~95/100).
   - Detected Threat Vectors: `URGENCY_THREAT`, `IMPERSONATION`, `SUSPICIOUS_LINKS`.
   - Specific Recommended Action: *"DO NOT click links, NEVER disclose credentials, block sender."*
   - Latency: Sub-10ms response.

### Scenario B: 2FA / OTP Stealer (Critical Rule Elevation)
1. Click the **"OTP Stealer"** preset:
   > *"Your verification code is 482910. Do not share this OTP with anyone. A customer care executive is waiting on the line to confirm your card details and unblock your account."*
2. Click **"Inspect for Scam Indicators"**.
3. **Observe:**
   - Classification: **`Likely Scam`** with `CRITICAL` severity indicator for `CREDENTIAL_HARVEST`.
   - Explains that authentic bank employees never request OTPs over the phone.

### Scenario C: Normal Benign Chat (Stage 1 Edge Filter Demonstration)
1. Click the **"Normal Chat"** preset:
   > *"Hey Sarah! Are we still meeting for lunch at the cafe around 1:00 PM today? Let me know if you want me to grab a table outside."*
2. Select Source: **"Android Notification Preview"**.
3. Click **"Inspect for Scam Indicators"**.
4. **Observe:**
   - Evaluated as **`Likely Safe`** under `STAGE_1_LOCAL_FILTER`.
   - Demonstrates that normal conversational notifications are resolved locally on the device in **0.5ms**, eliminating unnecessary cloud bandwidth.

### Scenario D: Ambiguous Short Message (Handling Uncertainty)
1. Click the **"Ambiguous"** preset:
   > *"Ok call me"*
2. Click **"Inspect for Scam Indicators"**.
3. **Observe:**
   - Classification: **`Unable to Determine`** (Confidence: 40%).
   - Demonstrates that the system resists overconfident false classifications when message context is inherently insufficient.

---

## 3. Demonstrating the Core Thesis Research Question

Navigate to the **"Research Benchmark"** tab in the web dashboard:
1. Show the **89.96% Server Traffic Reduction** achieved by the Two-Stage Selective Architecture (Model 4) on 1,115 held-out messages.
2. Defend the **False Negative Trade-off** (Professor Constraint):
   - Transparently disclose that conversational spam lacking overt links or financial keywords increases False Negative Rate from 5.37% to 40.94% during passive background monitoring.
   - Explain the architectural remedy: **Active User Workflows (Manual Paste and Share Sheet) bypass Stage 1 and utilize the 99.19% accurate cloud hybrid engine.**

---

## 4. Demonstrating the Android Mobile App

The native Android source is located in `android/`:
1. Open `D:\Project-1\android` in Android Studio.
2. Build and run on an Android device or emulator (Android 7.0+ / API 24–34).
3. **Supported Live Flows:**
   - **Manual Paste:** Paste text and tap *"Inspect for Scam Indicators"*.
   - **System Share Sheet:** Highlight text in WhatsApp, Chrome, or SMS, tap *"Share"*, and select *"ScamGuard"*.
   - **Background Notification Monitoring:** Tap *"Authorize Notification Access"* to enable the `NotificationListenerService`. Incoming status-bar alerts from WhatsApp, SMS, or Gmail are intercepted, deduplicated, prefiltered on-device, and high-risk lures trigger an immediate security warning!
