from __future__ import annotations

from pathlib import Path
import subprocess

from nbmetaclean.helpers import read_nb, write_nb


def run_app(
    nb_path: Path,
    args: list[str] = [],
) -> tuple[str, str]:
    """run app"""
    run_result = subprocess.run(
        ["python", "-m", "nbmetaclean.app_check", str(nb_path), *args],
        capture_output=True,
        check=False,
    )
    return run_result.stdout.decode("utf-8"), run_result.stderr.decode("utf-8")


example_nbs_path = Path("tests/test_nbs")
nb_name = "test_nb_3_ec.ipynb"


def test_check_nb_ec(tmp_path: Path):
    """test check `--ec`"""
    # base notebook - no execution_count

    test_nb = read_nb(example_nbs_path / nb_name)
    test_nb_path = tmp_path / nb_name
    write_nb(test_nb, test_nb_path)

    # check if no args
    res_out, res_err = run_app(test_nb_path, [])
    assert res_out.startswith(
        "No checks are selected. Please select at least one check: "
        "--ec (for execution_count) or --err (for errors in outputs) or "
        "--warn (for warnings in outputs)."
    )
    assert not res_err

    res_out, res_err = run_app(test_nb_path, ["--ec"])
    assert res_out.startswith("1 notebooks with wrong execution_count:\n")
    assert res_out.endswith("test_nb_3_ec.ipynb\n")
    assert not res_err
    # check with `no_exec` option
    res_out, res_err = run_app(test_nb_path, ["--ec", "--no_exec"])
    assert not res_out
    assert not res_err

    # set correct execution_count
    test_nb["cells"][2]["execution_count"] = 1
    test_nb["cells"][3]["execution_count"] = 2
    test_nb["cells"][5]["execution_count"] = 3
    write_nb(test_nb, test_nb_path)

    res_out, res_err = run_app(test_nb_path, ["--ec"])
    assert not res_out
    assert not res_err

    # test strict
    test_nb["cells"][5]["execution_count"] = 4
    write_nb(test_nb, test_nb_path)
    res_out, res_err = run_app(test_nb_path, ["--ec"])
    assert res_out.startswith("1 notebooks with wrong execution_count:\n")
    assert res_out.endswith("test_nb_3_ec.ipynb\n")
    assert not res_err

    res_out, res_err = run_app(test_nb_path, ["--ec", "--not_strict"])
    assert not res_out
    assert not res_err

    # empty source, but with execution_count
    test_nb["cells"][5]["execution_count"] = 3
    test_nb["cells"][6]["execution_count"] = 4
    write_nb(test_nb, test_nb_path)

    res_out, res_err = run_app(test_nb_path, ["--ec"])
    assert res_out.startswith("1 notebooks with wrong execution_count:\n")
    assert res_out.endswith("test_nb_3_ec.ipynb\n")
    assert not res_err
    res_out, res_err = run_app(test_nb_path, ["--ec", "--not_strict"])
    assert res_out.startswith("1 notebooks with wrong execution_count:\n")
    assert res_out.endswith("test_nb_3_ec.ipynb\n")
    assert not res_err

    # start not from 1
    test_nb = read_nb(example_nbs_path / nb_name)
    test_nb["cells"][2]["execution_count"] = 2
    test_nb["cells"][3]["execution_count"] = 3
    test_nb["cells"][5]["execution_count"] = 4
    write_nb(test_nb, test_nb_path)

    res_out, res_err = run_app(test_nb_path, ["--ec"])
    assert res_out.startswith("1 notebooks with wrong execution_count:\n")
    assert res_out.endswith("test_nb_3_ec.ipynb\n")
    assert not res_err
    res_out, res_err = run_app(test_nb_path, ["--ec", "--not_strict"])
    assert not res_out
    assert not res_err

    # next is less
    test_nb["cells"][3]["execution_count"] = 5
    write_nb(test_nb, test_nb_path)
    res_out, res_err = run_app(test_nb_path, ["--ec"])
    assert res_out.startswith("1 notebooks with wrong execution_count:\n")
    assert res_out.endswith("test_nb_3_ec.ipynb\n")
    assert not res_err

    # code cell without execution_count
    test_nb = read_nb("tests/test_nbs/test_nb_3_ec.ipynb")
    test_nb["cells"][2]["execution_count"] = 1
    write_nb(test_nb, test_nb_path)

    res_out, res_err = run_app(test_nb_path, ["--ec"])
    assert res_out.startswith("1 notebooks with wrong execution_count:\n")
    assert res_out.endswith("test_nb_3_ec.ipynb\n")
    assert not res_err

    # check with `no_exec` option should be False
    res_out, res_err = run_app(test_nb_path, ["--ec", "--no_exec"])
    assert res_out.startswith("1 notebooks with wrong execution_count:\n")
    assert res_out.endswith("test_nb_3_ec.ipynb\n")
    assert not res_err


def test_check_nb_errors(tmp_path: Path):
    """test check `--err` option."""
    test_nb_path = tmp_path / nb_name
    test_nb = read_nb(example_nbs_path / nb_name)
    write_nb(test_nb, test_nb_path)
    res_out, res_err = run_app(test_nb_path, ["--err"])
    assert not res_out
    assert not res_err

    test_nb["cells"][2]["outputs"][0]["output_type"] = "error"
    write_nb(test_nb, test_nb_path)
    res_out, res_err = run_app(test_nb_path, ["--err"])
    assert res_out.startswith("1 notebooks with errors in outputs:\n")
    assert res_out.endswith("test_nb_3_ec.ipynb\n")
    assert not res_err


def test_check_nb_warnings(tmp_path):
    """test check `--warn` option."""
    test_nb = read_nb(example_nbs_path / nb_name)
    test_nb_path = tmp_path / nb_name
    write_nb(test_nb, test_nb_path)
    res_out, res_err = run_app(test_nb_path, ["--warn"])
    assert not res_out
    assert not res_err

    # if error, result is OK
    test_nb["cells"][2]["outputs"][0]["output_type"] = "error"
    write_nb(test_nb, test_nb_path)
    res_out, res_err = run_app(test_nb_path, ["--warn"])
    assert not res_out
    assert not res_err

    test_nb["cells"][2]["outputs"][0]["output_type"] = "stream"
    test_nb["cells"][2]["outputs"][0]["name"] = "stderr"
    write_nb(test_nb, test_nb_path)
    res_out, res_err = run_app(test_nb_path, ["--warn"])
    assert res_out.startswith("1 notebooks with warnings in outputs:\n")
    assert res_out.endswith("test_nb_3_ec.ipynb\n")
    assert not res_err
