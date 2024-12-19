import os
from openai import OpenAI
import pandas as pd
from diskcache import Cache
from tqdm import tqdm

# Save the responses so we don't have to rerun
cache = Cache("cache/GPT_summerization")

# Access the saved OPEN_AI KEY
API_KEY = os.getenv("OPENAI_API_KEY_FEDERAL_USECASE_INVENTORY")
assert API_KEY

#f_data = "processed_responses/basic_consolidated.csv"
f_data = "2024_consolidated_ai_inventory_raw.csv"

model_name = "gpt-4o-mini"

df = pd.read_csv(f_data)

text_fields = [
    "2_use_case_name",
    "11_purpose_benefits",
    "12_outputs",
]

for key in text_fields:
    df[key] = df[key].fillna("")

df["full_text"] = (
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
for text in tqdm(df["full_text"]):
    summary_text = cached_openai_call(prompt, text)
    print("***********************")
    print(text)
    print("-----------------------")
    print(summary_text)
    data.append(summary_text)

df["summary_text"] = data

keep_cols = [
#    "Use Case ID",
    "2_use_case_name",
    "summary_text",
]

df = df[keep_cols]#.set_index("Use Case ID")
df.to_csv("processed_responses/summary_text.csv", index=False)
