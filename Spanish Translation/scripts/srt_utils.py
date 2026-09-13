#!/usr/bin/env python3
"""Shared .srt parsing used by check_episode.py and build_site_data.py."""

import re

TIMESTAMP_RE = re.compile(r"^(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})")


class Cue:
    __slots__ = ("index", "start", "end", "text")

    def __init__(self, index, start, end, text):
        self.index = index
        self.start = start
        self.end = end
        self.text = text


def parse_srt_text(raw, label):
    blocks = re.split(r"\n\s*\n", raw.strip())
    cues = []
    for block in blocks:
        lines = block.strip("\n").split("\n")
        if len(lines) < 2:
            raise ValueError(f"{label}: bloque SRT incompleto: {block!r}")
        index_line, timestamp_line, *text_lines = lines
        try:
            index = int(index_line.strip())
        except ValueError:
            raise ValueError(f"{label}: número de cue inválido: {index_line!r}")
        m = TIMESTAMP_RE.match(timestamp_line.strip())
        if not m:
            raise ValueError(f"{label}: timestamp inválido en cue {index}: {timestamp_line!r}")
        cues.append(Cue(index, m.group(1), m.group(2), "\n".join(text_lines).strip()))
    return cues


def parse_srt(path):
    return parse_srt_text(path.read_text(encoding="utf-8"), str(path))
