from pathlib import Path
from dspipe import Pipe
import hashlib
import pandas as pd

#f_save = "processed_responses/raw_agency_checksums.csv"

def compute(f0, f1):
    md5_hash = hashlib.md5()
    with open(f0, "rb") as file:
        # Read the file in chunks to handle large files efficiently
        for chunk in iter(lambda: file.read(4096), b""):
            md5_hash.update(chunk)
    hx = md5_hash.hexdigest()
    with open(f1, 'w') as FOUT:
        FOUT.write(hx)

    print(f1, hx)

Pipe("data/raw", "data/raw_agency_checksums", output_suffix='.txt')(compute, 1)
