import time
import openai

class Agent:
    def __init__(self, temperature=0.7, model='gpt-3.5-turbo', max_tokens=512, api_key = ""):
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
