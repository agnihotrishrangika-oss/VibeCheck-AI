from pathlib import Path
import json
import numpy as np
import pandas as pd
import torch

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    DataCollatorWithPadding,
)

SEED = 42
MODEL_NAME = "google/muril-base-cased"
TRAIN_FILE = Path("data/processed/trac_train_safe.csv")
TEST_FILE = Path("data/processed/trac_test_safe.csv")
OUT_DIR = Path("experiments/muril_real_data_pilot")

LABELS = ["harassment", "hate_speech", "normal"]
LABEL2ID = {label: i for i, label in enumerate(LABELS)}
ID2LABEL = {i: label for label, i in LABEL2ID.items()}

# Reproducibility
np.random.seed(SEED)
torch.manual_seed(SEED)

print("Loading datasets...")
train_df = pd.read_csv(TRAIN_FILE).dropna(subset=["text", "label"]).copy()
test_df = pd.read_csv(TEST_FILE).dropna(subset=["text", "label"]).copy()

train_df["text"] = train_df["text"].astype(str).str.strip()
test_df["text"] = test_df["text"].astype(str).str.strip()
train_df = train_df[train_df["text"] != ""]
test_df = test_df[test_df["text"] != ""]

train_df = train_df[train_df["risk_label"].isin(LABELS)]
test_df = test_df[test_df["risk_label"].isin(LABELS)]

# Remove exact duplicate texts from training only.
train_df = train_df.drop_duplicates(subset=["text"]).reset_index(drop=True)

# Stratified 3,000-example pilot for a manageable CPU experiment.
pilot_df, _ = train_test_split(
    train_df,
    train_size=min(3000, len(train_df)),
    random_state=SEED,
    stratify=train_df["risk_label"],
)

print("Pilot training rows:", len(pilot_df))
print("Test rows:", len(test_df))
print("Training class counts:")
print(pilot_df["label"].value_counts())
print("Test class counts:")
print(test_df["label"].value_counts())

print("\nLoading tokenizer and MuRIL...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

class TextDataset(torch.utils.data.Dataset):
    def __init__(self, frame):
        self.texts = frame["text"].tolist()
        self.labels = [LABEL2ID[x] for x in frame["risk_label"].tolist()]

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        item = tokenizer(
            self.texts[idx],
            truncation=True,
            max_length=128,
        )
        item["labels"] = self.labels[idx]
        return item

train_dataset = TextDataset(pilot_df)
test_dataset = TextDataset(test_df)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=3,
    label2id=LABEL2ID,
    id2label=ID2LABEL,
)

args = TrainingArguments(
    output_dir=str(OUT_DIR),
    num_train_epochs=2,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=8,
    gradient_accumulation_steps=4,
    learning_rate=2e-5,
    weight_decay=0.01,
    eval_strategy="epoch",
    save_strategy="no",
    logging_strategy="steps",
    logging_steps=50,
    report_to="none",
    use_cpu=True,
    seed=SEED,
    data_seed=SEED,
    dataloader_num_workers=0,
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
)

print("\nStarting MuRIL pilot training...")
trainer.train()

print("\nEvaluating on the existing test split...")
pred = trainer.predict(test_dataset)
y_true = pred.label_ids
y_pred = np.argmax(pred.predictions, axis=1)

accuracy = accuracy_score(y_true, y_pred)
macro_f1 = f1_score(y_true, y_pred, average="macro")

print(f"\nMuRIL pilot accuracy: {accuracy:.4f} ({accuracy * 100:.2f}%)")
print(f"MuRIL pilot macro F1: {macro_f1:.4f}")
print("\nClassification report:")
print(classification_report(
    y_true,
    y_pred,
    labels=[0, 1, 2],
    target_names=LABELS,
    zero_division=0,
))
print("Confusion matrix (actual rows, predicted columns):")
print(confusion_matrix(y_true, y_pred, labels=[0, 1, 2]))

OUT_DIR.mkdir(parents=True, exist_ok=True)
results = {
    "model": MODEL_NAME,
    "training_examples": len(pilot_df),
    "test_examples": len(test_df),
    "epochs": 2,
    "accuracy": float(accuracy),
    "macro_f1": float(macro_f1),
    "label_order": LABELS,
    "prediction_counts": {
        LABELS[i]: int((y_pred == i).sum()) for i in range(3)
    },
}
with open(OUT_DIR / "metrics.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print(f"\nMetrics saved to: {OUT_DIR / 'metrics.json'}")
print("This experiment did not modify the production app or SVM.")
