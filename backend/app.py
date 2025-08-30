from flask import Flask, request, jsonify
from flask_cors import CORS
from .faq_loader import load_faq, find_answer  
from .groq_fallback import ask_groq              
from .confidence import calculate_confidence   
import os

app = Flask(__name__)
CORS(app)

# Initialize FAQ data
faqs = load_faq("data/faqs.csv")

@app.route('/')
def home():
    return jsonify({"message": "Norton Chatbot API is running!", "status": "success"})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        # Step 1: Check FAQ first
        faq_answer = find_answer(question, faqs)
        if faq_answer:
            return jsonify({
                "answer": faq_answer,
                "source": "FAQ",
                "status": "success"
            })
        
        # Step 2: Use Groq directly (since GPT-2 model is too large for Render)
        groq_answer = ask_groq(question)
        return jsonify({
            "answer": groq_answer,
            "source": "Groq API",
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)