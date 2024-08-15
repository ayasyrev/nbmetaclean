---
hide:
  - navigation
---

# nbmetaclean

Pre-commit hook to clean Jupyter Notebooks metadata, execution_count and optionally output.

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/benchmark-utils)](https://pypi.org/project/nbmetaclean/)
[![PyPI Status](https://badge.fury.io/py/nbmetaclean.svg)](https://badge.fury.io/py/nbmetaclean)
[![Tests](https://github.com/ayasyrev/nbmetaclean/workflows/Tests/badge.svg)](https://github.com/ayasyrev/nbmetaclean/actions?workflow=Tests)  [![Codecov](https://codecov.io/gh/ayasyrev/nbmetaclean/branch/main/graph/badge.svg)](https://codecov.io/gh/ayasyrev/nbmetaclean)

Pure Python, no dependencies.

Can be used as a pre-commit hook or as a command line tool.

## Usage

### Pre-commit hook
add to `.pre-commit-config.yaml`:
```yaml
repos:
    - repo: https://github.com/ayasyrev/nbmetaclean
        rev: 0.0.9
        hooks:
        - id: nbclean
          name: nbclean
          entry: nbclean
          files: \.ipynb
```

If you want to leave execution_count or clean outputs, add `args` [ --not_ec ] or [ --clear_outputs ] line to `.pre-commit-config.yaml`.

```yaml
repos:
    - repo: https://github.com/ayasyrev/nbmetaclean
        rev: 0.0.9
        hooks:
        - id: nbclean
          name: nbclean
          entry: nbclean
          files: \.ipynb
          args: [ --not_ec ]
```


### Command line tool

Install:
```bash
pip install nbmetaclean
```

Usage:

```bash
nbclean
```

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
