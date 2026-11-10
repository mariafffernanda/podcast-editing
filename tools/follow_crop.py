"""Long video to social clips: a steady vertical crop that follows one speaker who walks around.

The frame holds still while the speaker sways, and glides (never whips) when they really move.
A crop from horizontal 4K stays sharp; from 1080p it is a 1.8x enlargement, so film vertical or in 4K when you can.
usage: follow_crop.py <video> > Work/crop_path.json      (needs: pip install opencv-python)
Then: follow_crop.py cmds Work/crop_path.json > Work/crop.cmd
      ffmpeg -i in.mp4 -vf "sendcmd=f=Work/crop.cmd,crop=W:H:0:0" -c:a copy out.mp4
"""
import json
import sys

import numpy as np

DEAD_ZONE = 0.15        # share of the crop width the speaker can move without the frame following
MAX_SPEED_PX_S = 600    # at most this fast on 4K, so the move reads as a glide
ACCEL_PX_S2 = 1200


def crop_size(w: int, h: int, aspect: float = 9 / 16) -> tuple[int, int]:
    cw = int(round(h * aspect))
    return cw - cw % 2, h


def path(x: np.ndarray, frame_w: int, crop_w: int, fps: float) -> np.ndarray:
    """Per-frame left edge of the crop, from the speaker's centre x per frame (NaN when not found)."""
    x = np.asarray(x, dtype=float)
    valid = ~np.isnan(x)
    c = x[valid][0] if valid.any() else frame_w / 2
    lo, hi = crop_w / 2, frame_w - crop_w / 2
    c = min(max(c, lo), hi)
    dz, vmax, acc = DEAD_ZONE * crop_w, MAX_SPEED_PX_S / fps, ACCEL_PX_S2 / fps / fps
    v, moving, out = 0.0, False, np.empty(len(x))
    target = c
    for i, xi in enumerate(x):
        if not np.isnan(xi):
            target = min(max(xi, lo), hi)               # a lost face holds the last target
        d = target - c
        if not moving and abs(d) > dz:
            moving = True
        if moving and abs(d) < dz / 3:
            moving = False
        want = np.sign(d) * min(vmax, abs(d) * 0.08) if moving else 0.0
        v = v + np.clip(want - v, -acc, acc)
        v = float(np.clip(v, -vmax, vmax))
        c = min(max(c + v, lo), hi)
        out[i] = c - crop_w / 2
    return np.round(out, 3)


def sendcmd(x: np.ndarray, fps: float) -> str:
    """ffmpeg sendcmd lines that move the crop; a line only where the position changes."""
    lines, last = [], None
    for i, v in enumerate(x):
        v = int(round(v)) - int(round(v)) % 2
        if v != last:
            lines.append(f"{i / fps:.4f} crop x {v};")
            last = v
    return "\n".join(lines) + "\n"


def detect(video: str, every: int = 3) -> tuple[np.ndarray, int, int, float]:
    """The biggest face's centre x per frame (NaN when none), sampled every `every` frames and filled in between."""
    import cv2  # optional dependency
    cap = cv2.VideoCapture(video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    face = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    xs, i = [], 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        if i % every == 0:
            g = cv2.cvtColor(cv2.resize(f, (W // 4, H // 4)), cv2.COLOR_BGR2GRAY)
            fs = face.detectMultiScale(g, 1.1, 5, minSize=(24, 24))
            xs.append(float((max(fs, key=lambda r: r[2] * r[3])[0] + max(fs, key=lambda r: r[2] * r[3])[2] / 2) * 4) if len(fs) else np.nan)
        else:
            xs.append(xs[-1] if xs else np.nan)
        i += 1
    return np.array(xs), W, H, fps


if __name__ == "__main__" and sys.argv[1] == "cmds":
    d = json.load(open(sys.argv[2]))
    print(sendcmd(np.array(d["x"]), d["fps"]), end="")
elif __name__ == "__main__":
    xs, W, H, fps = detect(sys.argv[1])
    cw, ch = crop_size(W, H)
    print(json.dumps({"fps": fps, "crop_w": cw, "crop_h": ch, "x": path(xs, W, cw, fps).tolist()}))
