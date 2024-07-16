import openai
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import re
import os

api_key = 'your-api-key-here'
openai.api_key = api_key

def find_first_integer(s):
    match = re.search(r'\d+', s)
    if match:
        return int(match.group())
    return None

def classify_with_gpt3(text):
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=f"This is a spam classifier. Please determine whether the following text is spam or not, return 0 (not spam) or 1 (spam).\n\nText:{text}\n\nClassification:",
        max_tokens=1,
        temperature=0
    )
    return int(response.choices[0].text.strip())

def check_folder_exists(folder_a, folder_b):
    folder_b_path = os.path.join(folder_a, folder_b)
    
    if os.path.isdir(folder_b_path):
        return True
    else: return False

def classify_message(text, model_path='./junk_classify_module/bert_model', tokenizer_path='./junk_classify_module/bert_tokenizer'):
    if check_folder_exists("./junk_classify_module/", "bert_model") == False:
        from junk_classify_module.data_processing import load_data, split_data
        from junk_classify_module.model_training import train_model, save_model
        df = load_data('./junk_classify_module/data.json')
        train_texts, val_texts, train_labels, val_labels = split_data(df)
        model, tokenizer = train_model(train_texts, train_labels, val_texts, val_labels)
        save_model(model, tokenizer)
    
    text = text.strip('!@#$%^&*()_+-=[]{}|;:\'",.<>?/`~')

    from junk_classify_module.model_training import load_model
    model, tokenizer = load_model(model_path, tokenizer_path)
    
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)

    if api_key == 'your-api-key-here':
        predictions = torch.argmax(outputs.logits, dim=-1).item() # BERT
    
    else:
        predictions = classify_with_gpt3(text) # GPT
        
    if isinstance(predictions, str): predictions = find_first_integer(predictions)
    print(predictions)
    return round(predictions)

if __name__ == "__main__":
    text = "あなたは当選しました！お金を受け取るためにここをクリックしてください。"
    final_result = classify_message(text)
    print(f'Result: {final_result}')

    text = "京都の町は綺麗です"
    final_result = classify_message(text)
    print(f'Result: {final_result}')
