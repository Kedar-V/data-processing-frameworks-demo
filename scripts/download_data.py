"""Download MovieLens 32M and extract only the two teaching files."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import ssl
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

URL = "https://files.grouplens.org/datasets/movielens/ml-32m.zip"
# Official checksum from https://files.grouplens.org/datasets/movielens/ml-32m.zip.md5
MD5 = "d472be332d4daa821edc399621853b57"
MEMBERS = {
    "ml-32m/ratings.csv": "ratings.csv",
    "ml-32m/movies.csv": "movies.csv",
}


def _ssl_verify_failed(exc: BaseException) -> bool:
    text = str(exc).lower()
    return "certificate_verify_failed" in text or "certificate has expired" in text


def open_url(url: str):
    try:
        return urllib.request.urlopen(url)
    except urllib.error.URLError as exc:
        if not _ssl_verify_failed(exc):
            raise
        print(
            "GroupLens TLS certificate failed verification "
            "(files.grouplens.org often has an expired cert). "
            "Retrying without certificate check, then verifying the zip MD5."
        )
        return urllib.request.urlopen(url, context=ssl._create_unverified_context())


def md5sum(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(destination: Path, force: bool = False) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    outputs = [destination / name for name in MEMBERS.values()]
    if all(path.exists() for path in outputs) and not force:
        print("MovieLens CSV files already exist; use --force to replace them.")
        return

    archive = destination / "ml-32m.zip.part"
    print(f"Downloading {URL}")
    with open_url(URL) as response, archive.open("wb") as target:
        shutil.copyfileobj(response, target)

    digest = md5sum(archive)
    if digest != MD5:
        archive.unlink(missing_ok=True)
        raise RuntimeError(
            f"Downloaded zip MD5 {digest} does not match GroupLens checksum {MD5}."
        )

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
