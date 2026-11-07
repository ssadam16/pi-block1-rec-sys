import argparse
import time

from data_loader import load_data
from evaluation import evaluate_all
from recommender import Recommender


def main():
    parser = argparse.ArgumentParser(description="Подбор фильмов ")
    parser.add_argument("--method", choices=["popular", "content", "collaborative"], default="content")
    parser.add_argument("--user-id", type=int, default=1)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--evaluate", action="store_true")
    args = parser.parse_args()

    movies, ratings = load_data()

    if args.evaluate:
        evaluate_all(movies, ratings)
        return

    recommender = Recommender(movies, ratings)
    started_at = time.perf_counter()
    recommendations = recommender.recommend(args.method, args.user_id, args.limit)
    elapsed = (time.perf_counter() - started_at) * 1000

    print(f"Рекомендации для пользователя {args.user_id} ({args.method}):")
    if not recommendations:
        print("Нет фильмов для рекомендации.")
        return

    for number, item in enumerate(recommendations, start=1):
        print(f"{number}. {item['title']} — {item['score']:.2f}")

    print(f"Время ответа: {elapsed:.2f} мс")


if __name__ == "__main__":
    main()
