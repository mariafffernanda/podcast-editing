# Long video to social clips

For a class, a talk, a workshop, a webinar or a live session: one long recording turned into social clips with the same intention as the podcast. Every clip gives one piece of value, opens on a hook, keeps the point and ends on a real line.

It reuses the podcast steps and changes only what a single camera and a teacher need. Do the steps in this order.

## 1. Organize (Step 1, as written)

Same session folder, same checksum copies. Put the camera files in `Raw/Cameras`, a wireless mic's own recording in `Raw/Audio`, and slides or a screen recording in `Raw/Screen`.

Gimbal and action cameras (an Osmo, a phone, a GoPro) split long recordings into several files. Join them in order before anything else, and check the joined length equals the sum of the parts:

```
for f in Raw/Cameras/*.MP4; do echo "file '$PWD/$f'"; done > Work/parts.txt
ffmpeg -f concat -safe 0 -i Work/parts.txt -c copy Work/full.mp4
```

## 2. Sound

- Best: the wireless mic's own internal recording (many clip-on mics, DJI ones included, record a backup on the transmitter). Line it up with the camera using `tools/audio.py drift`, as in Step 2.
- Next: the camera's track when the wireless mic fed into it.
- Only when nothing else exists: the camera's built-in mic. Here camera audio is allowed, because it is the only source; say so in the report and keep the processing light.
- Questions from the room are usually faint. Keep a question only if it can be understood at normal volume after a gentle lift; otherwise the teacher's answer stands alone, or opens with them repeating the question.
- Same targets: -14 LUFS, peaks under -1.5 dB, no jump over 3 dB at a join.

## 3. Transcript (Step 3, as written)

One speaker usually, so speaker labels are simple. Label audience voices as "Room".

## 4. Find the moments

```
python3 tools/moments.py Work/words.json 30 70     # social clips
python3 tools/moments.py Work/words.json 30 60     # LinkedIn
python3 tools/moments.py Work/words.json 15 30     # stories
```

It lists windows that start on a sentence's first word and end on a sentence's last, and never run across a long break. Read them all and keep the ones that stand alone. A class has more of these than a podcast:

- a definition or a framework said in one breath;
- a mistake people make, and the fix;
- a story from the teacher's own life;
- a strong opinion or a line that sounds like a quote;
- a question from the room that many people would ask, with its answer;
- an exercise someone can try today.

Rules on top of the Step 4 story rules:

- **Context in one line.** A teaching moment sometimes needs a setup to make sense. Keep at most one sentence of setup, and only if the hook still lands in the first 3 seconds; otherwise start later.
- **No "as I said before".** A clip that leans on something said earlier in the class doesn't stand alone. Drop it or find a moment that explains itself.
- **Slides.** If the point depends on a slide, the clip shows the slide (see 6). If it can't, pick another moment.
- **The CTA.** Classes often have no spoken ask. Look for one anywhere in the recording ("follow me", "join the next class", "write to me"); if there is none, end on the strongest line and say so in the plan. Never invent one.
- **Many clips from one class.** Go through it topic by topic. One class of an hour often gives 15 to 30 clips; quality first, never a clip just to fill a number.

## 5. Cutting (Step 5, as written)

Full sentences, no ums, no rough cuts, whole frames. `tools/cutlist.py` and `tools/joincheck.py` work the same.

## 6. Framing with one camera

This replaces Step 6's camera rules, because there is no second camera to cut to.

- **Filmed vertical:** use the frame as it is, with normal headroom.
- **Filmed horizontal:** crop a vertical frame that follows the teacher:

  ```
  pip install opencv-python
  python3 tools/follow_crop.py Work/full.mp4 > Work/crop_path.json
  python3 tools/follow_crop.py cmds Work/crop_path.json > Work/crop.cmd
  ffmpeg -i Work/full.mp4 -vf "sendcmd=f=Work/crop.cmd,crop=1214:2160:0:0,scale=1080:1920" -c:a copy Work/vertical.mp4
  ```

  The frame holds still while the teacher sways and glides when they really walk. From 4K the crop stays sharp. From 1080p it is a 1.8x enlargement and looks soft, so for classes film in 4K or vertical.
- **Jump cuts on one camera:** alternate between exactly two framings, the normal one and a slightly closer one (about 1.2x), so a cut never jumps on the same frame. Never more than two framings, never a zoom that moves, never the closer framing twice in a row. Where a slide or a screen recording fits, cut to it instead.
- **Slides:** show the slide full screen while the teacher talks over it, or slide on top and teacher below in vertical. Never shrink a slide so small it can't be read on a phone.
- **Zooms:** the same rule as Step 6. Only on a line that matters, about one a minute at most.

## 7 and 8. Final check and delivery (as written)

Every clip passes `tools/qa.py` and the join check before a human sees it. Low-res previews on one review page, full quality after approval, finals in `Final/3 Social clips`, `Final/5 LinkedIn` and `Final/6 Stories`. Captions burned in from the SRT (`steps/captions.md`); for classes they matter even more, because many people watch without sound.
