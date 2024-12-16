import os
from openai import OpenAI
import pandas as pd
from diskcache import Cache

# Save the responses so we don't have to rerun
cache = Cache("cache/GPT_summerization")

# Access the saved OPEN_AI KEY
API_KEY = os.getenv("OPENAI_API_KEY_FEDERAL_USECASE_INVENTORY")
assert API_KEY

f_data = "processed_responses/basic_consolidated.csv"
model_name = "gpt-4o-mini"

df = pd.read_csv(f_data)

text_fields = [
    'Use Case Name',
    'What is the intended purpose and expected benefits of the AI?',
    'Describe the AI system’s outputs.',
]

df['full_text'] = (df[text_fields[0]] + '\n' + df[text_fields[1]] + '\n' + df[text_fields[2]])

client = OpenAI(api_key=API_KEY)

def cached_openai_call(prompt, text):
    key = (prompt, text)
    if key in cache:
        return cache[key]

    messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": text}
    ]

    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model_name,
    )

    print(chat_completion)
    exit()

prompt = "Summarize the following project into two or three sentences. Use declarative language."

for text in df['full_text']:
    cached_openai_call(prompt, text)

