"""
Train and export the Machine Learning model pipeline on the genuine UCI SMS Spam Collection dataset.
Uses TF-IDF n-grams + regularized Logistic Regression with calibrated probabilities.
"""
import os
import json
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "SMSSpamCollection")
ARTIFACTS_DIR = os.path.join(os.path.dirname(BASE_DIR), "backend", "app", "ml", "artifacts")


def load_dataset(file_path: str):
    """Load and parse the tab-separated SMSSpamCollection file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found at {file_path}. Run download_dataset.py first.")

    texts = []
    labels = []  # 0 for ham, 1 for spam/scam

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
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

    return texts, labels


def train_and_evaluate():
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    print(f"Loading dataset from: {DATA_PATH}")
    texts, labels = load_dataset(DATA_PATH)
    total_samples = len(texts)
    spam_count = sum(labels)
    ham_count = total_samples - spam_count
    print(f"Loaded {total_samples} samples: {ham_count} ham ({(ham_count/total_samples)*100:.1f}%), {spam_count} spam/scam ({(spam_count/total_samples)*100:.1f}%)")

    # Stratified 80/20 train/test split with deterministic seed
    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.20,
        random_state=42,
        stratify=labels
    )
    print(f"Split sizes: Train={len(X_train)} (Ham: {y_train.count(0)}, Spam: {y_train.count(1)}), Test={len(X_test)} (Ham: {y_test.count(0)}, Spam: {y_test.count(1)})")

    # Feature extraction: word n-grams (1-2), min_df=2 to drop rare typos, sublinear TF scaling
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.90,
        sublinear_tf=True,
        token_pattern=r"(?u)\b\w+\b|[£\$€₹%]"
    )

    # Base classifier with balanced class weighting to address imbalance (86.6% ham vs 13.4% spam)
    base_clf = LogisticRegression(
        C=2.5,
        class_weight="balanced",
        max_iter=1000,
        solver="lbfgs",
        random_state=42
    )

    # Build and fit pipeline
    print("Vectorizing and training base Logistic Regression model...")
    X_train_vec = vectorizer.fit_transform(X_train)
    base_clf.fit(X_train_vec, y_train)

    # Probability calibration using 5-fold cross-validation calibration via CalibratedClassifierCV
    calibrated_clf = CalibratedClassifierCV(estimator=base_clf, method="sigmoid", cv=5)
    calibrated_clf.fit(X_train_vec, y_train)

    # Pack into complete inference pipeline
    pipeline = Pipeline([
        ("vectorizer", vectorizer),
        ("classifier", calibrated_clf)
    ])

    # Evaluate on held-out test split
    print("Evaluating model on held-out test set (20%)...")
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred))
    rec = float(recall_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred))
    roc_auc = float(roc_auc_score(y_test, y_prob))
    cm = confusion_matrix(y_test, y_pred).tolist()  # [[TN, FP], [FN, TP]]

    tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]
    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

    print("=" * 60)
    print("HELD-OUT EVALUATION METRICS:")
    print(f"Accuracy:         {acc * 100:.2f}%")
    print(f"Precision:        {prec * 100:.2f}%")
    print(f"Recall:           {rec * 100:.2f}%")
    print(f"F1-Score:         {f1 * 100:.2f}%")
    print(f"ROC-AUC:          {roc_auc * 100:.2f}%")
    print(f"False Pos. Rate:  {fpr * 100:.2f}% (FP: {fp} / TN: {tn})")
    print(f"False Neg. Rate:  {fnr * 100:.2f}% (FN: {fn} / TP: {tp})")
    print(f"Confusion Matrix: TN={tn}, FP={fp}, FN={fn}, TP={tp}")
    print("=" * 60)

    # Extract top feature weights for model interpretability
    feature_names = np.array(vectorizer.get_feature_names_out())
    coefs = base_clf.coef_[0]
    top_spam_indices = np.argsort(coefs)[-25:][::-1]
    top_ham_indices = np.argsort(coefs)[:25]

    top_spam_features = [{"feature": str(feature_names[i]), "weight": float(coefs[i])} for i in top_spam_indices]
    top_ham_features = [{"feature": str(feature_names[i]), "weight": float(coefs[i])} for i in top_ham_indices]

    # Save artifacts
    model_output_path = os.path.join(ARTIFACTS_DIR, "model.joblib")
    metrics_output_path = os.path.join(ARTIFACTS_DIR, "metrics.json")
    features_output_path = os.path.join(ARTIFACTS_DIR, "feature_weights.json")

    joblib.dump(pipeline, model_output_path)
    print(f"Saved trained pipeline to: {model_output_path}")

    metrics_payload = {
        "model_name": "TFIDF_CalibratedLogisticRegression",
        "dataset_name": "SMS Spam Collection v.1 (UCI ML Repository)",
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
    }

    with open(metrics_output_path, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)

    with open(features_output_path, "w", encoding="utf-8") as f:
        json.dump({
            "top_spam_indicators": top_spam_features,
            "top_ham_indicators": top_ham_features
        }, f, indent=2)

    print(f"Saved evaluation metrics to: {metrics_output_path}")
    print(f"Saved feature interpretability weights to: {features_output_path}")

    return metrics_payload


if __name__ == "__main__":
    train_and_evaluate()
