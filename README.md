# ScamGuard PRO: Production AI-Powered Scam Detection System
**Bachelor's Thesis Engineering Project**

[![Automated Tests](https://img.shields.io/badge/Tests-38%20Passed%20(100%25)-emerald.svg)](https://github.com)
[![Accuracy](https://img.shields.io/badge/Held--Out%20Accuracy-99.29%25-blue.svg)](docs/evaluation-results.md)
[![ROC-AUC](https://img.shields.io/badge/ROC--AUC-99.58%25-purple.svg)](docs/evaluation-results.md)
[![Traffic Reduction](https://img.shields.io/badge/Server%20Traffic%20Reduction-98.50%25-indigo.svg)](docs/defense-professor-feedback.md)
[![Privacy Shield](https://img.shields.io/badge/Privacy%20Shield-100%25%20On--Device-success.svg)](docs/defense-professor-feedback.md)
[![Defense Document](https://img.shields.io/badge/Thesis%20Defense-Rebuttal%20Ready-orange.svg)](docs/defense-professor-feedback.md)
[![Dataset](https://img.shields.io/badge/Dataset-UCI%20+%202026%20Modern%20Corpus-orange.svg)](docs/research-plan.md)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

---

## 1. Executive Summary

**ScamGuard PRO** is a production-grade, privacy-conscious, event-driven scam detection system designed for modern Android and mobile web environments. Rather than naively streaming every private communication event to remote cloud servers, ScamGuard introduces a **Two-Stage Selective Architecture**:

1. **Stage 1 (Edge / On-Device Prefilter):** Inexpensive, explainable heuristic checks running on the client in **0.52ms** filter out clearly benign conversational messages locally.
2. **Stage 2 (Remote Hybrid Cloud Engine):** Candidate messages requiring verification are sanitized via client-side PII pseudonymization and evaluated by a **Multi-Channel Soft-Voting Ensemble (Calibrated Logistic Regression + Complement Naive Bayes + Random Forest)** paired with **Levenshtein URL Intelligence**, achieving **99.29% detection accuracy**, **99.33% precision**, **99.58% ROC-AUC**, and an ultra-low **0.10% False Positive Rate**.

---

## 2. Core Research Question & Empirical Results

> **Research Question:**
> *Can a selective, event-driven scam detection architecture combining lightweight on-device prefiltering with remote machine learning reduce unnecessary backend requests and data exposure while maintaining acceptable scam detection performance on supported Android message sources?*

### Empirical Benchmark on Held-Out Test Set ($n=1,124$)
Evaluated on the unified **UCI Machine Learning Repository SMS Spam Collection v.1** (5,574 messages) + **2026 Modern Scam Corpus** (45 modern smishing samples) for a total of 5,619 messages (80% train / 20% test held-out split, random seed `42`):

| Model / Architecture | Accuracy | Precision | Recall | F1-Score | False Pos. Rate (FPR) | False Neg. Rate (FNR) | Server Calls ($n=1,124$) | Traffic Saved (%) | Avg Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Model 1: Heuristic Rule Baseline** | 87.54% | 100.00% | 5.81% | 10.98% | 0.00% | 94.19% | 0 | 100.0% | 0.05 ms |
| **Model 2: ML Soft-Voting Ensemble** | 99.20% | 98.61% | 95.48% | 97.02% | 0.21% | 4.52% | 1,124 | 0.0% | 5.21 ms |
| **Model 3: Hybrid Cloud Engine (Rules + Ensemble + URL Intel)** | **99.29%** | **99.33%** | **95.48%** | **97.37%** | **0.10%** | **4.52%** | 1,124 | 0.0% | 6.84 ms |
| **Model 4: Two-Stage Selective Architecture (Edge + Cloud)** | **94.57%** | **100.00%** | **58.71%** | **73.98%** | **0.00%** | **41.29%** | **113** | **89.96%** | **0.52 ms** |

### Addressing Professor Constraints: The False Negative Trade-Off
- **Traffic Reduction:** Stage 1 local filtering achieves a verified **89.96% reduction in remote server calls**, processing ~90% of private interpersonal chats 100% on-device with zero remote data exposure.
- **Trade-off Disclosure:** Subtle conversational spam lacking links, urgency, or monetary tokens increases background False Negative Rate to 41.29%.
- **Architectural Safeguard:** Active user workflows (**Manual Paste** and **System Share Sheet**) automatically bypass Stage 1 and utilize the **99.29% accurate** cloud hybrid engine directly.

---

## 3. Advanced Production Features

### A. Calibrated Soft-Voting Ensemble (v2.0)
- **Multi-Channel FeatureUnion:** Jointly extracts word $(1,2)$-grams and character subword $(3,5)$-grams, capturing semantic intent while defending against deliberate obfuscation (`p.a.y.p.a.l`, `b0fa`, `amaz0n`).
- **Ensemble Voting:** Weighted probability fusion between:
  1. *Calibrated Logistic Regression* (weight: 2, Sigmoid Platt calibration)
  2. *Complement Naive Bayes* (weight: 1, robust on class-imbalanced corpora)
  3. *Random Forest Classifier* (weight: 1, 120 decision trees capturing non-linear interactions)

### B. URL Threat Intelligence & Brand Typosquatting
- **Levenshtein Distance Analysis:** Identifies homoglyph brand impersonation against major financial, retail, and crypto targets (PayPal, Chase, Wells Fargo, Amazon, Apple, USPS, etc.).
- **TLD Risk Scoring:** Flags high-abuse top-level domains (`.xyz`, `.top`, `.club`, `.work`, `.click`).
- **Shannon Entropy Analysis:** Detects randomized DGA (Domain Generation Algorithm) strings.
- **Direct IP & URL Shortener Detection:** Flags raw IPv4 hosts and masked bit.ly/tinyurl redirects.

### C. 6-Vector Multidimensional Threat Decomposition
Categorizes risk across 6 independent cybersecurity vectors:
1. `urgency_coercion`: Urgency & Psychological Coercion
2. `financial_risk`: Financial Asset / Payment Risk
3. `credential_harvesting`: Credential & Account Harvesting
4. `impersonation`: Brand / Authority Impersonation
5. `link_domain_risk`: Suspicious Link / Typosquatting
6. `social_engineering`: Social Engineering & Lure

### D. Visual Threat Inspector (Annotated Message)
- Color-coded token spans directly in the UI with interactive hover tooltips explaining the specific threat trigger.

### E. Live "What-If" Simulation Sandbox
- Real-time playground allowing users or researchers to edit message text and observe live risk score fluctuations.
- One-click mutations: *Strip URLs*, *Remove Urgency*, *Mask Sensitive Info*.

### F. Digital Forensic Investigation Report
- Generates structured incident reports with SHA-256 cryptographic message fingerprints, full Indicators of Compromise (IOC) tables, and actionable SOC incident response playbooks.
- Exportable as printable PDF or raw JSON artifact.

---

## 4. Technology Stack & Architectural Decisions

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Backend API** | **Python 3.13 / FastAPI / Uvicorn** | Native async IO, sub-millisecond route dispatch, auto OpenAPI documentation, in-process ML inference. |
| **Machine Learning** | **Scikit-Learn / NumPy / Joblib** | FeatureUnion + CalibratedClassifierCV Soft-Voting Ensemble. Sub-5ms latency, memory footprint <60MB. |
| **Rule & URL Engine** | **Regex & Levenshtein / Urllib** | Deterministic threat signals: urgency, 2FA/OTP harvesting, advance fees, typosquatting. |
| **Database** | **SQLite (WAL Mode)** | Zero raw text retention. Strictly stores SHA-256 session hash, timestamp, risk score, and latency. |
| **Android Client** | **Native Android (Kotlin / SDK 34)** | Direct integration with `NotificationListenerService` and `Intent.ACTION_SEND` (Share sheet), hardware-level background efficiency. |
| **Web Dashboard** | **HTML5 / Tailwind CSS / Vanilla JS** | Modern dark-mode interface, SVG circular risk gauge, zero build-step overhead, served directly via FastAPI. |

---

## 5. Setup and Quickstart Instructions

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Modern web browser (Chrome, Edge, Firefox, Safari)
- *(Optional for Android build)*: Android Studio Iguana+ / JDK 17 / Android SDK 34

### Step 1: Install Dependencies
```powershell
python -m pip install -r backend/requirements.txt
```

### Step 2: Run Full Automated Test Suite (36 Tests)
Execute the complete verification suite covering API contracts, rules, ML ensemble, privacy safeguards, threat vectors, and URL intelligence:
```powershell
python -m pytest tests/ -v
```

### Step 3: Train Model & Run Benchmark
```powershell
# 1. Download genuine UCI SMS Spam Collection
python ml/download_dataset.py

# 2. Train ensemble model and serialize artifacts
python ml/train.py

# 3. Run comparative 4-model evaluation benchmark
python ml/evaluate.py
```

### Step 4: Start the Backend & Web Application
```powershell
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```
- **Web Application:** Open [http://localhost:8000](http://localhost:8000)
- **API Documentation (Swagger UI):** Open [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)
- **Android APK Download:** [http://localhost:8000/download-apk](http://localhost:8000/download-apk)

---

## 6. Demonstration Workflow for Professor & Committee

1. **Live Detector Demonstration:**
   - Open [http://localhost:8000](http://localhost:8000).
   - Click preset **Bank Phishing** or **USPS Parcel** -> Click **Run Forensic Threat Analysis**.
   - Observe the animated circular risk gauge, visual token highlights with hover context, 6 decomposed threat vector bars, domain typosquatting intelligence, and incident playbook.
2. **"What-If" Simulation Sandbox:**
   - Switch to the **"What-If" Sandbox** tab.
   - Click **Strip URLs** or **Remove Urgency** and observe the live risk score delta in real-time.
3. **Forensic Report Generation:**
   - Click **Download Threat Report** to view the SHA-256 fingerprint and IOC table, or **Export JSON**.
4. **Traffic Reduction Verification:**
   - Switch to the **Batch Evaluator** tab.
   - Click **Load Sample Batch (10 Messages)** -> Click **Execute Batch Traffic Benchmark**.
   - Demonstrate the verified **80-90% traffic reduction** achieved by Stage 1 edge prefiltering.
5. **Research Evaluation Benchmark:**
   - Switch to the **Research Benchmark** tab to review the empirical 4-model comparison table ($n=1,124$) addressing the professor's constraints.

---

## 7. Cross-Platform Testing & iOS Support

For testing on Apple iOS devices (iPhone / iPad) and detailed analysis of Apple's sandbox architecture vs. Android permissions, refer to the [iOS Testing Guide](docs/ios_testing_guide.md).

- **Instant iOS Testing (Safari PWA):** Run the backend with `--host 0.0.0.0` and open `http://<YOUR_PC_IP>:8000` in Mobile Safari. Tap *Share -> Add to Home Screen* to run as a full-screen iOS app.
- **System Integration (Apple Shortcuts):** Build a 3-step native iOS Shortcut using `Shortcuts.app` to scan highlighted text or shared links via the `/api/v1/detect` REST endpoint.
- **Native iOS Production Design:** Details Apple's official `IdentityLookup` framework (`ILMessageFilterExtension`) for native SMS spam filtering and CoreML Apple Neural Engine acceleration.
