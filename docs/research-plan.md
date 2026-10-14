# Research Plan: AI-Powered Selective Scam Detection System
**Bachelor's Thesis Project**

---

## 1. Problem Statement

Mobile messaging applications (SMS, WhatsApp, Telegram, Gmail) have become the primary vectors for digital fraud, including credential phishing, smishing, financial advance-fee scams, package impersonation, and urgent account takeover lures. Modern mobile users receive dozens of notifications daily. While cloud-based machine learning classifiers achieve high detection accuracy on spam/scam datasets, standard cloud-centric architectures suffer from two fundamental operational drawbacks:

1. **Unnecessary Backend Traffic and Scalability Bottlenecks:**
   Transmitting every incoming notification or benign message to a central remote server generates massive network bandwidth overhead, high backend server costs, and latency spikes under scale.
2. **Privacy and Data Minimization Risks:**
   Transmitting raw personal notifications (containing private conversations, family messages, sensitive emails, OTPs) to a remote cloud server violates modern data protection principles (e.g., GDPR data minimization) and exposes user PII to potential server-side compromise.

Simultaneously, naive on-device scam detection faces hardware constraints and struggles when relying solely on brittle keyword matching or heavy mobile deep-learning models.

---

## 2. Research Question

> **Primary Research Question:**
> *Can a selective, event-driven scam detection architecture combining lightweight on-device prefiltering with remote machine learning reduce unnecessary backend requests and data exposure while maintaining acceptable scam detection performance on supported Android message sources?*

### Sub-Questions & Hypotheses
- **$H_1$ (Request Reduction):** An explainable, lightweight on-device prefilter can filter out $\ge 60\%$ of clearly benign messages before any cloud transmission, reducing backend traffic and server inference cost by more than half.
- **$H_2$ (Detection Quality Preservation):** A two-stage architecture (Stage 1 heuristic prefiltering + Stage 2 remote hybrid ML/rule classification) maintains an overall detection Recall ($\ge 90\%$) comparable to an unrestricted full-cloud classification pipeline.
- **$H_3$ (Interpretability & Confidence):** Combining calibrated ML probabilities with interpretable rule triggers into a 4-tier decision taxonomy (*Likely Safe*, *Suspicious*, *Likely Scam*, *Unable to Determine*) provides higher confidence and user transparency than raw probability thresholds.

---

## 3. Intended Users and Supported Message Sources

### Target Users
- Everyday smartphone users vulnerable to digital fraud, smishing, and social engineering.
- Researchers and enterprise administrators seeking privacy-conscious mobile threat detection.

### Supported Android Message Sources & Realistic Access Constraints
Real-world Android security sandboxing strictly prohibits third-party apps from arbitrarily reading SQLite databases of WhatsApp or Gmail. The system implements only legally and technically supported mechanisms:

| Message Source | Android Mechanism | Content Actually Accessible | User Authorization Required | Limitations & Fallback |
| :--- | :--- | :--- | :--- | :--- |
| **Direct Manual Input / Paste** | UI Input / Clipboard | Full text pasted by user | None (direct user action) | Complete text available. |
| **System Share Sheet** | `Intent.ACTION_SEND` | Text or link shared from any app | User selects "Check with ScamGuard" | Full shared snippet available. |
| **WhatsApp Notifications** | `NotificationListenerService` | Title (Sender/Group) and Notification Body (`android.text`) | Explicit user grant in Android System Settings | Only notification snippet is visible; long messages are truncated by WhatsApp; fallback asks user to share/paste full text. |
| **SMS / Messages Notifications** | `NotificationListenerService` | Sender address and message body preview | Explicit user grant in Android System Settings | Preview text accessible without requiring privileged default SMS app status. |
| **Gmail Notifications** | `NotificationListenerService` | Subject line and brief email preview | Explicit user grant in Android System Settings | Full email body not accessible via notification; fallback encourages manual paste. |

---

## 4. System Architecture

The system operates across two coordinated stages:

