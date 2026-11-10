import json
from pathlib import Path
import organize


def test_session_layout(tmp_path: Path):
    s = organize.make_session(tmp_path / "2026-01-01 Guest")
    for d in ["Raw/Cameras", "Raw/Audio", "Work", "Review", "Final/1 Episode", "Final/2 Spicy cut",
              "Final/3 Social clips", "Final/4 Team social clips", "Final/5 LinkedIn", "Final/6 Stories"]:
        assert (s / d).is_dir(), d


def test_copy_verified_and_source_kept(tmp_path: Path):
    src = tmp_path / "card"; src.mkdir()
    (src / "CAM1.mp4").write_bytes(b"abc" * 1000)
    (src / "POD01.WAV").write_bytes(b"xyz" * 1000)
    dst = tmp_path / "Raw"
    rep = organize.copy_verified(src, dst)
    assert all(r["ok"] for r in rep) and len(rep) == 2
    assert (src / "CAM1.mp4").exists()
    assert (dst / "CAM1.mp4").read_bytes() == b"abc" * 1000


def test_broken_copy_is_caught(tmp_path: Path, monkeypatch):
    src = tmp_path / "card"; src.mkdir()
    (src / "CAM1.mp4").write_bytes(b"abc" * 1000)
    real = organize._copy
    def bad(a, b):
        real(a, b)
        data = bytearray(b.read_bytes()); data[10] ^= 0xFF; b.write_bytes(bytes(data))  # same size, wrong bytes
    monkeypatch.setattr(organize, "_copy", bad)
    rep = organize.copy_verified(src, tmp_path / "Raw")
    assert rep[0]["ok"] is False and rep[0]["bytes"] == 3000


def test_report_written(tmp_path: Path):
    s = organize.make_session(tmp_path / "S")
    src = tmp_path / "card"; src.mkdir(); (src / "a.wav").write_bytes(b"1")
    organize.intake(src, s / "Raw/Audio", s)
    rep = json.loads((s / "Work/copy_report.json").read_text())
    assert rep[0]["file"] == "a.wav" and rep[0]["ok"]
