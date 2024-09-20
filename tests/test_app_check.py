from __future__ import annotations

from pathlib import Path

import pytest

from cli_result import run_module, run_script
from nbmetaclean.helpers import read_nb, write_nb
from nbmetaclean.version import __version__


app_name = "nbmetaclean.app_check"
example_nbs_path = Path("tests/test_nbs")
nb_name = "test_nb_3_ec.ipynb"


def test_run_script():
    """test run script"""
    app_path = Path("src/nbmetaclean/app_check.py")
    res = run_script(app_path, ["-h"])
    assert res.returncode == 0
    assert res.stdout.startswith(
        "usage: nbcheck [-h] [--ec] [--err] [--warn] [--not_strict] [--no_exec]"
    )
    assert not res.stderr


def test_check_nb_ec(tmp_path: Path):
    """test check `--ec`"""
    # base notebook - no execution_count

    test_nb = read_nb(example_nbs_path / nb_name)
    test_nb_path = tmp_path / nb_name
    write_nb(test_nb, test_nb_path)

    # check if no args
    res = run_module(app_name, [test_nb_path])
    assert res.stdout.startswith(
        "No checks are selected. Please select at least one check: "
        "--ec (for execution_count) or --err (for errors in outputs) or "
        "--warn (for warnings in outputs)."
    )
    assert not res.stderr
    assert res.returncode == 1

    # default execution_count
    res = run_module(app_name, [test_nb_path, "--ec"])
    assert res.stdout.startswith("1 notebooks with wrong execution_count:\n")
    assert res.stdout.endswith("test_nb_3_ec.ipynb\n")
    assert not res.stderr
    assert res.returncode == 1

    # `-V` option
    res = run_module(app_name, [test_nb_path, "--ec", "-V"])
    assert res.stdout.startswith("Checking 1 notebooks.\n")
    assert not res.stderr
    assert res.returncode == 1

    # check with `no_exec` option
    res = run_module(app_name, [test_nb_path, "--ec", "--no_exec"])
    assert not res.stdout
    assert not res.stderr
    assert res.returncode == 0

    # set correct execution_count
    test_nb["cells"][2]["execution_count"] = 1
    test_nb["cells"][3]["execution_count"] = 2
    test_nb["cells"][5]["execution_count"] = 3
    write_nb(test_nb, test_nb_path)

    res = run_module(app_name, [test_nb_path, "--ec"])
    assert not res.stdout
    assert not res.stderr

    # test strict
    test_nb["cells"][5]["execution_count"] = 4
    write_nb(test_nb, test_nb_path)
    res = run_module(app_name, [test_nb_path, "--ec"])
    assert res.stdout.startswith("1 notebooks with wrong execution_count:\n")
    assert res.stdout.endswith("test_nb_3_ec.ipynb\n")
    assert not res.stderr

    res = run_module(app_name, [test_nb_path, "--ec", "--not_strict"])
    assert not res.stdout
    assert not res.stderr

    # empty source, but with execution_count
    test_nb["cells"][5]["execution_count"] = 3
    test_nb["cells"][6]["execution_count"] = 4
    write_nb(test_nb, test_nb_path)

    res = run_module(app_name, [test_nb_path, "--ec"])
    assert res.stdout.startswith("1 notebooks with wrong execution_count:\n")
    assert res.stdout.endswith("test_nb_3_ec.ipynb\n")
    assert not res.stderr
    res = run_module(app_name, [test_nb_path, "--ec", "--not_strict"])
    assert res.stdout.startswith("1 notebooks with wrong execution_count:\n")
    assert res.stdout.endswith("test_nb_3_ec.ipynb\n")
    assert not res.stderr

    # start not from 1
    test_nb = read_nb(example_nbs_path / nb_name)
    test_nb["cells"][2]["execution_count"] = 2
    test_nb["cells"][3]["execution_count"] = 3
    test_nb["cells"][5]["execution_count"] = 4
    write_nb(test_nb, test_nb_path)

    res = run_module(app_name, [test_nb_path, "--ec"])
    assert res.stdout.startswith("1 notebooks with wrong execution_count:\n")
    assert res.stdout.endswith("test_nb_3_ec.ipynb\n")
    assert not res.stderr
    res = run_module(app_name, [test_nb_path, "--ec", "--not_strict"])
    assert not res.stdout
    assert not res.stderr

    # next is less
    test_nb["cells"][3]["execution_count"] = 5
    write_nb(test_nb, test_nb_path)
    res = run_module(app_name, [test_nb_path, "--ec"])
    assert res.stdout.startswith("1 notebooks with wrong execution_count:\n")
    assert res.stdout.endswith("test_nb_3_ec.ipynb\n")
    assert not res.stderr

    # code cell without execution_count
    test_nb = read_nb("tests/test_nbs/test_nb_3_ec.ipynb")
    test_nb["cells"][2]["execution_count"] = 1
    write_nb(test_nb, test_nb_path)

    res = run_module(app_name, [test_nb_path, "--ec"])
    assert res.stdout.startswith("1 notebooks with wrong execution_count:\n")
    assert res.stdout.endswith("test_nb_3_ec.ipynb\n")
    assert not res.stderr

    # check with `no_exec` option should be False
    res = run_module(app_name, [test_nb_path, "--ec", "--no_exec"])
    assert res.stdout.startswith("1 notebooks with wrong execution_count:\n")
    assert res.stdout.endswith("test_nb_3_ec.ipynb\n")
    assert not res.stderr


