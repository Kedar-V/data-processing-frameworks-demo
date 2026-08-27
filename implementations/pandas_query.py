"""Pandas implementation of the shared MovieLens query."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

RATING_MIN = 0.5
RATING_RANGE = 4.5
COMPLETION_RANGE = 100.0
RATING_COLUMNS = [
    "movieId",
    "rating",
    "completion_pct",
    "watch_minutes",
    "helpful_votes",
    "rewatch_count",
]


def run_query(
    ratings_path: Path, movies_path: Path, min_ratings: int = 1_000
) -> pd.DataFrame:
    ratings = pd.read_parquet(ratings_path, columns=RATING_COLUMNS)
    movies = pd.read_parquet(movies_path, columns=["movieId", "title"])
    result = (
        ratings.groupby("movieId")
        .agg(
            average_rating=("rating", "mean"),
            rating_count=("rating", "count"),
            average_completion_pct=("completion_pct", "mean"),
            average_watch_minutes=("watch_minutes", "mean"),
            total_helpful_votes=("helpful_votes", "sum"),
            average_rewatch_count=("rewatch_count", "mean"),
        )
        .query("rating_count >= @min_ratings")
        .reset_index()
        .merge(movies, on="movieId")
    )
    result["audience_score"] = (
        (result["average_rating"] - RATING_MIN) / RATING_RANGE
        + result["average_completion_pct"] / COMPLETION_RANGE
    ) / 2
    return result.sort_values(
        ["audience_score", "rating_count", "movieId"],
        ascending=[False, False, True],
    ).reset_index(drop=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ratings", type=Path, default=Path("data/parquet/ratings_1m.parquet")
    )
    parser.add_argument(
        "--movies", type=Path, default=Path("data/parquet/movies.parquet")
    )
    parser.add_argument("--min-ratings", type=int, default=1_000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_query(args.ratings, args.movies, args.min_ratings)
    if args.output:
        result.to_csv(args.output, index=False)
    print(result.head(10).to_string(index=False))
