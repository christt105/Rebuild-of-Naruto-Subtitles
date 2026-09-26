#!/usr/bin/env python3
"""Check that the English baseline .srt is timed against a local video file.

Usage:
    check_video_sync.py <video-or-srt> <code> [--ffmpeg CMD] [--stream N] [--json]

<video-or-srt> is either a video with an embedded subtitle track (extracted
with ffmpeg) or an already extracted .srt. <code> is an episode code (S01E01).

The embedded track is compared with the English baseline cue by cue on start
and end timestamps. Text is not compared: the baseline wording was revised
after the videos were released, only the timings must still line up.

--ffmpeg is split like a shell command, so a containerised ffmpeg works too
(e.g. "docker exec jellyfin /usr/lib/jellyfin-ffmpeg/ffmpeg"); the video path
must then be the one the container sees.

Exit status is 0 when every baseline timing exists in the video, 1 otherwise.
"""

import argparse
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

from srt_utils import parse_srt, parse_srt_text

REPO_ROOT = Path(__file__).resolve().parents[2]
EN_DIR = REPO_ROOT / "Rebuild of Naruto - Subtitles"

CODE_RE = re.compile(r"^[Ss]\d{2}[Ee]\d{2}$")


def find_baseline(code):
    matches = [p for p in EN_DIR.rglob("*.en.srt") if code in p.name.upper()]
    if len(matches) != 1:
        sys.exit(f"expected one English baseline for {code}, found {len(matches)}")
    return matches[0]


def extract_embedded(video, ffmpeg, stream):
    cmd = shlex.split(ffmpeg) + [
        "-v", "error", "-i", video, "-map", f"0:s:{stream}", "-f", "srt", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0 or not result.stdout.strip():
        sys.exit(f"could not extract subtitle stream {stream} from {video}:\n{result.stderr.strip()}")
    return parse_srt_text(result.stdout.replace("\r", ""), video)


def compare(baseline, embedded):
    embedded_times = {(c.start, c.end) for c in embedded}
    baseline_times = {(c.start, c.end) for c in baseline}
    missing = [c for c in baseline if (c.start, c.end) not in embedded_times]
    extra = [c for c in embedded if (c.start, c.end) not in baseline_times]
    same_text = sum(1 for a, b in zip(baseline, embedded) if a.text == b.text)
    return {
        "baseline_cues": len(baseline),
        "video_cues": len(embedded),
        "baseline_timings_in_video": len(baseline) - len(missing),
        "video_timings_not_in_baseline": len(extra),
        "same_text_by_position": same_text,
        "missing_examples": [f"{c.index} {c.start} --> {c.end}" for c in missing[:5]],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source")
    parser.add_argument("code")
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--stream", type=int, default=0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not CODE_RE.match(args.code):
        sys.exit(f"invalid episode code: {args.code!r}")
    code = args.code.upper()

    baseline = parse_srt(find_baseline(code))
    if args.source.lower().endswith(".srt"):
        embedded = parse_srt(Path(args.source))
    else:
        embedded = extract_embedded(args.source, args.ffmpeg, args.stream)

    report = compare(baseline, embedded)
    ok = report["baseline_timings_in_video"] == report["baseline_cues"]

    if args.json:
        print(json.dumps({"code": code, "ok": ok, **report}, indent=2))
    else:
        print(f"{code}: {'OK' if ok else 'MISMATCH'}")
        print(f"  cues (baseline / video): {report['baseline_cues']} / {report['video_cues']}")
        print(f"  baseline timings found in video: {report['baseline_timings_in_video']} / {report['baseline_cues']}")
        print(f"  video timings not in baseline: {report['video_timings_not_in_baseline']}")
        print(f"  identical text by position: {report['same_text_by_position']}")
        for example in report["missing_examples"]:
            print(f"  missing: {example}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
