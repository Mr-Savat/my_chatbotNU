import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()  # Load environment variables from .env

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables!")

groq_client = Groq(api_key=GROQ_API_KEY)

def ask_groq(question: str) -> str:
    try:
        response = groq_client.chat.completions.create(
            model="compound-beta-mini",
            messages=[
                {"role": "system", "content": "You are a helpful chatbot."},
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Groq API error: {str(e)}"
