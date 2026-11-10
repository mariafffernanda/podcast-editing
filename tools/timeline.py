"""A timeline file (FCPXML 1.10) for DaVinci Resolve, Premiere Pro and Final Cut.

It points at the original camera files with every cut and camera change in place, so a person can nudge a cut,
swap a camera or add music, then render themselves. CapCut users get the finished video plus the .srt instead.
usage: timeline.py <pieces.json> <sources.json> <fps> <name> > piece.fcpxml
  pieces:  [{"in", "out", "cam"}] in source seconds
  sources: {"CAM1": {"path": "/abs/CAM1.mp4", "duration": 3600, "width": 1920, "height": 1080}}
"""
import json
import sys
from fractions import Fraction
from pathlib import Path
from xml.sax.saxutils import quoteattr


def _frame(fps) -> Fraction:
    f = Fraction(str(fps))
    return Fraction(1001, 30000) if abs(float(f) - 29.97) < 0.01 else (Fraction(1001, 60000) if abs(float(f) - 59.94) < 0.01 else 1 / f)


def _t(frames: int, fd: Fraction) -> str:
    v = frames * fd
    return f"{v.numerator}/{v.denominator}s" if v.denominator != 1 else f"{v.numerator}s"


def fcpxml(pieces: list[dict], sources: dict, fps=30, name: str = "Edit") -> str:
    fd = _frame(fps)
    fr = lambda s: int(round(Fraction(str(s)) / fd))
    first = next(iter(sources.values()))
    w, h = first.get("width", 1920), first.get("height", 1080)
    ids = {k: f"a{i + 1}" for i, k in enumerate(sources)}
    res = [f'<format id="r1" frameDuration="{_t(1, fd)}" width="{w}" height="{h}"/>']
    for k, s in sources.items():
        uri = Path(s["path"]).absolute().as_uri()
        res.append(f'<asset id="{ids[k]}" name={quoteattr(k)} start="0s" duration="{_t(fr(s["duration"]), fd)}" '
                   f'hasVideo="1" hasAudio="1" format="r1"><media-rep kind="original-media" src={quoteattr(uri)}/></asset>')
    spine, at = [], 0
    for p in pieces:
        cam = p.get("cam") or next(iter(sources))
        a, b = fr(p["in"]), fr(p["out"])
        spine.append(f'<asset-clip ref="{ids[cam]}" name={quoteattr(cam)} offset="{_t(at, fd)}" start="{_t(a, fd)}" '
                     f'duration="{_t(b - a, fd)}" format="r1"/>')
        at += b - a
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE fcpxml>\n<fcpxml version="1.10"><resources>' + "".join(res) +
            f'</resources><library><event name={quoteattr(name)}><project name={quoteattr(name)}>'
            f'<sequence format="r1" duration="{_t(at, fd)}" tcStart="0s" tcFormat="NDF"><spine>' + "".join(spine) +
            "</spine></sequence></project></event></library></fcpxml>\n")


if __name__ == "__main__":
    p = json.load(open(sys.argv[1]))
    print(fcpxml(p["pieces"] if isinstance(p, dict) else p, json.load(open(sys.argv[2])), sys.argv[3], sys.argv[4]), end="")
