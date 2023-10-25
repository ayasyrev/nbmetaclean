from pathlib import Path

from nbmetaclean.core import get_nb_names, read_nb, write_nb


def test_read_nb():
    """test read notebook"""
    file = Path("tests/test_nbs/test_nb_1.ipynb")
    nb = read_nb(file)
    assert isinstance(nb, dict)
    assert nb["metadata"] == {"language_info": {"name": "python"}}
    assert nb["nbformat"] == 4
    assert nb["nbformat_minor"] == 2
    cells = nb["cells"]
    assert isinstance(cells, list)
    assert len(cells) == 2
    # markdown
    assert cells[0]["cell_type"] == "markdown"
    assert cells[0]["source"] == ""
    assert cells[0]["metadata"] == {}
    # code
    assert cells[1]["cell_type"] == "code"
    assert cells[1]["source"] == ""
    assert cells[1]["execution_count"] is None
    assert cells[1]["metadata"] == {}
    assert cells[1]["outputs"] == []


def test_write_nb(tmp_path: Path):
    """test write notebook"""
    file = Path("tests/test_nbs/test_nb_1.ipynb")
    nb = read_nb(file)
    write_nb(nb, tmp_path / file.name)
    with open(tmp_path / file.name, "r", encoding="utf-8") as fh:
        res_text = fh.read()
    with open(file, "r", encoding="utf-8") as fh:
        org_text = fh.read()
    assert res_text == org_text

    # write with name w/o suffix
    result = write_nb(nb, tmp_path / "test_nb_1")
    assert result == tmp_path / "test_nb_1.ipynb"


def test_get_nb_names():
    """test get_nb_names"""
    path = Path("tests/test_nbs")
    file = path / "test_nb_1.ipynb"
    names = get_nb_names(file)
    assert len(names) == 1
    names.sort(key=lambda x: x.name)
    assert names[0] == file
    names = get_nb_names(path)
    assert len(names) == 3
    names.sort(key=lambda x: x.name)
    assert names[0] == file
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
    files = get_nb_names(tmp_path, filter_hidden=False)
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
    files = get_nb_names(tmp_path, filter_hidden=False)
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
    files = get_nb_names(tmp_path, filter_hidden=False)
    assert len(files) == 6
    files = get_nb_names(tmp_path)
    assert len(files) == 2
