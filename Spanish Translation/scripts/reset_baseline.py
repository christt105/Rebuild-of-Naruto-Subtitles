#!/usr/bin/env python3
"""Reset an episode's .es.srt to a literal copy of its English .en.srt baseline.

Used to discard an in-progress translation attempt without touching git
history (the abandoned branch/commits stay in git, untouched), or to
(re)generate the baseline for a newly published episode.

Usage:
    reset_baseline.py <code> [--force]
"""

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EN_DIR = REPO_ROOT / "Rebuild of Naruto - Subtitles"
ES_DIR = REPO_ROOT / "Spanish Translation" / "Subtitles"
CODE_RE = re.compile(r"[Ss]\d{2}[Ee]\d{2}")


def resolve(code):
    en_matches = list(EN_DIR.rglob(f"*{code}*.en.srt"))
    es_matches = list(ES_DIR.rglob(f"*{code}*.es.srt"))
    if len(en_matches) != 1:
        sys.exit(f"Esperaba 1 archivo .en.srt para {code}, encontrados {len(en_matches)}: {en_matches}")
    if len(es_matches) != 1:
        sys.exit(f"Esperaba 1 archivo .es.srt para {code}, encontrados {len(es_matches)}: {es_matches}")
    return en_matches[0], es_matches[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("code", help="Código de episodio, p.ej. S01E01")
    parser.add_argument("--force", action="store_true", help="Sobrescribe aunque el .es.srt ya tenga contenido traducido")
    args = parser.parse_args()

    code = args.code.upper()
    if not CODE_RE.fullmatch(code):
        sys.exit(f"'{args.code}' no tiene forma de código de episodio (SxxExx)")

    en_path, es_path = resolve(code)
    en_text = en_path.read_text(encoding="utf-8")
    es_text = es_path.read_text(encoding="utf-8") if es_path.exists() else None

    if es_text is not None and es_text != en_text and not args.force:
        sys.exit(f"{es_path} ya tiene contenido distinto al baseline en ingles. Usa --force si de verdad quieres descartarlo.")

    es_path.write_text(en_text, encoding="utf-8")
    print(f"{es_path.relative_to(REPO_ROOT)} restablecido al baseline en ingles")


if __name__ == "__main__":
    main()
