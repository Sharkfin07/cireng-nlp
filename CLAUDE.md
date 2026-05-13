# Cireng NLP (GARDA's NLP Pipeline) — CLAUDE.md

## Project Overview

GARDA (Grooming Analysis and Risk Detection Application) is an Indonesian-language NLP-based early detection system for predatory grooming. This file is the guide for Claude Code when assisting with the development of GARDA's NLP pipeline component. Cireng NLP is GARDA's NLP engine.

This pipeline is standalone (separate from the FastAPI server and Flutter app) and is responsible for:

1. Receiving Indonesian-language conversation text
2. Classifying text into grooming stages (multi-label)
3. Generating a risk score from 0–100
4. Returning structured output with explainability data

---

## Tech Stack

- **Python**: 3.11 (via pyenv)
- **ML Framework**: PyTorch + HuggingFace Transformers
- **Base model**: IndoBERTweet (`indolem/indobertweet-base-uncased`)
- **Package manager**: pip + venv
- **Training environment**: Google Colab (GPU) / local (CPU, inference only)
- **Experiment tracking**: MLflow
- **Testing**: pytest

---

## Folder Structure

```
garda-nlp/
├── CLAUDE.md                  # This file
├── README.md                  # Technical documentation
├── requirements.txt           # Dependencies
├── .env.example               # Environment variable template
├── .gitignore
│
├── data/                      # Datasets (DO NOT commit to git)
│   ├── raw/                   # Raw data before preprocessing
│   ├── processed/             # Preprocessed and labelled data
│   └── synthetic/             # Synthetically generated data
│
├── models/                    # Model weights (DO NOT commit to git)
│   ├── base/                  # Pre-trained IndoBERTweet
│   └── finetuned/             # Fine-tuned checkpoints
│
├── src/
│   ├── __init__.py
│   ├── pipeline.py            # Main pipeline entry point
│   │
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   ├── cleaner.py         # Text normalization, slang, abbreviations
│   │   └── tokenizer.py       # IndoBERTweet tokenizer wrapper
│   │
│   ├── heuristic/
│   │   ├── __init__.py
│   │   ├── engine.py          # Heuristic orchestrator
│   │   ├── keywords.py        # Keyword lists per grooming stage
│   │   ├── patterns.py        # Regex patterns
│   │   └── behavioral.py      # Behavioral signals (frequency, time, etc.)
│   │
│   ├── nlp/
│   │   ├── __init__.py
│   │   ├── model.py           # IndoBERTweet loader and inference
│   │   ├── classifier.py      # Multi-label classification head
│   │   └── trainer.py         # Fine-tuning logic (used in Colab)
│   │
│   ├── scoring/
│   │   ├── __init__.py
│   │   └── risk_scorer.py     # Combine heuristic + NLP scores → 0-100
│   │
│   └── explainability/
│       ├── __init__.py
│       └── explainer.py       # Extract stage labels, scores, text fragments
│
├── tests/
│   ├── __init__.py
│   ├── test_preprocessing.py
│   ├── test_heuristic.py
│   ├── test_nlp.py
│   └── test_scoring.py
│
├── notebooks/                 # Jupyter/Colab notebooks
│   ├── 01_exploration.ipynb   # Initial dataset exploration
│   ├── 02_inference_test.ipynb # Test pre-trained model inference
│   └── 03_finetuning.ipynb    # Fine-tuning on Colab
│
└── scripts/
    ├── download_model.py      # Download IndoBERTweet from HuggingFace
    ├── prepare_data.py        # Preprocess raw dataset
    └── evaluate.py            # Evaluate model (precision, recall, F1)
```

---

## Grooming Stage Labels

The pipeline uses 6 labels based on O'Connell (2003), validated by Lorenzo-Dus et al. (2016). Each message can have **more than one label** (multi-label classification):

| Label             | Stage                   | Example signals                            |
| ----------------- | ----------------------- | ------------------------------------------ |
| `FRIENDSHIP`      | Friendship-forming      | a/s/l, photo requests, excessive greetings |
| `RELATIONSHIP`    | Relationship-forming    | compliments, hobbies, family topics        |
| `RISK_ASSESSMENT` | Risk assessment         | parent location, delete chat requests      |
| `EXCLUSIVITY`     | Exclusivity / isolation | secrets, inclusive pronouns                |
| `SEXUAL`          | Sexual desensitization  | implicit hypothetical language             |
| `APPROACH`        | Approach / conclusion   | meeting invitations, logistics             |

