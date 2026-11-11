# Falcons Club Q&A

A small Flask app that answers questions about Falcons Club using sample documents, a free sentence-transformers embedding model, and a persisted FAISS vector index.

## What this project does

- Reads all `.txt` files in `data/`
- Splits each document into paragraph-size chunks on blank lines
- Embeds the chunks with `sentence-transformers/all-MiniLM-L6-v2`
- Stores the vectors in `data/index.faiss`
- Saves the chunk metadata in `data/chunks.json`
- Adds a `POST /ask` endpoint that retrieves the top 3 matching chunks and answers the user question with JSON output

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Build the FAISS index

```bash
python scripts/build_index.py
```

This creates:
- `data/index.faiss`
- `data/chunks.json`

## Run the app

```bash
python app.py
```

Then use:

```bash
curl -X POST http://127.0.0.1:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"When is the next soccer match?"}'
```

Example answer:

```json
{
  "answer": "The next club event is the Falcons Night Run on Saturday at 6:30 PM.",
  "source": "Saturday, May 18 – Falcons Night Run at 6:30 PM\nLocation: Northern Park Track"
}
```

## Why this is useful

This design keeps the app fast and accurate by turning the sample documents into searchable vectors. The top matching chunks provide grounded context to the LLM, and the returned `source` is the exact paragraph text that matched the question.
