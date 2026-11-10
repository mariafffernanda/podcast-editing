import xml.etree.ElementTree as ET
from fractions import Fraction
import pytest
import captions
import timeline


def words(n, step=0.3):
    return [{"w": f"w{i}" + ("." if i == 5 else ""), "start": i * step, "end": i * step + 0.25} for i in range(n)]


def test_srt_numbered_timed_and_short():
    s = captions.to_srt(words(10), max_words=4)
    blocks = s.strip().split("\n\n")
    assert blocks[0].splitlines()[0] == "1"
    assert blocks[0].splitlines()[1] == "00:00:00,000 --> 00:00:01,150"
    assert all(len(b.splitlines()[2].split()) <= 4 for b in blocks)
    assert blocks[1].splitlines()[2].endswith("w5.")   # a sentence end closes the caption


def test_remap_to_finished_time():
    pieces = [{"in": 0.0, "out": 1.0}, {"in": 3.0, "out": 4.0}]
    w = [{"w": "a", "start": 0.2, "end": 0.5}, {"w": "gone", "start": 2.0, "end": 2.3}, {"w": "b", "start": 3.1, "end": 3.4}]
    r = captions.remap(w, pieces)
    assert [x["w"] for x in r] == ["a", "b"]
    assert r[1]["start"] == pytest.approx(1.1)


def test_burn_explains_missing_filter(monkeypatch, tmp_path):
    monkeypatch.setattr(captions, "has_subtitles_filter", lambda: False)
    with pytest.raises(captions.CaptionFilterMissing, match="brew install ffmpeg"):
        captions.burn(tmp_path / "v.mp4", tmp_path / "v.srt", captions.STYLES["clean"], tmp_path / "o.mp4")


def test_styles_use_google_fonts():
    for s in captions.STYLES.values():
        assert s["font"] in captions.GOOGLE_FONTS


def test_fcpxml_clips_and_offsets():
    pieces = [{"in": 1.0, "out": 2.5, "cam": "CAM1"}, {"in": 4.0, "out": 5.0, "cam": "CAM2"}, {"in": 6.0, "out": 6.5, "cam": "CAM1"}]
    src = {"CAM1": {"path": "/x/CAM1.mp4", "duration": 100}, "CAM2": {"path": "/x/CAM2.mp4", "duration": 100}}
    x = timeline.fcpxml(pieces, src, fps=30, name="Test")
    root = ET.fromstring(x)
    assert root.tag == "fcpxml" and root.get("version") == "1.10"
    clips = root.findall(".//spine/asset-clip")
    assert len(clips) == 3
    t = Fraction(0)
    for c, p in zip(clips, pieces):
        assert Fraction(c.get("offset")[:-1]) == t
        t += Fraction(c.get("duration")[:-1])
    assert t == Fraction(3)
    assert len(root.findall(".//resources/asset")) == 2
