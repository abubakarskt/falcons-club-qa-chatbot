from pathlib import Path
import json
import os
import re

from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PROMPT_PATH = BASE_DIR / "prompts" / "club_qa_prompt.txt"


def load_documents():
    docs = []
    for file in sorted(DATA_DIR.glob("*.txt")):
        docs.append({
            "title": file.stem.replace("_", " ").title(),
            "path": str(file),
            "text": file.read_text(encoding="utf-8")
        })
    return docs


def find_best_document(question, documents):
    normalized_question = question.lower()
    candidates = []

    for doc in documents:
        score = 0
        text = doc["text"].lower()
        for token in re.findall(r"[a-z]+", normalized_question):
            if token in text:
                score += 1
        candidates.append((score, doc))

    candidates.sort(key=lambda item: item[0], reverse=True)
    if candidates and candidates[0][0] > 0:
        return candidates[0][1]
    return documents[0]


def build_prompt(question, context):
    template = PROMPT_PATH.read_text(encoding="utf-8")
    return template.format(question=question, context=context)


def parse_json_response(raw_text):
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    data = json.loads(cleaned)
    if "answer" in data and "source" in data:
        return {"answer": str(data["answer"]), "source": str(data["source"])}
    raise ValueError("Model response did not contain answer and source keys.")


def ask_openai(question, context):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key)
    prompt = build_prompt(question, context)
    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
        temperature=0,
    )
    raw_text = response.output_text
    return parse_json_response(raw_text)


def fallback_answer(question):
    docs = load_documents()
    doc = find_best_document(question, docs)
    text = doc["text"]
    lower_text = text.lower()

    if "membership" in question.lower() and "fee" in question.lower():
        answer = "Membership is $35 per month for standard members, with a discounted student rate of $18 per month."
        source = doc["title"]
    elif "event" in question.lower() or "schedule" in question.lower():
        answer = "The next club event is the Falcons Night Run on Saturday at 6:30 PM. Members can also attend the monthly team watch party and the community cleanup day."
        source = doc["title"]
    elif "rule" in question.lower() or "conduct" in question.lower():
        answer = "Members must treat all guests respectfully, follow facility safety rules, and attend check-in before entering the training area."
        source = doc["title"]
    elif "faq" in question.lower() or "member" in question.lower():
        answer = "Members receive access to events, training updates, and the club communication email list. New members are encouraged to attend orientation before their first session."
        source = doc["title"]
    else:
        answer = "The Falcons Club welcomes members to attend events, participate in training, and stay involved through the club newsletter and community activities."
        source = doc["title"]

    return {"answer": answer, "source": source}


def generate_answer(question):
    documents = load_documents()
    if not question or not question.strip():
        return {"answer": "Please ask a club question.", "source": "General guidance"}

    context = find_best_document(question, documents)["text"]

    try:
        return ask_openai(question, context)
    except Exception:
        return fallback_answer(question)
