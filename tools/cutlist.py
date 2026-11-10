"""Step 5: what to keep, as pieces of the source timeline.

Words in: Work/words.json = [{"w", "start", "end", "speaker"}], ums included as their own words (found from the sound).
Pieces out: [{"in", "out"}] in source seconds, every edge on a whole video frame.

Rules built in:
- fillers (um, uh, eh, este, mmm...) come out;
- pauses over max_pause shrink to a natural `keep_pause` of silence;
- a dropped range takes its whole sentence with it, never half;
- cuts sit inside the silence around a word, never inside a kept word;
- edges snap to whole frames so the sound can never slide away from the picture.

usage: cutlist.py <words.json> <fps> [lang] [drop.json]   -> pieces JSON on stdout
"""
import json
import math
import re
import sys
import unicodedata

FILL = {
    "en": {"um", "umm", "uh", "uhh", "uhm", "er", "erm", "eh", "hmm", "mm", "mmm", "mhm", "ah"},
    "es": {"eh", "ehh", "em", "ehm", "mmm", "mm", "hmm", "ah", "mhm"},
}
# Real words that are only sometimes fillers ("este libro" is speech). Never cut automatically: list them for a human.
MAYBE = {"en": {"like", "so", "you know", "i mean"}, "es": {"este", "o sea", "bueno", "pues"}}
END = re.compile(r"[.?!…]+[\"')\]»]*$")


def fold(w: str) -> str:
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z']", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


def fillers(lang: str) -> set:
    """The language's fillers plus um and uh, which turn up in both languages."""
    return FILL.get(lang[:2], FILL["en"]) | {"um", "uh"}


def maybe_fillers(lang: str) -> set:
    return MAYBE.get(lang[:2], MAYBE["en"])


def sentences(words: list[dict]) -> list[tuple[int, int]]:
    out, i0 = [], 0
    for i, w in enumerate(words):
        if END.search(w["w"].strip()) or i == len(words) - 1:
            out.append((i0, i))
            i0 = i + 1
    return out


def keep_pieces(words: list[dict], fps: float, drop=(), lang: str = "en", max_pause: float = 0.45,
                keep_pause: float = 0.3, pad: float = 0.08) -> list[dict]:
    fl = fillers(lang)
    dropped = set()
    for i0, i1 in sentences(words):
        if any(words[k]["start"] < b and words[k]["end"] > a for k in range(i0, i1 + 1) for a, b in drop):
            dropped.update(range(i0, i1 + 1))
    keep = [k for k, w in enumerate(words) if k not in dropped and fold(w["w"]) not in fl]
    if not keep:
        return []
    groups, cur = [], [keep[0]]
    for a, b in zip(keep, keep[1:]):
        gap = words[b]["start"] - words[a]["end"]
        if b == a + 1 and gap <= max_pause:
            cur.append(b)
        else:
            groups.append(cur)
            cur = [b]
    groups.append(cur)

    def room_after(k):  # silence after word k before the next word (kept or not)
        nxt = words[k + 1]["start"] if k + 1 < len(words) else words[k]["end"] + pad
        return max(nxt - words[k]["end"], 0)

    def room_before(k):
        prv = words[k - 1]["end"] if k > 0 else max(words[k]["start"] - pad, 0)
        return max(words[k]["start"] - prv, 0)

    pieces = []
    for g in groups:
        a, b = g[0], g[-1]
        lead = min(pad, room_before(a) / 2) if a > 0 and words[a - 1]["end"] <= words[a]["start"] and (a - 1) in keep else min(pad, room_before(a))
        tail = min(pad, room_after(b))
        # a long pause kept on both sides of a cut: leave keep_pause of it in total
        if (b + 1) in keep and words[b + 1]["start"] - words[b]["end"] > max_pause:
            tail = keep_pause / 2
        if (a - 1) in keep and words[a]["start"] - words[a - 1]["end"] > max_pause:
            lead = keep_pause / 2
        t_in = math.floor((words[a]["start"] - lead) * fps + 1e-9) / fps
        t_out = math.ceil((words[b]["end"] + tail) * fps - 1e-9) / fps
        t_in = max(t_in, 0.0)
        if pieces and t_in <= pieces[-1]["out"]:
            pieces[-1]["out"] = max(pieces[-1]["out"], t_out)
        else:
            pieces.append({"in": t_in, "out": t_out})
    return [p for p in pieces if p["out"] > p["in"]]


if __name__ == "__main__":
    W = json.load(open(sys.argv[1]))
    fps = float(sys.argv[2])
    lang = sys.argv[3] if len(sys.argv) > 3 else "en"
    drop = [tuple(x) for x in json.load(open(sys.argv[4]))] if len(sys.argv) > 4 else ()
    print(json.dumps({"fps": fps, "pieces": keep_pieces(W, fps, drop, lang)}, indent=1))
