from datasets import load_dataset
from transformers import GPT2LMHeadModel, GPT2Tokenizer, Trainer, TrainingArguments, DataCollatorForLanguageModeling

# Load the Q/A dataset
dataset = load_dataset("text", data_files={"train": "train.txt"})

# Load GPT-2 tokenizer & model
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token
model = GPT2LMHeadModel.from_pretrained("gpt2")

# Tokenize dataset
def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128)

tokenized_datasets = dataset.map(tokenize_function, batched=True, remove_columns=["text"])
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# Training configuration
training_args = TrainingArguments(
    output_dir="./gpt2-norton",
    overwrite_output_dir=True,
    num_train_epochs=5,        # Can increase if dataset is small
    per_device_train_batch_size=2,
    save_steps=500,
    save_total_limit=2,
    prediction_loss_only=True
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    tokenizer=tokenizer,
    data_collator=data_collator
)

# Train and save
trainer.train()
model.save_pretrained("./gpt2-norton")
tokenizer.save_pretrained("./gpt2-norton")

print("✅ Fine-tuning complete! Model saved to ./gpt2-norton")
