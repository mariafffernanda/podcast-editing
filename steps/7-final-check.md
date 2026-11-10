# Step 7. Final check

Nothing reaches a human until every line passes. Each piece gets a report card in `Work/checks/<video>.json`.

```
python3 tools/qa.py "Final/3 Social clips/<Person>/<file>.mp4" social
```

`qa.py` covers decoding, length, loudness and peaks. The rest of the card is filled in from the steps below.

**What the engine actually used** (top of every report)

- the audio for every second: which file, which track, whose mic;
- which mics were open or turned down during each speaker's turn;
- which camera and which crop for each shot;
- which plan version and which tools made it;
- the bitrate and size of the final, always rendered from the original camera files (smaller working copies look soft).

**Sound**

- No breathing or noise from another mic under a speaker: measure each closed mic's level during every turn.
- Level -14 LUFS (within 1 LU), peaks under -1.5 dB, no jumps over 3 dB at joins.
- Sync: lips and sound within 40 ms everywhere. Measure it with `audio.py drift` between the finished file's sound and the camera's own sound, in windows across the whole piece.

**Words**

- Transcribe the finished video and compare it word by word to the plan: 0 lost words, 0 clipped words.
- List any um or pause left over.
- A reviewer reads the finished text as a viewer: does the hook stop the scroll, does the setup get its payoff, is the CTA real and spoken.

**Picture**

- At every speaker change, the new speaker is on screen within 0.2 s; report the total seconds the talker is hidden.
- No jump cut on the same camera and crop, no repeated zooms.
- A contact sheet (one frame per shot) checked for framing, headroom, empty chairs and stray body parts.

**File**

- Decodes with 0 errors; length inside the format's limits.

**Every check is tested on a known failure first.** Shift a file 120 ms and make sure the sync check catches it; feed `qa.py` a broken file and make sure it fails. A checker once "passed" vertical videos because it couldn't read them.
