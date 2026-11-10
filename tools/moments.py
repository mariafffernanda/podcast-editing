"""Long video to social clips: candidate moments that start on a sentence's first word and end on a sentence's last.

It only proposes windows of the right length. Choosing which ones carry a hook, a point and an ending is the
plan's job (steps/4-content-plan.md and steps/long-video.md): read every candidate, keep the ones that stand alone.
usage: moments.py <words.json> [min_s] [max_s]     defaults 30 70 (social); stories 15 30; LinkedIn 30 60
"""
import json
import sys

from cutlist import sentences


def candidates(words: list[dict], min_s: float = 30, max_s: float = 70, max_gap: float = 5.0) -> list[dict]:
    S = sentences(words)
    out, i = [], 0
    while i < len(S):
        j, ok = i, False
        while j < len(S):
            if j > i and words[S[j][0]]["start"] - words[S[j - 1][1]]["end"] > max_gap:
                break                                   # a long break (a pause in the class, a cut) ends the moment
            dur = words[S[j][1]]["end"] - words[S[i][0]]["start"]
            if dur > max_s:
                break
            if dur >= min_s:
                ok = True
                break
            j += 1
        if ok:
            a, b = S[i][0], S[j][1]
            out.append({"i0": a, "i1": b, "start": words[a]["start"], "end": words[b]["end"],
                        "text": " ".join(w["w"].strip() for w in words[a:b + 1])})
            i = j + 1
        else:
            i += 1
    return out


if __name__ == "__main__":
    W = json.load(open(sys.argv[1]))
    lo = float(sys.argv[2]) if len(sys.argv) > 2 else 30
    hi = float(sys.argv[3]) if len(sys.argv) > 3 else 70
    for k, c in enumerate(candidates(W, lo, hi), 1):
        m = lambda t: f"{int(t) // 60}:{int(t) % 60:02d}"
        print(f"{k:3d}  {m(c['start'])}-{m(c['end'])}  {c['end'] - c['start']:.0f}s  {c['text'][:140]}")
