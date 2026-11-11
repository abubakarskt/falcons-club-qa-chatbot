from flask import Flask, jsonify, render_template, request
from falcons_qa import generate_answer

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.post("/ask")
def ask():
    payload = request.get_json(silent=True)
    if isinstance(payload, dict):
        question = payload.get("question", "")
    else:
        question = ""

    if not question:
        question = request.form.get("question", "")

    if not isinstance(question, str) or not question.strip():
        return jsonify({"error": "A non-empty 'question' is required."}), 400

    try:
        return jsonify(generate_answer(question))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
