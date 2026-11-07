from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile


URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
DATA_DIR = Path(__file__).parent / "data"


def main():
    with urlopen(URL, timeout=30) as response:
        archive_data = response.read()

    with ZipFile(BytesIO(archive_data)) as archive:
        for name in ["movies.csv", "ratings.csv"]:
            target = DATA_DIR / name
            target.write_bytes(archive.read(f"ml-latest-small/{name}"))

    print(f"Данные сохранены в {DATA_DIR}")


if __name__ == "__main__":
    main()
