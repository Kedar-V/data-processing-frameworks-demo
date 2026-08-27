PYTHON := .venv/bin/python
PIP := .venv/bin/pip
RATINGS := data/parquet/ratings_1m.parquet
MOVIES := data/parquet/movies.parquet
BENCHMARK_SIZES ?= 1m
SIMPLE_BENCHMARK_SIZES := 100 200k 500k 1m 10m 32m
JAVA_HOME ?= $(shell if command -v brew >/dev/null 2>&1 && brew --prefix openjdk@17 >/dev/null 2>&1; then echo "$$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home"; else /usr/libexec/java_home -v 17 2>/dev/null; fi)
SPARK_LOCAL_IP ?= 127.0.0.1

export JAVA_HOME
export SPARK_LOCAL_IP

.PHONY: setup data synthetic pandas polars spark benchmark benchmark-crossover benchmark-big validate format notebook

setup:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -e .
	$(PYTHON) -m ipykernel install --user --name dataframe-engine-benchmark --display-name "Dataframe Engines"

data:
	$(PYTHON) scripts/download_data.py
	$(PYTHON) scripts/prepare_data.py

synthetic:
	$(PYTHON) scripts/create_synthetic_data.py

pandas:
	$(PYTHON) implementations/pandas_query.py --ratings $(RATINGS) --movies $(MOVIES)

polars:
	$(PYTHON) implementations/polars_query.py --mode lazy --ratings $(RATINGS) --movies $(MOVIES)

spark:
	$(PYTHON) implementations/spark_query.py --ratings $(RATINGS) --movies $(MOVIES)

benchmark:
	$(PYTHON) benchmarks/benchmark.py --framework all --sizes $(BENCHMARK_SIZES)

benchmark-crossover:
	$(PYTHON) benchmarks/benchmark.py --framework pandas --sizes $(SIMPLE_BENCHMARK_SIZES) --repeats 3 --output results/benchmark_results_simple.csv
	$(PYTHON) benchmarks/benchmark.py --framework polars --sizes $(SIMPLE_BENCHMARK_SIZES) --repeats 3 --output results/benchmark_results_simple.csv
	$(PYTHON) benchmarks/benchmark.py --framework spark --sizes $(SIMPLE_BENCHMARK_SIZES) --repeats 3 --output results/benchmark_results_simple.csv

benchmark-big:
	$(PYTHON) benchmarks/benchmark.py --framework spark --sizes 1b --repeats 3
	$(PYTHON) benchmarks/benchmark.py --framework polars-lazy --sizes 1b --repeats 3

validate:
	$(PYTHON) benchmarks/validate.py

format:
	$(PYTHON) -m black --target-version py311 benchmarks implementations scripts notebooks/*.ipynb

notebook:
	$(PYTHON) -m jupyter lab notebooks/movielens_dataframe_engines.ipynb
