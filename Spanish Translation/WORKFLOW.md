# Translation workflow

One task = one episode. Each episode goes through two passes before it's
considered done.

## Model
Both passes use Claude Sonnet 5. Opus is reserved for individual episodes
that turn out unusually hard (dense technical exposition, wordplay) rather
than used by default — at this volume (70+ episodes and growing) the cost
difference isn't worth it for typical shonen dialogue.

## Inputs given to the translation pass
- The episode's English `.srt` from `../Rebuild of Naruto - Subtitles/`.
- `Terminology/naruto_glosario_es_es.yml` (fixed reference, always).
- `Context/season-XX-*.md` for the episode's season (arc primer: setting,
  characters present, register notes, continuity) — written once per
  season/arc and reused across its episodes, not rebuilt per episode.

## Pass A — Translate
1. Translate the full episode `.srt` in one continuous task (see "Full
   episode, not chunked" below), preserving cue numbers and timestamps
   exactly, translating only the text.
2. Apply the glossary terms as fixed choices; don't re-decide terminology
   already in the glossary.
3. Where the missing visual context (no speaker labels in the source
   `.srt`) leaves real ambiguity — who's talking, tone, a reference that
   depends on what's on screen — flag the cue instead of guessing.
4. Output:
   - `<episode>.es.srt` — draft translation, same filename pattern as the
     English source with `.es.srt` instead of `.en.srt`, committed under a
     season folder mirroring `Rebuild of Naruto - Subtitles/`.
   - `<episode>.notes.md` next to it, listing only the flagged cues (cue
     number, English line, the doubt).
5. Update the episode's row in `PROGRESS.md` to `Traducido`.

## Pass B — Review
1. If a verified Crunchyroll ES rip exists for this exact episode (checked
   by content, not by OpenSubtitles' episode listing — see the project
   note's warning about mismatched listings), cross-check the flagged
   cues and spot-check terminology against it.
2. If no verified external source exists, review is: resolve each flagged
   cue with best judgment, re-read the full episode for register
   consistency (`vosotros`, not `ustedes` — see nrtq02 finding) and
   glossary compliance.
3. Delete `<episode>.notes.md` once every flagged cue is resolved (either
   fixed or judged fine as translated).
4. Update the episode's row in `PROGRESS.md` to `Revisado`.

## Full episode, not chunked
Episode `.srt` files (even the longest, ~1250 cues) fit comfortably in a
single translation task's context alongside the glossary and arc primer —
chunking by scene/cue-block isn't needed for context-window reasons and
would risk tone/terminology drift between chunks. If an episode's output
needs to be written in multiple batches for practical reasons, that's an
implementation detail within the same task — it must not become an
independently-translated, independently-reviewed chunk.

## Tracking
`PROGRESS.md` in this folder is the single source of truth for episode
status. No per-episode Obsidian tasks — only the project-level tasks for
open design questions.

## Committing
One commit per finished episode (post Pass B) is fine directly on `main` —
this is a personal fork with review built into Pass B, no need for PRs
per episode.
