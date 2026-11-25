from flask import Flask, jsonify, render_template, request
from falcons_qa import generate_answer, load_faiss_index

app = Flask(__name__)
MAX_QUESTION_LENGTH = 1000

# Load the persisted index before the server starts accepting requests. If it is
# missing (for example during local development), load_faiss_index builds it.
load_faiss_index()


@app.route("/")
def home():
    return render_template("index.html")


@app.get("/healthz")
def health():
    return jsonify({"status": "ok"})


@app.post("/ask")
def ask():
    payload = request.get_json(silent=True)
    if isinstance(payload, dict):
        question = payload.get("question", "")
    else:
        question = request.form.get("question", "")

    if not isinstance(question, str) or not question.strip():
        return jsonify({"error": "A non-empty 'question' is required."}), 400
    if len(question) > MAX_QUESTION_LENGTH:
        return jsonify({"error": f"Questions must be {MAX_QUESTION_LENGTH} characters or fewer."}), 413

    try:
        return jsonify(generate_answer(question))
    except Exception:
        app.logger.exception("Failed to generate an answer")
        return jsonify({"error": "The assistant is temporarily unavailable. Please try again later."}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
