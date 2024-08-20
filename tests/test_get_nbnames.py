from pathlib import Path

from nbmetaclean.helpers import get_nb_names, is_notebook


def test_is_notebook():
    """test is_notebook"""
    assert is_notebook(Path("tests/test_nbs/test_nb_1.ipynb"))
    assert not is_notebook(Path("tests/test_nbs/test_nb_1.py"))
    assert not is_notebook(Path("tests/test_nbs/.test_nb_2_meta.ipynb"))
    assert is_notebook(Path("tests/test_nbs/.test_nb_2_meta.ipynb"), hidden=True)


def test_get_nb_names():
    """test get_nb_names"""
    path = Path("tests/test_nbs")
    # filename as argument
    file = path / "test_nb_1.ipynb"
    names = get_nb_names(file)
    assert len(names) == 1
    names.sort(key=lambda x: x.name)
    assert names[0] == file
    # filename but not nb
    names = get_nb_names("tests/test_clean.py")
    assert len(names) == 0

    # path as argument
    names = get_nb_names(path)
    assert len(names) == 3
    names.sort(key=lambda x: x.name)
    assert names[0] == file
    # path as argument. add hidden files
    names = get_nb_names(path, hidden=True)
    assert len(names) == 4
    try:
        get_nb_names("wrong_name")
        assert False
    except FileNotFoundError as ex:
        assert True
        assert str(ex) == "wrong_name not exists!"


def test_get_nb_names_recursive_hidden(tmp_path: Path):
    """test get_nb_names recursive hidden"""
    suffix = ".ipynb"
    # add one nb
    with open((tmp_path / "tst").with_suffix(suffix), "w", encoding="utf-8") as _:
        pass
    files = get_nb_names(tmp_path)
    assert len(files) == 1

    # add hidden nb
    with open((tmp_path / ".tst").with_suffix(suffix), "w", encoding="utf-8") as _:
        pass
    files = get_nb_names(tmp_path)
    assert len(files) == 1
    files = get_nb_names(tmp_path, hidden=True)
    assert len(files) == 2
    # add simple file
    with open((tmp_path / "simple"), "w", encoding="utf-8") as _:
        pass
    files = get_nb_names(tmp_path)
    assert len(files) == 1

    # add dir with one nb, hidden nb
    new_dir = tmp_path / "new_dir"
    new_dir.mkdir()
    with open((new_dir / "tst").with_suffix(suffix), "w", encoding="utf-8") as _:
        pass
    with open((new_dir / ".tst").with_suffix(suffix), "w", encoding="utf-8") as _:
        pass
    files = get_nb_names(tmp_path)
    assert len(files) == 2
    files = get_nb_names(tmp_path, hidden=True)
    assert len(files) == 4

    files = get_nb_names(tmp_path, recursive=False)
    assert len(files) == 1

    # add hidden dir
    hid_dir = tmp_path / ".hid_dir"
    hid_dir.mkdir()
    with open((hid_dir / "tst").with_suffix(suffix), "w", encoding="utf-8") as _:
        pass
    with open((hid_dir / ".tst").with_suffix(suffix), "w", encoding="utf-8") as _:
        pass
    files = get_nb_names(tmp_path, hidden=True)
    assert len(files) == 6
    files = get_nb_names(tmp_path)
    assert len(files) == 2

    # add checkpoint dir and file
    # files at this dir will be skipped
    checkpoint_dir = tmp_path / ".ipynb_checkpoints"
    checkpoint_dir.mkdir()
    with open(
        (checkpoint_dir / "nb-checkpoint").with_suffix(suffix), "w", encoding="utf-8"
    ) as _:
        pass
    with open(
        (checkpoint_dir / "some_nb").with_suffix(suffix), "w", encoding="utf-8"
    ) as _:
        pass
    files = get_nb_names(tmp_path)
    assert len(files) == 2
    files = get_nb_names(tmp_path, hidden=True)
    assert len(files) == 6
