"""Step 2: which mic is whose, and how the recorder lines up with each camera.

usage:
  audio.py map   <recorder.wav | folder of one WAV per mic>        -> who talks every 0.25 s
  audio.py drift <camera.wav> <recorder.wav> [--track N]           -> offset and drift
Extract a camera's sound first: ffmpeg -i CAM1.mp4 -vn -ac 1 -ar 16000 cam1.wav
"""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

SILENT_DB = -60.0


class MissingTrack(Exception):
    """A mic track is silent or missing. Stop and ask: never fall back to camera audio."""


def load_tracks(path) -> tuple[int, np.ndarray]:
    """One polyphonic file (many tracks) or a folder of one WAV per mic -> (sr, [tracks, samples])."""
    path = Path(path)
    if path.is_dir():
        files = sorted(p for p in path.iterdir() if p.suffix.lower() in (".wav", ".flac"))
        data = [sf.read(f, dtype="float32", always_2d=True) for f in files]
        srs = {sr for _, sr in data}
        if len(srs) != 1:
            raise ValueError("the mic files have different sample rates")
        n = min(len(x) for x, _ in data)
        return srs.pop(), np.stack([x[:n, 0] for x, _ in data])
    x, sr = sf.read(path, dtype="float32", always_2d=True)
    return sr, x.T.copy()


def levels_db(x: np.ndarray, sr: int, win: float = 0.25) -> np.ndarray:
    hop = int(sr * win)
    n = x.shape[1] // hop
    blocks = x[:, : n * hop].reshape(x.shape[0], n, hop)
    rms = np.sqrt(np.mean(blocks.astype(np.float64) ** 2, axis=2))
    return 20 * np.log10(np.maximum(rms, 1e-9))


def check_tracks(x: np.ndarray) -> None:
    peak = 20 * np.log10(np.maximum(np.abs(x).max(axis=1), 1e-9))
    dead = [i + 1 for i, p in enumerate(peak) if p < SILENT_DB]
    if dead:
        raise MissingTrack(f"track(s) {dead} are silent. Stop and ask before going on.")


def who_talks(levels: np.ndarray, margin_db: float = 6.0, floor_db: float = -50.0) -> list:
    """Per window: the track at least margin_db louder than every other, else None (not sure)."""
    out = []
    for col in levels.T:
        order = np.argsort(col)[::-1]
        top = col[order[0]]
        second = col[order[1]] if len(col) > 1 else -np.inf
        out.append(int(order[0]) if top > floor_db and top - second >= margin_db else None)
    return out


def _lag(ref: np.ndarray, other: np.ndarray, sr: int, center: float, win: float, search: float) -> float:
    a0, a1 = int((center - win / 2) * sr), int((center + win / 2) * sr)
    m = int(search * sr)
    seg = ref[a0:a1]
    big = other[max(a0 - m, 0): a1 + m]
    pad_front = m - (a0 - max(a0 - m, 0))
    big = np.concatenate([np.zeros(pad_front, np.float32), big])
    n = 1 << int(np.ceil(np.log2(len(big) + len(seg))))
    c = np.fft.irfft(np.fft.rfft(big, n) * np.conj(np.fft.rfft(seg, n)), n)[: len(big) - len(seg) + 1]
    k = int(np.argmax(c))
    if 0 < k < len(c) - 1:  # parabolic peak for sub-sample precision
        y0, y1, y2 = c[k - 1], c[k], c[k + 1]
        d = y0 - 2 * y1 + y2
        k = k + (0.5 * (y0 - y2) / d if d else 0)
    return (k - m) / sr


def offsets(ref: np.ndarray, other: np.ndarray, sr: int, points: int = 8, win: float = 10.0,
            search: float = 2.0) -> list[tuple[float, float]]:
    """Time of the same sound in `other` minus in `ref`, measured at `points` places across the file."""
    dur = min(len(ref), len(other)) / sr
    centers = np.linspace(win / 2 + search, dur - win / 2 - search, points)
    return [(float(t), _lag(ref, other, sr, t, win, search)) for t in centers]


def fit_drift(offs: list[tuple[float, float]]) -> tuple[float, float]:
    """(offset in seconds at time 0, drift in ppm). Positive ppm: `other` runs fast, so the lag shrinks over time."""
    t = np.array([o[0] for o in offs]); lag = np.array([o[1] for o in offs])
    slope, icpt = np.polyfit(t, lag, 1)
    return float(icpt), float(-slope * 1e6)


def mono16(path: str, track: int | None = None) -> np.ndarray:
    x, sr = sf.read(path, dtype="float32", always_2d=True)
    x = x[:, track] if track is not None else x.mean(axis=1)
    if sr != 16000:
        t = np.arange(0, len(x) / sr, 1 / 16000)
        x = np.interp(t, np.arange(len(x)) / sr, x).astype(np.float32)
    return x


if __name__ == "__main__":
    if sys.argv[1] == "map":
        sr, x = load_tracks(sys.argv[2])
        check_tracks(x)
        who = who_talks(levels_db(x, sr))
        sure = [w for w in who if w is not None]
        print(json.dumps({"windows": len(who), "sure": len(sure),
                          "share": {f"track {i + 1}": round(sure.count(i) / max(len(sure), 1), 3) for i in range(x.shape[0])}}))
    elif sys.argv[1] == "drift":
        tr = int(sys.argv[sys.argv.index("--track") + 1]) - 1 if "--track" in sys.argv else None
        offs = offsets(mono16(sys.argv[2]), mono16(sys.argv[3], tr), 16000)
        off, ppm = fit_drift(offs)
        worst = max(abs(l - (off - ppm / 1e6 * t)) for t, l in offs)
        print(json.dumps({"offset_s": round(off, 4), "drift_ppm": round(ppm, 2), "worst_fit_ms": round(worst * 1000, 1),
                          "points": [[round(t, 1), round(l, 4)] for t, l in offs]}))
