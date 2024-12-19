from pathlib import Path
from dspipe import Pipe
import hashlib
import pandas as pd


def compute_file_checksum(f0):
    md5_hash = hashlib.md5()
    with open(f0, "rb") as file:
        # Read the file in chunks to handle large files efficiently
        for chunk in iter(lambda: file.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def compute(f0, f1):
    hx = compute_file_checksum(f0)

    with open(f1, "w") as FOUT:
        FOUT.write(hx)

    print(f1, hx)


if __name__ == "__main__":
    Pipe("data/raw", "data/checksums", output_suffix=".txt")(compute, 1)
