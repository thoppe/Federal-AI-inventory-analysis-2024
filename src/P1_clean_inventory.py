import pandas as pd

# Update this as needed
f_csv = "data/raw/19-12-2024_consolidated_ai_inventory_raw.csv"

df = pd.read_csv(f_csv)

# Clean processing errors

# Remove any leading or trailing spaces
for key in df.columns:
    if df[key].dtype == "object":
        df[key] = df[key].str.strip()

# Assign use-case IDs in the format of [AGENCY]-2024-[0001-9999]

df["1_use_case_id"] = None
for key, dx in df.groupby("3_abr"):
    dx["1_use_case_id"] = [f"{key}-2024-{n+1:04d}" for n in range(len(dx))]
    df.loc[dx.index, "1_use_case_id"] = dx["1_use_case_id"]
df = df.set_index("1_use_case_id")

print(df)
# se_case_ID = df['3_abr']
# rint(df.columns[:10])
# print(df['3_abr'])


# Supplement the DHS additional information