---

## Pipeline Input/Output Format

### Input

```python
{
    "conversation_id": "str",       # Unique conversation ID
    "messages": [
        {
            "sender": "unknown",    # Sender (unknown = suspicious party)
            "text": "str",          # Message content
            "timestamp": "str"      # ISO 8601
        }
    ]
}
```

### Output

```python
{
    "conversation_id": "str",
    "risk_score": float,            # 0.0 - 100.0
    "labels": [
        {
            "label": "str",         # Grooming stage name
            "confidence": float,    # 0.0 - 1.0
            "triggered_by": "str"   # Triggering text fragment (max 50 chars)
        }
    ],
    "alert": bool,                  # True if risk_score > threshold
    "threshold_used": float         # Threshold applied
}
```

---

## Heuristic Signals Per Stage

### High-risk keywords (Indonesian)

```python
RISK_KEYWORDS = {
    "RISK_ASSESSMENT": [
        "orang tua kamu ada", "bokap nyokap ada", "sendirian gak",
        "hapus chat", "delete pesan", "jangan kasih tau", "rahasia ya",
        "ada yang liat", "lagi sama siapa"
    ],
    "EXCLUSIVITY": [
        "rahasia kita", "cuma kita berdua", "jangan bilang siapapun",
        "kamu beda dari", "gak ada yang ngerti", "special buat kamu"
    ],
    "APPROACH": [
        "mau ketemu", "ketemuan yuk", "aku jemput", "rumahnya dimana",
        "kapan bisa ketemu", "mau kemana"
    ],
    "HIGH_RISK_LEXICON": [
        "open BO", "japri", "VCS", "pindah WA", "add discord",
        "diamond gratis", "skin gratis", "pulsa gratis", "saldo"
    ]
}
```

### Behavioral signals

- Message frequency > 20 messages/hour from a single contact
- Active messages between 22:00 - 04:00
- New contact (< 7 days) with unusually high message intensity
- Platform migration request detected in conversation

---

## Running Locally

```bash
# 1. Clone and set up environment
git clone <repo>
cd cireng-nlp
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Download base model
python scripts/download_model.py

# 3. Quick inference test
python -c "
from src.pipeline import GardaPipeline
pipeline = GardaPipeline()
result = pipeline.analyze('orang tua kamu ada di rumah gak? hapus chat ini ya')
print(result)
"

# 4. Run tests
pytest tests/
```

---

## Guidelines for Claude Code

### Allowed

- Modify any file under `src/`
- Add new keywords and patterns in `src/heuristic/`
- Write and run tests in `tests/`
- Create and run scripts in `scripts/`
- Modify `requirements.txt`

### NOT allowed

- Commit files in `data/` or `models/` to git
- Hard-code any API keys or credentials
- Change the pipeline input/output format without confirmation
- Install new packages without updating `requirements.txt`

### Current development priorities

1. **Complete `src/heuristic/engine.py`** — easiest to start, no GPU needed
2. **Test inference in `src/nlp/model.py`** — verify IndoBERTweet loads and runs
3. **Integrate in `src/pipeline.py`** — combine heuristic + NLP
4. **Write tests** — minimum coverage for heuristic engine

### Code conventions

- Docstrings required for all public functions
- Type hints required
- Comment language: English throughout
- Max 100 characters per line

---

## Relevant Academic References

- O'Connell (2003) — 6-stage online grooming model
- Lorenzo-Dus et al. (2020) — empirical justification for multi-label classification
- Koto et al. (2021) — IndoBERTweet paper
- Gupta et al. (2012) — LIWC features for grooming detection
- Vogt et al. (2021) — early detection + sliding window approach

---

## Development Status

- [x] Environment setup and folder structure
- [ ] Download and test IndoBERTweet inference
- [ ] Implement heuristic engine
- [ ] Implement risk scorer
- [ ] Implement explainability module
- [ ] End-to-end pipeline integration
- [ ] Collect and label dataset
- [ ] Fine-tune on Colab
- [ ] Evaluate model (precision, recall, F1-latency)
