import json
from pathlib import Path
import build


def test_pages_made_for_every_guest(tmp_path):
    data = json.loads((Path(__file__).parent / "guests.json").read_text())
    out = tmp_path / "public"
    build.build(data, out)
    assert (out / "index.html").exists() and (out / "entrar/index.html").exists()
    page = (out / "g/alex-rivera/index.html").read_text()
    assert "Alex Rivera" in page and "The first client who said no" in page
    assert page.count('class="card') == 2
    assert "noindex" in page
    # the front page never lists guests
    assert "Alex Rivera" not in (out / "index.html").read_text()


def test_text_is_escaped(tmp_path):
    data = {"show": "S", "host": "H", "lang": "es", "guests": [{"slug": "a", "name": "<b>x</b>", "pieces": []}]}
    build.build(data, tmp_path)
    assert "<b>x</b>" not in (tmp_path / "g/a/index.html").read_text()


def test_bad_slug_refused(tmp_path):
    import pytest
    with pytest.raises(ValueError):
        build.build({"show": "S", "host": "H", "guests": [{"slug": "../x", "name": "n", "pieces": []}]}, tmp_path)


def test_password_hash_matches_middleware():
    import sys; sys.path.insert(0, str(Path(__file__).parent / "tools"))
    import set_password
    # the same value middleware.js computes for sign("pw:alex-rivera:" + norm(" Café  Lunes ")) with secret "s"
    assert set_password.keyed("s", "alex-rivera", " Café  Lunes ") == "e8471bbb85e826f11472a88dca0ac0697d26fbbfb7b357e6ff3a2d1e4d9bff2d"
