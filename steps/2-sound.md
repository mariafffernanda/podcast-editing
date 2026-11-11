# Step 2. Sound: one mic per person

- Use the recorder's own per-mic tracks (one file with many tracks, like a RØDECaster, or one file per mic). Never camera audio: it sounds "inside a box". Never the quiet mic copy a video switcher saves.
- Work out which track is whose by measuring, not by guessing. A person's own mic reads about 18 dB above the bleed from the others, and a window counts as theirs only when their mic is at least 6 dB louder than every other.

```
python3 tools/audio.py map "<session>/Raw/Audio/<file>.wav"
```

- Line the recorder up with each camera at 8 or more points across the session, measure the slow drift between them and correct it, then confirm it holds within a few milliseconds from start to end:

```
ffmpeg -i "Raw/Cameras/CAM 1.mp4" -vn -ac 1 -ar 16000 Work/cam1.wav
python3 tools/audio.py drift Work/cam1.wav "Raw/Audio/<file>.wav" --track 1
```

  `worst_fit_ms` should be under 5. If it isn't, a camera stopped or skipped: split the session at that point and sync each part.
- Sync against the cleanest copy of the sound on the camera clock. A video switcher that records its own copy of the recorder's feed (an ATEM's `MIC 1.wav`) is ideal: it shares the cameras' clock and has no room echo. A camera's built-in mic across the room makes the readings wobble by about 10 ms and can push `worst_fit_ms` past 30 even when nothing is wrong. Before splitting a session, check again with more points (`offsets(..., points=40)`) against the cleaner copy.
- Each speaker's voice comes from their own mic, and while they talk the other mics are turned down or muted. No breathing, "mm-hmm" or chair noise under the speaker. A listener's mic opens only for a reaction chosen on purpose, like a laugh.
- Light processing: a low cut and gentle compression, no heavy noise removal. Final level -14 LUFS, peaks under -1.5 dB, no jump over 3 dB where two pieces meet.
- If a mic track is missing or silent, `audio.py` stops with `MissingTrack`. Stop and ask. Never fall back to camera audio quietly.
