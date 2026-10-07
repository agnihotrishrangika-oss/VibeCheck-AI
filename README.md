# VibeCheck-AI: Adaptive Multimodal Content-Risk Detection & Multi-Platform Policy Engine

**A Research-Grade Adaptive Multimodal Content-Risk Moderation System for Short Hindi-English (Hinglish) and Code-Switched Social Media Videos.**

---

## 1. Problem Statement & Motivation

Short-form video platforms (YouTube Shorts, Instagram Reels, TikTok) have experienced explosive growth in multilingual, code-switched content—especially across Indo-Aryan languages like Hindi-English ("Hinglish"). Hinglish speech exhibits complex linguistic phenomena:
1. **Phonetic and Transliterated Orthography:** When code-switched speech is transcribed or rendered into text, non-standard Romanized spelling variations (*"bhai"*, *"bhaii"*, *"kya"*, *"kyaa"*, *"saale"*, *"dimag"*) break standard monolingual vocabularies.
2. **Cultural Nuance & Sarcasm:** Colloquial slurs, dog-whistles, and localized harassment can easily evade generic keyword filters.
3. **Subword Fragmentation Pathology in Monolingual Models:** Standard English models (such as HateBERT) fragment transliterated Hindi roots into disconnected subword tokens, degrading performance.
4. **Policy Divergence Across Platforms:** A detected risk event is not treated uniformly across platforms. YouTube Community Guidelines and Meta/Instagram Community Standards have differing thresholds, protected characteristics, and exception structures (e.g. Meta's distinction between public figures and private individuals, YouTube's 3-strike penalty system).

### The Foundational Principle: `Detection ≠ Policy ≠ Action`

```
   ┌─────────────────────────────────────────────────────────────┐
   │                     1. DETECTION                            │
   │   ML Model determines WHAT happened in speech/video.         │
   │   (e.g., timestamp: 14.2–18.7s, label: harassment, conf: 0.87)│
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                       2. POLICY                             │
   │   Independent Engine evaluates prospective alignment        │
   │   against explicit, platform-specific Community Guidelines. │
   │   (Evaluates YouTube and Meta guidelines independently)     │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                       3. ACTION                             │
   │   Human moderation queue / Platform enforcement authority.   │
   │   (NEVER guaranteed or predicted by VibeCheck-AI).          │
   └─────────────────────────────────────────────────────────────┘
```

---

## 2. End-to-End Pipeline Architecture

```
                 Short Social Video (MP4 / MOV / WebM)
                                   │
                                   ▼
                 [ Step 1: Input Validation & FFmpeg ]
                 - Video duration check (≤ 60s)
                 - Audio stream demuxing: 16 kHz Mono PCM WAV
                                   │
                                   ▼
                 [ Step 2: faster-whisper ASR Engine ]
                 - Word-level & segment timestamps
                 - VAD (Voice Activity Detection) filter
                 - Original language transcription (preserves code-switching)
                                   │
                                   ▼
                 [ Step 3: Segment-Level ML Risk Classifier ]
                 - Subword Morphological Word+Char Calibrated Model
                 - Outputs calibrated probability distributions over:
                   {normal, harassment, hate_speech}
                                   │
                                   ▼
                 [ Step 4: Temporal Postprocessor ]
                 - Confidence threshold filtering
                 - Temporal merging of adjacent risk segments (gap ≤ 1.0s)
                 - Exact timestamp preservation [start, end]
                                   │
                                   ▼
                 [ Step 5: Independent Policy Engine ]
                  Identical Timestamps & Detected Risk
                     ↙                           ↘
         [ YouTube Policy Layer ]      [ Meta/Instagram Policy Layer ]
         - Rule YT-HATE-01             - Standard 13: Hate Speech
         - Rule YT-HARASS-01           - Standard 14: Bullying & Harass
         - Rule YT-THREAT-01           - Standard 1: Violence & Threat
         - EDSA Exception Checks       - Tier System & Public Figure Test
                     ↘                           ↙
                 [ Step 6: Interactive Dashboard & History ]
                 - Synchronized seekable video playback
                 - Dynamic temporal risk timeline with clickable seek
                 - Side-by-side platform policy comparison
                 - Policy adaptation experiment (v1 vs v2 simulation)
                 - Persistent SQLite activity logging
```

