# Setup (before class)

You will need about **1 GB of free disk**. Spark cells skip themselves if Java is missing. The Rust notebook will not run without the Rust kernel.

## What you need

- Python **3.11+**
- **Java 17+** (PySpark)
- **Rust** (`rustc` / `cargo`) for part 2
- **VS Code** with the [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) and [Jupyter](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) extensions
- Git (to clone the repo)

Clone the project, then `cd` into the project folder. Follow **macOS** or **Windows** below, or paste the Copilot prompt in the next section and let it walk you through the same steps on your machine.

If `make data` warns that the GroupLens TLS certificate failed, that is expected. Let it finish.

---

## Copilot prompt (if you get stuck)

GitHub Copilot is [free for students](https://education.github.com/pack). In VS Code, open this repo, open Copilot Chat, and paste:

```text
I am setting up this course repo on my computer before class.

Follow SETUP.md in this repo. Detect whether I am on macOS or Windows and use only that section.

I need:
- Python 3.11 or newer
- Java 17 or newer (for PySpark)
- Rust (rustc and cargo) for part 2
- VS Code with the Python and Jupyter extensions
- The "Dataframe Engines" Jupyter kernel (part 1)
- The Rust Jupyter kernel from `make rust-kernel` or `evcxr_jupyter --install` (part 2)

Do the installs in order. After each step, tell me the exact command to run and what success looks like (for example `python --version`, `java -version`, `rustc --version`).

If `make data` warns that the GroupLens TLS certificate failed, that is expected — keep going.

Do not skip the Rust kernel. Do not switch me to a different Python distribution, Java version, or notebook kernel than SETUP.md specifies. If a command fails, explain the error and the next command to try. Stop when both notebooks have the right kernel: part 1 = Dataframe Engines, part 2 = Rust.
```

---

## macOS

### 1. Homebrew

If you do not have it: <https://brew.sh>

### 2. Python and Java

```bash
brew install python@3.12 openjdk@17
```

If `java -version` is not 17+, add this to `~/.zprofile`, then open a **new** terminal:

```bash
export PATH="$(brew --prefix openjdk@17)/bin:$PATH"
```

### 3. Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

Open a **new** terminal, then check:

```bash
rustc --version
cargo --version
```

### 4. Project

In the project folder:

```bash
make setup
make data
make rust-kernel
```

`make rust-kernel` compiles for a few minutes the first time. Let it finish.

### 5. Kernels in VS Code

Open the project in VS Code.

- Part 1: `notebooks/movielens_dataframe_engines_simple.ipynb` → kernel **Dataframe Engines**
- Part 2: `notebooks/rust_vs_python_intro.ipynb` → kernel **Rust**

To pick the Rust kernel: kernel name → **Select Another Kernel...** → **Jupyter Kernel...** → **Rust**. If `let` is a `SyntaxError`, you are still on Python.

---

## Windows

### 1. Install

- Python 3.11+ from <https://www.python.org/downloads/> — check **Add python.exe to PATH**
- Java 17 (Temurin is fine): <https://adoptium.net/>
- Git for Windows: <https://git-scm.com/download/win>
- VS Code: <https://code.visualstudio.com/> — then install the *Python* and *Jupyter* extensions

### 2. Rust

Download `rustup-init.exe` from <https://rustup.rs> and run it. Close the terminal, open a **new** one, then check:

```bat
rustc --version
cargo --version
java -version
python --version
```

### 3. Project

In the project folder (PowerShell or Command Prompt):

```bat
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python -m ipykernel install --user --name dataframe-engine-benchmark --display-name "Dataframe Engines"
.venv\Scripts\python scripts/download_data.py
.venv\Scripts\python scripts/prepare_data.py
```

### 4. Rust Jupyter kernel

```bat
cargo install evcxr_jupyter
evcxr_jupyter --install
```

If `evcxr_jupyter` is not found, close the terminal and open a new one so `%USERPROFILE%\.cargo\bin` is on `PATH`.

### 5. Kernels in VS Code

Same as macOS: part 1 = **Dataframe Engines**, part 2 = **Rust**. If `let` is a `SyntaxError`, you are still on Python.

---

## You are done when

- `python --version` is 3.11+
- `java -version` is 17+
- `rustc --version` works
- Part 1 runs with the **Dataframe Engines** kernel
- Part 2 runs with the **Rust** kernel
