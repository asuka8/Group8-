import pandas as pd
import json
from sklearn.model_selection import train_test_split

def load_data(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    df = pd.DataFrame(data)
    return df

def split_data(df, test_size=0.2, random_state=42):
    X = df['text']
    y = df['label']
    return train_test_split(X, y, test_size=test_size, random_state=random_state)
