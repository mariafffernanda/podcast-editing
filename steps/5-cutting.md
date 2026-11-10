# Step 5. Cutting

```
python3 tools/cutlist.py Work/words.json 30 en Work/never.json > Work/pieces/<video>.json
```

`cutlist.py` turns the words you chose for a video into pieces of the source, with these rules built in. Pass only the words of that video's moments (from the plan); it handles the inside.

- Ums, "eh" and "mmm" come out, found from the sound, not the text. Words that are only sometimes fillers ("like", "so", "este", "o sea", "bueno") are never cut automatically: list them for a human.
- Pauses over about 0.45 s shrink to a natural 0.3 s, only where the sound confirms silence. Emotional pauses can stay (take them out of the automatic pass by hand).
- Retakes: keep the last complete take of each line.
- Every sentence whole and said once. Never clip the start or end of a word; let the last syllable fade.
- Cut at the quietest point inside a real silence, never inside a word.
- Careful with automatic repeat removal: "with Ana. Ana was born" is real speech, not a stutter. A word that ends a sentence is never a false start.
- Never trim the gap before a number; word timing for numbers is often wrong.
- Bleep swear words if the show asks for it.
- Join pieces on whole video frames, so the sound never slides away from the picture. Joining exact-length sound pieces once drifted 120 ms and the lips stopped matching.

## No rough cuts

Rough cuts are the error that comes up most: a join you can hear (a click, a breath chopped in half, a word that starts too hard, the room sound dropping out) or see (a jump on the same frame). Every join is a place to check.

**Full sentences first.** A cut that drops content only happens after a complete sentence (taking out an um or a pause inside a sentence keeps every word of it). The sentence before the cut is said in full, from its first word to its last, and the piece after the cut starts on a new sentence's first word. A cut never lands mid-sentence or between a setup and its point. If a sentence can't be kept whole, the whole sentence goes, never half of it. The join check reads both sides of every cut and fails any join where a sentence is left unfinished.

1. Sound joins get a tiny crossfade (10 to 20 ms, ffmpeg `acrossfade=d=0.015`), so there's never a click. The picture still cuts clean.
2. The cut lands inside a real silence, never at its edge, leaving a natural breath of space before the next word.
3. A breath stays or goes whole, never half.
4. Where a pause is shortened, the quiet room sound underneath stays continuous, so the background never drops out.
5. When a thought continues across a cut, the sound can lead the picture by a few frames, which hides the join.
6. Join check: render the finished sound, then

   ```
   python3 tools/joincheck.py Work/<video>.wav Work/joins/<video>.json
   ```

   It fails a join on a level jump over 3 dB or a click. Also read each join back with Whisper (2 s either side) and compare with the planned words: a missing or half word fails. A join that fails is moved or fixed before the full render.
7. The 10 riskiest joins of each piece go in its report, with times, for a human to listen to.