```
[ Incoming Message Event ]
(WhatsApp / SMS / Gmail Notification OR Share-to-App OR Manual Paste)
             │
             ▼
┌───────────────────────────────────────────────────────────┐
│ STAGE 1: On-Device Lightweight Event Filter (Client)      │
│ 1. Event Deduplication (Hash Cache)                       │
│ 2. Cheap Heuristic Scoring (Urgency, Money, Links, Auth)   │
│ 3. PII Pre-Sanitization (Mask phone/card/email identifiers)│
└────────────────────────────┬──────────────────────────────┘
                             │
            Is message flagged as candidate OR
            explicitly requested by user?
            ├─── NO (Clearly Benign) ────► [ Log Local Stat: Kept On Device ]
            │                              [ Classification: Likely Safe (Local) ]
            └─── YES (Needs Server Verification)
                             │
                             ▼ (Encrypted HTTPS Payload)
┌───────────────────────────────────────────────────────────┐
│ STAGE 2: Remote Detection Engine (Backend API)            │
│ 1. Request Validation & Token-Bucket Rate Limiter         │
│ 2. Deep Heuristic Rule Engine (Grammar, Obfuscation, IP)  │
│ 3. Calibrated ML Classifier (TF-IDF + Logistic Regression)│
│ 4. Hybrid Decision Matrix & Confidence Calibration        │
│ 5. Privacy-Preserving Ephemeral Audit (Zero Raw Text)     │
└────────────────────────────┬──────────────────────────────┘
                             │
                             ▼
[ 4-Tier Structured Response: Likely Safe | Suspicious | Likely Scam | Unable to Determine ]
[ Actionable Explanation, Risk Score 0-100, Suggested Mitigation ]
```

---

## 5. Technical Contributions

1. **Defensible Two-Stage Architecture:** Implementation and empirical evaluation of an event-driven edge-cloud pipeline demonstrating the exact trade-off between backend request reduction and false negative rate.
2. **Transparent 4-Tier Decision Matrix:** A hybrid decision model harmonizing statistical ML probability with deterministic security rule indicators, preventing overconfident false positives on ambiguous texts.
3. **Privacy-Preserving Threat Inspection:** A zero-retention backend design where raw messages are never logged or persisted to disk, accompanied by optional client-side PII pseudonymization.
4. **Multi-Source Android Integration:** A working native implementation utilizing `NotificationListenerService` and `ACTION_SEND` intent receiver with non-intrusive local deduplication and alert delivery.
5. **Reproducible Experimental Benchmark:** Full evaluation script and documented public dataset proving the quantitative trade-offs of the system.

---

## 6. Evaluation Methodology

### Datasets
- **Primary Corpus:** SMS Spam Collection Dataset (UCI Machine Learning Repository, 5,574 genuine labeled SMS messages, Public Domain / CC BY 4.0).
- **Secondary Targeted Benchmark:** Labeled set of modern WhatsApp/smishing/phishing templates (delivery scams, banking alerts, impersonation, 2FA credential harvest, lottery awards) + ambiguous benign communications.

### Experimental Comparison Models
1. **Model A (Baseline Rule Detector):** Regex heuristics matching urgency keywords, financial lures, suspicious URLs, and authority impersonation.
2. **Model B (Baseline ML Classifier):** N-gram TF-IDF vectorizer + Logistic Regression with balanced class weighting.
3. **Model C (Hybrid Rule + ML Engine):** Combined decision logic where rule triggers adjust ML confidence scores and resolve boundary cases.
4. **Model D (Two-Stage Selective System):** Stage 1 local prefilter filtering out benign items, routing only candidate messages to Model C.

### Metrics Recorded
- **Accuracy, Precision, Recall, F1-Score** (Scam vs Ham)
- **False Positive Rate (FPR)** and **False Negative Rate (FNR)**
- **Confusion Matrix**
- **Backend Request Reduction Rate (%)**: $\frac{\text{Total Messages} - \text{Server Requests}}{\text{Total Messages}} \times 100\%$
- **Latency / Processing Time (ms)**: Local filter time vs Network + Server inference time.
- **Privacy Exposure Metric**: Total bytes transmitted across selective vs unrestricted pipelines.

---

## 7. Feasibility Constraints & Known Limitations

- **Notification Truncation:** Android notifications often truncate messages beyond ~200 characters. Long multi-paragraph phishing lures may have key scam elements outside the notification snippet.
- **Pre-filtering False Negatives:** Any aggressive local filter that discards subtle, conversational social engineering messages risks introducing false negatives. This trade-off will be explicitly measured and reported.
- **Zero OS Accessibility Exploitation:** Accessibility Services are deliberately avoided to adhere to Google Play Developer policies and user privacy boundaries.
- **Network Dependency:** Stage 2 requires network connectivity. Offline devices rely exclusively on Stage 1 local heuristic checks.
