"""Step 5 and 7: listen across every join of a finished piece.

A join fails on a level jump over 3 dB or a click. The 10 riskiest go in the report for a human to hear.
usage: joincheck.py <finished.wav> <joins.json: [seconds in the finished piece, ...]>
"""
import json
import sys

import numpy as np
import soundfile as sf

MAX_JUMP_DB = 3.0


def _db(x):
    return 20 * np.log10(max(float(np.sqrt(np.mean(x.astype(np.float64) ** 2))), 1e-9))


def join_report(x: np.ndarray, sr: int, joins: list[float], win: float = 0.05) -> list[dict]:
    if x.ndim > 1:
        x = x.mean(axis=1)
    n = int(win * sr)
    d = np.abs(np.diff(x))
    out = []
    for t in joins:
        k = int(round(t * sr))
        before, after = x[max(k - n, 0):k], x[k:k + n]
        jump = abs(_db(after) - _db(before)) if len(before) and len(after) else 0.0
        near = d[max(k - 48, 0):k + 48]                     # about 1 ms each side at 48 kHz
        around = d[max(k - 10 * n, 0):k + 10 * n]
        click = bool(len(near) and near.max() > 4 * max(np.percentile(around, 99), 1e-6))
        out.append({"t": round(t, 3), "jump_db": round(jump, 2), "click": click, "fail": bool(jump > MAX_JUMP_DB or click)})
    return out


def riskiest(report: list[dict], n: int = 10) -> list[dict]:
    return sorted(report, key=lambda r: (r["fail"], r["click"], r["jump_db"]), reverse=True)[:n]


if __name__ == "__main__":
    x, sr = sf.read(sys.argv[1], dtype="float32")
    rep = join_report(x, sr, json.load(open(sys.argv[2])))
    print(json.dumps({"joins": len(rep), "failed": sum(r["fail"] for r in rep), "riskiest": riskiest(rep)}, indent=1))
