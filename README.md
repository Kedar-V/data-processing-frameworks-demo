# Dataframe Engines Teaching Demo

Two short, run-it-yourself notebooks for a data engineering course. Students
run the cells and watch the numbers change, rather than being told what to
expect. Neither is a data analysis assignment — that comes later, on a dataset
each student chooses.

```text
notebooks/movielens_dataframe_engines_simple.ipynb   # part 1: formats and engines
notebooks/rust_vs_python_intro.ipynb                 # part 2: a first look at Rust
```

Each is designed to be walked through in about 20 minutes, and each executes
in well under a minute on a modern laptop. Part 2 stands on part 1's punchline:
Polars was several times faster than Pandas, and Polars is written in Rust.

## Part 1: formats and engines

Students watch file size and runtime change with scale, and leave with a feel
for CSV vs Parquet and Pandas vs Polars vs PySpark.

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

## What part 1 covers

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

## Part 2: a first look at Rust

`notebooks/rust_vs_python_intro.ipynb` introduces the handful of Rust ideas
that explain part 1's timings, for students who only know Python. It is not a
programming course: each idea gets one tiny program, and roughly half of those
programs are *expected to fail*, because the point is that in Rust a whole
category of bug is a compile error.

It needs Rust, which students install with `rustup`:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh   # macOS, Linux
```

On Windows, run `rustup-init.exe` from <https://rustup.rs>. On macOS
`brew install rust` also works. No new Jupyter kernel is needed — the notebook
runs on the same **Dataframe Engines** kernel and shells out to `rustc`.

It covers, in order:

1. **The compile step** — the same file checked before it runs, and what a
   binary is. Pip-installing Polars downloads one.
2. **Immutable by default** — `let` vs `let mut`, next to Python, where every
   name is rebindable and a frozen dataclass only complains at runtime.
3. **Where the memory goes** — no garbage collector and no reference counting;
   a `Drop` implementation prints at the exact moment memory is released, and
   the Python cell next to it shows a reference cycle surviving `del` until the
   collector runs.
4. **Ownership** — moving, borrowing, and cloning, against the Python aliasing
   bug where `b = a` gives two names for one list.
5. **Borrowing** — one writer or many readers, and the Python loop that removes
   items while iterating and silently returns the wrong answer.
6. **Concurrency** — the same CPU-bound total on 1, 2, 4, and 8 threads in both
   languages. Rust's speedup line climbs and Python's is flat, because of the
   GIL. Then four threads sharing a counter, rejected at compile time.
7. **The same group-by, both languages** — five million ratings generated from
   the same seed with the same arithmetic, counted in half-stars so the totals
   are integers and cannot drift. The notebook asserts the answers match before
   it compares any timings, then adds Polars to the chart, which is the point:
   you do not have to choose between Python's ecosystem and Rust's speed.

The Rust files are real files, not notebook strings, so students can keep
editing them after class:

```text
rust/examples/0{1..7}_*.rs              # the working examples
rust/examples/wont_compile/*.rs         # the four that must not compile
```

```bash
make rust          # compile and run every working example
make rust-errors   # compile the four that should fail, and show the errors
make rust-notebook
```

`make rust-errors` exits non-zero if any of them *succeeds*, which is what
keeps the teaching examples honest as Rust versions change. Compiled binaries
go to `rust/build/`, which is Git-ignored.

### Teaching part 2 in 20 minutes

The notebook is built as one question — *where does Polars get its speed?* —
with six numbered answers that accumulate as you go. Section *n* ends by adding
line *n* to a list, and section 8 reads the finished list back. Each heading
carries its own time budget, and they add up to twenty minutes.

Run it once before class. The first `rustc` call has to compile, and you want
that already done.

| Time | Section | The one thing to say | Point at |
|---|---|---|---|
| 0:00 | intro | Polars beat Pandas in part 1, and Polars is Rust. We are opening the hood. | the ~3x from part 1 |
| 2:00 | 1 | The compiler reads everything before anything runs. | the compile line, then the instant run |
| 4:00 | 2 | `mut` is how the compiler learns what can change. | the `help:` line in the E0384 error |
| 6:00 | 3 | No collector. The `free` is written while compiling. | `FREE 64 MB` landing *before* "back in main" |
| 9:00 | 4 | One owner, so there is always one place the `free` belongs. | "value moved here" |
| 11:00 | 5 | One writer or many readers, never both. | the Python loop that leaves one `2` behind |
| 13:00 | 6 | That same rule is what makes threads safe. | the flat Python line against the climbing Rust one |
| 16:00 | 7 | Same answer in both languages first, then the number. | the assertion passing, then the bar chart |
| 18:00 | 8 | Read the six back, and name the tools they already use. | the finished list |

If you are running behind, section 2 and the Python cell in section 4 are the
most skippable. Do not cut section 3 or the chart in section 7 — those are the
two moments the argument actually lands.

Questions that come up every time:

- *Why is debug Rust slower than Polars?* Because `-O` is off. That is why the
  file is compiled twice.
- *Is Rust always fifty times faster?* No. That is one hand-written loop on one
  machine, and the notebook prints the machine under the chart for that reason.
  The shape is the lesson, not the multiple.
- *Should I learn Rust?* Not in order to do data analysis. To write the layer
  underneath one, or to read the source of the tools you already depend on.
- *Why `&Vec<f64>` and not `&[f64]`?* Because slices are one more concept, and
  these files deliberately trade idiom for readability. Clippy will disagree,
  and clippy is right about real code.

## The shared query

One query definition is used by part 1's notebook, the CLI entry points in
`implementations/`, the benchmark harness, and `make validate`:

```text
read movieId, rating -> group by movieId -> mean(rating), count(rating)
  -> keep count >= 1000 -> join movies for title
  -> sort avg_rating desc, movieId asc
```

Keeping a single definition is what makes the notebook's live timings and the
pre-measured scaling chart comparable.

Part 2 uses its own dataset — five million ratings generated from a fixed seed
in both languages — because its comparison is between Python and Rust, not
between file formats. It asserts the two answers match before reporting any
timing.

## Commands

```bash
make format     # Black over the Python sources and every notebook
make pandas
make polars
make spark
make benchmark
make validate
make rust           # part 2: compile and run the working Rust examples
make rust-errors    # part 2: the examples that must not compile
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

The same caveat applies to part 2. Its Rust-versus-Python ratios describe one
machine and one hand-written loop, and the notebook prints the machine under
each chart for that reason. The lesson is the shape of the gap, not the number.

## Data layout

```text
data/raw/ratings.csv
data/raw/movies.csv
data/parquet/ratings_{100,200k,500k,1m,10m,32m}.parquet
data/parquet/movies.parquet
data/formats/ratings_{100,100k,1m}.{csv,parquet}
data/synthetic/ratings_{70m,100m,350m,500m,1b}.parquet/
```

Part 2 needs none of this: it generates its own five million rows in memory
from a fixed seed, so it runs on a laptop that has never run `make data`.

Raw and generated data are intentionally ignored by Git. MovieLens is provided
by GroupLens; review its dataset README and terms before redistributing data.
