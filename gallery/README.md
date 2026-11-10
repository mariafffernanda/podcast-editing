# Guest gallery

A small website: each guest gets a page behind their own password with previews, full-quality downloads, captions to copy and the transcript. The front page never lists guests.

## Set it up once (about 15 minutes)

1. **Make your copy of the repo private** (GitHub > Settings > Danger Zone > Change visibility).
2. In Vercel: **Add New > Project**, import your repo, set **Root Directory** to `gallery`, and deploy.
3. Make a secret and save it in Vercel, without showing it on screen:

   ```
   openssl rand -hex 32 > ~/.gallery_secret
   npx vercel env add COOKIE_SECRET production < ~/.gallery_secret
   ```

4. Set your own password (it opens every guest page) and one per guest. You type each password at a hidden prompt:

   ```
   export COOKIE_SECRET="$(cat ~/.gallery_secret)"
   python3 tools/set_password.py owner
   python3 tools/set_password.py alex-rivera
   ```

5. Commit `data/access.js` and push. Vercel publishes it.

## Add a guest

Edit `guests.json` (from the browser is fine: press the period key on your repo page on GitHub):

```json
{ "slug": "jamie-lee", "name": "Jamie Lee", "session": "Episode 4", "transcript": "<link>",
  "pieces": [ { "title": "...", "kind": "social", "preview": "<video link>", "download": "<Google Drive link>", "caption": "..." } ] }
```

- `kind`: `episode`, `spicy`, `social`, `team`, `linkedin` or `story`. Vertical kinds show as 9:16.
- `preview`: a small, low-res video link (Vercel Blob or any host that streams video). Downloads go to the full-quality file, for example a Google Drive share link.
- Then set the guest's password (step 4 above) and send them `https://<your-site>/g/<slug>/` with the password, in two separate messages.

## How the lock works

`middleware.js` runs before every guest page. The password form posts to `/entrar/`. The password is checked against a keyed hash in `data/access.js`, and a signed cookie keeps the guest in for a year. Your `owner` password opens every page. Passwords are never stored anywhere, and the key lives only in Vercel.

## Costs

Vercel's free plan is for non-commercial use. A studio that charges clients needs Vercel Pro ($20 a month). Storing previews in Vercel Blob is free up to its plan limit, and then billed by use.

## Test

```
node --test
python3 -m pytest
```
