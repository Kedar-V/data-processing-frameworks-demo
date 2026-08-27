"""Create deterministic, nested Parquet datasets for the live demo."""

from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

SEED = 42
TINY = 100
TWO_HUNDRED_THOUSAND = 200_000
FIVE_HUNDRED_THOUSAND = 500_000
ONE_MILLION = 1_000_000
TEN_MILLION = 10_000_000


def prepare(raw: Path, output: Path, force: bool = False) -> None:
    ratings_csv = raw / "ratings.csv"
    movies_csv = raw / "movies.csv"
    if not ratings_csv.exists() or not movies_csv.exists():
        raise FileNotFoundError("MovieLens CSV files are missing. Run `make data`.")

    output.mkdir(parents=True, exist_ok=True)
    expected = [
        output / "ratings_100.parquet",
        output / "ratings_200k.parquet",
        output / "ratings_500k.parquet",
        output / "ratings_1m.parquet",
        output / "ratings_10m.parquet",
        output / "ratings_32m.parquet",
        output / "movies.parquet",
    ]
    if all(path.exists() for path in expected) and not force:
        print("Prepared Parquet files already exist; use --force to replace them.")
        return

    print("Reading MovieLens 32M ratings (preparation may take a few minutes)...")
    ratings = pl.read_csv(
        ratings_csv,
        schema_overrides={
            "userId": pl.Int32,
            "movieId": pl.Int32,
            "rating": pl.Float32,
            "timestamp": pl.Int64,
        },
    )
    if ratings.height < TEN_MILLION:
        raise ValueError(f"Expected at least 10M ratings, found {ratings.height:,}.")

    # One seeded shuffle creates nested subsets: the 1M rows are inside the 10M rows.
    ten_million = ratings.sample(n=TEN_MILLION, shuffle=True, seed=SEED)
    one_million = ten_million.head(ONE_MILLION)
    tiny = one_million.head(TINY)
    two_hundred_thousand = one_million.head(TWO_HUNDRED_THOUSAND)
    five_hundred_thousand = one_million.head(FIVE_HUNDRED_THOUSAND)

    ratings.write_parquet(output / "ratings_32m.parquet", compression="zstd")
    ten_million.write_parquet(output / "ratings_10m.parquet", compression="zstd")
    one_million.write_parquet(output / "ratings_1m.parquet", compression="zstd")
    five_hundred_thousand.write_parquet(
        output / "ratings_500k.parquet", compression="zstd"
    )
    two_hundred_thousand.write_parquet(
        output / "ratings_200k.parquet", compression="zstd"
    )
    tiny.write_parquet(output / "ratings_100.parquet", compression="zstd")
    pl.read_csv(
        movies_csv,
        schema_overrides={"movieId": pl.Int32, "title": pl.String, "genres": pl.String},
    ).write_parquet(output / "movies.parquet", compression="zstd")

    print(
        f"Wrote deterministic subsets (seed={SEED}): "
        f"{tiny.height:,}, {two_hundred_thousand.height:,}, "
        f"{five_hundred_thousand.height:,}, {one_million.height:,}, "
        f"{ten_million.height:,}, and {ratings.height:,} ratings."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, default=Path("data/raw"))
    parser.add_argument("--output", type=Path, default=Path("data/parquet"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    prepare(args.raw, args.output, args.force)
