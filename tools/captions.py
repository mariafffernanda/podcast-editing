"""Captions: an editable SRT next to every video, and burned-in captions made from that SRT.

Fix a typo in the .srt, never in the video. Fonts come from Google Fonts only, so anyone can use them.
usage:
  captions.py srt  <words.json> <pieces.json> > piece.srt     (words in source time, remapped to the finished piece)
  captions.py burn <video> <srt> <style> <out>
"""
import json
import subprocess
import sys
from pathlib import Path

GOOGLE_FONTS = {"Montserrat", "Inter", "Poppins", "Bebas Neue", "Roboto", "Lato"}
# Simplest styles first. Position is kept clear of the app buttons at the bottom of vertical videos.
STYLES = {
    "clean":   {"font": "Inter", "size": 14, "color": "&H00FFFFFF", "outline": 1, "bold": 1, "margin_v": 90},
    "bold":    {"font": "Montserrat", "size": 16, "color": "&H00FFFFFF", "outline": 2, "bold": 1, "margin_v": 90},
    "poster":  {"font": "Bebas Neue", "size": 20, "color": "&H00FFFFFF", "outline": 2, "bold": 0, "margin_v": 110},
    "soft":    {"font": "Poppins", "size": 14, "color": "&H00F0F0F0", "outline": 1, "bold": 0, "margin_v": 90},
}


class CaptionFilterMissing(RuntimeError):
    pass


def _ts(t: float) -> str:
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def remap(words: list[dict], pieces: list[dict]) -> list[dict]:
    """Source-time words -> finished-piece time. Words outside every piece are dropped."""
    out, acc = [], 0.0
    for p in pieces:
        for w in words:
            mid = (w["start"] + w["end"]) / 2
            if p["in"] <= mid < p["out"]:
                out.append({**w, "start": acc + max(w["start"], p["in"]) - p["in"], "end": acc + min(w["end"], p["out"]) - p["in"]})
        acc += p["out"] - p["in"]
    return out


def to_srt(words: list[dict], max_words: int = 4, max_gap: float = 0.6) -> str:
    groups, cur = [], []
    for w in words:
        if cur and (len(cur) >= max_words or w["start"] - cur[-1]["end"] > max_gap):
            groups.append(cur); cur = []
        cur.append(w)
        if w["w"].rstrip().endswith((".", "?", "!", "…")):
            groups.append(cur); cur = []
    if cur:
        groups.append(cur)
    return "".join(f"{i}\n{_ts(g[0]['start'])} --> {_ts(g[-1]['end'])}\n{' '.join(x['w'].strip() for x in g)}\n\n"
                   for i, g in enumerate(groups, 1))


def has_subtitles_filter() -> bool:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True)
    return any(l.split()[1:2] == ["subtitles"] for l in r.stdout.splitlines() if len(l.split()) > 1)


def burn(video: Path, srt: Path, style: dict, out: Path) -> None:
    if not has_subtitles_filter():
        raise CaptionFilterMissing("This ffmpeg can't draw captions (no libass). On a Mac: brew install ffmpeg. "
                                   "Then install the font from fonts.google.com.")
    force = (f"FontName={style['font']},FontSize={style['size']},PrimaryColour={style['color']},"
             f"Outline={style['outline']},Bold={style['bold']},MarginV={style['margin_v']},Alignment=2")
    esc = str(srt).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vf", f"subtitles='{esc}':force_style='{force}'",
                    "-c:a", "copy", str(out)], check=True)


if __name__ == "__main__":
    if sys.argv[1] == "srt":
        p = json.load(open(sys.argv[3]))
        print(to_srt(remap(json.load(open(sys.argv[2])), p["pieces"] if isinstance(p, dict) else p)), end="")
    elif sys.argv[1] == "burn":
        burn(Path(sys.argv[2]), Path(sys.argv[3]), STYLES[sys.argv[4]], Path(sys.argv[5]))
