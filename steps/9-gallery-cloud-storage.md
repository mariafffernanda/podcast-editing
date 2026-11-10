# Step 9. Guest gallery, the cloud and storage

## Guest gallery

`gallery/` is a small website: each guest gets a page behind their own password with previews, full-quality downloads, captions to copy and the transcript. The front page never lists guests. See `gallery/README.md` to set it up.

- Passwords are never stored. `gallery/tools/set_password.py` saves a keyed hash, and the key (`COOKIE_SECRET`) lives in Vercel's environment variables, never in the repo.
- Make your copy of this repo **private** before you add real guests.
- Downloads can be any link: a Google Drive share link works well.
- Vercel's free plan is for non-commercial use. A studio that charges clients needs Vercel Pro ($20 a month).

## Working in the cloud

The code lives on GitHub and nobody needs a local server.

1. Your copy of the repo sits on GitHub and is connected to Vercel once (Vercel > Add New > Project > import the repo, Root Directory `gallery`). Every change saved to the main branch publishes the gallery by itself.
2. To change the code, open the repo in Claude Code on the web (claude.ai/code). It works on a cloud machine, makes the change and saves it to GitHub.
3. For a small text fix (a title, a caption in `guests.json`), GitHub's own web editor is enough: press the period key on the repo page.
4. What stays on the computer is the video work. Footage is too big to send to a cloud machine, so cutting and rendering run where the files are. The cloud holds the code, the gallery and the skill. The computer holds the footage.

## Storage we recommend

- **Google One 2 TB** at $9.99 a month ($99.99 a year) for finals, transcripts and project files. Check the current price at one.google.com.
- Raw footage stays on a NAS or an external drive. The card is erased only after the files are checked in two places (Step 1).
