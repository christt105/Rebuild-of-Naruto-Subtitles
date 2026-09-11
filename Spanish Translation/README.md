# Spanish (Spain) Translation

Spanish (`es-ES`) subtitles for the *Rebuild of Naruto* fan edit, translated
from the English `.en.srt` files in this repository's
[`Rebuild of Naruto - Subtitles`](../Rebuild%20of%20Naruto%20-%20Subtitles)
folder.

## Terminology

[`Terminology/naruto_glosario_es_es.yml`](Terminology/naruto_glosario_es_es.yml)
is the fixed glossary of Japanese/English terms → Spain Spanish, used as a
reference so terminology stays consistent across episodes. Each entry
records its source and whether it's been verified against an official
source (see the file header for the verification criteria and source
priority order).

## Context

[`Context/`](Context) holds one arc/season primer per season (characters
present, register notes, continuity) — fixed reference reused across all
episodes in that season, alongside the glossary.

## Subtitles

[`Subtitles/`](Subtitles) mirrors the season/episode structure of the
English source, but files are already named with their Spanish title and
`.es.srt` extension. Each file starts as an untouched copy of the English
text (baseline) and gets translated in place, one episode per branch/PR —
see `WORKFLOW.md`.

## Workflow

See [`WORKFLOW.md`](WORKFLOW.md) for the one-branch-one-PR-per-episode
process, and [`PROGRESS.md`](PROGRESS.md) for per-episode status.

## Status

Baseline committed for all 73 currently published episodes (English text
under Spanish filenames). Translation happens episode by episode via PR
from here.
