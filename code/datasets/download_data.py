"""Download the Auto MPG dataset from the UCI repository."""

from pathlib import Path
from urllib.request import urlopen


DATASET_URL = "https://archive.ics.uci.edu/static/public/9/data.csv"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "auto_mpg.csv"


def download_data(destination: Path = RAW_DATA_PATH) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(DATASET_URL, timeout=30) as response:
        destination.write_bytes(response.read())
    return destination


if __name__ == "__main__":
    print(download_data())

