# Step 3. Transcript

- Transcribe locally for free with Whisper (`faster-whisper`, model `large-v3`). A paid service with the user's own key is an option and often gets names right more often. Check its data and training settings before sending a guest's voice.
- Line up every word with the audio (forced alignment, for example WhisperX). Transcribers place word starts late, and late starts make cuts clip the front of words.
- Save `Work/words.json`: `[{"w": "Hello", "start": 12.31, "end": 12.58, "speaker": "Host"}, ...]` in recorder time. Ums are their own words in this list.
- Speakers come from the mic tracks (the mic that's 6 dB louder wins, from `audio.py`), then get checked by eye on camera. Voice matching alone swaps people.
- Find ums from the sound itself: transcribers leave them out of the text and stretch the words around them. Listen to (or re-transcribe with a filler-friendly prompt) every gap longer than a word that the text says is empty.
- Write a clean transcript with names and times (`Final/Transcript.txt`). It's a gift for the guest and the map for the edit.
- Mark what must never be used in `Work/never.json` as `[[start, end, "reason"], ...]`: private talk, crew talk, someone's employer, anything a guest asked to keep out. Step 5 drops these whole sentences.
