# Podcast editing skill

A Claude Code skill that takes a video podcast from the memory card to finished, checked videos: an episode, a spicy cut, social clips per person, team clips, LinkedIn clips, stories and a transcript. It also comes with a private guest gallery you can deploy.

Every rule in it comes from a mistake made on real sessions. The full list is in [`lessons.md`](lessons.md).

## What you need

- Claude Code
- A conversation recorded on 1 to 4 cameras (each camera saved as its own file) and a recorder with one track per mic, like a RØDECaster
- A Mac or Linux computer with Python 3.11+ and ffmpeg

## Install

Click **Use this template** at the top of this page to get your own copy, then:

```
git clone https://github.com/<you>/<your-copy>.git ~/.claude/skills/podcast-editing
cd ~/.claude/skills/podcast-editing
pip install -r requirements.txt
```

Then tell Claude Code "edit my podcast session in <folder>". The skill walks the steps in order: [`SKILL.md`](SKILL.md).

To skip the questions on every new session, copy [`profile.example.md`](profile.example.md) to `~/.claude/podcast-profile.md` and fill it in. Then say "activate my podcast skill".

## What's inside

| | |
|---|---|
| `SKILL.md` | the steps in order, with what to stop and ask about |
| `steps/` | one file per step: organize, sound, transcript, content plan, cutting, cameras, final check, delivery, gallery |
| `tools/` | small tested Python tools: checksum copies, mic map and sync drift, cut lists, join checks, the final report card, captions (SRT), timelines for DaVinci, Premiere and Final Cut (FCPXML) |
| `gallery/` | a guest gallery website: a page per guest behind their own password |
| `lessons.md` | what went wrong and the rule it became |

## The guest gallery

Each guest gets a private page with previews, full-quality downloads, captions to copy and the transcript. It runs on Vercel and publishes itself every time you save a change on GitHub, so you can edit it from the browser with Claude Code on the web (claude.ai/code) and never run a local server. Setup is in [`gallery/README.md`](gallery/README.md).

Make your copy **private** before you add real guests.

## Storage

We recommend **Google One 2 TB** ($9.99 a month or $99.99 a year) for finals, transcripts and project files. Keep raw footage on a NAS or an external drive, and erase the card only after every file is checked in two places.

## Tests

```
pytest
cd gallery && node --test
```

Every check is tested on a known failure (a broken file, a 120 ms sync shift, a level jump at a join), because a checker that passes what it can't read is worse than no checker.

## License

MIT
