import csv
from pathlib import Path


DATA_DIR = Path(__file__).parent / "data"


def load_data(data_dir=DATA_DIR):
    data_path = Path(data_dir)
    movies = []
    ratings = []

    with (data_path / "movies.csv").open(encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            movies.append({
                "movie_id": int(row["movieId"]),
                "title": row["title"],
                "genres": [genre for genre in row["genres"].split("|") if genre and genre != "(no genres listed)"],
            })

    with (data_path / "ratings.csv").open(encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            ratings.append({
                "user_id": int(row["userId"]),
                "movie_id": int(row["movieId"]),
                "rating": float(row["rating"]),
                "timestamp": int(row.get("timestamp", 0)),
            })

    return movies, ratings
