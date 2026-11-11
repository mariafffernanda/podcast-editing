# Lessons

Every rule in this skill came from one of these. Add a row each time something goes wrong.

| What went wrong | The rule |
|---|---|
| Camera audio sounded boxed in | always the recorder's mic tracks |
| The switcher's mic copy sounded bad boosted | use the recorder's own files |
| One mixed track let the other person's breathing through | one mic per speaker, others down |
| A whole batch had the picture 110 ms ahead of the sound | sync check after every render |
| Joining exact-length sound pieces drifted 120 ms | join on whole frames |
| Copies came out the right size but broken | verify with checksums |
| A drive erased with the work files cost 10 edits | work files beside the footage |
| Voice matching swapped two speakers | confirm by mic level and by eye |
| Late word starts made cuts clip words | align every word first |
| Repeat removal ate real speech | a sentence-ending word is never a false start |
| Close-ups cropped too tight looked soft | cap the zoom near 1.7x |
| Re-centring every shot made the frame jump | one crop per person per video |
| Punch-ins on every cut ("I hate the zooms") | change camera instead |
| Reactions hid the speaker for 77 s in one cut | reactions only inside a turn |
| Clips ended on a nice thought with no ask | a real spoken CTA, or say there is none |
| Clips opened with context nobody cares about | open on the hook |
| A checker passed videos it couldn't read | test every check on a known failure |
| Renders from working copies looked soft | render finals from the originals |
| A camera drive dropped out for a moment during the copy and every file after it failed | copy the card first, before any other reading, and re-run failed files; the md5 check catches what a drop-out breaks |
| Pausing a copy to the network drive froze every other program writing there | never pause a copy to a network drive; keep in-progress work files on the computer and copy them over when done |
| The transcript slowed to a crawl while a second big job ran | one big job at a time, or split the audio at a silence and run two halves, never two jobs that swap memory |
