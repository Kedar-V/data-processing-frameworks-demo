# Dataframe Engines Teaching Demo

A short, run-it-yourself introduction to data formats and dataframe engines,
built for a data engineering course. Students run the cells, watch file size
and runtime change with scale, and leave with a feel for CSV vs Parquet and
Pandas vs Polars vs PySpark. It is deliberately **not** a data analysis
assignment — that comes later, on a dataset each student chooses.

The classroom notebook is:

```text
notebooks/movielens_dataframe_engines_simple.ipynb
```

It is designed to be walked through in about 20 minutes and executes in well
under a minute on a modern laptop.

## Student setup

Cursor no longer offers its education plan, so students should use **VS Code
with GitHub Copilot** (free through the GitHub Student Developer Pack) plus the
*Python* and *Jupyter* extensions.

Requirements:

- Python 3.11+
- Java 17+ for local PySpark (the Spark cells are skipped, not failed, if it is missing)
- roughly 1 GB of free disk space for the notebook's own data

```bash
make setup   # creates .venv and registers the "Dataframe Engines" kernel
make data    # downloads MovieLens 32M and writes the Parquet subsets
make notebook
```

Pick the **Dataframe Engines** kernel if Jupyter does not select it
automatically. `make data` extracts only `ratings.csv` and `movies.csv` from the
MovieLens 32M archive and writes seeded, nested 100-row, 200K, 500K, 1M, 10M,
and full 32M Parquet subsets. Run the notebook once before class so Java and
the data are known-good.

## What the notebook covers

1. **Environment** — kernel, packages, and a printed description of the machine,
   since every runtime below belongs to that machine.
2. **100 rows in CSV** — what the format actually is, read as plain text.
3. **Scaling to 100K and 1M rows** — CSV size, parse time, missing schema, and
   the inability to skip columns, all measured side by side against Parquet.
4. **Why Parquet** — columnar layout, embedded schema, compression, column
   pruning, and the round-trip that silently widens `float32` to `float64`.
5. **A minimal cleaning workflow** — deduplicate, impute, normalize, one line
   each, with a prompt for what students would add.
6. **One task, three engines** — the same query in Pandas, Polars, and PySpark,
   with a syntax comparison table and an equality check across every result.
   Polars appears in both modes: `read_parquet` runs immediately, while
   `scan_parquet` builds a plan that only `collect()` executes. The printed plan
   shows the optimizer deducing `PROJECT 2/8 COLUMNS` on its own.
7. **Scaling** — two charts. The first is measured live at 100, 200K, 1M, 10M,
   and 32M rows on the student's machine. The second is pre-measured out to one
   billion rows, where PySpark's fixed overhead finally pays off: it passes
   Pandas at 100M, Polars Lazy at 500M, and is more than twice as fast at 1B
   (5.54 s vs 13.49 s). Going from 500M to 1B costs Spark 1.8x more time but
   costs Polars Lazy 3.6x — one machine running out of room.

The notebook writes its CSV/Parquet comparison files to `data/formats/`, which
is Git-ignored and recreated on every run.

## The shared query

One query definition is used by the notebook, the CLI entry points in
`implementations/`, the benchmark harness, and `make validate`:

```text
read movieId, rating -> group by movieId -> mean(rating), count(rating)
  -> keep count >= 1000 -> join movies for title
  -> sort avg_rating desc, movieId asc
```

Keeping a single definition is what makes the notebook's live timings and the
pre-measured scaling chart comparable.

## Commands

```bash
make format     # Black over the Python sources and both notebooks
make pandas
make polars
make spark
make benchmark
make validate
```

`make validate` checks row counts, schemas, nested subsets, and that Pandas,
Polars, and PySpark agree within floating-point tolerance. Correctness comes
before performance: a fast wrong answer is still wrong.

## Extended material

`notebooks/movielens_dataframe_engines.ipynb` is the longer instructor
reference, with an execution-model walkthrough the classroom notebook leaves
out. It is self-contained and reads `results/benchmark_results.csv`, which is
frozen: those numbers were measured with an older, wider six-column
aggregation and predate the single shared query described above. Do not mix
them with `results/benchmark_results_simple.csv`.

`results/benchmark_results_simple.csv` holds the shared query timed from 100
rows through one billion, three repeats per point, median reported. The
classroom notebook reads it for its second scaling chart and measures everything
else live. The partitioned 70M through 1B inputs come from `make synthetic` and
need roughly 20 GB of free disk space; the 1B directory alone is 9.7 GB.

Pandas stops at 100M and Polars Eager at 350M by design. At a billion rows the
two required columns alone are about 8 GB before any grouping, so only Polars
Lazy and PySpark run the largest sizes.

To regenerate:

```bash
make synthetic
make benchmark-crossover
```

`make benchmark-crossover` already covers every framework and size pair,
including 350M and 500M. `make benchmark-big` re-runs only the large sizes and
is useful when just those need refreshing.

Each prepared run creates and stops its own Spark session, so PySpark's fixed
cost is included at every point. The notebook's live chart reuses one session
and therefore shows lower PySpark numbers at small sizes; both are disclosed in
the notebook.

These results describe the machine that produced them, not a universal
framework ranking. Startup cost, filesystem caches, JVM warm-up, available
cores, and optimizer behavior all matter. The lesson is not "Spark wins after
exactly N rows" — it is that Spark's fixed overhead stops mattering once the
data outgrows one machine.

## Data layout

```text
data/raw/ratings.csv
data/raw/movies.csv
data/parquet/ratings_{100,200k,500k,1m,10m,32m}.parquet
data/parquet/movies.parquet
data/formats/ratings_{100,100k,1m}.{csv,parquet}
data/synthetic/ratings_{70m,100m,350m,500m,1b}.parquet/
```

Raw and generated data are intentionally ignored by Git. MovieLens is provided
by GroupLens; review its dataset README and terms before redistributing data.
