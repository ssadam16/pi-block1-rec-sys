import time

from recommender import Recommender


def split_ratings(ratings):
    by_user = {}
    for row in ratings:
        by_user.setdefault(row["user_id"], []).append(row)

    train = []
    test = []
    for user_rows in by_user.values():
        user_rows.sort(key=lambda row: row["timestamp"])
        if len(user_rows) < 5:
            train.extend(user_rows)
            continue
        positive_rows = [row for row in user_rows if row["rating"] >= 4]
        if not positive_rows:
            train.extend(user_rows)
            continue
        held_out = positive_rows[-1]
        train.extend(row for row in user_rows if row is not held_out)
        test.append(held_out)

    return train, test


def evaluate_method(movies, ratings, method, k=10):
    train, test = split_ratings(ratings)
    relevant_by_user = {}
    for row in test:
        if row["rating"] >= 4:
            relevant_by_user.setdefault(row["user_id"], set()).add(row["movie_id"])

    recommender = Recommender(movies, train)
    precisions = []
    recalls = []
    hits = []
    recommended_movies = set()
    elapsed_times = []

    for user_id, relevant_movies in relevant_by_user.items():
        started_at = time.perf_counter()
        recommendations = recommender.recommend(method, user_id, k)
        elapsed_times.append((time.perf_counter() - started_at) * 1000)
        recommended_ids = {item["movie_id"] for item in recommendations}
        recommended_movies.update(recommended_ids)
        found = len(recommended_ids & relevant_movies)
        precisions.append(found / k)
        recalls.append(found / len(relevant_movies))
        hits.append(1 if found else 0)

    user_count = len(relevant_by_user)
    if not user_count:
        return None

    return {
        "precision": sum(precisions) / user_count,
        "recall": sum(recalls) / user_count,
        "hit_rate": sum(hits) / user_count,
        "coverage": len(recommended_movies) / len(movies) if movies else 0,
        "latency": sum(elapsed_times) / len(elapsed_times),
        "users": user_count,
    }


def evaluate_all(movies, ratings, k=10):
    print(f"K={k}")
    for method in ["popular", "content", "collaborative"]:
        result = evaluate_method(movies, ratings, method, k)
        if not result:
            print(f"{method}: недостаточно данных")
            continue
        print(
            f"{method}: precision={result['precision']:.3f}, "
            f"recall={result['recall']:.3f}, "
            f"hit_rate={result['hit_rate']:.3f}, "
            f"coverage={result['coverage']:.1%}, "
            f"latency={result['latency']:.2f} мс, "
            f"users={result['users']}"
        )
