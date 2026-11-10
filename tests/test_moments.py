import moments


def talk(n_sent, words_per=8, wdur=0.3, gap=0.6):
    """n_sent sentences; each word wdur long, sentences separated by gap."""
    out, t = [], 0.0
    for s in range(n_sent):
        for k in range(words_per):
            w = f"s{s}w{k}" + ("." if k == words_per - 1 else "")
            out.append({"w": w, "start": t, "end": t + wdur - 0.02, "speaker": "A"})
            t += wdur
        t += gap
    return out


def test_windows_start_and_end_on_sentences():
    w = talk(40)                                      # each sentence 2.4 s + 0.6 s gap = 3 s
    c = moments.candidates(w, min_s=30, max_s=70)
    assert c
    for x in c:
        assert w[x["i0"]]["w"].endswith("w0")          # first word of a sentence
        assert w[x["i1"]]["w"].endswith(".")           # last word of a sentence
        assert 30 <= x["end"] - x["start"] <= 70


def test_windows_do_not_overlap():
    c = moments.candidates(talk(60), min_s=30, max_s=70)
    for a, b in zip(c, c[1:]):
        assert a["i1"] < b["i0"]


def test_long_silence_breaks_a_window():
    w = talk(30)
    for x in w[80:]:                                  # a 20 s break after sentence 10 (a break in the class)
        x["start"] += 20; x["end"] += 20
    for x in moments.candidates(w, min_s=20, max_s=70, max_gap=5):
        assert not (x["i0"] < 80 <= x["i1"])


def test_story_lengths():
    c = moments.candidates(talk(40), min_s=15, max_s=30)
    assert all(15 <= x["end"] - x["start"] <= 30 for x in c)
