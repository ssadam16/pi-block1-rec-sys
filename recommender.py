import math


class Recommender:
    def __init__(self, movies, ratings):
        self.movies = {movie["movie_id"]: movie for movie in movies}
        self.user_ratings = {}
        self.movie_ratings = {}

        for row in ratings:
            user_id = row["user_id"]
            movie_id = row["movie_id"]
            rating = row["rating"]
            self.user_ratings.setdefault(user_id, {})[movie_id] = rating
            self.movie_ratings.setdefault(movie_id, []).append(rating)

        all_ratings = [row["rating"] for row in ratings]
        self.global_average = sum(all_ratings) / len(all_ratings) if all_ratings else 0

    def recommend(self, method, user_id, limit=10):
        if limit < 1:
            return []

        if method == "popular":
            return self.popular(user_id, limit)
        if method == "content":
            return self.content_based(user_id, limit)
        if method == "collaborative":
            return self.user_based(user_id, limit)
        raise ValueError(f"Нет такого метода: {method}")

    def popular(self, user_id=None, limit=10):
        watched = set(self.user_ratings.get(user_id, {}))
        recommendations = []

        for movie_id, movie in self.movies.items():
            ratings = self.movie_ratings.get(movie_id, [])
            if not ratings or movie_id in watched:
                continue

            count = len(ratings)
            average = sum(ratings) / count
            score = (count * average + 5 * self.global_average) / (count + 5)
            recommendations.append(self._item(movie_id, score))

        return sorted(recommendations, key=lambda item: item["score"], reverse=True)[:limit]

    def content_based(self, user_id, limit=10):
        user_ratings = self.user_ratings.get(user_id, {})
        profile = {}

        for movie_id, rating in user_ratings.items():
            if rating < 4:
                continue
            movie = self.movies.get(movie_id)
            if not movie:
                continue
            for genre in movie["genres"]:
                profile[genre] = profile.get(genre, 0) + rating - 3

        if not profile:
            return self.popular(user_id, limit)

        recommendations = []
        for movie_id, movie in self.movies.items():
            if movie_id in user_ratings or not movie["genres"]:
                continue
            score = sum(profile.get(genre, 0) for genre in movie["genres"]) / len(movie["genres"])
            if score > 0:

                recommendations.append(self._item(movie_id, score))

        if not recommendations:
            return self.popular(user_id, limit)
        return sorted(recommendations, key=lambda item: item["score"],reverse=True)[:limit]

    def user_based(self, user_id, limit=10):
        target_ratings = self.user_ratings.get(user_id, {})
        if not target_ratings:
            return self.popular(user_id, limit)

        neighbors = []
        for other_id, other_ratings in self.user_ratings.items():
            if other_id == user_id:
                continue
            similarity = self._user_similarity(target_ratings, other_ratings)
            if similarity > 0:
                neighbors.append((other_id, similarity))

        scores = {}
        weights = {}
        for other_id, similarity in neighbors:
            for movie_id, rating in self.user_ratings[other_id].items():
                if movie_id in target_ratings or movie_id not in self.movies:
                    continue
                scores[movie_id] = scores.get(movie_id, 0) + similarity * rating
                weights[movie_id] = weights.get(movie_id, 0) + similarity

        recommendations = [
            self._item(movie_id, scores[movie_id] / weights[movie_id])
            for movie_id in scores
        ]

        if not recommendations:
            return self.popular(user_id, limit)
        return sorted(recommendations, key=lambda item: item["score"], reverse=True)[:limit]

    def _user_similarity(self, first, second):
        shared = first.keys() & second.keys()
        if len(shared) < 2:
            return 0

        first_average = sum(first[movie_id] for movie_id in shared) / len(shared)
        second_average = sum(second[movie_id] for movie_id in shared) / len(shared)
        numerator = sum(
            (first[movie_id] - first_average) * (second[movie_id] - second_average)
            for movie_id in shared
        )
        first_size = math.sqrt(sum((first[movie_id] - first_average) ** 2 for movie_id in shared))
        second_size = math.sqrt(sum((second[movie_id] - second_average) ** 2 for movie_id in shared))
        if first_size == 0 or second_size == 0:
            return 0
        return numerator / (first_size * second_size)

    def _item(self, movie_id, score):
        return {
            "movie_id": movie_id,
            "title": self.movies[movie_id]["title"],
            "score": score,
        }
