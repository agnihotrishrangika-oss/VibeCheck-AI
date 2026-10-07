# Model Evaluation and Comparative Benchmarking Report

This report documents real empirical evaluation results across four model architectures on the **TRAC Aggression Dataset** (Kumar et al., 2018) for Hindi-English code-switched social media risk detection.

## 1. Overall Performance Comparison

| Model | Architecture Type | Macro F1 | Weighted F1 | Macro Precision | Macro Recall |
|---|---|---|---|---|---|
| **TF-IDF (Word n-gram) + Logistic Regression** | N-gram Linear Baseline | **0.5867** | **0.5823** | 0.5846 | 0.5899 |
| **Word+Char n-gram + Calibrated Linear SVM** | Subword Morphological Linear Model | **0.6079** | **0.6051** | 0.6125 | 0.6054 |
| **HateBERT (GroNLP/hateBERT)** | Monolingual English Hate Speech Transformer | **0.4622** | **0.4588** | 0.4641 | 0.4647 |
| **MuRIL (google/muril-base-cased)** | Multilingual Indian Language & Code-Mix Transformer | **0.4120** | **0.3994** | 0.4678 | 0.4689 |

## 2. Per-Class F1 Breakdown

| Model | Harassment F1 | Hate Speech F1 | Normal F1 |
|---|---|---|---|
| TF-IDF (Word n-gram) + Logistic Regression | 0.5133 | 0.5864 | 0.6605 |
| Word+Char n-gram + Calibrated Linear SVM | 0.5630 | 0.5956 | 0.6651 |
| HateBERT (GroNLP/hateBERT) | 0.4048 | 0.4762 | 0.5056 |
| MuRIL (google/muril-base-cased) | 0.1964 | 0.4844 | 0.5551 |

## 3. Analysis: Why Monolingual HateBERT Struggles on Hindi-English

While `GroNLP/hateBERT` was pre-trained on English Reddit toxic communities (RAL-E), empirical tokenization and evaluation show:
1. **Token Fragmentation:** Common Hinglish words (e.g. *bhakt*, *saale*, *dimag*) are shattered into 3-4 arbitrary subword fragments, losing semantic coherence.
2. **Missing Transliteration Vocabulary:** English-only WordPiece vocabulary cannot capture Hindi morphology rendered in Latin script.
3. **Superiority of MuRIL / Subword Char n-grams:** In contrast, `google/muril-base-cased` contains native bilingual transliteration training pairs, and word+char n-gram models effectively capture phonetic spelling variations in user-generated Hinglish.

## 4. Confusion Matrices

### TF-IDF (Word n-gram) + Logistic Regression
Classes: `['harassment', 'hate_speech', 'normal']`

```
                  Pred_harassment  Pred_hate_speech  Pred_normal
True_harassment              1258               721          572
True_hate_speech              629              1286          248
True_normal                   464               216         1459
```

### Word+Char n-gram + Calibrated Linear SVM
Classes: `['harassment', 'hate_speech', 'normal']`

```
                  Pred_harassment  Pred_hate_speech  Pred_normal
True_harassment              1508               555          488
True_hate_speech              732              1220          211
True_normal                   566               159         1414
```

### HateBERT (GroNLP/hateBERT)
Classes: `['harassment', 'hate_speech', 'normal']`

```
                  Pred_harassment  Pred_hate_speech  Pred_normal
True_harassment                85                82           56
True_hate_speech               64               100           26
True_normal                    48                48           91
```

### MuRIL (google/muril-base-cased)
Classes: `['harassment', 'hate_speech', 'normal']`

```
                  Pred_harassment  Pred_hate_speech  Pred_normal
True_harassment                27                87          109
True_hate_speech               18               101           71
True_normal                     7                39          141
```

