# Step 8. Previews and delivery

1. Low-res previews first (`ffmpeg -i final.mp4 -vf scale=-2:540 -c:v libx264 -crf 30 -c:a aac -b:a 96k preview.mp4`), all on one review page, never dozens of files in a chat.
2. Full quality only after the host approves.
3. Finals go into the right `Final/` folder with clear names: `<Person> - <title> - 9x16.mp4`.
4. Never delete: a replaced final moves to a backup folder first.
5. Captions for posting are optional, written with a human-sounding writing skill, never with invented facts.
6. Reusing old sessions (best-of reels, one person's compilation) is a short extra step built from clips that already passed Step 7.
