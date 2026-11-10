# Timeline for DaVinci and other editors

- Every piece also comes out as a timeline file (FCPXML 1.10) pointing at the original camera files, with each cut and camera change already in place.
- DaVinci Resolve, Premiere Pro and Final Cut open it, so a person can nudge a cut, swap a camera or add music, then render themselves.
- CapCut doesn't import timeline files. CapCut users get the finished video plus the caption file.

```
python3 tools/timeline.py Work/pieces/<video>.json Work/sources.json 30 "<video>" > "<video>.fcpxml"
```

`Work/sources.json`: `{"CAM1": {"path": "/abs/path/CAM 1.mp4", "duration": 3600, "width": 1920, "height": 1080}, ...}`. Each piece names its camera with `"cam"`. Add the recorder's mic tracks in the editor and line them up with the offset from Step 2.
