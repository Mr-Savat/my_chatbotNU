import csv

def csv_to_txt(csv_file, output_txt):
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        with open(output_txt, mode="w", encoding="utf-8") as out:
            for row in reader:
                question = row["question"].strip()
                answer = row["answer"].strip()
                out.write(f"Q: {question}\nA: {answer}\n\n")

if __name__ == "__main__":
    csv_to_txt("data/faqs.csv", "train.txt")
    print("✅ train.txt created from faqs.csv")
