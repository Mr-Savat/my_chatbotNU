from transformers import pipeline

# Load GPT-2 model
chatbot = pipeline("text-generation", model="./gpt2-norton")


def ask_gpt2(prompt):
    result = chatbot(prompt, max_length=100, num_return_sequences=1)
    return result[0]['generated_text']
