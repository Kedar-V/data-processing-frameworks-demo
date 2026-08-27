"""Validate prepared schemas, ranges, nesting, and exact row counts."""

from __future__ import annotations

import json
from pathlib import Path

import polars as pl
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
PARQUET = ROOT / "data/parquet"
SYNTHETIC = ROOT / "data/synthetic"

EXPECTED_COLUMNS = {
    "userId",
    "movieId",
    "rating",
    "timestamp",
    "completion_pct",
    "watch_minutes",
    "helpful_votes",
    "rewatch_count",
}
PREPARED_ROWS = {
    "ratings_100.parquet": 100,
    "ratings_200k.parquet": 200_000,
    "ratings_500k.parquet": 500_000,
    "ratings_1m.parquet": 1_000_000,
    "ratings_10m.parquet": 10_000_000,
    "ratings_32m.parquet": 32_000_204,
}
SYNTHETIC_ROWS = {
    "ratings_70m.parquet": 70_000_000,
    "ratings_100m.parquet": 100_000_000,
    "ratings_350m.parquet": 350_000_000,
    "ratings_500m.parquet": 500_000_000,
}


def directory_rows(path: Path) -> int:
    return sum(
        fragment.metadata.num_rows
        for fragment in pq.ParquetDataset(path).fragments
        if fragment.metadata is not None
    )


def main() -> None:
    for name, expected_rows in PREPARED_ROWS.items():
        path = PARQUET / name
        actual_rows = pq.ParquetFile(path).metadata.num_rows
        assert actual_rows == expected_rows, (path, actual_rows, expected_rows)
        assert EXPECTED_COLUMNS.issubset(pl.read_parquet_schema(path)), path

    one_million = pl.read_parquet(PARQUET / "ratings_1m.parquet")
    for name, rows in [
        ("ratings_100.parquet", 100),
        ("ratings_200k.parquet", 200_000),
        ("ratings_500k.parquet", 500_000),
    ]:
        assert pl.read_parquet(PARQUET / name).equals(one_million.head(rows)), name
    ten_million_head = (
        pl.scan_parquet(PARQUET / "ratings_10m.parquet").head(1_000_000).collect()
    )
    assert ten_million_head.equals(one_million), "1M subset is not nested in 10M"

    ranges = one_million.select(
        pl.col("rating").min().alias("rating_min"),
        pl.col("rating").max().alias("rating_max"),
        pl.col("completion_pct").min().alias("completion_min"),
        pl.col("completion_pct").max().alias("completion_max"),
        pl.col("watch_minutes").min().alias("watch_min"),
        pl.col("watch_minutes").max().alias("watch_max"),
        pl.col("helpful_votes").min().alias("helpful_min"),
        pl.col("helpful_votes").max().alias("helpful_max"),
        pl.col("rewatch_count").min().alias("rewatch_min"),
        pl.col("rewatch_count").max().alias("rewatch_max"),
    ).row(0, named=True)
    assert 0.5 <= ranges["rating_min"] <= ranges["rating_max"] <= 5.0
    assert 0 <= ranges["completion_min"] <= ranges["completion_max"] <= 100
    assert 20 <= ranges["watch_min"] <= ranges["watch_max"] <= 180
    assert 0 <= ranges["helpful_min"] <= ranges["helpful_max"] <= 50
    assert 0 <= ranges["rewatch_min"] <= ranges["rewatch_max"] <= 5

    for name, expected_rows in SYNTHETIC_ROWS.items():
        path = SYNTHETIC / name
        actual_rows = directory_rows(path)
        assert actual_rows == expected_rows, (path, actual_rows, expected_rows)
        manifest = json.loads((path / "_synthetic_manifest.json").read_text())
        assert manifest["rows"] == expected_rows, path
        first_part = next(path.glob("*.parquet"))
        assert EXPECTED_COLUMNS.issubset(pl.read_parquet_schema(first_part)), path

    print("✓ Prepared schemas, ranges, nesting, and row counts are valid")


if __name__ == "__main__":
    main()
