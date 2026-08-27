# dataframe-engine-benchmark

A teaching-first, 45-minute comparison of Pandas, Polars, and PySpark using
MovieLens 32M.

The lesson asks one question—**which movies are highly rated and widely
rated?**—and follows the same filter/group/join/aggregate workload through three
execution architectures. The default live path uses a deterministic 1M-rating
subset so it runs comfortably on a laptop.

## Quick start

Requirements:

- Python 3.11+
- Java 17+ for local PySpark
- roughly 4 GB of free disk space for the download and prepared datasets

```bash
make setup
make data
make notebook
```

Choose the **Dataframe Engines** kernel if Jupyter does not select it
automatically. `make data` downloads the stable MovieLens 32M archive, extracts
only `ratings.csv` and `movies.csv`, and creates seeded, nested 1M and 10M
subsets plus the complete Parquet file.

## Classroom path

The main artifact is
`notebooks/movielens_dataframe_engines.ipynb`. It defaults to:

```python
FAST_DEMO = True
MIN_RATINGS = 1_000
TOP_N = 10
```

For a shorter presentation with one Polars path and no mode comparison, use
`notebooks/movielens_dataframe_engines_simple.ipynb`.

The notebook is paced for:

- 0–3 min: one table and three shared queries
- 3–11 min: Pandas local/eager execution
- 11–24 min: Polars eager/lazy execution and optimization
- 24–34 min: PySpark planning and distributed processing
- 34–41 min: one equivalent-workload benchmark
- 41–45 min: execution-path comparison, tool choice, and recap

Run it once before class to warm caches, confirm Java, and save trusted outputs.
Spark is deliberately local in this demo; its multi-machine architecture is
explained conceptually.

## Commands

```bash
make pandas
make polars
make spark
make benchmark
make validate
```

`make benchmark` runs only 1M by default. Regenerate larger precomputed results
outside class with:

```bash
make benchmark BENCHMARK_SIZES="1m 10m 32m"
```

The benchmark runner also supports one engine at a time:

```bash
.venv/bin/python benchmarks/benchmark.py --framework polars-lazy --sizes 1m 10m 32m
```

Results are merged into `results/benchmark_results.csv`. They describe the
machine that produced them, not a universal framework ranking. Startup,
filesystem caches, JVM warm-up, available cores, and optimizer behavior all
matter.

The committed CSV contains only measurements actually produced during project
verification. Missing framework/size combinations are intentionally omitted,
not estimated; regenerate them on the instructor laptop before class. The
notebook displays live 1M measurements separately from the prepared chart.

`make validate` compares Pandas, eager Polars, lazy Polars, and PySpark results
with floating-point tolerance. This detailed check stays outside the live
teaching path.

## Data layout

```text
data/raw/ratings.csv
data/raw/movies.csv
data/parquet/ratings_1m.parquet
data/parquet/ratings_10m.parquet
data/parquet/ratings_32m.parquet
data/parquet/movies.parquet
```

Raw and prepared data are intentionally ignored by Git. MovieLens is provided
by GroupLens; review its dataset README and terms before redistributing data.

## Optional billion-row scale experiment

On a 24 GB laptop, the useful Spark demonstration is not “Spark becomes the
fastest after exactly N rows.” Local Polars may remain faster. Spark's advantage
is that its partitioned execution model can continue onto a cluster when one
machine is no longer sufficient.

Create a deterministic 1,024,006,528-row Parquet dataset by repeating the 32M
ratings file as 32 partitions:

```bash
make synthetic
make benchmark-big
```

This needs approximately 5 GiB of disk. `benchmark-big` intentionally runs only
lazy Polars and local PySpark; running eager Pandas at this scale may exhaust
laptop memory. For a genuine Spark performance advantage, put the same
partitioned dataset on distributed storage and use multiple executors on
multiple machines.

## Optional extensions

After the core lesson, instructors can explore warm-vs-cold runs, other
thresholds, or a real Spark cluster. Recommendation systems, tags, UDFs, and
advanced optimizer internals are intentionally outside the 45-minute demo.