
import csv

def load_faq(file_path):
    faqs = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            faqs.append({"question": row["question"], "answer": row["answer"]})
    return faqs

def find_answer(user_question, faqs):
    user_question = user_question.lower()
    for faq in faqs:
        if faq["question"].lower() in user_question:
            return faq["answer"]
    return None









# import json
# from difflib import get_close_matches

# # Load FAQ from JSON file
# def load_faq(path="faq.json"):
#     with open(path, "r", encoding="utf-8") as f:
#         return json.load(f)

# # Find best match in FAQ
# def find_answer(user_question, faqs, threshold=0.6):
#     questions = [faq["question"] for faq in faqs]
#     matches = get_close_matches(user_question, questions, n=1, cutoff=threshold)
    
#     if matches:
#         best_question = matches[0]
#         for faq in faqs:
#             if faq["question"] == best_question:
#                 return faq["answer"], True
#     return None, False
