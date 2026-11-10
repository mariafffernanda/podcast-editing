import subprocess
import numpy as np
import pytest
import joincheck
import qa

SR = 48000
rng = np.random.default_rng(2)


def test_level_jump_flagged_smooth_passes():
    a = rng.standard_normal(SR) * 0.1
    b = rng.standard_normal(SR) * 0.1 * 10 ** (6 / 20)       # 6 dB louder after the join
    rep = joincheck.join_report(np.concatenate([a, b]), SR, [1.0])
    assert rep[0]["fail"] and rep[0]["jump_db"] > 3
    c = rng.standard_normal(SR) * 0.1
    rep = joincheck.join_report(np.concatenate([a, c]), SR, [1.0])
    assert not rep[0]["fail"]


def test_click_flagged():
    x = np.cos(2 * np.pi * 220 * np.arange(2 * SR) / SR) * 0.2
    x[SR:] *= -1                                              # flipped at a peak: a hard step = audible click
    rep = joincheck.join_report(x, SR, [1.0])
    assert rep[0]["click"] and rep[0]["fail"]


def test_riskiest_order():
    rep = [{"t": 1, "jump_db": 1.0, "click": False, "fail": False}, {"t": 2, "jump_db": 4.0, "click": False, "fail": True}]
    assert joincheck.riskiest(rep, 1)[0]["t"] == 2


def tone(path, sec):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"sine=f=1000:d={sec}:sample_rate=48000",
                    "-af", "volume=7dB", str(path)], check=True)


def test_good_social_passes(tmp_path):
    f = tmp_path / "ok.wav"; tone(f, 40)
    r = qa.qa(f, "social")
    assert r["pass"], r["fails"]
    assert abs(r["lufs"] + 14) <= 1


def test_too_long_fails(tmp_path):
    f = tmp_path / "long.wav"; tone(f, 80)
    r = qa.qa(f, "social")
    assert not r["pass"] and any("length" in x for x in r["fails"])


def test_unreadable_file_fails_never_passes(tmp_path):
    f = tmp_path / "broken.mp4"; f.write_bytes(b"\x00" * 5000)
    r = qa.qa(f, "social")
    assert r["pass"] is False


def test_truncated_file_fails(tmp_path):
    f = tmp_path / "ok.wav"; tone(f, 40)
    g = tmp_path / "cut.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-c:a", "aac", str(g)], check=True)
    data = g.read_bytes(); g.write_bytes(data[: len(data) // 2])
    assert qa.qa(g, "social")["pass"] is False
