#!/usr/bin/env python3
"""Local reference database built from the Spanish (Planeta) manga and guides.

Runs OCR once per page (Tesseract, CPU only), groups words into speech
bubbles or paragraphs, and stores them in SQLite with full-text search so
terminology can be looked up while translating instead of re-running OCR.

The database holds copyrighted text and lives outside the repo
(`MANGA_REF_DB`, default `~/.local/share/manga-ref/manga_ref.db`). Never commit it.

Usage:
    manga_ref.py ingest <file.cbr> --kind manga|guide --title "Naruto" [--volume N] [--pages 10-40]
    manga_ref.py search "chakra" [--title Naruto] [--volume 1] [-n 20]
    manga_ref.py page <title> <volume> <page>
    manga_ref.py stats

Requires `tesseract` (with the `spa` language) and `unar` on PATH.
"""

import argparse
import csv
import io
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_DB = Path.home() / ".local/share/manga-ref/manga_ref.db"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
MIN_WORD_CONF = 50
MAX_OCR_HEIGHT = 2600
ENGINE = "tesseract-spa"

SCHEMA = """
CREATE TABLE IF NOT EXISTS works (
    id INTEGER PRIMARY KEY,
    kind TEXT NOT NULL CHECK (kind IN ('manga', 'guide')),
    title TEXT NOT NULL,
    volume INTEGER NOT NULL DEFAULT 0,
    source_file TEXT NOT NULL,
    UNIQUE (title, volume)
);
CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY,
    work_id INTEGER NOT NULL REFERENCES works(id) ON DELETE CASCADE,
    page INTEGER NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    engine TEXT NOT NULL,
    UNIQUE (work_id, page)
);
CREATE TABLE IF NOT EXISTS blocks (
    id INTEGER PRIMARY KEY,
    page_id INTEGER NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
    idx INTEGER NOT NULL,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    w INTEGER NOT NULL,
    h INTEGER NOT NULL,
    conf REAL NOT NULL,
    text TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS blocks_page ON blocks(page_id, idx);
CREATE VIRTUAL TABLE IF NOT EXISTS blocks_fts USING fts5(
    text, content='blocks', content_rowid='id',
    tokenize='unicode61 remove_diacritics 2'
);
"""


def db_path():
    return Path(os.environ.get("MANGA_REF_DB", DEFAULT_DB))


def connect():
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


def image_size(path):
    from PIL import Image

    with Image.open(path) as img:
        return img.size


def shrink_for_ocr(image, tmp_dir):
    """Downscale very large (e.g. AI-upscaled) pages: OCR time grows with pixel count.

    Returns the image to OCR; stored bounding boxes and page size refer to that image.
    """
    from PIL import Image

    with Image.open(image) as img:
        if img.height <= MAX_OCR_HEIGHT:
            return image
        scale = MAX_OCR_HEIGHT / img.height
        small = img.convert("L").resize((round(img.width * scale), MAX_OCR_HEIGHT), Image.LANCZOS)
        target = Path(tmp_dir) / "ocr_page.png"
        small.save(target)
        return target


def run_tesseract(image, psm):
    result = subprocess.run(
        ["tesseract", str(image), "-", "-l", "spa", "--psm", str(psm), "tsv"],
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "OMP_THREAD_LIMIT": "1"},
    )
    reader = csv.DictReader(io.StringIO(result.stdout), delimiter="\t", quoting=csv.QUOTE_NONE)
    words = []
    for row in reader:
        text = (row["text"] or "").strip()
        if row["level"] != "5" or not text:
            continue
        conf = float(row["conf"])
        if conf < MIN_WORD_CONF:
            continue
        words.append(
            {
                "text": text,
                "conf": conf,
                "x": int(row["left"]),
                "y": int(row["top"]),
                "w": int(row["width"]),
                "h": int(row["height"]),
                "line": (int(row["block_num"]), int(row["par_num"]), int(row["line_num"])),
                "para": (int(row["block_num"]), int(row["par_num"])),
            }
        )
    return words


