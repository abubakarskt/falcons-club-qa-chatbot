from functools import lru_cache
import json
import os
import re
from pathlib import Path

import faiss
import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PROMPT_PATH = BASE_DIR / "prompts" / "club_qa_prompt.txt"
INDEX_PATH = DATA_DIR / "index.faiss"
CHUNKS_PATH = DATA_DIR / "chunks.json"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_documents():
    docs = []
    for file in sorted(DATA_DIR.glob("*.txt")):
        docs.append(
            {
                "title": file.stem.replace("_", " ").title(),
                "path": str(file),
                "text": file.read_text(encoding="utf-8"),
            }
        )
    return docs


def split_documents_into_chunks():
    chunks = []
    for file in sorted(DATA_DIR.glob("*.txt")):
        text = file.read_text(encoding="utf-8")
        for paragraph in re.split(r"\n\s*\n", text):
            paragraph = paragraph.strip()
            if paragraph:
                chunks.append({"source": file.name, "text": paragraph})
    return chunks


@lru_cache(maxsize=1)
def get_embedding_model():
    return SentenceTransformer(EMBEDDING_MODEL)


def build_index():
    chunks = split_documents_into_chunks()
    if not chunks:
        raise RuntimeError(f"No paragraph text found in {DATA_DIR}.")

    model = get_embedding_model()
    vectors = model.encode(
        [chunk["text"] for chunk in chunks],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    ).astype(np.float32)

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))
    CHUNKS_PATH.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    return index, chunks


def load_faiss_index():
    if not INDEX_PATH.exists() or not CHUNKS_PATH.exists():
        build_index()
    index = faiss.read_index(str(INDEX_PATH))
    chunks = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
    return index, chunks


def retrieve_chunks(question, top_k=3):
    index, chunks = load_faiss_index()
    if index.ntotal == 0:
        return []

    vector = get_embedding_model().encode(
        [question], convert_to_numpy=True, normalize_embeddings=True
    ).astype(np.float32)
    _, ids = index.search(vector, min(top_k, index.ntotal))
    return [chunks[int(i)] for i in ids[0] if i >= 0]


def build_prompt(question, context_chunks):
    template = PROMPT_PATH.read_text(encoding="utf-8")
    context = "\n\n".join(
        f"Source: {chunk['source']}\n{chunk['text']}" for chunk in context_chunks
    )
    return template.replace("{question}", question).replace("{context}", context)


def parse_json_response(raw_text):
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE)
    data = json.loads(cleaned)
    if not isinstance(data, dict) or "answer" not in data:
        raise ValueError("Model response did not contain an answer field.")
    return str(data["answer"])


def ask_openai(question, context_chunks):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key)
    prompt = build_prompt(question, context_chunks)
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        input=prompt,
        temperature=0,
    )
    return parse_json_response(response.output_text)


def generate_answer(question):
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    chunks = retrieve_chunks(question.strip(), top_k=3)
    if not chunks:
        return {"answer": "I could not find relevant information in the club documents.", "source": ""}

    source = chunks[0]["text"]
    try:
        answer = ask_openai(question.strip(), chunks)
    except Exception:
        answer = source

    return {"answer": answer, "source": source}
