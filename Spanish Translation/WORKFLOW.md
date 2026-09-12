# Translation workflow

One episode = one branch = one PR.

## Model
Translation uses Claude Sonnet 5. Opus is reserved for individual episodes
that turn out unusually hard (dense technical exposition, wordplay) rather
than used by default — at this volume (70+ episodes and growing) the cost
difference isn't worth it for typical shonen dialogue.

## Baseline
`Subtitles/` mirrors the season/episode structure of
[`../Rebuild of Naruto - Subtitles`](../Rebuild%20of%20Naruto%20-%20Subtitles),
but every file is named with its Spanish episode title and `.es.srt`
extension, while still containing the untouched **English** text copied
from the source. This baseline is a fixed point: translating a file in
place from here on means every PR's diff *is* the translation — no
separate before/after comparison needed.

Regenerating the baseline (e.g. when Maediem publishes new episodes) is a
direct commit to `main`, not a PR — it's scaffolding, not a translation
deliverable, and titles here are already the ones agreed in `PROGRESS.md`.

Ccuenta's 6 existing drafts (`Rebuild-of-Naruto-Subtitles-es`, Naruto
S01E01–S01E06) are discarded, not reused — see nrtq02 (Latin American
dialect, doesn't clear the Spain-Spanish bar). All 73 episodes translate
from the English baseline the same way.

## Per episode
1. Branch off `main`: `translate/<code>` (e.g. `translate/s01e07`).
2. Translate the body text of that one `.es.srt` file **in place**,
   English → Spanish, preserving cue numbers and timestamps exactly. See
   `AGENTS.md` for the exact, token-efficient execution procedure (what to
   read, how to batch the work, terminology precedence and staging).
3. If a verified Crunchyroll ES match exists for this exact episode
   (confirmed by content, not by relying on OpenSubtitles' episode
   listing — Rebuild's episode order and cuts don't line up with
   Crunchyroll's, so most episodes won't have one), note it and use it as
   a terminology/register cross-check.
4. Run `scripts/check_episode.py <code> --strict` — must pass before
   opening a PR. It's also the CI gate on the PR (see below).
5. Push the branch, open a PR against `main` with `gh pr create`. The diff
   is the whole review surface: English baseline vs. translated text,
   cue by cue.
6. Update the episode's row in `PROGRESS.md` via
   `scripts/update_progress.py <code> "PR abierta" --pr <N>` in the same PR.
7. Christian reviews the diff, comments/iterates on the branch as needed,
   and merges when satisfied (merging is always his call, never automatic;
   the CI check can fail a PR but never merges one). On merge, flip
   `PROGRESS.md` to `Fusionado` the same way.

## CI
`.github/workflows/validate-subtitles.yml` runs `check_episode.py --strict`
on every changed `.es.srt` in a PR (cue count, numbering, timestamps,
undocumented `{CODE}` tags) and reports pass/fail in the job summary. It
catches structural mistakes a human reviewer shouldn't have to — it doesn't
judge translation quality.

## Full episode, not chunked
Episode `.srt` files (even the longest, ~1250 cues) fit comfortably in a
single translation task's context alongside the glossary and arc primer —
chunking by scene/cue-block isn't needed for context-window reasons and
would risk tone/terminology drift between chunks. If an episode's output
needs to be written in multiple batches for practical reasons, that's an
implementation detail within the same task/branch — it must not become an
independently-translated, independently-reviewed chunk.

## Tracking
`PROGRESS.md` in this folder is the single source of truth for episode
status. No per-episode Obsidian tasks — only the project-level tasks for
open design questions.
