#!/usr/bin/env python3
"""Build the JSON data consumed by the static site under site/.

Usage:
    build_site_data.py [--diff-against <git-ref>] [--out <dir>]

Reads every EN/ES .srt pair, PROGRESS.md, the glossary YAML and
pending-glossary-review.md, and writes:
    <out>/index.json            lightweight episode/season/totals index
    <out>/glossary.json         glossary entries + pending {CODE} tags
    <out>/episodes/<CODE>.json  full cue table for one episode

With --diff-against <ref>, each cue also gets an "es_prev" field (the ES
text at that git ref) whenever it differs from the working tree — used for
PR preview diff rendering. Always rebuilds every episode rather than only
the ones touched by a given ref, since parsing ~73 short .srt files is
cheap and it avoids a second code path.
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from srt_utils import parse_srt, parse_srt_text

REPO_ROOT = Path(__file__).resolve().parents[2]
EN_DIR = REPO_ROOT / "Rebuild of Naruto - Subtitles"
ES_DIR = REPO_ROOT / "Spanish Translation" / "Subtitles"
PROGRESS = REPO_ROOT / "Spanish Translation" / "PROGRESS.md"
GLOSSARY = REPO_ROOT / "Spanish Translation" / "Terminology" / "naruto_glosario_es_es.yml"
PENDING_REVIEW = REPO_ROOT / "Spanish Translation" / "Terminology" / "pending-glossary-review.md"

CODE_RE = re.compile(r"[Ss]\d{2}[Ee]\d{2}")
TAG_RE = re.compile(r"\{([A-Z0-9]+)\}")
PENDING_ENTRY_RE = re.compile(r"^### `\{([A-Z0-9]+)\}` — (.+)$", re.MULTILINE)


def load_progress_rows():
    lines = PROGRESS.read_text(encoding="utf-8").splitlines()
    rows = []
    for line in lines:
        if not CODE_RE.match(line.strip().strip("|").split("|")[0].strip()):
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) != 6:
            continue
        code, title_en, title_es, season, status, notes = cols
        rows.append(
            {
                "code": code,
                "title_en": title_en,
                "title_es": title_es,
                "season": season,
                "status": status,
                "notes": notes,
            }
        )
    return rows


def load_glossary():
    return yaml.safe_load(GLOSSARY.read_text(encoding="utf-8")) or []


def extract_glossary_terms(spanish_es):
    quoted = re.findall(r'"([^"]+)"', spanish_es)
    if quoted:
        return [t.strip() for t in quoted if t.strip()]
    terms = []
    for part in re.split(r"\s*/\s*", spanish_es):
        part = re.sub(r"\([^)]*\)", "", part).strip().strip("«»")
        if part:
            terms.append(part)
    return terms


def load_pending_tags():
    text = PENDING_REVIEW.read_text(encoding="utf-8")
    matches = list(PENDING_ENTRY_RE.finditer(text))
    entries = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        entries.append({"code": m.group(1), "title": m.group(2).strip(), "body": text[start:end].strip()})
    return entries


def git_show(ref, path):
    rel = path.relative_to(REPO_ROOT).as_posix()
    result = subprocess.run(
        ["git", "show", f"{ref}:{rel}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def resolve_srt_paths(code):
    en_matches = list(EN_DIR.rglob(f"*{code}*.en.srt"))
    if not en_matches:
        # A few upstream episodes ship as "<title>.srt" instead of "<title>.en.srt".
        en_matches = [p for p in EN_DIR.rglob(f"*{code}*.srt") if not p.name.endswith(".es.srt")]
    es_matches = list(ES_DIR.rglob(f"*{code}*.es.srt"))
    if len(en_matches) != 1 or len(es_matches) != 1:
        return None, None
    return en_matches[0], es_matches[0]


def build_episode(row, diff_ref):
    code = row["code"]
    en_path, es_path = resolve_srt_paths(code)
    if en_path is None:
        sys.exit(f"No se encontraron .srt para {code}")

    try:
        en_cues = parse_srt(en_path)
        es_cues = parse_srt(es_path)
    except ValueError as e:
        message = str(e).replace(str(REPO_ROOT) + "/", "")
        print(f"AVISO: {code} omitido, .srt malformado: {message}", file=sys.stderr)
        return None, {"cue_count": 0, "translated_count": 0, "unresolved_tags": set(), "srt_error": message}

    prev_text_by_index = {}
    if diff_ref:
        prev_raw = git_show(diff_ref, es_path)
        if prev_raw is not None:
            try:
                for cue in parse_srt_text(prev_raw, f"{diff_ref}:{es_path.name}"):
                    prev_text_by_index[cue.index] = cue.text
            except ValueError:
                pass

    cues = []
    unresolved_tags = set()
    translated_count = 0
    for en, es in zip(en_cues, es_cues):
        tags = TAG_RE.findall(es.text)
        unresolved_tags.update(tags)
        es_clean = TAG_RE.sub("", es.text).rstrip()
        translated = es_clean != en.text.strip()
        if translated:
            translated_count += 1
        prev_text = prev_text_by_index.get(en.index)
        cues.append(
            {
                "index": en.index,
                "start": en.start,
                "end": en.end,
                "en": en.text,
                "es": es.text,
                "translated": translated,
                "tags": tags,
                "es_prev": prev_text if (prev_text is not None and prev_text != es.text) else None,
            }
        )

    episode = {
        **row,
        "en_path": en_path.relative_to(REPO_ROOT).as_posix(),
        "es_path": es_path.relative_to(REPO_ROOT).as_posix(),
        "cues": cues,
    }
    stats = {
        "cue_count": len(cues),
        "translated_count": translated_count,
        "unresolved_tags": unresolved_tags,
        "srt_error": None,
    }
    return episode, stats


def build_glossary_index(episodes_by_code):
    entries = []
    for entry in load_glossary():
        terms = [t.lower() for t in extract_glossary_terms(entry.get("spanish_es", ""))]
        matched_episodes = []
        for code, episode in episodes_by_code.items():
            es_text = " ".join(cue["es"] for cue in episode["cues"]).lower()
            if any(term and term in es_text for term in terms):
                matched_episodes.append(code)
        entries.append({**entry, "episodes": matched_episodes})
    return {"entries": entries, "pending_tags": load_pending_tags()}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--diff-against", help="Git ref para calcular es_prev por cue (previews de PR)")
    parser.add_argument("--out", default=str(REPO_ROOT / "site" / "data"), help="Directorio de salida")
    args = parser.parse_args()

    out_dir = Path(args.out)
    episodes_dir = out_dir / "episodes"
    episodes_dir.mkdir(parents=True, exist_ok=True)

    rows = load_progress_rows()
    episodes_by_code = {}
    index_episodes = []
    totals = {"cues_total": 0, "cues_translated": 0}
    all_unresolved_tags = set()

    for row in rows:
        episode, stats = build_episode(row, args.diff_against)
        if episode is not None:
            episodes_by_code[row["code"]] = episode
            (episodes_dir / f"{row['code']}.json").write_text(
                json.dumps(episode, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        totals["cues_total"] += stats["cue_count"]
        totals["cues_translated"] += stats["translated_count"]
        all_unresolved_tags.update(stats["unresolved_tags"])
        index_episodes.append(
            {
                **row,
                "cue_count": stats["cue_count"],
                "translated_count": stats["translated_count"],
                "unresolved_tags": sorted(stats["unresolved_tags"]),
                "srt_error": stats["srt_error"],
            }
        )

    seasons = []
    seen_seasons = set()
    for row in rows:
        if row["season"] not in seen_seasons:
            seen_seasons.add(row["season"])
            seasons.append(row["season"])

    index = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "seasons": seasons,
        "episodes": index_episodes,
        "totals": {
            "episodes": len(index_episodes),
            "cues_total": totals["cues_total"],
            "cues_translated": totals["cues_translated"],
            "unresolved_tags": len(all_unresolved_tags),
        },
    }
    (out_dir / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    glossary = build_glossary_index(episodes_by_code)
    (out_dir / "glossary.json").write_text(json.dumps(glossary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OK: {len(index_episodes)} episodios -> {out_dir}")


if __name__ == "__main__":
    main()
