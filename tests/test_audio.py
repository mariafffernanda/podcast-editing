import numpy as np
import pytest
import soundfile as sf
import audio

SR = 16000
rng = np.random.default_rng(1)


def burst(sec, db):
    return rng.standard_normal(int(sec * SR)) * 10 ** (db / 20)


def test_load_poly_and_folder(tmp_path):
    x = np.stack([burst(1, -20), burst(1, -30)], axis=1)
    sf.write(tmp_path / "poly.wav", x, SR)
    sr, t = audio.load_tracks(tmp_path / "poly.wav")
    assert sr == SR and t.shape == (2, SR)
    d = tmp_path / "mics"; d.mkdir()
    sf.write(d / "mic1.wav", x[:, 0], SR); sf.write(d / "mic2.wav", x[:, 1], SR)
    assert audio.load_tracks(d)[1].shape == (2, SR)


def test_who_talks_needs_margin():
    a = np.concatenate([burst(1, -20), burst(1, -40), burst(1, -20)])
    b = np.concatenate([burst(1, -38), burst(1, -20), burst(1, -23)])
    who = audio.who_talks(audio.levels_db(np.stack([a, b]), SR, win=0.25))
    assert who[:4] == [0] * 4 and who[4:8] == [1] * 4
    assert set(who[8:]) == {None}   # only 3 dB apart: not sure, never a guess


def test_silent_track_stops(tmp_path):
    x = np.stack([burst(2, -20), np.zeros(2 * SR)])
    with pytest.raises(audio.MissingTrack):
        audio.check_tracks(x)


def test_offset_and_drift():
    n = 120 * SR
    ref = rng.standard_normal(n).astype(np.float32)
    lag, ppm = 0.120, 50
    t = np.arange(n) / SR
    src_t = t * (1 + ppm / 1e6) - lag            # other = ref delayed by lag, running slow by ppm
    other = np.interp(src_t, t, ref, left=0, right=0).astype(np.float32)
    offs = audio.offsets(ref, other, SR, points=8, win=4.0)
    assert len(offs) == 8
    off, p = audio.fit_drift(offs)
    assert abs(off - lag) < 0.001
    assert abs(p - ppm) < 5
