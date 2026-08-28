"""Eager and lazy Polars implementations of the shared MovieLens query."""

from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

RATING_COLUMNS = ["movieId", "rating"]


def _parquet_source(path: Path) -> str | Path:
    """Return a glob for partitioned Parquet directories."""
    return str(path / "*.parquet") if path.is_dir() else path


def _pipeline(
    ratings: pl.DataFrame | pl.LazyFrame,
    movies: pl.DataFrame | pl.LazyFrame,
    min_ratings: int,
):
    return (
        ratings.group_by("movieId")
        .agg(
            pl.col("rating").mean().alias("avg_rating"),
            pl.len().alias("rating_count"),
        )
        .filter(pl.col("rating_count") >= min_ratings)
        .join(movies.select("movieId", "title"), on="movieId")
        .sort(["avg_rating", "movieId"], descending=[True, False])
    )


def run_query(
    ratings_path: Path,
    movies_path: Path,
    min_ratings: int = 1_000,
    lazy: bool = True,
) -> pl.DataFrame:
    ratings_source = _parquet_source(ratings_path)
    if lazy:
        return _pipeline(
            pl.scan_parquet(ratings_source).select(RATING_COLUMNS),
            pl.scan_parquet(movies_path),
            min_ratings,
        ).collect()
    return _pipeline(
        pl.read_parquet(ratings_source, columns=RATING_COLUMNS),
        pl.read_parquet(movies_path, columns=["movieId", "title"]),
        min_ratings,
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
    parser.add_argument("--mode", choices=["eager", "lazy"], default="lazy")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_query(args.ratings, args.movies, args.min_ratings, args.mode == "lazy")
    if args.output:
        result.write_csv(args.output)
    print(result.head(10))
