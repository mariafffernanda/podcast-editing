# Step 1. Organize the files from the card

One folder per session, always the same shape:

```
<date> <guest + topic>/
  Raw/Cameras/   one file per camera, named by seat (CAM 1 host, CAM 2 guest, CAM 3 wide)
  Raw/Audio/     the recorder's files, untouched
  Work/          transcript, word times, camera map, sync, plans, check reports
  Review/        the latest low-res previews only
  Final/
    1 Episode/  2 Spicy cut/  3 Social clips/<Person>/  4 Team social clips/  5 LinkedIn/  6 Stories/
    Transcript.txt
```

```
python3 tools/organize.py new  "<session>"
python3 tools/organize.py copy /Volumes/<card>/<cameras> "<session>/Raw/Cameras" "<session>"
python3 tools/organize.py copy /Volumes/<card>/<audio>   "<session>/Raw/Audio"   "<session>"
```

- Every copy is checked against the original with a checksum, not just its size. Copies can come out the right size and still be broken.
- Never erase the card until every file is checked in two places (the session folder and a backup). Erasing a drive that held the only copy of the work files has cost finished edits.
- Work files live beside the footage, never in a temporary folder that a restart wipes.
- Map the cameras in `Work/cameras.json`: which seat each one sees, which are dead or out of focus, and where framing changes (people move, seats change). Check one still per camera every few minutes.
- One heavy job at a time. Several renders at once can run the computer out of memory.
