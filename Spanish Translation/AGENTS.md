# Agent instructions: translating one episode

Read this once at the start of a translation task, then execute without
re-deriving the process. It exists so a single short instruction ("translate
S01E08") is enough — no need to re-explain the workflow each time.

## Scope

One agent, one episode, start to finish, in its own isolated task (the
`Agent` tool, not the main conversation — keeps the large translation
context out of the session you use to supervise/check in from your phone).
Do not split one episode across multiple agents or worktrees — see
`WORKFLOW.md` ("Full episode, not chunked") for why.

## Before writing anything (minimal reads — this is what actually saves tokens)

1. Resolve the episode code (e.g. `S01E01`) and locate its two files by
   globbing for the code, same convention the scripts use — don't guess
   paths by hand.
2. Run `python3 "Spanish Translation/scripts/check_episode.py" <code>`
   first. If it reports untranslated cues starting partway through, this is
   a resume, not a fresh start — pick up from there, don't re-translate or
   re-read what's already done.
3. Run `python3 "Spanish Translation/scripts/relevant_glossary.py" <path-to-.en.srt>`
   instead of opening `Terminology/naruto_glosario_es_es.yml` in full. If you
   later suspect a term exists in the glossary but didn't show up in the
   filtered output, grep the full file directly rather than assuming it's
   absent.
4. Read the season's arc primer (`Context/season-XX-*.md`) in full — it's
   small and meant to be loaded whole.
5. Read `Terminology/pending-glossary-review.md` in full — also small.
   Check whether any of its open codes apply to lines in this episode.

Do not re-read the target `.es.srt` end-to-end more than once. It starts as
a literal copy of the English source, so its initial content is already
known from the English file.

## Translating, in a way that keeps turns (and tokens) low

Turn count matters more than raw context size here: each turn resends the
whole conversation so far, so a translation split into many small
back-and-forth turns cost far more than the same output produced in a few
large ones — this, not the episode's length, is what exhausted a full
session on a single episode before. Concretely:

- Work in large batches (roughly 150-300 cues per write), not cue by cue.
- Use `Edit` with block replacements; avoid rewriting the whole file with
  `Write` more than once (at most, for the very first batch if starting
  fresh).
- Preserve cue numbers and timestamps exactly — only the text lines change.
- Commit to the episode branch whenever you reach a natural, stable
  stopping point (your judgment on cadence — this is a crash-recovery
  checkpoint, not a review unit; nothing gets reviewed independently until
  the final PR).

## Precedence when translating a term

1. `Terminology/naruto_glosario_es_es.yml` (`verified: true` entries are
   fixed — do not deviate even if it reads awkwardly; `verified: false`
   entries are the working choice unless episode context actively
   contradicts them, in which case flag it, don't silently override).
2. The season's arc primer (register, characters, continuity).
3. Decisions already made earlier in this same episode (stay consistent
   with yourself).
4. Your own judgment — only when none of the above applies, and only for
   genuinely new terms.

## Staging new or uncertain terminology

Never edit `naruto_glosario_es_es.yml` directly during a translation task.

For a term that's new, ambiguous, or bends an existing convention:
1. Tag it inline in the `.es.srt` text with a short, UPPERCASE code in
   curly braces, e.g. `¡El Nueve Colas! {NC}`.
2. Append an entry for that code to `Terminology/pending-glossary-review.md`
   (append at the end of the file — don't edit existing entries — this
   keeps concurrent episodes from conflicting on this file).
3. `check_episode.py --strict` fails if a code is used but not documented,
   so this isn't optional bookkeeping — it's a merge gate.

Tags must never reach a merged PR as tags — they get resolved (glossary
updated, tags stripped from every episode that used them) in a separate,
periodic glossary-review pass, not per episode.

## Real ambiguity (not terminology)

If the `.srt`'s lack of speaker labels leaves genuine ambiguity (who's
talking, tone, an on-screen reference), don't guess silently — note it in
the PR description, per `WORKFLOW.md`.

## Don'ts

- Don't create extra branches/worktrees for the same episode.
- Don't do a full self-review re-read of the finished episode as a separate
  pass — that's expensive and `check_episode.py` already catches everything
  a script can catch. Trust it.
- Don't touch `naruto_glosario_es_es.yml`.
- Don't leave a `{CODE}` tag undocumented.
- Don't merge or push to `main` — PR only, merge is always Christian's call.

## Finishing up

1. `python3 "Spanish Translation/scripts/check_episode.py" <code> --strict`
   must pass before opening a PR.
2. Push the branch, `gh pr create` against `main` (include any noted
   ambiguity in the description).
3. `python3 "Spanish Translation/scripts/update_progress.py" <code> "PR abierta" --pr <N>`.
4. Report back briefly: cues translated, any new `{CODE}` tags raised, any
   ambiguity flagged, the PR link. Not a line-by-line recap.
