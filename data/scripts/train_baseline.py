"""
Training pipeline for VibeCheck-AI Risk Classification Models.
Trains:
  1. TF-IDF (Word n-gram) + Logistic Regression Baseline
  2. TF-IDF (Word + Char-wb n-gram) + Calibrated Linear SVM
Saves model bundles to backend/app/models/saved_models/
"""

import time
from pathlib import Path
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report, f1_score


def train_models():
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_path = base_dir / "data" / "processed" / "trac_aggression_processed.csv"
    if not data_path.exists():
        from preprocess import download_and_preprocess_trac
        download_and_preprocess_trac()

    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} samples from {data_path}")

    # Stratified 80/20 train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["risk_label"], test_size=0.2, random_state=42, stratify=df["risk_label"]
    )
    classes = sorted(df["risk_label"].unique())

    models_dir = base_dir / "backend" / "app" / "models" / "saved_models"
    models_dir.mkdir(parents=True, exist_ok=True)

    # 1. TF-IDF + Logistic Regression
    print("\n[1/2] Training TF-IDF (Word) + Logistic Regression...")
    vec_word = TfidfVectorizer(ngram_range=(1, 2), max_features=25000, sublinear_tf=True)
    X_tr_w = vec_word.fit_transform(X_train)
    X_te_w = vec_word.transform(X_test)

    clf_lr = LogisticRegression(C=2.0, max_iter=1000, class_weight="balanced", random_state=42)
    clf_lr.fit(X_tr_w, y_train)
    y_pred_lr = clf_lr.predict(X_te_w)

    print("Baseline LogReg Macro F1:", f1_score(y_test, y_pred_lr, average="macro"))
    joblib.dump(
        {"vectorizer": vec_word, "classifier": clf_lr, "classes": classes},
        models_dir / "tfidf_logreg_baseline.joblib"
    )

    # 2. Word + Char TF-IDF + Calibrated Linear SVM
    print("\n[2/2] Training Word + Char TF-IDF + Calibrated Linear SVM...")
    union = FeatureUnion([
        ("word", TfidfVectorizer(ngram_range=(1, 2), analyzer="word", max_features=25000, sublinear_tf=True)),
        ("char", TfidfVectorizer(ngram_range=(3, 5), analyzer="char_wb", max_features=35000, sublinear_tf=True)),
    ])
    X_tr_wc = union.fit_transform(X_train)
    X_te_wc = union.transform(X_test)

    base_svm = LinearSVC(C=0.8, class_weight="balanced", random_state=42, max_iter=2000)
    calibrated_svm = CalibratedClassifierCV(base_svm, cv=3)
    calibrated_svm.fit(X_tr_wc, y_train)
    y_pred_svm = calibrated_svm.predict(X_te_wc)

    print("Calibrated SVM Macro F1:", f1_score(y_test, y_pred_svm, average="macro"))
    print("\nClassification Report (Calibrated SVM):")
    print(classification_report(y_test, y_pred_svm, digits=4))

    joblib.dump(
        {"vectorizer": union, "classifier": calibrated_svm, "classes": classes},
        models_dir / "word_char_svm_calibrated.joblib"
    )
    print(f"\nModel bundles saved to {models_dir}")


if __name__ == "__main__":
    train_models()