---

## 3. Real Datasets Used

VibeCheck-AI exclusively uses real, publicly available, peer-reviewed social media datasets:

| Dataset | Primary Source | Samples | Language | Labels | Description & Limitations |
|---|---|---|---|---|---|
| **TRAC-1 Aggression Dataset** | Kumar et al. (COLING 2018) | **34,264** | Hindi (Romanized / Hinglish), Indian English | `NAG` (Normal: 10,695), `CAG` (Harassment: 12,755), `OAG` (Hate Speech: 10,814) | Real Facebook and Twitter user comments collected for the First Shared Task on Aggression Identification. Covers transliterated Hindi slang and Indian social debate. Limitation: Collected in 2018, contains spelling drift from current Gen-Z slang. |
| **PRISM Hinglish Dataset** | Biswas et al. | **26,546** | Hinglish, Devanagari Hindi, English | `0` (Normal: 14,218), `1` (Hate Speech: 12,328) | Real multi-turn social conversation and comment corpus across English, Hindi, and code-mixed Hinglish. |

### Research Taxonomy Mapping
- **`normal`:** Non-aggressive, normative social media speech (`NAG` in TRAC, `0` in PRISM).
- **`harassment`:** Covert aggression, targeted insults, derogatory mocking (`CAG` in TRAC).
- **`hate_speech`:** Overt aggression, violent threats, communal slurs, calls for harm (`OAG` in TRAC, `1` in PRISM).

---

## 4. Empirical Model Evaluation & Comparative Benchmark

We conducted a real comparative benchmark evaluating four architectures on the TRAC test partition (6,853 held-out stratified test samples):

### Benchmark Results Table

| Model Architecture | Model Family | Macro F1 | Weighted F1 | Macro Precision | Macro Recall |
|---|---|---|---|---|---|
| **TF-IDF (Word n-gram) + Logistic Regression** | Linear N-gram Baseline | `0.5867` | `0.5823` | `0.5846` | `0.5899` |
| **Word+Char Subword n-gram + Calibrated Linear SVM** | Subword Morphological Linear | **`0.6079`** | **`0.6051`** | **`0.6125`** | **`0.6054`** |
| **HateBERT (`GroNLP/hateBERT`)** | Monolingual English Transformer | `0.4622` | `0.4588` | `0.4641` | `0.4647` |
| **MuRIL (`google/muril-base-cased`)** | Multilingual Indian Transformer | `0.4120` | `0.3994` | `0.4678` | `0.4689` |

### Per-Class F1 Breakdown

| Model | Harassment F1 | Hate Speech F1 | Normal F1 |
|---|---|---|---|
| **TF-IDF + Logistic Regression** | 0.5133 | 0.5864 | 0.6605 |
| **Word+Char Calibrated Linear SVM** | **0.5630** | **0.5956** | **0.6651** |
| **HateBERT (`GroNLP/hateBERT`)** | 0.4048 | 0.4762 | 0.5056 |
| **MuRIL (`google/muril-base-cased`)** | 0.1964 | 0.4844 | 0.5551 |

### Why Monolingual HateBERT Struggles on Hindi-English
`GroNLP/hateBERT` was pre-trained on English Reddit toxic communities (RAL-E). Our tokenization inspection revealed:
1. **Severe Subword Fragmentation:** Common Hinglish words are shattered into nonsensical subword fragments:
   - *"bhakt"* → `['b', '##hak', '##t']`
   - *"dimag"* → `['dim', '##ag']`
   - *"kya"* → `['ky', '##a']`
2. **Missing Transliteration Vocabulary:** Because HateBERT lacks Latin-script Indic morphology, it cannot capture root morphemes.
3. **Subword Character n-grams Excel:** In contrast, character n-grams (`3-5 char_wb`) combined with word n-grams capture phonetic spelling variations (e.g. *"bhai"*, *"bhaii"*, *"bhayya"*) without Out-Of-Vocabulary (OOV) bottlenecks.

---

## 5. Independent Policy Engine & Platform Profiles

The policy engine operates completely separate from the classifier. It uses official platform guidelines:

