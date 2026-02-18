"""
Download O*NET bulk data files from US Department of Labor.
Run once during setup to populate backend/data/onet_raw/
"""

import requests
import os
from pathlib import Path
import urllib3

# Suppress SSL warnings when verification is disabled
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# O*NET bulk data URL
ONET_BASE_URL = "https://www.onetcenter.org/dl_files/database/db_28_2_text/"

# Files to download
FILES_TO_DOWNLOAD = [
    "Skills.txt",
    "Knowledge.txt",
    "Abilities.txt",
    "Occupation Data.txt",
    "Content Model Reference.txt"
]

def download_onet_database():
    """Download all O*NET data files"""
    # Note: SSL verification disabled for O*NET downloads due to certificate chain issues
    # This is acceptable for one-time setup from official government website

    data_dir = Path(__file__).parent.parent / "data" / "onet_raw"
    data_dir.mkdir(parents=True, exist_ok=True)

    print("Downloading O*NET database files...")

    for filename in FILES_TO_DOWNLOAD:
        url = f"{ONET_BASE_URL}{filename}"
        output_path = data_dir / filename

        print(f"Downloading {filename}...", end=" ")

        try:
            response = requests.get(url, timeout=30, verify=False)  # Disable SSL verification for O*NET downloads
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                f.write(response.content)

            print(f"✓ ({len(response.content) // 1024} KB)")
        except requests.RequestException as e:
            print(f"✗ Failed: {e}")
            raise

    print(f"\n✓ Downloaded {len(FILES_TO_DOWNLOAD)} files to {data_dir}")
    return data_dir

if __name__ == "__main__":
    download_onet_database()
