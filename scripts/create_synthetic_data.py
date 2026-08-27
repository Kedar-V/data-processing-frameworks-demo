"""Create a large partitioned Parquet dataset from MovieLens 32M.

The rows are repeated intentionally. This artifact tests execution scale, not
statistical insight; the shared group/filter/join/sort query remains equivalent.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import pyarrow.parquet as pq

DEFAULT_COPIES = 32


def create(source: Path, output: Path, copies: int, force: bool = False) -> None:
    if not source.exists():
        raise FileNotFoundError(f"{source} is missing. Run `make data` first.")
    if copies < 1:
        raise ValueError("--copies must be at least 1.")

    rows_per_copy = pq.ParquetFile(source).metadata.num_rows
    expected_rows = rows_per_copy * copies
    manifest_path = output / "_synthetic_manifest.json"

    if manifest_path.exists() and not force:
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("rows") == expected_rows:
            print(
                f"Synthetic dataset already exists: {expected_rows:,} rows at {output}"
            )
            return
        raise FileExistsError(f"{output} exists with different settings; use --force.")

    if output.exists() and force:
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    source_size = source.stat().st_size
    print(
        f"Creating {copies} Parquet parts: {expected_rows:,} rows, "
        f"approximately {source_size * copies / 1024**3:.1f} GiB on disk."
    )
    for index in range(copies):
        destination = output / f"part-{index:05d}.parquet"
        shutil.copyfile(source, destination)
        print(f"\rCopied part {index + 1}/{copies}", end="", flush=True)
    print()

    manifest_path.write_text(
        json.dumps(
            {
                "source": str(source),
                "copies": copies,
                "rows_per_copy": rows_per_copy,
                "rows": expected_rows,
            },
            indent=2,
        )
        + "\n"
    )
    print(f"Wrote {expected_rows:,} synthetic rows to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("data/parquet/ratings_32m.parquet"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/synthetic/ratings_1b.parquet"),
    )
    parser.add_argument("--copies", type=int, default=DEFAULT_COPIES)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    create(args.source, args.output, args.copies, args.force)
