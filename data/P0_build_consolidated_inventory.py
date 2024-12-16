import pandas as pd
from pathlib import Path

f_save = "processed_responses/basic_consolidated.csv"

required_columns = [
    "Use Case ID",
    "Use Case Name",
    "Agency",
    "Component",
    "What is the intended purpose and expected benefits of the AI?",
    "Describe the AI system’s outputs.",
]


data = []
for f in Path("cleaned_agency_responses").glob("*.csv"):
    dx = pd.read_csv(f)

    for key in required_columns:
        if key not in dx.columns:
            print(f"Missing '{key}' in {f}")
            exit(1)

    dx = dx[required_columns]
    data.append(dx)

df = pd.concat(data).set_index("Use Case ID")
df.to_csv(f_save)
print(df)