### YouTube Community Guidelines
- **YT-HATE-01 (Hate Speech Policy):**
  - *Source:* [YouTube Help: Hate speech policy](https://support.google.com/youtube/answer/2801939)
  - *Protected Characteristics:* Age, Caste, Disability, Ethnicity, Gender identity/expression, Nationality, Race, Immigration status, Religion, Sex/Gender, Sexual orientation, Victims of major violent events.
  - *Context Exceptions:* Educational, Documentary, Scientific, or Artistic (EDSA); counter-speech; neutral reporting.
  - *Recommended Action:* Channel strike (3-strike penalty system), video removal, age restriction for borderline discussions.
- **YT-HARASS-01 (Harassment & Cyberbullying Policy):**
  - *Source:* [YouTube Help: Harassment policy](https://support.google.com/youtube/answer/2802268)
  - *Rules:* Malicious insults, derogatory slurs, sustained humiliation, non-consensual sexualization.
  - *Exceptions:* Comedy, satire, public figure debate.
- **YT-THREAT-01 (Violent Criminal Threats Policy):**
  - *Source:* [YouTube Help: Violent threats policy](https://support.google.com/youtube/answer/2801924)

### Meta / Instagram Community Standards
- **META-HATE-01 (Community Standard 13: Hate Speech):**
  - *Source:* [Meta Transparency: Hate Speech](https://transparency.meta.com/policies/community-standards/hate-speech/)
  - *Three-Tier System:* Tier 1 (violent/dehumanizing speech, animal/disease slurs); Tier 2 (contempt, disgust); Tier 3 (exclusion calls).
  - *Protected Characteristics:* Race, Ethnicity, National origin, Disability, Religious affiliation, Caste, Sexual orientation, Sex, Gender identity, Serious disease.
  - *Context Exceptions:* Clear condemning intent, humorous intent/mutual banter, self-referential/reclaimed terms.
- **META-BULLY-01 (Community Standard 14: Bullying and Harassment):**
  - *Source:* [Meta Transparency: Bullying and Harassment](https://transparency.meta.com/policies/community-standards/bullying-harassment/)
  - *Core Distinction:* Private Individuals vs. Public Figures. Heightened protections for private individuals against unwanted mass targeting.
- **META-VIOL-01 (Community Standard 1: Violence and Incitement):**
  - *Source:* [Meta Transparency: Violence and Incitement](https://transparency.meta.com/policies/community-standards/violence-incitement/)

---

## 6. Research Experiments: Policy Adaptation

### Experiment 1: Dual Platform Evaluation on Identical Event
- A single detected segment: `[14.2s - 18.7s] "Abe idiot chup kar bakwas band kar", label: harassment, conf: 0.72`
- Evaluated under YouTube: `Potential Policy Violation (YT-HARASS-01, Medium-High Severity)`
- Evaluated under Meta: `Potential Policy Violation (META-BULLY-01, Medium-High Severity)`
- Both platforms share identical timestamps and detected risk, but independently evaluate prospective guideline compliance.

### Experiment 2: Policy Evolution Without ML Retraining
- A borderline detected segment: `[10.0s - 13.5s] "Borderline uncivil speech", label: harassment, conf: 0.55`
- Under **Policy Profile v1 (Standard)**:
  - YouTube threshold = 0.65 → Assessment: **`Requires Review`** (Medium severity).
- Under **Policy Profile v2 (Strict Civic Safety Update)**:
  - YouTube threshold tightened to 0.50 → Assessment: **`Potential Policy Violation`** (High severity).
- **CRITICAL:** The ML model was **NOT retrained**. The raw detection remained completely unchanged (`label=harassment, conf=0.55`). This empirically proves that content-risk assessment is a function of evolving platform policy, not just static classifier prediction.

---

## 7. Installation & Setup

### Prerequisites
- Windows, Linux, or macOS
- Python 3.11 installed
- FFmpeg and ffprobe installed and available on system `PATH`

### 1. Create and Activate Virtual Environment
```powershell
# Windows
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Verify Model Artifacts or Train
Pre-trained calibrated models are included or can be trained in 30 seconds:
```powershell
# Preprocess data
python data/scripts/preprocess.py

# Train models
python data/scripts/train_baseline.py

# Run comparative benchmark
python data/scripts/evaluate_models.py
```

### 4. Run the Full Test Suite
```powershell
$env:PYTHONPATH="backend"
pytest -v
```

---

## 8. Running the System

### Start the FastAPI Server
```powershell
# From the project root:
$env:PYTHONPATH="backend"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Open the Frontend Dashboard
Navigate to:
```
http://127.0.0.1:8000/
```
(Or open `frontend/index.html` via VS Code Live Server on port 5500; CORS is preconfigured).

---

## 9. API Reference

### `POST /api/analyze`
Accepts multipart video file upload (MP4, MOV, WebM, MKV, AVI, max 60s).
- **Parameters:**
  - `file`: Video file binary
  - `youtube_version`: Query param (`v1` or `v2`)
  - `meta_version`: Query param (`v1` or `v2`)
- **Response Structure:**
```json
{
  "video_id": "4b7e8d2e-13c5-4a67-9c98-123456789abc",
  "filename": "video.mp4",
  "duration_seconds": 18.5,
  "language": "hi",
  "segments": [
    {
      "start": 14.2,
      "end": 18.5,
      "text": "Abe idiot chup kar bilkul bakwas kar raha hai",
      "label": "harassment",
      "confidence": 0.769,
      "youtube_policy": {
        "platform": "YouTube",
        "policy_version": "v1.2-standard",
        "status": "potential_policy_violation",
        "status_label": "Potential Policy Violation",
        "policy_category": "Harassment & Cyberbullying",
        "triggered_rule_id": "YT-HARASS-01",
        "severity": "Medium-High",
        "recommended_action": "Potential policy issue: Flag for contextual review...",
        "source_url": "https://support.google.com/youtube/answer/2802268"
      },
      "instagram_policy": {
        "platform": "Instagram / Meta",
        "policy_version": "v2026.1-standard",
        "status": "potential_policy_violation",
        "status_label": "Potential Policy Violation",
        "policy_category": "Bullying and Harassment (Standard 14)",
        "triggered_rule_id": "META-BULLY-01",
        "severity": "Medium-High",
        "recommended_action": "Potential policy issue: Hide or remove reel...",
        "source_url": "https://transparency.meta.com/policies/community-standards/bullying-harassment/"
      }
    }
  ],
  "policy_overview": {
    "youtube": {
      "total_flagged": 1,
      "potential_violations": 1,
      "requires_review": 0,
      "highest_severity": "Medium-High"
    },
    "instagram_meta": {
      "total_flagged": 1,
      "potential_violations": 1,
      "requires_review": 0,
      "highest_severity": "Medium-High"
    }
  }
}
```

### `POST /api/analyze/text`
Accepts direct text snippet for fast testing:
```json
{
  "text": "Abe saale chup kar bakwas kar raha hai",
  "youtube_policy_version": "v1",
  "meta_policy_version": "v1"
}
```

### `POST /api/policy/adapt`
Runs Policy Adaptation Experiment 2 across `v1` and `v2` policy profiles.

### `GET /api/history`
Returns past activity from SQLite database.

### `GET /api/history/{id}`
Returns full detailed analysis payload for a historical session.

### `GET /api/policies`
Returns registered policy definitions and rule catalogs.

---

## 10. Limitations & Future Work

### Limitations
1. **Audio/Speech Modality Only:** Visual frames (on-screen text, gestures, violence) are not yet integrated into the feature extractor.
2. **Dialectal Variation:** Romanized transliterations vary widely across regions (Bhojpuri-Hindi, Punjabi-Hinglish, Urban Delhi slang); uncommon slang requires continuous active-learning updates.
3. **Context Disambiguation:** Sarcasm, quoting counter-speech, and consensual friendly banter remain challenging without user relationship graphs.

### Future Work
1. **Multimodal Fusion:** Incorporating CLIP/Video-LLaVA visual frame representations with Whisper audio embeddings.
2. **Contextual Knowledge Graph:** Modeling creator-audience relationship history to differentiate friendly creator banter from malicious external harassment campaigns.
3. **Explainable AI (XAI):** Generating token-level attribution heatmaps to assist human moderators in contextual auditing.

---

## 11. Research Integrity Notice

- **No Fabricated Data or Metrics:** All reported benchmark scores, confusion matrices, and dataset parameters reflect real executions on public corpora.
- **No Enforcement Claims:** VibeCheck-AI provides automated policy compliance assessments based on public guidelines. It does not speak for or guarantee actions by YouTube LLC, Google LLC, or Meta Platforms, Inc.
