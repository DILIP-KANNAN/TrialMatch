import torch
from datasets import load_dataset
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    TrainingArguments,
    Trainer
)
import numpy as np
import evaluate

def compute_metrics(eval_pred):
    metric = evaluate.load("accuracy")
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

def main():
    print("CUDA available:", torch.cuda.is_available())
    model_name = "dmis-lab/biobert-base-cased-v1.1"
    output_dir = "./biobert_nli_finetuned"
    
    print("Loading tokenizer and model...")
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForSequenceClassification.from_pretrained(model_name, num_labels=3)
    
    print("Loading SNLI dataset...")
    # Load just a subset to make training fast for this mini project (~5-10 minutes)
    dataset = load_dataset("snli")
    
    # Filter out invalid labels (-1)
    train_dataset = dataset["train"].filter(lambda x: x["label"] in [0, 1, 2])
    eval_dataset = dataset["validation"].filter(lambda x: x["label"] in [0, 1, 2])
    
    # Select small subset to be fast: 8000 train, 1000 eval
    train_dataset = train_dataset.select(range(8000))
    eval_dataset = eval_dataset.select(range(1000))
    
    def tokenize_function(examples):
        # We pass premise and hypothesis to be encoded together separated by [SEP]
        return tokenizer(
            examples["premise"], 
            examples["hypothesis"], 
            padding="max_length", 
            truncation=True, 
            max_length=128
        )
        
    print("Tokenizing datasets...")
    tokenized_train = train_dataset.map(tokenize_function, batched=True)
    tokenized_eval = eval_dataset.map(tokenize_function, batched=True)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=2,
        weight_decay=0.01,
        save_strategy="epoch",
        load_best_model_at_end=True,
        fp16=True, # Mixed precision for faster training on RTX 4060
        logging_steps=100
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_eval,
        compute_metrics=compute_metrics,
    )
    
    print("Starting training...")
    trainer.train()
    
    print(f"Training complete. Saving model to {output_dir}...")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("Model saved successfully.")

if __name__ == "__main__":
    main()
