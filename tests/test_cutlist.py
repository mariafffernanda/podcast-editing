import cutlist

FPS = 30


def W(spec):
    """'word@start-end' tokens -> words list."""
    out = []
    for tok in spec.split():
        w, t = tok.split("@"); a, b = t.split("-")
        out.append({"w": w, "start": float(a), "end": float(b), "speaker": "A"})
    return out


def kept_text(words, pieces):
    return [w["w"] for w in words if any(p["in"] <= (w["start"] + w["end"]) / 2 <= p["out"] for p in pieces)]


def timeline_gap(pieces, t_prev_end, t_next_start):
    """Seconds of silence the viewer hears between two words after the cut."""
    total = 0.0
    for p in pieces:
        a, b = max(p["in"], t_prev_end), min(p["out"], t_next_start)
        total += max(b - a, 0)
    return total


def test_fillers_out():
    w = W("So@0.0-0.3 um@0.4-0.7 we@0.8-1.0 started.@1.0-1.5 Eh@1.6-1.9 bueno.@2.0-2.4")
    p = cutlist.keep_pieces(w, FPS, lang="en")
    assert kept_text(w, p) == ["So", "we", "started.", "bueno."]
    assert "eh" in cutlist.fillers("es")
    assert "este" not in cutlist.fillers("es") and "este" in cutlist.maybe_fillers("es")


def test_long_pause_shrinks_short_pause_stays():
    w = W("One.@0.0-0.5 Two@1.7-2.0 three@2.3-2.6 four.@2.6-3.0")
    p = cutlist.keep_pieces(w, FPS)
    g = timeline_gap(p, 0.5, 1.7)
    assert 0.2 <= g <= 0.45
    assert abs(timeline_gap(p, 2.0, 2.3) - 0.3) < 1 / FPS + 1e-9


def test_drop_takes_whole_sentence():
    w = W("Keep@0.0-0.3 this.@0.3-0.6 Private@1.0-1.4 stuff@1.4-1.8 here.@1.8-2.2 Back@2.5-2.8 again@2.8-3.1")
    p = cutlist.keep_pieces(w, FPS, drop=[(1.5, 1.9)])
    assert kept_text(w, p) == ["Keep", "this.", "Back", "again"]


def test_last_words_without_period_are_a_sentence():
    w = W("Hello@0.0-0.4 there.@0.4-0.8 and@1.0-1.2 then@1.2-1.5")
    assert cutlist.sentences(w) == [(0, 1), (2, 3)]


def test_frames_order_and_no_overlap():
    w = W("a@0.013-0.21 um@0.22-0.4 b@0.41-0.6 c.@1.9-2.27 d@2.28-2.5 um@2.51-2.6 e.@2.61-3.0")
    p = cutlist.keep_pieces(w, FPS)
    for x in p:
        assert x["in"] < x["out"]
        for t in (x["in"], x["out"]):
            assert abs(t * FPS - round(t * FPS)) < 1e-6
    for x, y in zip(p, p[1:]):
        assert x["out"] < y["in"]


def test_cut_never_inside_a_kept_word():
    w = W("a@0.0-0.5 um@0.5-0.6 b.@0.6-1.0")
    p = cutlist.keep_pieces(w, FPS)
    for x in p:
        for word in w:
            if word["w"] != "um":
                assert not (word["start"] < x["in"] < word["end"]) and not (word["start"] < x["out"] < word["end"])
