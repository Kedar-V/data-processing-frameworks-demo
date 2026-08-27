# Dataframe Engines TA Demo

A question-driven, 45-minute teaching demo of Pandas, Polars, and PySpark using
MovieLens data.

The goal is not to declare a universal benchmark winner. The lesson uses one
analytics question—

> **Which widely rated movies have the strongest combined rating and viewing-completion score?**

—to show why similar dataframe syntax can follow very different execution
paths. Students build the analysis from filtering and grouping, run the same
pipeline in three engines, verify that the answers match, and then interpret
runtime through execution architecture.

By the end, students should be able to ask:

1. **Where** does the work run?
2. **When** does execution begin?
3. **How** does the engine organize the work?
4. Which execution model fits the workload they actually have?

## Quick start

Requirements:

- Python 3.11+
- Java 17+ for local PySpark
- roughly 20 GB of free disk space for all prepared and synthetic scale datasets

```bash
make setup
make data
.venv/bin/jupyter lab notebooks/movielens_dataframe_engines_simple.ipynb
```

Choose the **Dataframe Engines** kernel if Jupyter does not select it
automatically. `make data` downloads the stable MovieLens 32M archive, extracts
only `ratings.csv` and `movies.csv`, and creates seeded, nested 100-row, 200K,
500K, 1M, and 10M subsets plus the complete Parquet file. Preparation adds
deterministic synthetic numeric engagement metrics for the teaching workload.
Run `make synthetic` separately to create the exact 70M, 100M, 350M, and 500M
partitioned inputs.

Run the notebook once before class to confirm Java, refresh trusted outputs, and
avoid spending teaching time on environment setup.

## Teaching notebook

The primary artifact is:

```text
notebooks/movielens_dataframe_engines_simple.ipynb
```

Every markdown section starts with a question that the following explanation,
code, or output answers. The main path uses one Polars implementation so the
story remains focused on execution architecture. The benchmark compares both
Polars Eager and Polars Lazy, and the optional appendix explains the lazy plan.

The live demo defaults to:

```python
FAST_DEMO = True
MIN_RATINGS = 1_000
TOP_N = 10
```

`FAST_DEMO=True` uses a deterministic 1M-row subset so all three engines can run
comfortably during class. `MIN_RATINGS=1_000` gives “widely rated” a concrete
meaning and prevents a movie with one five-star rating from dominating the
answer. Rating and completion are normalized to 0–1 before they contribute
equally to the final audience score.

### 45-minute storyline

- **0–4 min:** Are the environment and input data ready?
- **4–9 min:** Is the dataset clean, and when would normalization help?
- **9–15 min:** What do filtering and grouping do to rows?
- **15–21 min:** How does Pandas execute the complete analysis?
- **21–26 min:** What changes when Polars uses a parallel native engine?
- **26–34 min:** How does PySpark turn the request into partitioned work?
- **34–40 min:** Do the answers match, and how does runtime change with scale?
- **40–45 min:** Which engine fits which workload?

Spark is deliberately local in this demo; its multi-machine architecture is
explained conceptually. The optional Polars planning section appears after the
main takeaway so it does not interrupt the 45-minute storyline.

The longer `notebooks/movielens_dataframe_engines.ipynb` is retained as an
extended reference for instructors who want a deeper Polars mode comparison.

## Commands

```bash
make format
make pandas
make polars
make spark
make benchmark
make benchmark-crossover
make validate
```

`make format` applies Black to the Python source and both notebooks.

`make validate` checks exact row counts, enriched schemas, feature ranges,
nested subsets, and equivalent Pandas, Polars, and PySpark results within
floating-point tolerance. Correctness comes before performance: a fast wrong
answer is still wrong.

## Benchmark methodology

The notebook deliberately separates:

- **Live measurements:** one cold, end-to-end run during the demo. These create
  immediacy but are too noisy for ranking.
- **Prepared measurements:** the median of three end-to-end runs. These form the
  scaling chart.

The shared timed path is:

```text
read six metrics → aggregate movie profiles → filter → normalize
                 → join → sort → materialize
```

`make benchmark` runs the 1M dataset by default. `make benchmark-crossover`
regenerates the simplified notebook's results from 100 rows through 500M using
three repeats. To protect local memory, Pandas stops after 100M, Polars Eager
after 350M, and Polars Lazy plus PySpark continue through 500M.

To regenerate the extended comparison directly:

```bash
.venv/bin/python benchmarks/benchmark.py \
  --framework all \
  --sizes 1m 10m 32m \
  --repeats 3
```

Results are merged into `results/benchmark_results.csv`. They describe the
machine that produced them, not a universal framework ranking. Startup,
filesystem caches, JVM warm-up, available cores, and optimizer behavior all
matter.

The simplified notebook reads `results/benchmark_results_simple.csv`. Live 1M
measurements are shown separately and never overwrite the prepared medians.
Its small-scale chart compares Pandas with both Polars execution modes and
calculates their speedups. On the recorded machine, both Polars modes are
already faster at 100 rows, so the evidence does not show a crossover within
the tested range; it shows that the crossover is below 100 rows, or absent for
this workload and benchmark boundary.

## Data layout

```text
data/raw/ratings.csv
data/raw/movies.csv
data/parquet/ratings_100.parquet
data/parquet/ratings_200k.parquet
data/parquet/ratings_500k.parquet
data/parquet/ratings_1m.parquet
data/parquet/ratings_10m.parquet
data/parquet/ratings_32m.parquet
data/parquet/movies.parquet
data/synthetic/ratings_70m.parquet/
data/synthetic/ratings_100m.parquet/
data/synthetic/ratings_350m.parquet/
data/synthetic/ratings_500m.parquet/
```

Raw and prepared data are intentionally ignored by Git. MovieLens is provided
by GroupLens; review its dataset README and terms before redistributing data.

## Large synthetic scale points

The chart includes exact 70M, 100M, 350M, and 500M-row synthetic points. Each
repeats the enriched 32M ratings source and writes a partial final partition
when needed, so these inputs test scale rather than new movie behavior.

To reproduce it:

```bash
make synthetic
make benchmark-big
```

The large Polars run uses its planning interface so the engine can scan
partitioned sources without first creating one enormous eager dataframe.
Unsafe framework/size combinations are intentionally omitted rather than
treated as zero-runtime results.

The lesson is not “Spark wins after exactly N rows.” Hardware, caching,
partitioning, and optimizer behavior can move the crossover. Spark's durable
advantage is that the same partitioned execution model can extend from one
laptop to multiple machines.

## Optional extensions

After the core lesson, instructors can explore:

- the optional Polars planning appendix;
- warm-versus-cold timing;
- different popularity thresholds;
- a real multi-machine Spark cluster.

Recommendation systems, tags, UDFs, and advanced optimizer internals are
intentionally outside the core demo.