"""
Advanced Multi-Modal ML Training Pipeline for Scam & Phishing Detection.
Trains a high-performance Calibrated Soft-Voting Ensemble (Logistic Regression + Complement Naive Bayes + Random Forest)
using a FeatureUnion of Word N-grams and Character N-grams on the unified UCI + Modern Scam Corpus.
"""
import os
import json
import joblib
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import ComplementNB
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UCI_DATA_PATH = os.path.join(BASE_DIR, "data", "SMSSpamCollection")
MODERN_DATA_PATH = os.path.join(BASE_DIR, "data", "modern_scam_corpus.json")
ARTIFACTS_DIR = os.path.join(os.path.dirname(BASE_DIR), "backend", "app", "ml", "artifacts")


def load_dataset():
    """Load both UCI gold-standard corpus and modern scam extension dataset."""
    texts = []
    labels = []  # 0 for ham/legitimate, 1 for scam/spam

    # 1. Load UCI SMS Spam Collection
    if not os.path.exists(UCI_DATA_PATH):
        raise FileNotFoundError(f"UCI dataset not found at {UCI_DATA_PATH}")

    with open(UCI_DATA_PATH, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t", 1)
            if len(parts) == 2:
                tag, text = parts
                tag = tag.strip().lower()
                text = text.strip()
                if tag in ("ham", "spam") and text:
                    labels.append(1 if tag == "spam" else 0)
                    texts.append(text)

    uci_count = len(texts)
    print(f"Loaded {uci_count} samples from UCI SMS Spam Collection.")

    # 2. Load Modern Scam Corpus Extension
    modern_count = 0
    if os.path.exists(MODERN_DATA_PATH):
        try:
            with open(MODERN_DATA_PATH, "r", encoding="utf-8") as f:
                modern_samples = json.load(f)
                for item in modern_samples:
                    t = item.get("text", "").strip()
                    lbl = item.get("label", 0)
                    if t:
                        texts.append(t)
                        labels.append(lbl)
                        modern_count += 1
            print(f"Enriched with {modern_count} modern 2026 smishing & interpersonal samples.")
        except Exception as e:
            print(f"Warning: Could not load modern corpus: {e}")

    return texts, labels


def train_advanced_pipeline():
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    texts, labels = load_dataset()
    total_samples = len(texts)
    spam_count = sum(labels)
    ham_count = total_samples - spam_count
    print(f"Total unified corpus: {total_samples} messages ({ham_count} ham, {spam_count} scam/spam).")

    # Stratified 80/20 train/test partition with deterministic seed 42
    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.20,
        random_state=42,
        stratify=labels
    )
    print(f"Partition: Train={len(X_train)} (Ham={y_train.count(0)}, Scam={y_train.count(1)}), Test={len(X_test)} (Ham={y_test.count(0)}, Scam={y_test.count(1)})")

    # Multi-Channel Feature Extraction Pipeline
    print("Configuring multi-channel FeatureUnion (Word TF-IDF + Character-WB TF-IDF)...")
    word_vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.90,
        sublinear_tf=True,
        token_pattern=r"(?u)\b\w+\b|[£\$€₹%]"
    )

    char_vectorizer = TfidfVectorizer(
        ngram_range=(3, 5),
        analyzer="char_wb",
        min_df=3,
        max_df=0.90,
        sublinear_tf=True
    )

    feature_union = FeatureUnion([
        ("word_features", word_vectorizer),
        ("char_features", char_vectorizer)
    ])

    # Fit feature representation
    print("Fitting feature representations on training partition...")
    X_train_vec = feature_union.fit_transform(X_train)
    X_test_vec = feature_union.transform(X_test)

    # Candidate Estimators for Soft-Voting Ensemble
    clf_lr = LogisticRegression(
        C=3.0,
        class_weight="balanced",
        max_iter=1000,
        solver="lbfgs",
        random_state=42
    )

    clf_cnb = ComplementNB(
        alpha=0.5,
        norm=True
    )

    clf_rf = RandomForestClassifier(
        n_estimators=120,
        max_depth=25,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    # Evaluate individual candidate estimators
    print("\nBenchmarking individual estimator candidates on training split (5-fold CV)...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    lr_cv = cross_val_score(clf_lr, X_train_vec, y_train, cv=cv, scoring="f1").mean()
    cnb_cv = cross_val_score(clf_cnb, X_train_vec, y_train, cv=cv, scoring="f1").mean()
    rf_cv = cross_val_score(clf_rf, X_train_vec, y_train, cv=cv, scoring="f1").mean()

    print(f" - Calibrated Logistic Regression 5-Fold F1: {lr_cv*100:.2f}%")
    print(f" - Complement Naive Bayes 5-Fold F1:         {cnb_cv*100:.2f}%")
    print(f" - Random Forest 5-Fold F1:                  {rf_cv*100:.2f}%")

    # Build Soft-Voting Ensemble
    print("\nBuilding Production Calibrated Soft-Voting Ensemble (Weights: LR=2, CNB=1, RF=1)...")
    ensemble = VotingClassifier(
        estimators=[
            ("lr", clf_lr),
            ("cnb", clf_cnb),
            ("rf", clf_rf)
        ],
        voting="soft",
        weights=[2, 1, 1]
    )

    # Fit ensemble with probability calibration
    calibrated_ensemble = CalibratedClassifierCV(
        estimator=ensemble,
        method="sigmoid",
        cv=3
    )
    calibrated_ensemble.fit(X_train_vec, y_train)

    # Also fit standalone Logistic Regression for interpretable feature weights
    clf_lr.fit(X_train_vec, y_train)

    # Assemble complete inference pipeline
    inference_pipeline = Pipeline([
        ("features", feature_union),
        ("ensemble", calibrated_ensemble)
    ])

    # Evaluate on held-out test split (20%)
    print("\nEvaluating Production Ensemble on Held-Out Test Split (n={})...".format(len(X_test)))
    y_pred = inference_pipeline.predict(X_test)
    y_prob = inference_pipeline.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred))
    rec = float(recall_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred))
    roc_auc = float(roc_auc_score(y_test, y_prob))
    cm = confusion_matrix(y_test, y_pred).tolist()

    tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]
    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

    print("=" * 65)
    print("PRODUCTION ENSEMBLE HELD-OUT PERFORMANCE:")
    print(f"Accuracy:         {acc * 100:.2f}%")
    print(f"Precision:        {prec * 100:.2f}%")
    print(f"Recall:           {rec * 100:.2f}%")
    print(f"F1-Score:         {f1 * 100:.2f}%")
    print(f"ROC-AUC:          {roc_auc * 100:.2f}%")
    print(f"False Pos. Rate:  {fpr * 100:.2f}% (FP: {fp} / TN: {tn})")
    print(f"False Neg. Rate:  {fnr * 100:.2f}% (FN: {fn} / TP: {tp})")
    print(f"Confusion Matrix: TN={tn}, FP={fp}, FN={fn}, TP={tp}")
    print("=" * 65)

    # Extract word feature weights for explainability
    word_feature_names = np.array(word_vectorizer.get_feature_names_out())
    # The first len(word_feature_names) features in X_train_vec correspond to word features
    word_count_len = len(word_feature_names)
    word_coefs = clf_lr.coef_[0][:word_count_len]

    top_spam_indices = np.argsort(word_coefs)[-30:][::-1]
    top_ham_indices = np.argsort(word_coefs)[:30]

    top_spam_features = [{"feature": str(word_feature_names[i]), "weight": float(word_coefs[i])} for i in top_spam_indices]
    top_ham_features = [{"feature": str(word_feature_names[i]), "weight": float(word_coefs[i])} for i in top_ham_indices]

    # Save artifacts
    model_output_path = os.path.join(ARTIFACTS_DIR, "model.joblib")
    metrics_output_path = os.path.join(ARTIFACTS_DIR, "metrics.json")
    features_output_path = os.path.join(ARTIFACTS_DIR, "feature_weights.json")
    ensemble_breakdown_path = os.path.join(ARTIFACTS_DIR, "ensemble_breakdown.json")

    joblib.dump(inference_pipeline, model_output_path)
    print(f"Saved production ensemble pipeline to: {model_output_path}")

    metrics_payload = {
        "model_name": "Calibrated_SoftVoting_Ensemble",
        "architecture": "Multi-Channel FeatureUnion (Word (1,2) + Char_wb (3,5)) + Calibrated VotingClassifier [LR + CNB + RF]",
        "dataset_name": "Unified UCI SMS Spam Collection v.1 + 2026 Modern Scam Corpus",
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "total_samples": total_samples,
        "class_distribution": {"ham": ham_count, "spam": spam_count},
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "confusion_matrix": {
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn,
            "true_positives": tp,
        },
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4),
        "cross_validation_f1": {
            "logistic_regression": round(lr_cv, 4),
            "complement_naive_bayes": round(cnb_cv, 4),
            "random_forest": round(rf_cv, 4),
        }
    }

    with open(metrics_output_path, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)

    with open(features_output_path, "w", encoding="utf-8") as f:
        json.dump({
            "top_spam_indicators": top_spam_features,
            "top_ham_indicators": top_ham_features
        }, f, indent=2)

    with open(ensemble_breakdown_path, "w", encoding="utf-8") as f:
        json.dump({
            "estimators": [
                {"name": "Calibrated Logistic Regression", "weight": 2, "cv_f1": round(lr_cv, 4), "role": "Linear boundary & calibrated Platt scaling"},
                {"name": "Complement Naive Bayes", "weight": 1, "cv_f1": round(cnb_cv, 4), "role": "High-speed Bayesian generative prior for imbalanced data"},
                {"name": "Random Forest Classifier", "weight": 1, "cv_f1": round(rf_cv, 4), "role": "Non-linear interaction modeling & adversarial evasion defense"}
            ],
            "ensemble_f1": round(f1, 4),
            "ensemble_accuracy": round(acc, 4)
        }, f, indent=2)

    print(f"Saved evaluation metrics to: {metrics_output_path}")
    print(f"Saved feature interpretability weights to: {features_output_path}")
    print(f"Saved ensemble architecture breakdown to: {ensemble_breakdown_path}")

    return metrics_payload


if __name__ == "__main__":
    train_advanced_pipeline()
