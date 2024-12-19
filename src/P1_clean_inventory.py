import pandas as pd

# Update this as needed
f_csv = "data/raw/OMB_19-12-2024_consolidated_ai_inventory_raw.csv"
f_save = "data/cleaned_OMB_inventory.csv"
df = pd.read_csv(f_csv)

# Clean processing errors: remove any leading or trailing spaces

for key in df.columns:
    if df[key].dtype == "object":
        df[key] = df[key].str.strip()

# Assign use-case IDs in the format of [AGENCY]-2024-[0001-9999]

df["1_use_case_id"] = None
for key, dx in df.groupby("3_abr"):
    dx["1_use_case_id"] = [f"{key}-2024-{n+1:04d}" for n in range(len(dx))]
    df.loc[dx.index, "1_use_case_id"] = dx["1_use_case_id"]
df = df.set_index("1_use_case_id")

dx = pd.read_csv("data/raw/DHS_24_1216_ocio_2024-dhs-ai-use-case-inventory.csv")

# DHS provides more information. Append this into "12_outputs"
# Supplement the DHS additional information

# Check that all DHS names are unique
names0 = dx["Use Case Name"].tolist()
assert len(names0) == len(set(names0))

names1 = df[df["3_abr"] == "DHS"]["2_use_case_name"].tolist()
assert len(names1) == len(set(names1))

additional_column0 = "Summary of Use Case"
for _, row in dx.iterrows():
    name = row["Use Case Name"]
    idx = (df["2_use_case_name"] == name) & (df["3_abr"] == "DHS")
    assert idx.sum() <= 1
    df.loc[idx, "12_outputs"] = (
        df.loc[idx, "12_outputs"] + "\n" + row[additional_column0]
    )

df.to_csv(f_save)
print(df)