def test_check_nb_errors(tmp_path: Path):
    """test check `--err` option."""
    nb_name = "test_nb_3_ec.ipynb"
    test_nb = read_nb(example_nbs_path / nb_name)
    assert test_nb is not None

    test_nb_path = tmp_path / nb_name
    write_nb(test_nb, test_nb_path)
    res = run_module(app_name, [test_nb_path, "--err"])
    assert not res.stdout
    assert not res.stderr

    test_nb["cells"][2]["outputs"][0]["output_type"] = "error"
    write_nb(test_nb, test_nb_path)
    res = run_module(app_name, [test_nb_path, "--err"])
    assert res.stdout.startswith("1 notebooks with errors in outputs:\n")
    assert res.stdout.endswith("test_nb_3_ec.ipynb\n")
    assert not res.stderr


def test_check_nb_warnings(tmp_path):
    """test check `--warn` option."""
    test_nb = read_nb(example_nbs_path / nb_name)
    test_nb_path = tmp_path / nb_name
    write_nb(test_nb, test_nb_path)
    res = run_module(app_name, [test_nb_path, "--warn"])
    assert not res.stdout
    assert not res.stderr

    # if error, result is OK
    test_nb["cells"][2]["outputs"][0]["output_type"] = "error"
    write_nb(test_nb, test_nb_path)
    res = run_module(app_name, [test_nb_path, "--warn"])
    assert not res.stdout
    assert not res.stderr

    test_nb["cells"][2]["outputs"][0]["output_type"] = "stream"
    test_nb["cells"][2]["outputs"][0]["name"] = "stderr"
    write_nb(test_nb, test_nb_path)
    res = run_module(app_name, [test_nb_path, "--warn"])
    assert res.stdout.startswith("1 notebooks with warnings in outputs:\n")
    assert res.stdout.endswith("test_nb_3_ec.ipynb\n")
    assert not res.stderr


def test_check_app_version():
    """test check `--version` option."""
    res = run_module(app_name, ["--version"])
    assert res.stdout == f"nbcheck from nbmetaclean, version: {__version__}\n"
    assert not res.stderr

    res = run_module(app_name, ["-v"])
    assert res.stdout == f"nbcheck from nbmetaclean, version: {__version__}\n"
    assert not res.stderr


@pytest.mark.parametrize("arg", ["--ec", "--err", "--warn"])
def test_check_app_read_error(tmp_path: Path, arg: str):
    """test check_app with wrong nb file."""
    test_nb_path = tmp_path / "test_nb.ipynb"
    with open(test_nb_path, "w") as fh:
        fh.write("")

    res = run_module(app_name, [test_nb_path] + [arg])
    assert res.stdout.startswith("1 notebooks with read error:\n")
    assert res.stdout.endswith("test_nb.ipynb\n")
    assert not res.stderr
