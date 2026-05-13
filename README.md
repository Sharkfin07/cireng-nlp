# Cireng NLP

Cireng NLP is GARDA's Indonesian-language NLP pipeline for early detection of
predatory grooming. This repository focuses on the standalone pipeline: text
classification, risk scoring, and explainability.

## Environment setup

### 1) Create and activate a virtual environment

```bash
python -m venv venv
```

Windows (PowerShell):

```bash
venv\Scripts\Activate.ps1
```

Windows (CMD):

```bash
venv\Scripts\activate.bat
```

macOS/Linux:

```bash
source venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Configure environment variables

```bash
copy .env.example .env
```

Edit `.env` if you want to change model or tracking paths.

### 4) Download the base model

```bash
python scripts/download_model.py
```

### 5) Run tests

```bash
pytest tests/
```
