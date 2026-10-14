"""
Download and prepare the genuine UCI Machine Learning Repository SMS Spam Collection dataset.
"""
import io
import os
import urllib.request
import zipfile

DATASET_URL = "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"
TARGET_DIR = os.path.join(os.path.dirname(__file__), "data")


def download_and_extract():
    os.makedirs(TARGET_DIR, exist_ok=True)
    raw_file = os.path.join(TARGET_DIR, "SMSSpamCollection")
    readme_file = os.path.join(TARGET_DIR, "README_UCI.txt")

    if os.path.exists(raw_file):
        print(f"Dataset already present at: {raw_file}")
        return

    print(f"Downloading genuine dataset from UCI ML Repository: {DATASET_URL}")
    req = urllib.request.Request(
        DATASET_URL,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Academic-Research-Client"}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        zip_data = response.read()

    print(f"Downloaded {len(zip_data)} bytes. Extracting files...")
    with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
        for name in z.namelist():
            if name.lower().endswith("smsspamcollection"):
                with open(raw_file, "wb") as f_out:
                    f_out.write(z.read(name))
                print(f"Extracted dataset to {raw_file}")
            elif name.lower().endswith("readme"):
                with open(readme_file, "wb") as f_out:
                    f_out.write(z.read(name))
                print(f"Extracted readme to {readme_file}")

    # Verify counts
    with open(raw_file, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    print(f"Verification complete: {len(lines)} messages loaded.")


if __name__ == "__main__":
    download_and_extract()
