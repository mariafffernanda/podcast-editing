import numpy as np
import follow_crop


def test_crop_size_for_vertical_from_4k():
    assert follow_crop.crop_size(3840, 2160) == (1214, 2160)   # even width, full height


def test_steady_inside_dead_zone():
    x = 1920 + np.random.default_rng(0).normal(0, 20, 300)       # small sway around the centre
    path = follow_crop.path(x, frame_w=3840, crop_w=1214, fps=30)
    assert np.ptp(path) == 0                                     # the frame does not move at all


def test_follows_a_walk_smoothly_and_stays_inside():
    x = np.concatenate([np.full(90, 1000.0), np.linspace(1000, 3000, 120), np.full(90, 3000.0)])
    p = follow_crop.path(x, frame_w=3840, crop_w=1214, fps=30)
    assert p.min() >= 0 and p.max() <= 3840 - 1214
    assert abs((p[-1] + 1214 / 2) - 3000) < 1214 / 4             # ends with the speaker framed
    assert np.abs(np.diff(p)).max() <= follow_crop.MAX_SPEED_PX_S / 30 + 1e-6   # never whips


def test_missing_detections_hold_the_frame():
    x = np.full(100, 2500.0); x[40:60] = np.nan                  # face lost for 20 frames
    p = follow_crop.path(x, frame_w=3840, crop_w=1214, fps=30)
    assert np.ptp(p[35:65]) == 0


def test_sendcmd_only_on_change_and_even():
    s = follow_crop.sendcmd(np.array([100.0, 100.2, 101.0, 103.0]), fps=25)
    assert s.splitlines() == ["0.0000 crop x 100;", "0.1200 crop x 102;"]
