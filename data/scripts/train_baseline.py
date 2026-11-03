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
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score
)
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt



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

    
    # 2. Tuned Word + Character TF-IDF + Linear SVM
    print("\n[2/2] Tuning Word + Character TF-IDF + Linear SVM...")

    features = FeatureUnion([
        ("word", TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            max_features=25000,
            min_df=2,
            sublinear_tf=True
        )),
        ("char", TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            max_features=35000,
            min_df=2,
            sublinear_tf=True
        )),
    ])

    pipeline = Pipeline([
        ("features", features),
        ("classifier", LinearSVC(
            random_state=42,
            max_iter=5000
        ))
    ])

    # Every candidate is evaluated using training data only.
    cv = StratifiedKFold(
        n_splits=3,
        shuffle=True,
        random_state=42
    )

    param_grid = {
        "classifier__C": [0.1, 0.3, 0.8, 1.0, 2.0],
        "classifier__class_weight": [None, "balanced"],
        "features__word__ngram_range": [(1, 1), (1, 2)],
        "features__char__ngram_range": [(2, 5), (3, 5)],
    }

    search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        scoring="f1_macro",
        cv=cv,
        n_jobs=-1,
        verbose=2,
        refit=True,
        error_score="raise"
    )

    search.fit(X_train, y_train)

    best_pipeline = search.best_estimator_
    y_pred_svm = best_pipeline.predict(X_test)

    print("\nBest CV Macro F1:", search.best_score_)
    print("Best parameters:", search.best_params_)

    print("\n--- Tuned SVM Test Evaluation ---")
    print("Accuracy:", accuracy_score(y_test, y_pred_svm))
    print("Macro F1:", f1_score(
        y_test, y_pred_svm, average="macro"
    ))
    print("Weighted F1:", f1_score(
        y_test, y_pred_svm, average="weighted"
    ))

    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred_svm, labels=classes)
    print(cm)

    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=classes
    )
    disp.plot(cmap="Blues", values_format="d")
    plt.tight_layout()
    plt.show()

    print("\nClassification Report:")
    print(classification_report(
        y_test,
        y_pred_svm,
        labels=classes,
        digits=4,
        zero_division=0
    ))

    # Preserve the bundle format used by the existing model loader.
    joblib.dump(
        {
            "vectorizer": best_pipeline.named_steps["features"],
            "classifier": best_pipeline.named_steps["classifier"],
            "classes": classes,
        },
        models_dir / "word_char_svm_calibrated.joblib"
    )

    print(f"\nModel bundles saved to {models_dir}")
