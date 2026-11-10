"""Step 1: one folder per session, and copies from the card checked by checksum.

usage:
  organize.py new  <session folder>
  organize.py copy <card folder> <session>/Raw/Cameras|Raw/Audio <session>
Never deletes anything. Erase the card yourself, only after every file is checked in two places.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

LAYOUT = ["Raw/Cameras", "Raw/Audio", "Work", "Review",
          "Final/1 Episode", "Final/2 Spicy cut", "Final/3 Social clips",
          "Final/4 Team social clips", "Final/5 LinkedIn", "Final/6 Stories"]


def make_session(root: Path) -> Path:
    for d in LAYOUT:
        (root / d).mkdir(parents=True, exist_ok=True)
    return root


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _copy(a: Path, b: Path) -> None:
    shutil.copyfile(a, b)


def copy_verified(src: Path, dst: Path) -> list[dict]:
    """Copy every file in src to dst and compare whole-file checksums, never only sizes."""
    dst.mkdir(parents=True, exist_ok=True)
    out = []
    for f in sorted(p for p in src.iterdir() if p.is_file() and not p.name.startswith(".")):
        t = dst / f.name
        _copy(f, t)
        a, b = sha256(f), sha256(t)
        out.append({"file": f.name, "sha256": a, "bytes": f.stat().st_size, "ok": a == b})
    return out


def intake(src: Path, dst: Path, session: Path) -> list[dict]:
    rep = copy_verified(src, dst)
    p = session / "Work/copy_report.json"
    old = json.loads(p.read_text()) if p.exists() else []
    p.write_text(json.dumps(old + rep, indent=1))
    return rep


if __name__ == "__main__":
    if sys.argv[1] == "new":
        print(make_session(Path(sys.argv[2])))
    elif sys.argv[1] == "copy":
        r = intake(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
        bad = [x["file"] for x in r if not x["ok"]]
        print(f"{len(r)} copied, {len(bad)} failed" + (": " + ", ".join(bad) if bad else ""))
        sys.exit(1 if bad else 0)
