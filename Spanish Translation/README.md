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

## Manga reference database

When a term ends up in `Terminology/pending-glossary-review.md` because no
official Spanish rendering could be confirmed, `scripts/manga_ref.py` is a
personal tool to help settle it: it OCRs the Spanish (Planeta) manga volumes
and official character guides you own, once, on CPU only, and stores the
text in a local SQLite database with full-text search, so an undecided
translation can be checked against how the manga actually rendered it
instead of guessed. It's a private lookup aid for volumes already in your
possession, not a scraper or a way to publish the manga's text — nothing it
extracts is meant to leave your machine or land in this repo.

```
python3 "Spanish Translation/scripts/manga_ref.py" ingest <volume.cbr> --kind manga --title Naruto --volume 1
python3 "Spanish Translation/scripts/manga_ref.py" ingest <guide.cbr> --kind guide --title "Guia oficial" --volume 1
python3 "Spanish Translation/scripts/manga_ref.py" search "multiplicación" --title Naruto
python3 "Spanish Translation/scripts/manga_ref.py" page Naruto 1 23
```

Needs `tesseract` with the `spa` language pack and `unar`. Ingestion is
resumable (pages already stored are skipped) and runs at the lowest CPU
priority with one OCR thread. The database holds copyrighted text extracted
from volumes you own for this personal-reference use, so it lives outside
the repo (`MANGA_REF_DB`, default `~/.local/share/manga-ref/manga_ref.db`)
and must never be committed. OCR output is noisy on small or stylised
lettering: treat hits as leads to confirm on the page image, not as
verified text.

## Workflow

See [`WORKFLOW.md`](WORKFLOW.md) for the one-branch-one-PR-per-episode
process, and [`PROGRESS.md`](PROGRESS.md) for per-episode status.

## Status

Baseline committed for all 73 currently published episodes (English text
under Spanish filenames). Translation happens episode by episode via PR
from here.