def make_block(words):
    x0 = min(w["x"] for w in words)
    y0 = min(w["y"] for w in words)
    x1 = max(w["x"] + w["w"] for w in words)
    y1 = max(w["y"] + w["h"] for w in words)
    return {
        "x": x0,
        "y": y0,
        "w": x1 - x0,
        "h": y1 - y0,
        "conf": sum(w["conf"] for w in words) / len(words),
        "words": words,
    }


def group_lines(words):
    lines = {}
    for word in words:
        lines.setdefault(word["line"], []).append(word)
    result = []
    for line_words in lines.values():
        line_words.sort(key=lambda w: w["x"])
        result.append(make_block(line_words))
    return result


def merge_bubbles(lines):
    """Union lines that are close relative to their own height (same bubble)."""
    parent = list(range(len(lines)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def near(a, b):
        line_h = max(1, min(a["h"], b["h"]))
        gap_y = max(a["y"], b["y"]) - min(a["y"] + a["h"], b["y"] + b["h"])
        gap_x = max(a["x"], b["x"]) - min(a["x"] + a["w"], b["x"] + b["w"])
        return gap_y < 1.2 * line_h and gap_x < 2.0 * line_h

    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            if near(lines[i], lines[j]):
                parent[find(i)] = find(j)

    groups = {}
    for i, line in enumerate(lines):
        groups.setdefault(find(i), []).append(line)
    blocks = []
    for group in groups.values():
        group.sort(key=lambda l: (l["y"], l["x"]))
        words = [w for line in group for w in line["words"]]
        block = make_block(words)
        block["text"] = join_lines(group)
        blocks.append(block)
    return blocks


def reading_order(blocks, height, rtl):
    """Rows of the page top to bottom, right to left inside a row (manga)."""
    band = max(1, height // 6)
    sign = -1 if rtl else 1
    blocks.sort(key=lambda b: (b["y"] // band, sign * (b["x"] + b["w"] // 2)))
    return blocks


def join_lines(lines):
    """Join words per line, merging words split by a line-end hyphen."""
    text = ""
    for line in lines:
        chunk = " ".join(w["text"] for w in line["words"])
        if text.endswith("-"):
            text = text[:-1] + chunk
        else:
            text = f"{text}\n{chunk}" if text else chunk
    return text


def usable(block):
    letters = sum(c.isalpha() for c in block["text"])
    return letters >= 3 and letters / max(1, len(block["text"].replace("\n", ""))) >= 0.5


def ocr_page(image, kind, tmp_dir):
    image = shrink_for_ocr(image, tmp_dir)
    width, height = image_size(image)
    if kind == "guide":
        words = run_tesseract(image, 3)
        paragraphs = {}
        for word in words:
            paragraphs.setdefault(word["para"], []).append(word)
        blocks = []
        for para_words in paragraphs.values():
            lines = sorted(group_lines(para_words), key=lambda l: (l["y"], l["x"]))
            block = make_block(para_words)
            block["text"] = join_lines(lines)
            blocks.append(block)
        blocks.sort(key=lambda b: (b["y"], b["x"]))
    else:
        words = run_tesseract(image, 11)
        blocks = reading_order(merge_bubbles(group_lines(words)), height, rtl=True)
    return width, height, [b for b in blocks if usable(b)]


def parse_range(spec):
    if not spec:
        return None
    start, _, end = spec.partition("-")
    return int(start), int(end or start)


def list_pages(root):
    images = [p for p in root.rglob("*") if p.suffix.lower() in IMAGE_SUFFIXES]
    return sorted(images, key=lambda p: str(p))


def cmd_ingest(args):
    os.nice(19)
    source = Path(args.file).expanduser()
    conn = connect()
    volume = args.volume or 0
    conn.execute(
        "INSERT OR IGNORE INTO works (kind, title, volume, source_file) VALUES (?, ?, ?, ?)",
        (args.kind, args.title, volume, source.name),
    )
    work_id = conn.execute(
        "SELECT id FROM works WHERE title = ? AND volume = ?", (args.title, volume)
    ).fetchone()[0]
    done = {r[0] for r in conn.execute("SELECT page FROM pages WHERE work_id = ?", (work_id,))}
    span = parse_range(args.pages)

    with tempfile.TemporaryDirectory(prefix="manga-ref-") as tmp:
        subprocess.run(["unar", "-q", "-o", tmp, str(source)], check=True, stdout=subprocess.DEVNULL)
        pages = list_pages(Path(tmp))
        total = len(pages)
        for number, image in enumerate(pages, start=1):
            if span and not span[0] <= number <= span[1]:
                continue
            if number in done:
                continue
            width, height, blocks = ocr_page(image, args.kind, tmp)
            with conn:
                cur = conn.execute(
                    "INSERT INTO pages (work_id, page, width, height, engine) VALUES (?, ?, ?, ?, ?)",
                    (work_id, number, width, height, ENGINE),
                )
                for idx, block in enumerate(blocks):
                    row = conn.execute(
                        "INSERT INTO blocks (page_id, idx, x, y, w, h, conf, text) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (cur.lastrowid, idx, block["x"], block["y"], block["w"], block["h"],
                         round(block["conf"], 1), block["text"]),
                    )
                    conn.execute(
                        "INSERT INTO blocks_fts (rowid, text) VALUES (?, ?)",
                        (row.lastrowid, block["text"]),
                    )
            print(f"{args.title} {volume} page {number}/{total}: {len(blocks)} blocks", file=sys.stderr)
    conn.close()


def fts_query(text):
    return " ".join('"' + term.replace('"', "") + '"' for term in text.split())


def cmd_search(args):
    conn = connect()
    sql = (
        "SELECT w.title, w.volume, p.page, b.idx, b.text "
        "FROM blocks_fts f JOIN blocks b ON b.id = f.rowid "
        "JOIN pages p ON p.id = b.page_id JOIN works w ON w.id = p.work_id "
        "WHERE blocks_fts MATCH ?"
    )
    params = [fts_query(args.query)]
    if args.title:
        sql += " AND w.title = ?"
        params.append(args.title)
    if args.volume is not None:
        sql += " AND w.volume = ?"
        params.append(args.volume)
    sql += " ORDER BY w.title, w.volume, p.page, b.idx LIMIT ?"
    params.append(args.n)
    for title, volume, page, idx, text in conn.execute(sql, params):
        print(f"[{title} {volume} p{page} #{idx}] {text.replace(chr(10), ' ')}")


def cmd_page(args):
    conn = connect()
    rows = conn.execute(
        "SELECT b.idx, b.conf, b.text FROM blocks b JOIN pages p ON p.id = b.page_id "
        "JOIN works w ON w.id = p.work_id WHERE w.title = ? AND w.volume = ? AND p.page = ? "
        "ORDER BY b.idx",
        (args.title, args.volume, args.page),
    ).fetchall()
    for idx, conf, text in rows:
        print(f"#{idx} ({conf:.0f}) {text.replace(chr(10), ' ')}")


def cmd_stats(_args):
    conn = connect()
    for row in conn.execute(
        "SELECT w.kind, w.title, w.volume, COUNT(DISTINCT p.id), COUNT(b.id) "
        "FROM works w LEFT JOIN pages p ON p.work_id = w.id LEFT JOIN blocks b ON b.page_id = p.id "
        "GROUP BY w.id ORDER BY w.title, w.volume"
    ):
        print("{} {} vol {}: {} pages, {} blocks".format(*row))


def main():
    for tool in ("tesseract", "unar"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found on PATH")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    ingest = sub.add_parser("ingest")
    ingest.add_argument("file")
    ingest.add_argument("--kind", choices=["manga", "guide"], required=True)
    ingest.add_argument("--title", required=True)
    ingest.add_argument("--volume", type=int)
    ingest.add_argument("--pages", help="page range, e.g. 10-40")
    ingest.set_defaults(func=cmd_ingest)

    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--title")
    search.add_argument("--volume", type=int)
    search.add_argument("-n", type=int, default=20)
    search.set_defaults(func=cmd_search)

    page = sub.add_parser("page")
    page.add_argument("title")
    page.add_argument("volume", type=int)
    page.add_argument("page", type=int)
    page.set_defaults(func=cmd_page)

    stats = sub.add_parser("stats")
    stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
