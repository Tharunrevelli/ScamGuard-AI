# ScamGuard AI: AI-Powered Scam Detection System
**Bachelor's Thesis Engineering Project**

[![Automated Tests](https://img.shields.io/badge/Tests-30%20Passed%20(100%25)-emerald.svg)](https://github.com)
[![Accuracy](https://img.shields.io/badge/Held--Out%20Accuracy-99.19%25-blue.svg)](docs/evaluation-results.md)
[![Traffic Reduction](https://img.shields.io/badge/Cloud%20Traffic%20Reduction-89.96%25-indigo.svg)](docs/evaluation-results.md)
[![Dataset](https://img.shields.io/badge/Dataset-UCI%20SMS%20Spam%20Corpus-orange.svg)](docs/research-plan.md)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

---

## 1. Executive Summary

**ScamGuard AI** is a privacy-conscious, event-driven scam detection system designed for modern Android and mobile web environments. Rather than naively streaming every private communication event to remote cloud servers, ScamGuard introduces a **Two-Stage Selective Architecture**:

1. **Stage 1 (Edge / On-Device Prefilter):** Inexpensive, explainable heuristic checks running on the client in **0.5ms** filter out clearly benign conversational messages locally.
2. **Stage 2 (Remote Hybrid Cloud Engine):** Candidate messages requiring verification are sanitized via client-side PII redaction and evaluated by a **Hybrid Rule + Calibrated Machine Learning Classifier**, achieving **99.19% detection accuracy** with an ultra-low **0.10% False Positive Rate**.

---

## 2. Core Research Question & Empirical Results

> **Research Question:**
> *Can a selective, event-driven scam detection architecture combining lightweight on-device prefiltering with remote machine learning reduce unnecessary backend requests and data exposure while maintaining acceptable scam detection performance on supported Android message sources?*

### Empirical Benchmark on Held-Out Test Set ($n=1,115$)
Evaluated on the genuine **UCI Machine Learning Repository SMS Spam Collection v.1** (5,574 authentic messages; 80% train / 20% test held-out split, random seed `42`):

| Model / Architecture | Accuracy | Precision | Recall | F1-Score | False Pos. Rate (FPR) | False Neg. Rate (FNR) | Server Calls ($n=1,115$) | Traffic Saved (%) | Avg Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Model 1: Rule-Based Baseline** | 87.35% | 100.00% | 5.37% | 10.19% | 0.00% | 94.63% | 0 | 100.0% | 0.05 ms |
| **Model 2: ML Classifier (TF-IDF + Calibrated LogReg)** | 98.92% | 97.24% | 94.63% | 95.92% | 0.41% | 5.37% | 1,115 | 0.0% | 4.43 ms |
| **Model 3: Hybrid Cloud Engine (Rules + ML)** | 99.19% | 99.30% | 94.63% | 96.91% | 0.10% | 5.37% | 1,115 | 0.0% | 6.59 ms |
| **Model 4: Two-Stage Selective (Stage 1 Edge + Stage 2 Remote)** | **94.53%** | **100.00%** | **59.06%** | **74.26%** | **0.00%** | **40.94%** | **112** | **89.96%** | **0.52 ms** |

### Addressing Professor Constraints: The False Negative Trade-Off
- **Finding:** Stage 1 local filtering achieves a verified **89.96% reduction in remote server calls**, processing ~90% of private chats 100% on-device with zero cloud exposure.
- **Trade-off:** Subtle conversational spam lacking links, urgency, or monetary tokens increases background False Negative Rate to 40.94%.
- **Architectural Safeguard:** Active user workflows (**Manual Paste** and **Share-to-App**) bypass Stage 1 and utilize the **99.19% accurate** cloud hybrid engine directly.

---

## 3. Technology Stack & Architectural Decisions

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Backend API** | **Python 3.13 / FastAPI / Uvicorn** | Native async IO, sub-millisecond route dispatch, auto OpenAPI documentation, in-process ML inference. |
| **Machine Learning** | **Scikit-Learn / NumPy** | TF-IDF n-grams + Calibrated Logistic Regression (Platt Sigmoid / 5-fold CV). Instant cold-start loading (<50ms), low memory footprint (<50MB). |
| **Rule Engine** | **Native Regex Heuristics** | Deterministic threat signals: urgency, 2FA/OTP harvesting, advance fees, obfuscated/IP URLs. |
| **Database** | **SQLite (WAL Mode)** | Zero raw text retention. Strictly stores SHA-256 session hash, timestamp, risk score, and latency. |
| **Android Client** | **Native Android (Kotlin / SDK 34)** | Direct integration with `NotificationListenerService` and `Intent.ACTION_SEND` (Share sheet), hardware-level background efficiency. |
| **Web Dashboard** | **HTML5 / Tailwind CSS / Vanilla JS** | Zero build-step overhead, responsive across desktop and mobile, served directly via FastAPI static files. |

---

## 4. Setup and Quickstart Instructions

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Modern web browser (Chrome, Edge, Firefox, Safari)
- *(Optional for Android build)*: Android Studio Iguana+ / JDK 17 / Android SDK 34

### Step 1: Clone and Install Dependencies
```powershell
git clone <repo-url>
cd D:\Project-1
python -m pip install -r backend/requirements.txt
```

### Step 2: Run Automated Tests
Execute the 30-test automated verification suite covering API contracts, rules, ML inference, privacy safeguards, and prefiltering:
```powershell
python -m pytest tests/ -v
```

### Step 3: Run or Re-Train ML Benchmark
The repository includes pre-trained model artifacts. To re-train or re-evaluate:
```powershell
# 1. Download genuine UCI SMS Spam Collection
python ml/download_dataset.py

# 2. Train model and generate calibrated artifacts
python ml/train.py

# 3. Run comparative 4-model evaluation benchmark
python ml/evaluate.py
```

### Step 4: Start the Backend & Web Application
```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
- **Web Dashboard:** Open [http://localhost:8000](http://localhost:8000)
- **API Documentation (Swagger UI):** Open [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 5. Demonstration Workflow for Professor & Committee

1. **Live Detection Demonstration:**
   - Open [http://localhost:8000](http://localhost:8000).
   - Test **"Bank Phishing"** preset -> Observe **`Likely Scam`** (Score: ~95/100), threat vector tags (`URGENCY_THREAT`, `IMPERSONATION`), and actionable recommendations.
   - Test **"OTP Stealer"** preset -> Observe `CRITICAL` severity rating on credential harvest.
   - Test **"Normal Chat"** preset with source *"Android Notification"* -> Observe **`Likely Safe`** under Stage 1 Local Filter (0.5ms on-device resolution).
   - Test **"Ambiguous"** preset (*"Ok call me"*) -> Observe **`Unable to Determine`** handling of contextual uncertainty.
2. **Privacy Redaction Verification:**
   - Toggle *"Redact PII Locally"* ON.
   - Input: *"Call +1-555-0199 or email alert@bank.com with card 4111-2222-3333-4444 to verify account."*
   - Verify that phone numbers, emails, and cards are masked while threat tokens and domain URLs remain intact for classification.
3. **Research Benchmark Inspection:**
   - Navigate to the **Research Benchmark** tab.
   - Review the empirical comparison table, confusion matrices, and the **89.96% server traffic reduction**.
4. **Interactive Batch Evaluator:**
   - Navigate to the **Batch Evaluator** tab.
   - Click *"Load Sample Batch"* and run benchmark to watch real-time partitioning between on-device filtering and cloud routing.

---

## 6. Supported Message Sources & Real Android Constraints

| Channel | Android Mechanism | Content Accessible | Authorization | Operating System Boundary |
| :--- | :--- | :--- | :--- | :--- |
| **Manual Input / Web** | Direct User Input | Complete text | None | Full text analyzed. |
| **Share Sheet** | `Intent.ACTION_SEND` | Text or URL shared from any app | User explicit action | Complete shared snippet analyzed. |
| **WhatsApp Notifications** | `NotificationListenerService` | Title & Notification text preview | Explicit user grant in Settings | Sandboxed: cannot read internal SQLite chat history; long messages truncated by WhatsApp. |
| **SMS Notifications** | `NotificationListenerService` | Sender & SMS preview | Explicit user grant in Settings | Safe preview access without requiring default SMS app permissions. |
| **Gmail Notifications** | `NotificationListenerService` | Subject & brief snippet | Explicit user grant in Settings | Sandboxed: email body and attachments are not accessible via status bar. |

---

## 7. Known Limitations and Future Work

1. **Multilingual Scams:** The current ML vectorizer and rule dictionary are trained primarily on English mobile corpora. Expanding to regional languages (e.g., Hindi, Spanish) is planned for future work.
2. **Conversational Social Engineering:** As reported in the thesis findings, social engineering scams devoid of links or urgency keywords require multi-turn conversational analysis.
3. **On-Device Compact ML:** Future iterations will evaluate quantizing lightweight ONNX or TensorFlow Lite models for local edge inference.
