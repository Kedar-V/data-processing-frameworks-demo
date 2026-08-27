"""Create a large partitioned Parquet dataset from MovieLens 32M.

The rows are repeated intentionally. This artifact tests execution scale, not
statistical insight; the shared group/filter/join/sort query remains equivalent.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

DEFAULT_ROWS = 500_000_000
PARTIAL_BATCH_ROWS = 1_000_000


def write_partial_partition(
    parquet_file: pq.ParquetFile, destination: Path, rows: int
) -> None:
    """Write exactly ``rows`` from the source without loading it all in memory."""
    remaining = rows
    writer = pq.ParquetWriter(
        destination, parquet_file.schema_arrow, compression="zstd"
    )
    try:
        for batch in parquet_file.iter_batches(batch_size=PARTIAL_BATCH_ROWS):
            selected = batch.slice(0, min(remaining, batch.num_rows))
            writer.write_table(pa.Table.from_batches([selected]))
            remaining -= selected.num_rows
            if remaining == 0:
                break
    finally:
        writer.close()
    if remaining:
        raise ValueError(f"Source ended with {remaining:,} rows still required.")


def create(source: Path, output: Path, rows: int, force: bool = False) -> None:
    if not source.exists():
        raise FileNotFoundError(f"{source} is missing. Run `make data` first.")
    if rows < 1:
        raise ValueError("--rows must be at least 1.")

    parquet_file = pq.ParquetFile(source)
    rows_per_copy = parquet_file.metadata.num_rows
    full_parts, remainder_rows = divmod(rows, rows_per_copy)
    manifest_path = output / "_synthetic_manifest.json"

    if manifest_path.exists() and not force:
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("rows") == rows:
            print(f"Synthetic dataset already exists: {rows:,} rows at {output}")
            return
        raise FileExistsError(f"{output} exists with different settings; use --force.")

    if output.exists() and force:
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    source_size = source.stat().st_size
    estimated_size = source_size * (rows / rows_per_copy)
    part_count = full_parts + bool(remainder_rows)
    print(
        f"Creating {part_count} Parquet parts: {rows:,} rows, "
        f"approximately {estimated_size / 1024**3:.1f} GiB on disk."
    )
    for index in range(full_parts):
        destination = output / f"part-{index:05d}.parquet"
        shutil.copyfile(source, destination)
        print(f"\rCopied part {index + 1}/{part_count}", end="", flush=True)
    if remainder_rows:
        destination = output / f"part-{full_parts:05d}.parquet"
        write_partial_partition(parquet_file, destination, remainder_rows)
        print(f"\rWrote part {part_count}/{part_count}", end="", flush=True)
    print()

    manifest_path.write_text(
        json.dumps(
            {
                "source": str(source),
                "rows_per_copy": rows_per_copy,
                "full_parts": full_parts,
                "remainder_rows": remainder_rows,
                "rows": rows,
            },
            indent=2,
        )
        + "\n"
    )
    print(f"Wrote {rows:,} synthetic rows to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("data/parquet/ratings_32m.parquet"),
    )
    parser.add_argument(
        "--output", type=Path, default=Path("data/synthetic/ratings_500m.parquet")
    )
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    create(args.source, args.output, args.rows, args.force)
