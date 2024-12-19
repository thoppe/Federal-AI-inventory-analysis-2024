import os
from openai import OpenAI
import pandas as pd
from diskcache import Cache
from tqdm import tqdm
import numpy as np

f_data = "processed/summary_text.csv"
f_save = "processed/GPT_embedding.npy"
model_name = "text-embedding-3-large"

# Save the responses so we don't have to rerun
cache = Cache("data/cache/GPT_embeddings")

# Access the saved OPEN_AI KEY
API_KEY = os.getenv("OPENAI_API_KEY_FEDERAL_USECASE_INVENTORY")
assert API_KEY

df = pd.read_csv(f_data)
client = OpenAI(api_key=API_KEY)


def cached_openai_call(text):
    key = (text,)
    if key in cache:
        return cache[key]

    response = client.embeddings.create(input=text, model=model_name)

    z = response.data[0].embedding

    cache[key] = z
    return cache[key]


Z = []
for text in tqdm(df["summary_text"]):
    single_embedding = cached_openai_call(text)
    Z.append(single_embedding)
    print(text)
    print(single_embedding[:5])

Z = np.array(Z)
np.save(f_save, Z)

print(Z)
print(Z.shape)
