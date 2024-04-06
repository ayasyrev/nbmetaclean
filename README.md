# nbmetaclean

Pre-commit hook to clean Jupyter Notebooks metadata, execution_count and optionally output.

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
