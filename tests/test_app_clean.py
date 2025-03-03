from __future__ import annotations

from pathlib import Path

import subprocess

from nbmetaclean.helpers import read_nb, write_nb


def run_app(
    nb_path: Path | list[Path] | None = None,
    args: list[str] | None = None,
    cwd: Path | None = None,
) -> tuple[str, str]:
    """run app"""
    args = args or []
    if isinstance(nb_path, Path):
        args.insert(0, str(nb_path))
    elif isinstance(nb_path, list):
        args = [str(nb) for nb in nb_path] + args

    run_result = subprocess.run(
        ["python", "-m", "nbmetaclean.app_clean", *args],
        capture_output=True,
        check=False,
        cwd=cwd,
    )
    return run_result.stdout.decode("utf-8"), run_result.stderr.decode("utf-8")


example_nbs_path = Path("tests/test_nbs")

# this test conflict with coverage - need to be fixed
# def test_app_clean_no_args(tmp_path: Path) -> None:
#     """test app_clean with no args"""
#     res_out, res_err = run_app(cwd=tmp_path)
#     assert res_out == "No notebooks found at current directory.\n"
#     assert not res_err

#     # prepare test clean notebook
#     nb_name_clean = "test_nb_2_clean.ipynb"
#     test_nb = read_nb(example_nbs_path / nb_name_clean)
#     test_nb_path = tmp_path / nb_name_clean
#     write_nb(test_nb, test_nb_path)

#     res_out, res_err = run_app(cwd=tmp_path)
#     assert res_out == "Checked: 1 notebooks. All notebooks are clean.\n"
#     assert not res_err

#     # add metadata
#     test_nb["metadata"]["some key"] = "some value"
#     write_nb(test_nb, test_nb_path)

#     res_out, res_err = run_app(cwd=tmp_path)
#     assert res_out == "cleaned: test_nb_2_clean.ipynb\n"
#     assert not res_err


def test_clean_nb_metadata(tmp_path: Path) -> None:
    """test clean_nb_metadata"""
    nb_name_clean = "test_nb_2_clean.ipynb"
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


def test_clean_nb_ec_output(tmp_path: Path):
    """test execution count and output"""
    nb_name_clean = "test_nb_2_clean.ipynb"
    test_nb = read_nb(example_nbs_path / nb_name_clean)
    test_nb_path = tmp_path / nb_name_clean

    test_nb["cells"][1]["execution_count"] = 1
    test_nb["cells"][1]["outputs"][0]["execution_count"] = 1
    write_nb(test_nb, test_nb_path)

    # default settings
    res_out, res_err = run_app(test_nb_path, [])
    assert res_out.startswith("cleaned:")
    assert res_out.endswith("test_nb_2_clean.ipynb\n")
    assert not res_err
    nb = read_nb(test_nb_path)
    assert nb["cells"][1]["execution_count"] is None
    assert nb["cells"][1]["outputs"][0]["data"] == {"text/plain": ["2"]}
    assert nb["cells"][1]["outputs"][0]["execution_count"] is None

    # dry run
    write_nb(test_nb, test_nb_path)
    res_out, res_err = run_app(test_nb_path, ["-D"])
    assert res_out.startswith("cleaned:")
    assert res_out.endswith("test_nb_2_clean.ipynb\n")
    assert not res_err
    nb = read_nb(test_nb_path)
    assert nb["cells"][1]["execution_count"] == 1
    assert nb["cells"][1]["outputs"][0]["execution_count"] == 1
    # dry, verbose
    res_out, res_err = run_app(test_nb_path, ["-DV"])
    assert res_out.startswith("Path: ")
    assert nb_name_clean in res_out
    assert res_out.endswith("test_nb_2_clean.ipynb\n")
    assert not res_err

    # silent
    write_nb(test_nb, test_nb_path)
    res_out, res_err = run_app(test_nb_path, ["-s"])
    assert not res_out
    assert not res_err
    nb = read_nb(test_nb_path)
    assert nb["cells"][1]["execution_count"] is None
    assert nb["cells"][1]["outputs"][0]["execution_count"] is None

    # clean output
    write_nb(test_nb, test_nb_path)
    res_out, res_err = run_app(test_nb_path, ["--clear_outputs"])
    assert res_out.startswith("cleaned:")
    assert res_out.endswith("test_nb_2_clean.ipynb\n")
    assert not res_err
    nb = read_nb(test_nb_path)
    assert nb["cells"][1]["execution_count"] is None
    assert nb["cells"][1]["outputs"] == []

    # path as arg
    write_nb(test_nb, test_nb_path)
    res_out, res_err = run_app(test_nb_path, [])
    assert res_out.startswith("cleaned:")
    assert res_out.endswith("test_nb_2_clean.ipynb\n")
    assert not res_err
    nb = read_nb(test_nb_path)
    assert nb["metadata"]["authors"][0]["name"] == "Andrei Yasyrev"
    assert nb["cells"][1]["execution_count"] is None
    assert nb["cells"][1]["outputs"][0]["execution_count"] is None

    # two nbs
    write_nb(test_nb, test_nb_path)
    # add second notebook
    nb_name_clean_2 = "test_nb_3_ec.ipynb"
    test_nb_2 = read_nb(example_nbs_path / nb_name_clean_2)
    test_nb_2["metadata"]["some key"] = "some value"
    write_nb(test_nb_2, tmp_path / nb_name_clean_2)

    res_out, res_err = run_app(tmp_path, [])
    assert res_out.startswith("cleaned: 2 notebooks\n")
    assert nb_name_clean in res_out
    assert nb_name_clean_2 in res_out
    assert not res_err


def test_clean_nb_wrong_file(tmp_path: Path):
    """test app_clean with wrong file"""
    nb_name = tmp_path / "wrong.ipynb"
    with nb_name.open("w", encoding="utf-8") as fh:
        fh.write("some text")

    res_out, res_err = run_app(nb_name, [])
    assert res_out.startswith("with errors: 1")
    assert str(nb_name) in res_out
    assert not res_err


def test_app_clean_version():
    """test check `--version` option."""
    res_out, res_err = run_app(args=["--version"])
    assert res_out.startswith("nbmetaclean version: ")
    assert not res_err

    res_out, res_err = run_app(args=["-v"])
    assert res_out.startswith("nbmetaclean version: ")
    assert not res_err
