"""Confirm that every engine returns the same analytical answer."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from implementations.pandas_query import run_query as pandas_query
from implementations.polars_query import run_query as polars_query

RATINGS = ROOT / "data/parquet/ratings_1m.parquet"
MOVIES = ROOT / "data/parquet/movies.parquet"
MIN_RATINGS = 1_000
COLUMNS = [
    "movieId",
    "average_rating",
    "rating_count",
    "average_completion_pct",
    "average_watch_minutes",
    "total_helpful_votes",
    "average_rewatch_count",
    "audience_score",
]


def canonical(frame: pd.DataFrame) -> pd.DataFrame:
    return frame[COLUMNS].sort_values("movieId").reset_index(drop=True)


def assert_matches(expected: pd.DataFrame, actual: pd.DataFrame, name: str) -> None:
    pd.testing.assert_frame_equal(
        canonical(expected),
        canonical(actual),
        check_dtype=False,
        atol=1e-6,
        rtol=1e-6,
    )
    print(f"✓ {name} matches Pandas")


def main() -> None:
    if not RATINGS.exists():
        raise FileNotFoundError("Prepared data is missing. Run `make data`.")

    expected = pandas_query(RATINGS, MOVIES, MIN_RATINGS)
    assert_matches(
        expected,
        polars_query(RATINGS, MOVIES, MIN_RATINGS, lazy=False).to_pandas(),
        "Polars Eager",
    )
    assert_matches(
        expected,
        polars_query(RATINGS, MOVIES, MIN_RATINGS, lazy=True).to_pandas(),
        "Polars Lazy",
    )

    from implementations.spark_query import create_session, run_query

    spark = create_session()
    try:
        actual = run_query(spark, RATINGS, MOVIES, MIN_RATINGS).toPandas()
        assert_matches(expected, actual, "PySpark")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
