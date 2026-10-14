# Dataset Provenance and Licensing Documentation
**Dataset:** SMS Spam Collection v.1 (UCI Machine Learning Repository)

---

## 1. Overview and Citation
- **Title:** SMS Spam Collection v.1
- **Source:** UCI Machine Learning Repository
- **URL:** https://archive.ics.uci.edu/dataset/228/sms+spam+collection
- **Original Authors & Researchers:**
  - Tiago A. Almeida (Federal University of Sao Carlos - UFSCar)
  - Jose Maria Gomez Hidalgo (R&D Department, Optenet)
  - Akebo Yamakami (University of Campinas - UNICAMP)
- **Primary Publication Citation:**
  > Almeida, T.A., Gómez Hidalgo, J.M., Yamakami, A. (2011). *Contributions to the Study of SMS Spam Filtering: New Collection and Results*. Proceedings of the 2011 ACM Symposium on Document Engineering (DocEng'11), Mountain View, CA, USA, pp. 259–262.

---

## 2. Permitted Usage and Licensing
- **License:** Open for academic, scientific, and educational research purposes (Public Domain / Attribution).
- **Compliance:** Used in this Bachelor's Thesis project strictly for training, benchmarking, and evaluating mobile scam and spam detection algorithms.

---

## 3. Dataset Characteristics and Statistics
- **Total Record Count:** 5,574 text messages
- **Class Labels:**
  - `ham`: 4,827 legitimate messages (86.6%)
  - `spam`: 747 unsolicited scam, phishing, promotion, or fraudulent messages (13.4%)
- **Message Language:** English
- **Data Source Distribution:**
  - 425 spam messages manually compiled from UK consumer complaints on Grumbletext.
  - 450 ham messages from Caroline Tagg's PhD corpus (University of Birmingham).
  - 3,375 ham messages from the NUS SMS Corpus (National University of Singapore).
  - 1,002 ham and 322 spam messages from the SMS Spam Corpus v.0.1 Small.

---

## 4. Preprocessing & Experimental Split Strategy
1. **Stratified Partitioning:**
   - 80% Training Set (4,459 messages: 3,861 ham, 598 spam/scam)
   - 20% Held-Out Test Set (1,115 messages: 966 ham, 149 spam/scam)
   - Stratified sampling ensures class proportion balance is strictly preserved between splits.
   - Random seed fixed at `42` for 100% reproducibility across all runs.
2. **Feature Extraction Pipeline:**
   - Case-folding and token normalization.
   - Word and character n-grams (unigrams and bigrams, $n \in [1, 2]$).
   - Sublinear term-frequency scaling ($\log(1 + tf)$) to prevent word repetition skew.
   - Minimum document frequency threshold ($min\_df=2$) to eliminate unique typos.
3. **Data Leakage Safeguards:**
   - Vectorizer is fitted strictly on the 80% training partition; held-out test data is transformed without fitting.
   - Heuristic rules and vocabulary thresholds are developed without tuning on the held-out test split.
