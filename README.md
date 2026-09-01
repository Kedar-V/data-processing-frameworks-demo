# Dataframe Engines

Two notebooks. Run every cell in order. This is a data engineering walkthrough,
not a data analysis assignment.

```text
notebooks/movielens_dataframe_engines_simple.ipynb   # part 1: CSV, Parquet, Pandas, Polars, PySpark
notebooks/rust_vs_python_intro.ipynb                 # part 2: a little Rust, then three ideas
```

## Learning objectives

**Part 1.** After `movielens_dataframe_engines_simple.ipynb` you should be able to:

- Explain why CSV gets expensive as it grows (size, parse time, no schema, no column skipping) and what Parquet changes.
- Clean a dirty table in three steps: drop duplicates, fill missing values, rescale a column.
- Write the same MovieLens query in Pandas, Polars (eager and lazy), and PySpark, and say when each engine is the right fit.

**Part 2.** After `rust_vs_python_intro.ipynb` you should be able to:

- Read a small Rust cell: `fn main`, `if` / `else if`, and `for`.
- Say why Polars can be fast from Python: it is compiled Rust, checked before it runs.
- Contrast `let` vs `let mut`, `b = a` (Python shares; Rust moves), and changing a list while looping (Python can skip an item; Rust will not compile).
- Change a **Your turn** cell (a string, a number, an `if`, `mut`, `.clone()`) and read a compiler error you caused on purpose.

## What you need

- Python 3.11+
- Java 17+ (Spark cells skip themselves if this is missing)
- Rust (`rustc` / `cargo`) for part 2
- About 1 GB of free disk

Use **VS Code** with the *Python* and *Jupyter* extensions.

## Setup

Full student instructions (macOS and Windows), including a Copilot prompt: [SETUP.md](SETUP.md).

In the project folder:

```bash
make setup   # creates .venv and registers the "Dataframe Engines" Jupyter kernel
make data    # downloads MovieLens 32M and writes the Parquet files
make rust-kernel
```

If `make data` warns that the GroupLens TLS certificate failed, that is expected. Let it finish. The first `make rust-kernel` compiles for a few minutes.

## Part 1

Open `notebooks/movielens_dataframe_engines_simple.ipynb` (or run
`make notebook`).

Pick the **Dataframe Engines** kernel in the top right. Run the cells from top
to bottom.

## Part 2

Do part 1 first.

Open `notebooks/rust_vs_python_intro.ipynb` (or run `make rust-notebook`).

Pick the **Rust** kernel. VS Code and Cursor often attach Python when you open
any `.ipynb`. Click the kernel name → **Select Another Kernel...** →
**Jupyter Kernel...** → **Rust**. If `let` is a `SyntaxError`, you are still
on Python.

Run the cells from top to bottom. A few cells are supposed to fail: read the
one sentence that matters, then keep going. After the takeaway there is one
optional extra about memory.
