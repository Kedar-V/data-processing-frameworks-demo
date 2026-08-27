"""Download MovieLens 32M and extract only the two teaching files."""

from __future__ import annotations

import argparse
import shutil
import urllib.request
import zipfile
from pathlib import Path

URL = "https://files.grouplens.org/datasets/movielens/ml-32m.zip"
MEMBERS = {
    "ml-32m/ratings.csv": "ratings.csv",
    "ml-32m/movies.csv": "movies.csv",
}


def download(destination: Path, force: bool = False) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    outputs = [destination / name for name in MEMBERS.values()]
    if all(path.exists() for path in outputs) and not force:
        print("MovieLens CSV files already exist; use --force to replace them.")
        return

    archive = destination / "ml-32m.zip.part"
    print(f"Downloading {URL}")
    with urllib.request.urlopen(URL) as response, archive.open("wb") as target:
        shutil.copyfileobj(response, target)

    try:
        with zipfile.ZipFile(archive) as bundle:
            for member, filename in MEMBERS.items():
                with (
                    bundle.open(member) as source,
                    (destination / filename).open("wb") as target,
                ):
                    shutil.copyfileobj(source, target)
    finally:
        archive.unlink(missing_ok=True)

    print("Extracted ratings.csv and movies.csv.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/raw"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    download(args.output, args.force)
