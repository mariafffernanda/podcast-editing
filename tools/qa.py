"""Step 7: the report card for one finished file. Nothing reaches a human until it passes.

A file the checker cannot read FAILS. A check that "passes" what it could not read is worse than no check.
usage: qa.py <file> <episode|spicy|social|linkedin|story>
"""
import json
import re
import subprocess
import sys
from pathlib import Path

TARGET_LUFS, LUFS_TOL, MAX_PEAK = -14.0, 1.0, -1.5
LIMITS = {"social": (30, 70), "linkedin": (30, 60), "story": (15, 30), "episode": (60, None), "spicy": (60, None)}


def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def duration(f: Path) -> float | None:
    r = _run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)])
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


def qa(f: Path, kind: str) -> dict:
    f = Path(f)
    fails = []
    dec = _run(["ffmpeg", "-v", "error", "-xerror", "-i", str(f), "-f", "null", "-"])
    errors = len([l for l in dec.stderr.splitlines() if l.strip()])
    if dec.returncode != 0 or errors:
        fails.append(f"decode: {errors} error(s), exit {dec.returncode}")
    dur = duration(f)
    if dur is None:
        fails.append("decode: no duration")
    lo, hi = LIMITS[kind]
    if dur is not None and (dur < lo or (hi and dur > hi)):
        fails.append(f"length {dur:.1f}s outside {lo}-{hi or '∞'}s")
    lufs = peak = None
    r = _run(["ffmpeg", "-nostats", "-i", str(f), "-filter_complex", "ebur128=peak=true", "-f", "null", "-"])
    summ = r.stderr.split("Summary:")[-1] if "Summary:" in r.stderr else ""
    m = re.search(r"I:\s+(-?[\d.]+) LUFS", summ)
    p = re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", summ)
    if m:
        lufs = float(m.group(1))
        if abs(lufs - TARGET_LUFS) > LUFS_TOL:
            fails.append(f"loudness {lufs} LUFS, target {TARGET_LUFS}")
    else:
        fails.append("loudness: could not measure")
    if p and p.group(1) != "-inf":
        peak = float(p.group(1))
        if peak > MAX_PEAK:
            fails.append(f"peak {peak} dB over {MAX_PEAK}")
    elif not p:
        fails.append("peak: could not measure")
    return {"file": f.name, "kind": kind, "pass": not fails, "duration": dur, "lufs": lufs, "peak": peak,
            "decode_errors": errors, "fails": fails}


if __name__ == "__main__":
    r = qa(Path(sys.argv[1]), sys.argv[2])
    print(json.dumps(r, indent=1, ensure_ascii=False))
    sys.exit(0 if r["pass"] else 1)
