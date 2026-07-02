# ACMC_Oracle

ACMC_Oracle is a clustering experiment project based on graph propagation, representative ranking, and human-in-the-loop constraint voting.

The current project entry point is `run_ACMC.py`. It supports:

- standard batch execution
- a semi-asynchronous mode switch via `use_asy`
- a confidence update switch via `isUpdate`

## Project Structure

```text
ACMC_Oracle/
├── a_DMCons.py
├── b_ranking_allocation.py
├── c_neighborhood_initialization.py
├── d_influence_model_propagation.py
├── e_neighborhood_learning.py
├── run_ACMC.py
├── ensemble/
│   ├── a_pre_cluster.py
│   ├── b_construct_query_list.py
│   ├── c_iteration_stage_user_vote.py
│   ├── c_iteration_stage_user_vote_asy.py
│   └── user.py
├── datasets/
└── result/
```

## Environment

- Python `3.10` or `3.11`
- A virtual environment such as `venv` is recommended

## Dependencies

To run `run_ACMC.py` and the modules it depends on, install the following third-party packages:

- `numpy`
- `scipy`
- `scikit-learn`
- `networkx`
- `pandas`
- `matplotlib`

These packages are used for:

- `numpy`: numerical computation and data perturbation
- `scipy`: Euclidean distance calculation
- `scikit-learn`: `NearestNeighbors`, `LabelEncoder`, and `adjusted_rand_score`
- `networkx`: graph construction and traversal
- `pandas`: imported by `a_DMCons.py`
- `matplotlib`: imported by `a_DMCons.py`

Standard library modules such as `csv`, `os`, `math`, `threading`, `time`, and `random` do not need to be installed separately.

## Installation

### 1. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

You can also install them directly:

```bash
pip install numpy scipy scikit-learn networkx pandas matplotlib
```

## How To Run

Main entry file:

```bash
python run_ACMC.py
```

The default entry configuration is defined at the end of `run_ACMC.py`:

```python
if __name__ == '__main__':
    output_path = 'result/'
    dataset_source, repetitions_times = 'banknote', 1

    run_ACMC(
        output_path,
        'ACMC',
        dataset_source,
        repetitions_times,
        error_span=0.00,
        min_users_n=1,
        max_users_n=1,
        isUpdate=True,
        use_asy=False
    )
```

## `run_ACMC` Parameters

```python
run_ACMC(
    output_path,
    algo_name,
    dataset_source,
    repetitions_times,
    error_span,
    min_users_n,
    max_users_n,
    isUpdate=True,
    use_asy=False
)
```

- `output_path`: root directory for experiment outputs
- `algo_name`: algorithm name placeholder; currently it does not affect the output directory name
- `dataset_source`: dataset directory name, such as `banknote`, `haberman`, or `k_test`
- `repetitions_times`: number of repeated runs
- `error_span`: uniform user error rate
- `min_users_n`: minimum number of users assigned to each constraint query
- `max_users_n`: maximum number of users assigned to each constraint query
- `isUpdate`: whether confidence updating is enabled
- `use_asy`: whether to use the semi-asynchronous version

## Dataset Layout

The current code reads data from:

```text
datasets/<dataset_source>/
```

Examples:

- `datasets/banknote/banknote.csv`
- `datasets/haberman/haberman.csv`
- `datasets/k_test/*.csv`

Please note:

- this repository currently contains both `dataset/` and `datasets/`
- `run_ACMC.py` uses `datasets/`
- make sure the target data files are placed under `datasets/<dataset_source>/`

## Output

By default, results are written to:

```text
result/26_07_02/<dataset_source>/
```

Each dataset output folder includes:

- per-run `*_result.csv` files
- runtime files under `time/*_runtime.csv`

## Core Workflow

The algorithm follows this general pipeline:

1. Load features and labels from the dataset file
2. Add a very small perturbation to the data
3. Build the skeleton graph and compute representative ranking
4. Initialize neighborhoods
5. Propagate labels to obtain predicted labels
6. Select uncertain points based on uncertainty
7. Update neighborhoods through user voting
8. Repeat until termination

If `use_asy=True`, the voting stage uses the semi-asynchronous workflow.

If `isUpdate=False`, user confidence updating is disabled and the fixed user error behavior is retained.

## FAQ

### 1. The program cannot find the dataset file

Check the following:

- whether `dataset_source` is correct
- whether the data files are placed in `datasets/<dataset_source>/`

### 2. The program reports missing dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

### 3. How do I enable the semi-asynchronous version?

Change:

```python
use_asy=False
```

to:

```python
use_asy=True
```

### 4. How do I disable confidence updating?

Change:

```python
isUpdate=True
```

to:

```python
isUpdate=False
```

## Notes

This README is based on the current repository structure and the actual implementation in `run_ACMC.py`.
