# ACMC_Oracle

ACMC_Oracle is an experimental clustering project built around skeleton-graph construction, representative ranking, neighborhood initialization, uncertainty-driven querying, and label propagation.

The repository is organized so that the executable entry script stays at the project root, while the five core algorithm modules are grouped inside a dedicated folder.

## Project Layout

```text
ACMC_Oracle/
├── core/
│   ├── a_DMCons.py
│   ├── b_ranking_allocation.py
│   ├── c_neighborhood_initialization.py
│   ├── d_influence_model_propagation.py
│   └── e_neighborhood_learning.py
├── ensemble/
│   ├── a_pre_cluster.py
│   ├── b_construct_query_list.py
│   ├── c_iteration_stage_user_vote.py
│   ├── c_iteration_stage_user_vote_asy.py
│   └── user.py
├── datasets/
├── result/
├── requirements.txt
├── run_ACMC.py
└── README.md
```

## Core Modules

The `core/` folder contains the main ACMC pipeline:

- `a_DMCons.py`: skeleton graph construction
- `b_ranking_allocation.py`: representative ranking and order allocation
- `c_neighborhood_initialization.py`: neighborhood initialization
- `d_influence_model_propagation.py`: label propagation on the skeleton graph
- `e_neighborhood_learning.py`: iterative neighborhood learning and ACMC main routine

The `ensemble/` folder contains the user-voting and query-construction logic used during interaction.

## Requirements

- Python `3.10` or `3.11`
- A virtual environment is recommended

Third-party dependencies:

- `numpy`
- `scipy`
- `scikit-learn`
- `networkx`
- `pandas`
- `matplotlib`

Install all dependencies with:

```bash
pip install -r requirements.txt
```

## Running The Project

The entry point is:

```bash
python run_ACMC.py
```

`run_ACMC.py` imports the main algorithm from:

```python
from core.e_neighborhood_learning import ACMC
```

The default runnable example at the end of the script is:

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

## `run_ACMC(...)` Parameters

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

- `output_path`: root folder for outputs
- `algo_name`: reserved name parameter
- `dataset_source`: dataset folder name under `datasets/`
- `repetitions_times`: number of repeated runs
- `error_span`: user error rate
- `min_users_n`: minimum number of users per query
- `max_users_n`: maximum number of users per query
- `isUpdate`: enables or disables confidence updating
- `use_asy`: enables or disables the semi-asynchronous interaction routine

## Dataset Directory

The current implementation reads input data from:

```text
datasets/<dataset_source>/
```

Examples:

- `datasets/banknote/banknote.csv`
- `datasets/haberman/haberman.csv`
- `datasets/k_test/*.csv`

Make sure the selected dataset files exist under the corresponding `datasets/` subfolder before running the script.

## Output Directory

Results are currently written to:

```text
result/26_07_02/<dataset_source>/
```

Typical outputs include:

- `*_result.csv` for each run
- `time/*_runtime.csv` for runtime statistics

## Algorithm Workflow

The ACMC workflow is:

1. Load dataset features and labels
2. Add a small perturbation to the feature matrix
3. Build the skeleton graph
4. Rank nodes by representative order
5. Initialize neighborhoods from representative and uncertain nodes
6. Propagate labels on the graph
7. Select uncertain candidates for new queries
8. Update neighborhoods through user voting
9. Repeat until convergence or completion

When `use_asy=True`, the project uses the semi-asynchronous neighborhood learning path.

When `isUpdate=False`, user confidence updating is disabled.

## Notes

- The executable script remains at the repository root for convenience.
- The five algorithm modules have been moved into `core/` for cleaner project organization.
- The README reflects the current repository structure and import paths.
