from flask import Flask, request, jsonify, send_from_directory
from faq_loader import load_faq, find_answer
from gpt2_model import ask_gpt2
from groq_fallback import ask_groq
from confidence import calculate_confidence
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
faqs = load_faq("data/faqs.csv")
# faqs = load_faq("data/faqs.json")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Step 1: Check FAQ
    faq_answer = find_answer(question, faqs)
    if faq_answer:
        return jsonify({"answer": faq_answer, "source": "FAQ"})

    # Step 2: Ask GPT-2
    gpt2_answer = ask_gpt2(question)
    confidence = calculate_confidence(question, gpt2_answer)

    if confidence >= 0.7:
        return jsonify({
            "answer": gpt2_answer,
            "source": f"GPT-2 (confidence: {confidence:.2f})"
        })

    # Step 3: Groq fallback if GPT-2 confidence is low
    groq_answer = ask_groq(question)
    return jsonify({
        "answer": groq_answer,
        "source": f"Groq API (GPT-2 confidence: {confidence:.2f})"
    })


# Serve frontend
@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("../frontend", path)

if __name__ == "__main__":
    app.run(debug=True)

