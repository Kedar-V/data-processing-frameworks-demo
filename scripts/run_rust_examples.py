"""Compile and run the Rust examples from part 2 outside Jupyter.

python scripts/run_rust_examples.py            # the working examples
python scripts/run_rust_examples.py --errors    # the ones that must not compile
python scripts/run_rust_examples.py 04 06       # only examples matching a prefix
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "rust/examples"
FAILING = EXAMPLES / "wont_compile"
BUILD = ROOT / "rust/build"
EDITION = "2024"


def compile_one(source: Path, optimize: bool = True) -> tuple[Path | None, str, float]:
    binary = (BUILD / source.stem).resolve()
    command = ["rustc", "--edition", EDITION, source.name, "-o", str(binary)]
    if optimize:
        command.insert(1, "-O")
    start = time.perf_counter()
    # Compile from the file's own directory so errors name the file, not its path.
    done = subprocess.run(command, capture_output=True, text=True, cwd=source.parent)
    seconds = time.perf_counter() - start
    return (binary if done.returncode == 0 else None, done.stderr, seconds)


def run_working(sources: list[Path]) -> int:
    failures = 0
    for source in sources:
        print(f"\n{'=' * 70}\n{source.relative_to(ROOT)}\n{'=' * 70}")
        binary, message, seconds = compile_one(source)
        if binary is None:
            print(message)
            print(f"✗ {source.name} failed to compile")
            failures += 1
            continue
        # Flush so our heading lands above the subprocess output when piped.
        print(f"compiled in {seconds:.2f}s\n", flush=True)
        subprocess.run([str(binary)])
        sys.stdout.flush()
    return failures


def run_failing(sources: list[Path]) -> int:
    unexpected = 0
    for source in sources:
        print(
            f"\n{'=' * 70}\n{source.relative_to(ROOT)}  (expected to fail)\n{'=' * 70}"
        )
        binary, message, _ = compile_one(source)
        if binary is not None:
            print(f"✗ {source.name} compiled, but was supposed to fail")
            unexpected += 1
            continue
        print(message.strip())
    return unexpected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--errors",
        action="store_true",
        help="run the wont_compile examples instead of the working ones",
    )
    parser.add_argument("prefix", nargs="*", help="only examples starting with these")
    args = parser.parse_args()

    if shutil.which("rustc") is None:
        sys.exit("rustc not found. Install Rust from https://rustup.rs and try again.")

    BUILD.mkdir(parents=True, exist_ok=True)
    directory = FAILING if args.errors else EXAMPLES
    sources = sorted(p for p in directory.glob("*.rs"))
    if args.prefix:
        sources = [p for p in sources if any(p.name.startswith(a) for a in args.prefix)]
    if not sources:
        sys.exit(f"no matching examples in {directory.relative_to(ROOT)}")

    problems = run_failing(sources) if args.errors else run_working(sources)
    print()
    if problems:
        sys.exit(f"✗ {problems} of {len(sources)} examples did not behave as expected")
    kind = "failed to compile, as intended" if args.errors else "compiled and ran"
    print(f"✓ All {len(sources)} examples {kind}")


if __name__ == "__main__":
    main()
