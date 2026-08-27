# Dataframe Engines TA Demo

A question-driven, 45-minute teaching demo of Pandas, Polars, and PySpark using
MovieLens data.

The goal is not to declare a universal benchmark winner. The lesson uses one
analytics question—

> **Which movies are both highly rated and widely rated?**

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
- roughly 4 GB of free disk space for the download and prepared datasets

```bash
make setup
make data
.venv/bin/jupyter lab notebooks/movielens_dataframe_engines_simple.ipynb
```

Choose the **Dataframe Engines** kernel if Jupyter does not select it
automatically. `make data` downloads the stable MovieLens 32M archive, extracts
only `ratings.csv` and `movies.csv`, and creates seeded, nested 1M and 10M
subsets plus the complete Parquet file.

Run the notebook once before class to confirm Java, refresh trusted outputs, and
avoid spending teaching time on environment setup.

## Teaching notebook

The primary artifact is:

```text
notebooks/movielens_dataframe_engines_simple.ipynb
```

Every markdown section starts with a question that the following explanation,
code, or output answers. The main path uses one Polars implementation so the
story remains focused on execution architecture rather than API modes.

The live demo defaults to:

```python
FAST_DEMO = True
MIN_RATINGS = 1_000
TOP_N = 10
```

`FAST_DEMO=True` uses a deterministic 1M-row subset so all three engines can run
comfortably during class. `MIN_RATINGS=1_000` gives “widely rated” a concrete
meaning and prevents a movie with one five-star rating from dominating the
answer.

### 45-minute storyline

- **0–4 min:** Are the environment and input data ready?
- **4–12 min:** What do filtering and grouping do to rows?
- **12–18 min:** How does Pandas execute the complete analysis?
- **18–23 min:** What changes when Polars uses a parallel native engine?
- **23–31 min:** How does PySpark turn the request into partitioned work?
- **31–38 min:** Do the answers match, and how does runtime change with scale?
- **38–45 min:** Which engine fits which workload?

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
make validate
```

`make format` applies Black to the Python source and both notebooks.

`make validate` confirms that Pandas, Polars, and PySpark return equivalent
results within floating-point tolerance. Correctness comes before performance:
a fast wrong answer is still wrong.

## Benchmark methodology

The notebook deliberately separates:

- **Live measurements:** one cold, end-to-end run during the demo. These create
  immediacy but are too noisy for ranking.
- **Prepared measurements:** the median of three end-to-end runs. These form the
  scaling chart.

The shared timed path is:

```text
read → group → aggregate → filter → join → sort → materialize
```

`make benchmark` runs the 1M dataset by default. Regenerate the prepared 1M,
10M, and 32M results outside class with:

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

The simplified notebook reads `results/benchmark_results_simple.csv`, where the
framework is labeled simply as **Polars**. Live 1M measurements are shown
separately and never overwrite the prepared medians.

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

## Billion-row scale point

The chart includes a prepared 1,024,006,528-row synthetic point. It repeats the
32M ratings dataset as 32 Parquet partitions, so it tests scale rather than new
movie behavior.

To reproduce it:

```bash
make synthetic
make benchmark-big
```

This requires approximately 5 GiB of disk. The large Polars run uses its
planning interface, demonstrated in the optional notebook appendix, so the
engine can scan the partitioned source without first creating one enormous
input dataframe. Pandas is intentionally omitted at this size to avoid an
unsafe memory experiment.

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