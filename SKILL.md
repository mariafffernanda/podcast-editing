---
name: podcast-editing
description: Use when editing a video podcast recorded on several cameras and a multitrack recorder, or turning a long video (a class, talk, workshop or webinar, often one camera like an Osmo or a phone) into short social clips - from the memory card to finished, checked videos - organizing files, sound, transcript, content plan, cutting without rough cuts, camera choice and framing, final checks, previews, captions, editor timelines and a private guest gallery. Works in English and Spanish.
---

# Podcast editing

Takes a video podcast from the card to an episode, a spicy cut, social clips per person, team social clips, LinkedIn clips, stories and a transcript. Every rule here comes from a mistake made on real sessions (see `lessons.md`).

**Before anything:** if `~/.claude/podcast-profile.md` exists, read it. It holds this user's own folders, names, style and delivery, and it wins over the defaults here. With a profile, "activate my podcast skill" starts at Step 1 without a round of questions. Without one, ask only what the steps below cannot find out by themselves (copy `profile.example.md` to start one).

**Language:** read the session's language from the transcript and work in it (fillers, CTAs, captions, reports). Talk to the user in their language. In a bilingual session each piece follows the language spoken in it. See `steps/language.md`.

## Which kind of video

| You have | Follow |
|---|---|
| A podcast or interview on several cameras with one mic per person | the steps below, in order |
| A class, talk, workshop or webinar, usually one camera (an Osmo, a phone), to turn into social clips | `steps/long-video.md`: it reuses these steps and changes sound, finding moments and one-camera framing |

## The steps, in order

| Step | File | Tool | Writes |
|---|---|---|---|
| 1. Organize the card | `steps/1-organize.md` | `tools/organize.py` | session folders, `Work/copy_report.json` |
| 2. Sound, one mic per person | `steps/2-sound.md` | `tools/audio.py` | mic map, sync and drift |
| 3. Transcript | `steps/3-transcript.md` | Whisper + aligner | `Work/words.json`, clean transcript |
| 4. Content plan | `steps/4-content-plan.md` | (reading and judgement) | `Work/plan.md` |
| 5. Cutting, no rough cuts | `steps/5-cutting.md` | `tools/cutlist.py`, `tools/joincheck.py` | pieces per video |
| 6. Cameras and framing | `steps/6-cameras.md` | (plan per shot) | camera and crop per piece |
| 7. Final check | `steps/7-final-check.md` | `tools/qa.py`, `tools/joincheck.py` | `Work/checks/<video>.json` |
| 8. Previews and delivery | `steps/8-delivery.md` | ffmpeg | `Review/`, `Final/` |
| 9. Gallery, cloud, storage | `steps/9-gallery-cloud-storage.md` | `gallery/` | guest pages |

Also: `steps/captions.md` (`tools/captions.py`), `steps/timeline.md` (`tools/timeline.py`, FCPXML for DaVinci, Premiere, Final Cut).

## Stop and ask

- A mic track is missing or silent (never fall back to camera audio quietly; in a one-camera long video the camera track is allowed when it is the only source, and the report says so).
- A file fails its checksum after copying.
- You can't tell who is talking from the mics and the picture.
- A piece has no real spoken CTA (say so; never invent one).
- Anything would delete or overwrite: move the old file to a backup instead.

## Never

- Never erase the card before every file is checked in two places.
- Never cut inside a word or between a setup and its point.
- Never zoom to hide a jump cut: change camera.
- Never show a human a video that has not passed Step 7.
- Never invent facts in captions, titles or CTAs.

## Setup

Python 3.11+, ffmpeg (`brew install ffmpeg` on a Mac: it includes what burned-in captions need), and `pip install -r requirements.txt`. For transcripts: `pip install faster-whisper whisperx` (free, local). Run the tools from the repo root: `python3 tools/<tool>.py`.
