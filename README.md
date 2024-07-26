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
        rev: 0.0.8
        hooks:
        - id: nbclean
          name: nbclean
          entry: nbclean
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
