"""Small benchmark runner for the single shared teaching workload."""

from __future__ import annotations

import argparse
import statistics
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from implementations.pandas_query import run_query as pandas_query
from implementations.polars_query import run_query as polars_query

DATASETS = {
    "1m": (1_000_000, ROOT / "data/parquet/ratings_1m.parquet"),
    "10m": (10_000_000, ROOT / "data/parquet/ratings_10m.parquet"),
    "32m": (32_000_000, ROOT / "data/parquet/ratings_32m.parquet"),
    "1b": (1_024_006_528, ROOT / "data/synthetic/ratings_1b.parquet"),
}
FRAMEWORKS = ["pandas", "polars-eager", "polars-lazy", "spark"]
LABELS = {
    "pandas": "Pandas",
    "polars-eager": "Polars Eager",
    "polars-lazy": "Polars Lazy",
    "spark": "PySpark",
}


def timed_run(framework: str, ratings: Path, movies: Path, min_ratings: int) -> float:
    start = time.perf_counter()
    if framework == "pandas":
        pandas_query(ratings, movies, min_ratings)
    elif framework.startswith("polars"):
        polars_query(ratings, movies, min_ratings, lazy=framework.endswith("lazy"))
    elif framework == "spark":
        from implementations.spark_query import create_session, run_query

        spark = create_session()
        try:
            run_query(spark, ratings, movies, min_ratings).collect()
        finally:
            spark.stop()
    return time.perf_counter() - start


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--framework", choices=["all", *FRAMEWORKS], default="all")
    parser.add_argument("--sizes", nargs="+", choices=DATASETS, default=["1m"])
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--min-ratings", type=int, default=1_000)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "results/benchmark_results.csv"
    )
    args = parser.parse_args()

    selected = FRAMEWORKS if args.framework == "all" else [args.framework]
    movies = ROOT / "data/parquet/movies.parquet"
    records = []
    for size in args.sizes:
        rows, ratings = DATASETS[size]
        if not ratings.exists():
            raise FileNotFoundError(f"{ratings} is missing; run `make data`.")
        for framework in selected:
            samples = [
                timed_run(framework, ratings, movies, args.min_ratings)
                for _ in range(args.repeats)
            ]
            runtime = statistics.median(samples)
            records.append(
                {
                    "framework": LABELS[framework],
                    "rows": rows,
                    "runtime_seconds": round(runtime, 6),
                    "rows_per_second": round(rows / runtime),
                }
            )
            print(f"{LABELS[framework]:<14} {size:>3}: {runtime:.3f}s")

    fresh = pd.DataFrame(records)
    if args.output.exists():
        old = pd.read_csv(args.output)
        keys = set(zip(fresh.framework, fresh.rows))
        old = old[~old.apply(lambda row: (row.framework, row.rows) in keys, axis=1)]
        fresh = pd.concat([old, fresh], ignore_index=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fresh.sort_values(["rows", "framework"]).to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
