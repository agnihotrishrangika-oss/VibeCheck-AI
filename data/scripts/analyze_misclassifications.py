from pathlib import Path
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)

base = Path(__file__).resolve().parent.parent.parent
data_path = base / "data" / "processed" / "trac_aggression_processed.csv"
model_path = base / "backend" / "app" / "models" / "saved_models" / "word_char_svm_calibrated.joblib"
output_path = base / "data" / "processed" / "svm_misclassified_examples.csv"

if not data_path.exists():
    raise FileNotFoundError(f"Dataset not found: {data_path}")
if not model_path.exists():
    raise FileNotFoundError(
        f"Saved model not found: {model_path}. Train the model first."
    )

df = pd.read_csv(data_path)

# Reproduce the same stratified split used by the training script.
X_train, X_test, y_train, y_test = train_test_split(
    df["text"],
    df["risk_label"],
    test_size=0.2,
    random_state=42,
    stratify=df["risk_label"],
)

bundle = joblib.load(model_path)
vectorizer = bundle["vectorizer"]
classifier = bundle["classifier"]

X_test_features = vectorizer.transform(X_test)
predictions = classifier.predict(X_test_features)

results = pd.DataFrame({
    "text": X_test.to_numpy(),
    "actual_label": y_test.to_numpy(),
    "predicted_label": predictions,
})

# Include source metadata when available.
if "source" in df.columns:
    results["source"] = df.loc[X_test.index, "source"].to_numpy()

results["is_correct"] = (
    results["actual_label"] == results["predicted_label"]
)

classes = list(bundle.get("classes", sorted(df["risk_label"].unique())))

print("\n--- Loaded model evaluation ---")
print("Test examples:", len(results))
print("Accuracy:", round(accuracy_score(y_test, predictions), 4))
print("Macro F1:", round(
    f1_score(y_test, predictions, average="macro"), 4
))

print("\nConfusion matrix (rows = actual, columns = predicted):")
print("Class order:", classes)
print(confusion_matrix(y_test, predictions, labels=classes))

print("\nClassification report:")
print(classification_report(
    y_test, predictions, labels=classes, digits=4, zero_division=0
))

# Focus on confusion between harassment and hate speech.
pair = results[
    results["actual_label"].isin(["harassment", "hate_speech"])
    & results["predicted_label"].isin(["harassment", "hate_speech"])
    & (results["actual_label"] != results["predicted_label"])
].copy()

print("\nHarassment <-> hate speech errors:", len(pair))
print("\nExample errors:")
for _, row in pair.head(10).iterrows():
    print(f"\nActual: {row['actual_label']} | Predicted: {row['predicted_label']}")
    print(str(row["text"])[:500])

errors = results[~results["is_correct"]].copy()
errors.to_csv(output_path, index=False)

print(f"\nAll misclassified examples saved to: {output_path}")
print(f"Total misclassified examples: {len(errors)}")
