"""
Data Ingestion and Preprocessing Pipeline for VibeCheck-AI.
Downloads and standardizes real public datasets:
- TRAC-1 Aggression Corpus (Kumar et al., 2018 - Facebook/Twitter Hindi & English/Hinglish)
- PRISM Hinglish Hate Speech Dataset (Biswas et al.)
"""

import os
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = DATA_DIR / "processed"
RAW_DIR = DATA_DIR / "raw"

TRAC_URL = "https://huggingface.co/api/datasets/HuggMachas/aggression-dataset/parquet/default/train/0.parquet"
PRISM_TRAIN_URL = "https://huggingface.co/api/datasets/pankajbiswas6/prism-hinglish-hate-speech/parquet/default/train/0.parquet"
PRISM_TEST_URL = "https://huggingface.co/api/datasets/pankajbiswas6/prism-hinglish-hate-speech/parquet/default/test/0.parquet"


def download_and_preprocess_trac():
    print("Fetching TRAC Aggression dataset from Hugging Face...")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(TRAC_URL)

    # Clean text
    df = df.dropna(subset=["text", "label"])
    df["text"] = df["text"].astype(str).str.strip()
    df = df[df["text"].str.len() > 3]

    # Map TRAC labels to research taxonomy
    label_map = {
        "NAG": "normal",
        "CAG": "harassment",
        "OAG": "hate_speech",
    }
    df["risk_label"] = df["label"].map(label_map)
    df = df.dropna(subset=["risk_label"])

    out_path = PROCESSED_DIR / "trac_aggression_processed.csv"
    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"Saved {len(df)} standardized TRAC samples to {out_path}")
    print("Label distribution:\n", df["risk_label"].value_counts())
    return df


def download_and_preprocess_prism():
    print("Fetching PRISM Hinglish dataset from Hugging Face...")
    df_tr = pd.read_parquet(PRISM_TRAIN_URL)
    df_te = pd.read_parquet(PRISM_TEST_URL)
    df = pd.concat([df_tr, df_te], ignore_index=True)

    df["text"] = df["text"].astype(str).str.strip()
    df = df.dropna(subset=["text", "label"])
    df = df[df["text"].str.len() > 3]

    df["risk_label"] = df["label"].map({0: "normal", 1: "hate_speech"})
    out_path = PROCESSED_DIR / "prism_hinglish_processed.csv"
    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"Saved {len(df)} standardized PRISM samples to {out_path}")
    return df


if __name__ == "__main__":
    download_and_preprocess_trac()
    download_and_preprocess_prism()
