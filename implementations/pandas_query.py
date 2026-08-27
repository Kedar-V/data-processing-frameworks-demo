"""Pandas implementation of the shared MovieLens query."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def run_query(
    ratings_path: Path, movies_path: Path, min_ratings: int = 1_000
) -> pd.DataFrame:
    ratings = pd.read_parquet(ratings_path, columns=["movieId", "rating"])
    movies = pd.read_parquet(movies_path, columns=["movieId", "title"])
    return (
        ratings.groupby("movieId")
        .agg(average_rating=("rating", "mean"), rating_count=("rating", "count"))
        .query("rating_count >= @min_ratings")
        .reset_index()
        .merge(movies, on="movieId")
        .sort_values(
            ["average_rating", "rating_count", "movieId"],
            ascending=[False, False, True],
        )
        .reset_index(drop=True)
    )


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
