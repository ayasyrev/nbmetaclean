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
        ["python", "-m", "nbmetaclean.app_clean", str(nb_path), *args],
        capture_output=True,
        check=False,
    )
    return run_result.stdout.decode("utf-8"), run_result.stderr.decode("utf-8")


example_nbs_path = Path("tests/test_nbs")
nb_name_clean = "test_nb_2_clean.ipynb"


def test_clean_nb_metadata(tmp_path: Path):
    """test clean_nb_metadata"""
    test_nb = read_nb(example_nbs_path / nb_name_clean)
    test_nb_path = tmp_path / nb_name_clean
    write_nb(test_nb, test_nb_path)

    # default run no args, clean notebooks
    res_out, res_err = run_app(test_nb_path, [])
    assert not res_out
    assert not res_err

    # add metadata, new filter, mask not merged
    test_nb["metadata"]["some key"] = "some value"
    write_nb(test_nb, test_nb_path)

    # check with preserve mask, expect no changes
    res_out, res_err = run_app(
        test_nb_path, ["--nb_metadata_preserve_mask", "some key"]
    )
    assert not res_out
    assert not res_err
    res_nb = read_nb(test_nb_path)
    assert res_nb["metadata"]["some key"] == "some value"

    # check without preserve mask, dry run
    res_out, res_err = run_app(test_nb_path, ["-D"])
    assert res_out
    assert not res_err
    res_nb = read_nb(test_nb_path)
    assert res_nb["metadata"]["some key"] == "some value"

    # check without preserve mask, expect changes
    res_out, res_err = run_app(test_nb_path, [])
    assert res_out
    assert not res_err
    res_nb = read_nb(test_nb_path)
    nb_metadata = res_nb.get("metadata")
    assert nb_metadata
    assert not nb_metadata.get("some key")

    # verbose flag.
    # nb now cleaned
    res_out, res_err = run_app(test_nb_path, ["-V"])
    assert res_out.startswith("Path: ")
    assert res_out.endswith(
        "test_nb_2_clean.ipynb, preserve timestamp: True\nchecked: 1 notebooks\n"
    )
    assert not res_err

    # rewrite notebook
    write_nb(test_nb, test_nb_path)
    res_out, res_err = run_app(test_nb_path, ["-V"])
    assert res_out.startswith("Path: ")
    assert "cleaned:" in res_out
    assert res_out.endswith("test_nb_2_clean.ipynb\n")
    assert not res_err
