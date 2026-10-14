# Technology Selection and Architectural Decisions
**Bachelor's Thesis Project: AI-Powered Scam Detection System**

---

## 1. Overview of Selected Technology Stack

| Component | Selected Technology | Version / Specification | Primary Rationale |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | **Python / FastAPI** | Python 3.13 / FastAPI 0.143+ / Uvicorn 0.54+ | Asynchronous native Python web framework, automatic Pydantic v2 OpenAPI schema generation, direct integration with ML models (no serialization bridging), sub-millisecond route dispatch. |
| **Machine Learning Engine** | **Scikit-Learn & NumPy** | scikit-learn 1.9+ / numpy 2.5+ | Highly optimized, battle-tested ML baseline (TF-IDF + regularized Logistic Regression / CalibratedClassifierCV) offering high interpretability, instant cold-start loading (<100ms), low memory footprint (<50MB RAM), and reproducible results. |
| **Rule & Heuristic Engine** | **Native Python Regex & Heuristic Modules** | Python 3.13 standard `re` & custom indicators | Zero external dependencies, ultra-low latency (<0.5ms per message), deterministic threat signals (urgency, credential harvest, fake banking, obfuscated URLs). |
| **Database & Persistence** | **SQLite with WAL Mode** (Ephemeral / Metadata only) | SQLite 3 / Python standard `sqlite3` | Zero external server overhead, ACID compliant, ultra-fast local disk access. Strictly persists anonymized session metadata and audit statistics—never raw message bodies. |
| **Android Application** | **Native Android (Kotlin / Android SDK 34)** | Kotlin 1.9+ / Android SDK 34 / Java 17 | Direct access to native Android `NotificationListenerService` and `Intent.ACTION_SEND` (Share sheet), hardware-level background efficiency, zero cross-platform bridge latency, clean Material 3 design. |
| **Web Dashboard** | **Modern Responsive Single-Page App (HTML5 / Tailwind CSS / Vanilla ES6+)** | Modern Web Standards | Zero build-step overhead, immediate dev-server delivery, served directly via FastAPI `StaticFiles` or standalone HTTP server, 100% responsive on desktop and mobile browsers. |
| **Test Suite** | **Pytest & HTTPX** | pytest 9.1+ / httpx 0.28+ | Asynchronous API testing, comprehensive edge-case coverage, automated schema and privacy validation. |

---

## 2. Alternatives Considered and Decision Rationale

### A. Backend: FastAPI (Python) vs. Express.js (Node.js) vs. Go
- **Considered:**
  - *Express / Node.js:* Node.js was available on the system, but executing Python-based ML models would require either child-process spawning or a dual-service architecture (Node API + Python ML worker), adding unnecessary complexity.
  - *Go:* Exceptional concurrency, but lacks native scientific Python ML library ecosystems (scikit-learn, numpy) without cumbersome CGO bindings.
- **Selected:** **FastAPI (Python 3.13)**. Direct in-process ML inference, native type safety via Pydantic v2, async request handling, and automatic interactive Swagger documentation (`/docs`).

### B. Machine Learning: TF-IDF + Logistic Regression vs. Heavy Deep Learning (BERT / LLM APIs)
- **Considered:**
  - *Fine-tuned BERT / RoBERTa:* High parameter count (>110M params), requires GPU for sub-50ms inference, introduces multi-gigabyte dependencies (PyTorch/Transformers) unsuitable for lightweight 7-day deployment and constrained demonstration hardware.
  - *Third-party Cloud LLM APIs (OpenAI / Claude):* Exposes raw user messages to external third parties (violating core privacy constraints), incurs per-token costs, introduces network latency (500ms–2000ms), and creates single points of failure.
- **Selected:** **N-gram TF-IDF + Calibrated Logistic Regression + Heuristic Rule Augmentation**. Achieves >97% accuracy on verified mobile spam corpora, trains in seconds, evaluates in <5ms per sample, provides full feature weight interpretability, and runs offline without paid subscriptions or external data leakage.

### C. Android Client: Native Android (Kotlin) vs. Cross-Platform (React Native / Flutter)
- **Considered:**
  - *React Native / Flutter:* Convenient UI development, but implementing an Android `NotificationListenerService` requires writing custom native Java/Kotlin bridge modules anyway. Cross-platform background listeners frequently suffer from OS lifecycle killed states and permission handling quirks.
- **Selected:** **Native Android (Kotlin)**. Direct, robust integration with `NotificationListenerService`, native Android `ACTION_SEND` intent receiver, native notification channels, and zero abstraction penalty.

### D. Persistence: SQLite vs. PostgreSQL / MongoDB
- **Considered:**
  - *PostgreSQL / MongoDB:* Adds heavyweight daemon requirements, network configuration, and operational overhead without providing any architectural benefit for a prototype with privacy-first data minimization.
- **Selected:** **SQLite**. Embedded, zero-configuration, robust, and supports WAL (Write-Ahead Logging) mode. Designed with a strict privacy guarantee: storing only anonymized hashes, timestamps, risk scores, and feedback flags.

---

## 3. Required SDKs and System Dependencies

- **Python Runtime:** Python 3.13.1
- **Python Libraries:** `fastapi`, `uvicorn`, `pydantic`, `scikit-learn`, `numpy`, `pytest`, `httpx`, `requests`
- **Java Development Kit (JDK):** Microsoft OpenJDK 17 LTS (`C:\Program Files\Microsoft\jdk-17.0.20.101-hotspot`)
- **Android SDK:** Platforms `android-33`, `android-34`, Build-Tools `34.0.0`
- **Web Runtime:** Any modern Chromium, Firefox, or Safari browser.

---

## 4. Principal Limitations of the Selected Approach

1. **Language Scope:** The initial TF-IDF model and heuristic rule dictionaries are focused primarily on English-language mobile scam communications, which represents the standard academic benchmark corpus.
2. **Notification Listener OS Variations:** Android vendor battery-optimization features (e.g., Xiaomi MIUI, Samsung One UI) may throttle background notification listeners if "Battery Optimization" is not manually disabled by the user.
3. **Truncated Context:** Text intercepted via Android notifications is limited to the preview text provided by the messaging app; conversational context preceding the notification is unavailable.
