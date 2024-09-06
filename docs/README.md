---
hide:
  - navigation
---

# nbmetaclean
Collections of python scripts for checking and cleaning Jupyter Notebooks metadata, execution_count and optionally output.
Can be used as command line tool or pre-commit hook.


Pure Python, no dependencies.

Can be used as a pre-commit hook or as a command line tool.


[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/benchmark-utils)](https://pypi.org/project/nbmetaclean/)
[![PyPI Status](https://badge.fury.io/py/nbmetaclean.svg)](https://badge.fury.io/py/nbmetaclean)
[![Tests](https://github.com/ayasyrev/nbmetaclean/workflows/Tests/badge.svg)](https://github.com/ayasyrev/nbmetaclean/actions?workflow=Tests)  [![Codecov](https://codecov.io/gh/ayasyrev/nbmetaclean/branch/main/graph/badge.svg)](https://codecov.io/gh/ayasyrev/nbmetaclean)

## nbclean

Clean Jupyter Notebooks metadata, execution_count and optionally output.

## nbcheck
Check Jupyter Notebooks for errors and (or) warnings in outputs.


## Base usage

### Pre-commit hook
Nbmetaclean can be used as a pre-commit hook, with [pre-commit](https://pre-commit.com/pre-commit)
You do not need to install nbmetaclean, it will be installed automatically.
add to `.pre-commit-config.yaml`:
```yaml
repos:
    - repo: https://github.com/ayasyrev/nbmetaclean
        rev: 0.1
        hooks:
        - id: nbclean
        - id: nbcheck
          args: [ --ec, --err, --warn ]
```



### Command line tool

####  Install:
```bash
pip install nbmetaclean
```

Usage:
run `nbclean` or `nbcheck` command with `path` to notebook or folder with notebooks.
If no `path` is provided, current directory will be used as `path`.

```bash
nbclean
```

`nbcheck` should be run with flags:
- `--ec` for execution_count check
- `--err` for check errors in outputs
- `--warn` for check warnings in outputs
```bash
nbcheck --ec --err --warn
```


## Nbclean
### Default settings
By default, the following settings are used:

- Clean notebook metadata, except `authors` and `language_info / name`.
- Clean cells execution_count.
- Preserve metadata at  cells.
- Preserve cells outputs.
- After cleaning notebook, timestamp for file will be set to previous values.






### Arguments
Check available arguments:

```bash
nbclean -h

usage: nbclean [-h] [-s] [--not_ec] [--not-pt] [--dont_clear_nb_metadata] [--clear_cell_metadata] [--clear_outputs]
[--nb_metadata_preserve_mask NB_METADATA_PRESERVE_MASK [NB_METADATA_PRESERVE_MASK ...]]
[--cell_metadata_preserve_mask CELL_METADATA_PRESERVE_MASK [CELL_METADATA_PRESERVE_MASK ...]] [--dont_merge_masks] [--clean_hidden_nbs] [-D] [-V]
[path ...]

Clean metadata and execution_count from Jupyter notebooks.

positional arguments:
  path                  Path for nb or folder with notebooks.

options:
  -h, --help            show this help message and exit
  -s, --silent          Silent mode.
  --not_ec              Do not clear execution_count.
  --not-pt              Do not preserve timestamp.
  --dont_clear_nb_metadata
                        Do not clear notebook metadata.
  --clear_cell_metadata
                        Clear cell metadata.
  --clear_outputs       Clear outputs.
  --nb_metadata_preserve_mask NB_METADATA_PRESERVE_MASK [NB_METADATA_PRESERVE_MASK ...]
                        Preserve mask for notebook metadata.
  --cell_metadata_preserve_mask CELL_METADATA_PRESERVE_MASK [CELL_METADATA_PRESERVE_MASK ...]
                        Preserve mask for cell metadata.
  --dont_merge_masks    Do not merge masks.
  --clean_hidden_nbs    Clean hidden notebooks.
  -D, --dry_run         perform a trial run, don't write results
  -V, --verbose         Verbose mode. Print extra information.
```

### Execution_count
If you want to leave execution_count add `--not_ec` flag at command line or `args: [--not_ec]` line to `.pre-commit-config.yaml`.

```yaml
repos:
    - repo: https://github.com/ayasyrev/nbmetaclean
        rev: 0.1
        hooks:
        - id: nbclean
          args: [ --not_ec ]
```

```bash
nbclean --not_ec
```

### Clear outputs
If you want to clear outputs, add `--clear_outputs` at command line or `[ --clean_outputs ]` line to `.pre-commit-config.yaml`.
```yaml
repos:
    - repo: https://github.com/ayasyrev/nbmetaclean
        rev: 0.1
        hooks:
        - id: nbclean
          args: [ --clean_outputs ]
```

```bash
nbclean --clean_outputs
```

## Nbcheck
Check Jupyter Notebooks for correct execution_count, errors and (or) warnings in outputs.

### Execution_count
Check that all code cells executed one after another.

#### Strict mode
By default, execution_count check in `strict` mode.
All cells must be executed, one after another.

pre-commit config example:
```yaml
repos:
    - repo: https://github.com/ayasyrev/nbmetaclean
        rev: 0.1
        hooks:
        - id: nbcheck
          args: [ --ec ]
```

command line example:
```bash
nbcheck --ec
```

#### Not strict mode
`--not_strict` flag can be used to check that next cell executed after previous one, but execution number can be more than `+1`.

pre-commit config example:
```yaml
repos:
    - repo: https://github.com/ayasyrev/nbmetaclean
        rev: 0.1
        hooks:
        - id: nbcheck
          args: [ --ec, --not_strict ]
```

command line example:
```bash
nbcheck --ec --not_strict
```

#### Allow notebooks with no execution_count

`--no_exec` flag allows notebooks with all cells without execution_count.
If notebook has cells with execution_count and without execution_count, pre-commit will return error.

pre-commit config example:
```yaml
repos:
    - repo: https://github.com/ayasyrev/nbmetaclean
        rev: 0.1
        - id: nbcheck
          args: [ --ec, --no_exec ]
```

command line example:
```bash
nbcheck --ec --no_exec
```



### Errors and Warnings

`--err` and `--warn` flags can be used to check for errors and warnings in outputs.

pre-commit config example:
```yaml
repos:
    - repo: https://github.com/ayasyrev/nbmetaclean
        rev: 0.1
        hooks:
        - id: nbcheck
          args: [ --err, --warn ]
```

command line example:
```bash
nbcheck --err --warn
```
