# Falcons Club Q&A

A small Flask app that answers questions about club operations using sample documents from the Falcons Club and a reusable prompt template that returns JSON with `answer` and `source` fields.

## Features
- Minimal Flask home page with the header `Falcons Club Q&A`
- Sample club documents in the `data/` folder
- Reusable prompt template for LLM-based Q&A
- Test script that validates JSON output
- Works with OpenAI if an API key is available, and falls back to a local answer when no API key is configured

## Project layout
- `app.py` — Flask app entry point
- `falcons_qa.py` — document loading, prompt building, and answer generation logic
- `templates/index.html` — homepage
- `data/` — sample club documents
- `prompts/club_qa_prompt.txt` — reusable JSON prompt template
- `scripts/test_prompt.py` — prompt verification script

## Setup

1. Clone the repository
2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate   # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
python app.py
```

Then open: http://localhost:5000

## Optional OpenAI API
If you want to use the OpenAI API instead of the built-in local fallback, set your key before running the answer script:

```bash
export OPENAI_API_KEY="your-key-here"
```

## Why this project?
This project is a simple starter for building a document-based chat assistant. It demonstrates how to combine a small web app, sample source documents, and a prompt that asks an LLM to return structured JSON instead of plain text.
