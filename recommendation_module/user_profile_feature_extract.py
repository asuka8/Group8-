import torch
from transformers import BertTokenizer, BertForSequenceClassification

INTEREST_CATEGORIES = ['歴史', '自然', '博物館', '寺院', '建築', '美しい']

def encode_description(description, tokenizer):
    inputs = tokenizer(description, return_tensors="pt", padding=True, truncation=True, max_length=512)
    return inputs

def classify_description(inputs, model):
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    scores = torch.softmax(logits, dim=1).numpy()[0]
    return scores

def extract_interests(description, categories):
    model_name = "cl-tohoku/bert-base-japanese"
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForSequenceClassification.from_pretrained(model_name, num_labels=6)

    inputs = encode_description(description, tokenizer)
    scores = classify_description(inputs, model)
    interest_scores = dict(zip(categories, scores))
    return interest_scores
