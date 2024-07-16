import openai
from data_processing import load_data, preprocess_data, save_vectorizer, load_vectorizer
from model_training import train_model, evaluate_model, save_model, load_model

openai.api_key = 'your-api-key-here'

def classify_with_gpt3(text):
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=f"This is a spam classifier. Please determine whether the following text is spam or not, return 0 (not spam) or 1 (spam).\n\nText:{text}\n\nClassification:",
        max_tokens=1,
        temperature=0
    )
    return int(response.choices[0].text.strip())

def classify_message(text, model_path='spam_classifier.pkl', vectorizer_path='vectorizer.pkl'):
    clf = load_model(model_path)
    vectorizer = load_vectorizer(vectorizer_path)
    
    text_tfidf = vectorizer.transform([text])
    lr_classification = clf.predict(text_tfidf)[0]
    
    #gpt3_classification = classify_with_gpt3(text)
    
    #final_classification = (lr_classification + gpt3_classification) // 2
    return int(lr_classification)

if __name__ == "__main__":
    # # Load Training
    # df = load_data('data.json')
    
    # # Data Preprocessing
    # X, y, vectorizer = preprocess_data(df)
    # save_vectorizer(vectorizer)
    
    # # Model Training
    # clf = train_model(X, y)
    
    # # Evaluation
    # accuracy = evaluate_model(clf, X, y)
    # print(f'5-Fold Cross Validation Accuracy: {accuracy}')
    
    # # Save model
    # save_model(clf)
    
    # Add model (0: not spam, 1: spam)
    text = "あなたは当選しました！お金を受け取るためにここをクリックしてください。"
    final_result = classify_message(text)
    print(f'Results: {final_result}')

    text = "京都の金閣寺は美しい庭園と黄金の建物で知られています。"
    final_result = classify_message(text)
    print(f'Results: {final_result}')
