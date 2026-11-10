# Captions

- Simplest style: a few words at a time, following the speech, in the session's language, taken from the checked transcript.
- Fonts from Google Fonts only, so anyone can use and share them. `tools/captions.py` lists the styles (`clean`, `bold`, `poster`, `soft`): font, size, colour and a position clear of the app buttons. Install the font from fonts.google.com first.
- Make a sample sheet: burn each style onto a 3-second piece of the session and put the stills side by side, so the user picks by eye.
- Captions stay editable: a plain caption file (SRT) sits next to each video, so a typo gets fixed in the text, not the video. Burned-in captions are made from that file.

```
python3 tools/captions.py srt  Work/words.json Work/pieces/<video>.json > "<video>.srt"
python3 tools/captions.py burn "<video>.mp4" "<video>.srt" clean "<video> - captions.mp4"
```

If ffmpeg can't draw captions, `captions.py` says so and names the fix (`brew install ffmpeg`).
