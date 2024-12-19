import os
from openai import OpenAI
import pandas as pd
from diskcache import Cache
from pathlib import Path
from tqdm import tqdm

# Save the responses so we don't have to rerun
cache = Cache("data/cache/GPT_summerization")

# Access the saved OPEN_AI KEY
API_KEY = os.getenv("OPENAI_API_KEY_FEDERAL_USECASE_INVENTORY")
assert API_KEY

f_data = "data/cleaned_OMB_inventory.csv"
f_save = Path("data/processed/summary_text.csv")
f_save.parents[0].mkdir(parents=True, exist_ok=True)

model_name = "gpt-4o-mini"

df = pd.read_csv(f_data)

text_fields = [
    "2_use_case_name",
    "11_purpose_benefits",
    "12_outputs",
]

for key in text_fields:
    df[key] = df[key].fillna("")

df["x1_full_text"] = (
    df[text_fields[0]] + "\n" + df[text_fields[1]] + "\n" + df[text_fields[2]]
)

client = OpenAI(api_key=API_KEY)


def cached_openai_call(prompt, text):
    key = (prompt, text)
    if key in cache:
        return cache[key]

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": text},
    ]

    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model_name,
    )

    response = chat_completion.choices[0].message.content

    cache[key] = response
    return cache[key]


prompt = "Summarize the following project into two or three sentences. Use declarative language."

data = []
for text in tqdm(df["x1_full_text"]):
    summary_text = cached_openai_call(prompt, text)
    print("***********************")
    print(text)
    print("-----------------------")
    print(summary_text)
    data.append(summary_text)

df["x2_summary_text"] = data

keep_cols = [
    "1_use_case_id",
    "2_use_case_name",
    "x2_summary_text",
]

df = df[keep_cols].set_index("1_use_case_id")
df.to_csv(f_save)
