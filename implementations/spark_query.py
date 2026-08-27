"""Local PySpark implementation of the shared MovieLens query."""

from __future__ import annotations

import argparse
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession, functions as F

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


def create_session() -> SparkSession:
    spark = (
        SparkSession.builder.master("local[*]")
        .appName("MovieLens dataframe benchmark")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def run_query(
    spark: SparkSession,
    ratings_path: Path,
    movies_path: Path,
    min_ratings: int = 1_000,
) -> DataFrame:
    ratings = spark.read.parquet(str(ratings_path)).select(*RATING_COLUMNS)
    movies = spark.read.parquet(str(movies_path)).select("movieId", "title")
    return (
        ratings.groupBy("movieId")
        .agg(
            F.avg("rating").alias("average_rating"),
            F.count("*").alias("rating_count"),
            F.avg("completion_pct").alias("average_completion_pct"),
            F.avg("watch_minutes").alias("average_watch_minutes"),
            F.sum("helpful_votes").alias("total_helpful_votes"),
            F.avg("rewatch_count").alias("average_rewatch_count"),
        )
        .filter(F.col("rating_count") >= min_ratings)
        .join(movies, "movieId")
        .withColumn(
            "audience_score",
            (
                (F.col("average_rating") - RATING_MIN) / RATING_RANGE
                + F.col("average_completion_pct") / COMPLETION_RANGE
            )
            / 2,
        )
        .orderBy(
            F.desc("audience_score"),
            F.desc("rating_count"),
            F.asc("movieId"),
        )
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
    parser.add_argument("--explain", action="store_true")
    args = parser.parse_args()

    session = create_session()
    try:
        result = run_query(session, args.ratings, args.movies, args.min_ratings)
        if args.explain:
            result.explain("formatted")
        result.cache()
        print(result.limit(10).toPandas().to_string(index=False))
        if args.output:
            result.toPandas().to_csv(args.output, index=False)
    finally:
        session.stop()
