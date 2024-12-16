import os
from openai import OpenAI
import pandas as pd
from diskcache import Cache
from tqdm import tqdm
import numpy as np

# Save the responses so we don't have to rerun
cache = Cache("cache/GPT_embeddings")

# Access the saved OPEN_AI KEY
API_KEY = os.getenv("OPENAI_API_KEY_FEDERAL_USECASE_INVENTORY")
assert API_KEY

f_data = "processed_responses/summary_text.csv"
model_name = "text-embedding-3-large"

df = pd.read_csv(f_data)
client = OpenAI(api_key=API_KEY)

def cached_openai_call(text):
    key = (text,)
    if key in cache:
        return cache[key]

    
    response = client.embeddings.create(
        input=text,
        model=model_name
    )

    z = response.data[0].embedding
    
    cache[key] = z
    return cache[key]

Z = []
for text in tqdm(df['summary_text']):
    single_embedding = cached_openai_call(text)
    Z.append(single_embedding)
    print(text)
    print(single_embedding[:5])
    
Z = np.array(Z)
print(Z)
print(Z.shape)
