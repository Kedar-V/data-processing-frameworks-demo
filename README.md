# Dataframe Engines

Two notebooks. Run every cell in order. This is a data engineering walkthrough,
not a data analysis assignment.

```text
notebooks/movielens_dataframe_engines_simple.ipynb   # part 1: CSV, Parquet, Pandas, Polars, PySpark
notebooks/rust_vs_python_intro.ipynb                 # part 2: three Rust ideas
```

## Learning objectives

**Part 1.** After `movielens_dataframe_engines_simple.ipynb` you should be able to:

- Explain why CSV gets expensive as it grows (size, parse time, no schema, no column skipping) and what Parquet changes.
- Clean a dirty table in three steps: drop duplicates, fill missing values, rescale a column.
- Write the same MovieLens query in Pandas, Polars (eager and lazy), and PySpark, and say when each engine is the right fit.

**Part 2.** After `rust_vs_python_intro.ipynb` you should be able to:

- Say why Polars can be fast from Python: it is compiled Rust, checked before it runs.
- Contrast `let` vs `let mut`, and `b = a` in Python (two names, one list) vs Rust (ownership moves).
- Read a compiler error that is supposed to fail, instead of treating every red cell as a broken notebook.

## What you need

- Python 3.11+
- Java 17+ (Spark cells skip themselves if this is missing)
- Rust (`rustc` / `cargo`) for part 2
- About 1 GB of free disk

Use **VS Code** with the *Python* and *Jupyter* extensions. GitHub Copilot is
free for students through the GitHub Student Developer Pack.

## Setup

In the project folder:

```bash
make setup   # creates .venv and registers the "Dataframe Engines" Jupyter kernel
make data    # downloads MovieLens 32M and writes the Parquet files
```

If `make data` warns that the GroupLens TLS certificate failed, that is expected while
`files.grouplens.org` has an expired cert. The download still runs and checks the zip
against GroupLens's published MD5.

For part 2, install Rust, then the Rust Jupyter kernel:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

On Windows, run `rustup-init.exe` from <https://rustup.rs>. Open a **new**
terminal afterward so `cargo` is on your `PATH`.

```bash
make rust-kernel
```

The first kernel install compiles for a few minutes. Let it finish.

## Part 1

Open `notebooks/movielens_dataframe_engines_simple.ipynb` (or run
`make notebook`).

Pick the **Dataframe Engines** kernel in the top right. Run the cells from top
to bottom.

## Part 2

Do part 1 first. The last optional cells in part 2 read
`data/formats/ratings_1m.csv`, which part 1 writes.

Open `notebooks/rust_vs_python_intro.ipynb` (or run `make rust-notebook`).

Pick the **Rust** kernel. VS Code and Cursor often attach Python when you open
any `.ipynb`. Click the kernel name → **Select Another Kernel...** →
**Jupyter Kernel...** → **Rust**. If `let` is a `SyntaxError`, you are still
on Python.

Run the cells from top to bottom. Two cells are **supposed to fail** — read the
error and keep going. Sections 1–3 are the class. Everything after the takeaway
is optional.
