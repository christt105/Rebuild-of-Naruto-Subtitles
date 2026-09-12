#!/usr/bin/env python3
"""Print only the glossary entries whose English/Japanese term appears in a
given episode's English .srt, so a translation task doesn't need to load the
whole glossary.

This is a best-effort text filter, not a guarantee: inflected forms or terms
phrased differently than in the glossary's `english` field may be missed.
If a term is suspected but doesn't show up here, grep the full glossary
directly (Terminology/naruto_glosario_es_es.yml).

Usage:
    relevant_glossary.py <path-to-episode.en.srt>
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GLOSSARY = REPO_ROOT / "Spanish Translation" / "Terminology" / "naruto_glosario_es_es.yml"

ENTRY_RE = re.compile(
    r'- japanese:\s*"[^"]*"\n'
    r'\s*english:\s*"(?P<english>[^"]*)"\n'
    r'\s*spanish_es:\s*"[^"]*"\n'
    r'\s*source:\s*"[^"]*"\n'
    r'\s*verified:\s*(?:true|false)'
)


def load_entries(path):
    text = path.read_text(encoding="utf-8")
    return [(m.group("english"), m.group(0)) for m in ENTRY_RE.finditer(text)]


def matches(english_field, episode_text_lower):
    for term in re.split(r"\s*/\s*", english_field):
        term = re.sub(r"\s*\([^)]*\)", "", term).strip().lower()
        if term and term in episode_text_lower:
            return True
    return False


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: relevant_glossary.py <ruta-al-episodio.en.srt>")

    episode_path = Path(sys.argv[1])
    episode_text = episode_path.read_text(encoding="utf-8").lower()

    entries = load_entries(GLOSSARY)
    matched = [block for english, block in entries if matches(english, episode_text)]

    if not matched:
        print("(sin coincidencias; usar el glosario completo)")
        return

    print(f"# {len(matched)} de {len(entries)} entradas del glosario aparecen en este episodio")
    print(f"# Si sospechas que falta un termino, grepea el glosario completo: {GLOSSARY.relative_to(REPO_ROOT)}")
    print()
    for block in matched:
        print(block.strip())
        print()


if __name__ == "__main__":
    main()
