import difflib

def calculate_confidence(question, answer):
    ratio = difflib.SequenceMatcher(None, question.lower(), answer.lower()).ratio()
    return ratio
