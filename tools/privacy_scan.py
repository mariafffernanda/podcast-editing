"""Find private names (guests, clients, places) before anything is pushed.

usage: privacy_scan.py <root> --names <file kept OUTSIDE the repo, one name per line>
Exit code 1 when a name is found. Case and accents are ignored.
"""
import argparse
import sys
import unicodedata
from pathlib import Path

SKIP = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache"}


def fold(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def scan(root: Path, names: list[str]) -> list[tuple[str, int, str]]:
    keys = [(n, fold(n)) for n in names if n.strip()]
    hits = []
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if not p.is_file() or any(part in SKIP for part in rel.parts):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for i, line in enumerate(text.splitlines(), 1):
            f = fold(line)
            hits += [(str(rel), i, n) for n, k in keys if k in f]
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--names", type=Path, required=True)
    a = ap.parse_args()
    hits = scan(a.root, a.names.read_text(encoding="utf-8").splitlines())
    for f, line, _ in hits:
        print(f"{f}:{line}: private name")  # the name itself is never printed
    print(f"{len(hits)} hit(s)")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
