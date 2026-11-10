from pathlib import Path
from privacy_scan import scan


def test_finds_name_ignoring_case_and_accents(tmp_path: Path):
    (tmp_path / "a.md").write_text("line one\nWith JOSE PEREZ here\n")
    hits = scan(tmp_path, ["José Pérez"])
    assert hits == [("a.md", 2, "José Pérez")]


def test_clean_tree_has_no_hits(tmp_path: Path):
    (tmp_path / "a.md").write_text("nothing private\n")
    assert scan(tmp_path, ["José Pérez"]) == []


def test_skips_git_and_venv(tmp_path: Path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "x").write_text("jose perez")
    assert scan(tmp_path, ["José Pérez"]) == []
