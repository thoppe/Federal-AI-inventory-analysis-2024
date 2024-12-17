from pathlib import Path
import hashlib
import pandas as pd

f_save = "processed_responses/raw_agency_checksums.csv"

def compute_md5(file_path):
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as file:
        # Read the file in chunks to handle large files efficiently
        for chunk in iter(lambda: file.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


data = []

for f in Path("raw_agency_responses").glob("*"):
    if f.suffix in [".xlsx", ".csv"]:
        if "checksums" in f.name:
            continue

        hx = compute_md5(f)
        agency = f.name.split("_")[0]
        data.append(
            {
                "filename": f.name,
                "agency": agency,
                "md5sum": hx,
            }
        )
df = pd.DataFrame(data).set_index("agency")
df.to_csv(f_save)
print(df)
