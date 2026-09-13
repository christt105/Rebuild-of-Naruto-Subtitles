#!/usr/bin/env python3
"""Validate an episode's Spanish .srt against its English baseline.

Usage:
    check_episode.py <code-or-path> [--strict] [--json]

<code-or-path> is either an episode code (S01E01) or a path containing one
(e.g. the .es.srt file itself) — used by the check-episode GitHub Action,
which passes changed file paths from `git diff`.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from srt_utils import parse_srt

REPO_ROOT = Path(__file__).resolve().parents[2]
EN_DIR = REPO_ROOT / "Rebuild of Naruto - Subtitles"
ES_DIR = REPO_ROOT / "Spanish Translation" / "Subtitles"
PENDING_REVIEW = REPO_ROOT / "Spanish Translation" / "Terminology" / "pending-glossary-review.md"

CODE_RE = re.compile(r"[Ss]\d{2}[Ee]\d{2}")
TAG_RE = re.compile(r"\{([A-Z0-9]+)\}")
DOCUMENTED_CODE_RE = re.compile(r"`\{([A-Z0-9]+)\}`")


def resolve_target(target):
    m = CODE_RE.search(target)
    if not m:
        sys.exit(f"No se pudo extraer un código de episodio (SxxExx) de: {target}")
    code = m.group(0).upper()

    target_path = Path(target)
    if target_path.is_file() and target_path.name.endswith(".es.srt"):
        es_path = target_path.resolve()
    else:
        es_matches = list(ES_DIR.rglob(f"*{code}*.es.srt"))
        if len(es_matches) != 1:
            sys.exit(f"Esperaba 1 archivo .es.srt para {code}, encontrados {len(es_matches)}: {es_matches}")
        es_path = es_matches[0]

    en_matches = list(EN_DIR.rglob(f"*{code}*.en.srt"))
    if len(en_matches) != 1:
        sys.exit(f"Esperaba 1 archivo .en.srt para {code}, encontrados {len(en_matches)}: {en_matches}")

    return code, en_matches[0], es_path


def load_documented_codes():
    if not PENDING_REVIEW.exists():
        return set()
    return set(DOCUMENTED_CODE_RE.findall(PENDING_REVIEW.read_text(encoding="utf-8")))


def check(code, en_path, es_path):
    result = {
        "code": code,
        "en_path": str(en_path.relative_to(REPO_ROOT)),
        "es_path": str(es_path.relative_to(REPO_ROOT)),
        "errors": [],
        "warnings": [],
        "untranslated_cues": [],
        "tags": {},
    }

    try:
        en_cues = parse_srt(en_path)
        es_cues = parse_srt(es_path)
    except ValueError as e:
        result["errors"].append(str(e))
        return result

    if len(en_cues) != len(es_cues):
        result["errors"].append(f"número de cues no coincide: EN={len(en_cues)} ES={len(es_cues)}")

    documented = load_documented_codes()
    seen_tags = {}

    for i, (en, es) in enumerate(zip(en_cues, es_cues), start=1):
        if en.index != i or es.index != i:
            result["errors"].append(f"numeración fuera de secuencia en posición {i}: EN#{en.index} ES#{es.index}")
        if en.start != es.start or en.end != es.end:
            result["errors"].append(
                f"timestamp no coincide en cue {i}: EN {en.start}-->{en.end} vs ES {es.start}-->{es.end}"
            )

        es_clean = TAG_RE.sub("", es.text).rstrip()
        if es_clean == en.text.strip():
            result["untranslated_cues"].append(i)

        for tm in TAG_RE.finditer(es.text):
            seen_tags.setdefault(tm.group(1), []).append(i)

    for tag, cues in seen_tags.items():
        result["tags"][tag] = {"cues": cues, "documented": tag in documented}
        if tag not in documented:
            result["errors"].append(f"tag {{{tag}}} usado en cues {cues} pero no documentado en pending-glossary-review.md")

    if result["untranslated_cues"]:
        n = len(result["untranslated_cues"])
        shown = ", ".join(str(c) for c in result["untranslated_cues"][:20])
        result["warnings"].append(
            f"{n} cue(s) idénticos al inglés (puede ser intencional o trabajo pendiente): {shown}"
            + ("..." if n > 20 else "")
        )

    return result


def format_text(result):
    lines = [
        f"Episodio {result['code']}",
        f"  EN: {result['en_path']}",
        f"  ES: {result['es_path']}",
        f"  Cues sin traducir (idénticos a EN): {len(result['untranslated_cues'])}",
    ]
    if result["tags"]:
        for tag, info in sorted(result["tags"].items()):
            marker = "OK" if info["documented"] else "SIN DOCUMENTAR"
            lines.append(f"  Tag {{{tag}}} en cues {info['cues']} [{marker}]")
    else:
        lines.append("  Sin tags {CODE} pendientes")
    for w in result["warnings"]:
        lines.append(f"  AVISO: {w}")
    for e in result["errors"]:
        lines.append(f"  ERROR: {e}")
    lines.append("RESULTADO: " + ("OK" if not result["errors"] else "FALLO"))
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("target", help="Código de episodio (S01E01) o ruta a su .es.srt")
    parser.add_argument("--strict", action="store_true", help="Sale con código 1 si hay errores estructurales o tags {CODE} sin documentar")
    parser.add_argument("--json", action="store_true", help="Salida en JSON en vez de texto")
    args = parser.parse_args()

    code, en_path, es_path = resolve_target(args.target)
    result = check(code, en_path, es_path)

    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else format_text(result))

    if args.strict and result["errors"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
