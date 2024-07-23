import openai
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import re
import os
import time

api_key = 'sk-proj-iVLzb4XmpgjatOIsfjCUT3BlbkFJWu6FAh5ZMJA0Drfs8Rth'

class Agent:
    def __init__(self, temperature=0.7, model='gpt-4o', max_tokens=512, api_key = ""):
        self.temperature = temperature
        self.model = model
        self.max_tokens = max_tokens
        openai.api_key = api_key
    
    def communicate(self, context):
        prompt = context
        message = ""

        retries = 3
        backoff_factor = 2
        current_retry = 0

        while current_retry < retries:
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=self.max_tokens,
                    n=1,
                    temperature=self.temperature,
                    top_p=1
                )
                message = response['choices'][0]['message']['content'].strip()
                return message
            except openai.error.RateLimitError as e:
                if current_retry < retries - 1:
                    wait_time = backoff_factor ** current_retry
                    print(f"RateLimitError: Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    current_retry += 1
                else:
                    print(f"Error {e}")
                    raise e
            except openai.error.APIError as e:
                if current_retry < retries - 1:
                    wait_time = backoff_factor ** current_retry
                    print(f"RateLimitError: Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    current_retry += 1
                else:
                    raise e
            except Exception as e:
                if current_retry < retries - 1:
                    wait_time = backoff_factor ** current_retry
                    print(f"RateLimitError: Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    current_retry += 1
                else:
                    print(f"Error {e}")
                    raise e

def find_first_integer(s):
    match = re.search(r'\d+', s)
    if match:
        return int(match.group())
    return None

def classify_with_gpt3(text):
    agent = Agent(api_key=api_key)
    response = agent.communicate(f"This is a spam classifier. Please determine whether the following text is spam or not, return 0 (not spam) or 1 (spam). Note that information without clear meaning or advertisement is also considered as spam, e.g., あああ and 大特価セール中！今すぐクリックしてお得な情報をチェックしてください！ are spam\n\nText:{text}\n\nYour classification:")
    return response

def check_folder_exists(folder_a, folder_b):
    folder_b_path = os.path.join(folder_a, folder_b)
    
    if os.path.isdir(folder_b_path):
        return True
    else: return False

def classify_message(text, model_path='./junk_classify_module/bert_model', tokenizer_path='./junk_classify_module/bert_tokenizer'):
    if api_key == 'your-api-key-here': # BERT
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
        
        predictions = torch.argmax(outputs.logits, dim=-1).item()
    
    else: # GPT
        predictions = classify_with_gpt3(text)
        
    if isinstance(predictions, str): predictions = find_first_integer(predictions)
    return round(predictions)

if __name__ == "__main__":
    text = "あなたは当選しました！お金を受け取るためにここをクリックしてください。"
    final_result = classify_message(text)
    print(f'Result: {final_result}')

    text = "京都の町は綺麗です"
    final_result = classify_message(text)
    print(f'Result: {final_result}')
