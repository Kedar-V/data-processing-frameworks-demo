"""Small benchmark runner for the single shared teaching workload."""

from __future__ import annotations

import argparse
import statistics
import sys
import threading
import time
from pathlib import Path

import pandas as pd
from tqdm.auto import tqdm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from implementations.pandas_query import run_query as pandas_query
from implementations.polars_query import run_query as polars_query

DATASETS = {
    "100": (100, ROOT / "data/parquet/ratings_100.parquet"),
    "200k": (200_000, ROOT / "data/parquet/ratings_200k.parquet"),
    "500k": (500_000, ROOT / "data/parquet/ratings_500k.parquet"),
    "1m": (1_000_000, ROOT / "data/parquet/ratings_1m.parquet"),
    "10m": (10_000_000, ROOT / "data/parquet/ratings_10m.parquet"),
    "32m": (32_000_204, ROOT / "data/parquet/ratings_32m.parquet"),
    "70m": (70_000_000, ROOT / "data/synthetic/ratings_70m.parquet"),
    "100m": (100_000_000, ROOT / "data/synthetic/ratings_100m.parquet"),
    "350m": (350_000_000, ROOT / "data/synthetic/ratings_350m.parquet"),
    "500m": (500_000_000, ROOT / "data/synthetic/ratings_500m.parquet"),
}
FRAMEWORKS = ["pandas", "polars-eager", "polars-lazy", "spark"]
LABELS = {
    "pandas": "Pandas",
    "polars-eager": "Polars Eager",
    "polars-lazy": "Polars Lazy",
    "spark": "PySpark",
}
DEFAULT_ROWS_PER_SECOND = {
    "pandas": 30_000_000,
    "polars-eager": 100_000_000,
    "polars-lazy": 120_000_000,
    "spark": 30_000_000,
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


def timed_run_with_progress(
    framework: str,
    ratings: Path,
    movies: Path,
    min_ratings: int,
    rows: int,
    row_progress: tqdm,
    completed_rows: int,
    expected_seconds: float,
) -> float:
    """Run one sample while showing explicitly estimated in-flight row progress."""
    finished = threading.Event()
    started = time.perf_counter()

    def refresh_estimate() -> None:
        while not finished.wait(0.2):
            elapsed = time.perf_counter() - started
            estimated_rows = min(int(rows * elapsed / expected_seconds), rows - 1)
            row_progress.n = completed_rows + estimated_rows
            row_progress.set_postfix_str(f"running {elapsed:.1f}s; rows estimated")
            row_progress.refresh()

    updater = threading.Thread(target=refresh_estimate, daemon=True)
    updater.start()
    try:
        return timed_run(framework, ratings, movies, min_ratings)
    finally:
        finished.set()
        updater.join()
        row_progress.n = completed_rows + rows
        row_progress.refresh()


def save_record(record: dict[str, object], output: Path) -> None:
    """Merge one completed measurement immediately so interrupted runs keep progress."""
    fresh = pd.DataFrame([record])
    if output.exists():
        old = pd.read_csv(output)
        key = (record["framework"], record["rows"])
        old = old[~old.apply(lambda row: (row.framework, row.rows) == key, axis=1)]
        fresh = pd.concat([old, fresh], ignore_index=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(f"{output.suffix}.tmp")
    fresh.sort_values(["rows", "framework"]).to_csv(temporary, index=False)
    temporary.replace(output)


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
    dataset_progress = tqdm(
        args.sizes,
        desc="Datasets",
        unit="dataset",
        dynamic_ncols=True,
        disable=False,
    )
    for size in dataset_progress:
        rows, ratings = DATASETS[size]
        if not ratings.exists():
            raise FileNotFoundError(f"{ratings} is missing; run `make data`.")
        dataset_progress.set_postfix_str(f"{size}: {rows:,} rows")
        for framework in selected:
            samples = []
            completed_rows = 0
            default_seconds = max(
                rows / DEFAULT_ROWS_PER_SECOND[framework],
                0.1 if framework != "spark" else 0.5,
            )
            with tqdm(
                total=rows * args.repeats,
                desc=f"{LABELS[framework]} {size}",
                unit="row",
                unit_scale=True,
                dynamic_ncols=True,
                leave=False,
                disable=False,
            ) as row_progress:
                for repeat in range(args.repeats):
                    expected_seconds = (
                        statistics.median(samples) if samples else default_seconds
                    )
                    runtime = timed_run_with_progress(
                        framework,
                        ratings,
                        movies,
                        args.min_ratings,
                        rows,
                        row_progress,
                        completed_rows,
                        expected_seconds,
                    )
                    samples.append(runtime)
                    completed_rows += rows
                    row_progress.set_postfix_str(
                        f"repeat {repeat + 1}/{args.repeats}: {runtime:.3f}s"
                    )
            runtime = statistics.median(samples)
            record = {
                "framework": LABELS[framework],
                "rows": rows,
                "runtime_seconds": round(runtime, 6),
                "rows_per_second": round(rows / runtime),
            }
            save_record(record, args.output)
            tqdm.write(f"{LABELS[framework]:<14} {size:>4}: {runtime:.3f}s")


if __name__ == "__main__":
    main()
