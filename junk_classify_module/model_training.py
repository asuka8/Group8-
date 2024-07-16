import torch
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
import joblib

def tokenize_function(examples, tokenizer):
    return tokenizer(examples["text"], padding="max_length", truncation=True)

def train_model(train_texts, train_labels, val_texts, val_labels):
    tokenizer = BertTokenizer.from_pretrained("cl-tohoku/bert-base-japanese")
    train_encodings = tokenizer(train_texts.tolist(), truncation=True, padding=True)
    val_encodings = tokenizer(val_texts.tolist(), truncation=True, padding=True)

    train_dataset = Dataset.from_dict({
        'input_ids': train_encodings['input_ids'],
        'attention_mask': train_encodings['attention_mask'],
        'labels': train_labels
    })

    val_dataset = Dataset.from_dict({
        'input_ids': val_encodings['input_ids'],
        'attention_mask': val_encodings['attention_mask'],
        'labels': val_labels
    })

    model = BertForSequenceClassification.from_pretrained("cl-tohoku/bert-base-japanese", num_labels=2)

    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        evaluation_strategy="epoch"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset
    )

    trainer.train()

    return model, tokenizer

def save_model(model, tokenizer, model_path='./junk_classify_module/bert_model', tokenizer_path='./junk_classify_module/bert_tokenizer'):
    model.save_pretrained(model_path)
    tokenizer.save_pretrained(tokenizer_path)

def load_model(model_path='bert_model', tokenizer_path='bert_tokenizer'):
    model = BertForSequenceClassification.from_pretrained(model_path)
    tokenizer = BertTokenizer.from_pretrained(tokenizer_path)
    return model, tokenizer
