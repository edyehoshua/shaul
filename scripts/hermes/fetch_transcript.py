#!/usr/bin/env python3
"""Fetch YouTube transcripts for Hermes research workflows.

Strategy:
1) Try youtube-transcript-api first.
2) Fall back to yt-dlp auto subtitles if needed.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

YouTubeTranscriptApi: Any = None
NoTranscriptFound: type[Exception] = Exception
TranscriptsDisabled: type[Exception] = Exception
VideoUnavailable: type[Exception] = Exception
_YTA_LOADED = False


def load_transcript_api() -> None:
    """Load youtube-transcript-api lazily to keep fallback behavior when missing."""
    global YouTubeTranscriptApi
    global NoTranscriptFound
    global TranscriptsDisabled
    global VideoUnavailable
    global _YTA_LOADED

    if _YTA_LOADED:
        return

    try:
        from importlib import import_module

        module = import_module("youtube_transcript_api")
        errors_module = import_module("youtube_transcript_api._errors")

        YouTubeTranscriptApi = getattr(module, "YouTubeTranscriptApi", None)
        NoTranscriptFound = getattr(errors_module, "NoTranscriptFound", Exception)
        TranscriptsDisabled = getattr(errors_module, "TranscriptsDisabled", Exception)
        VideoUnavailable = getattr(errors_module, "VideoUnavailable", Exception)
    except ImportError:
        # Keep defaults so caller can transparently use fallback logic.
        pass

    _YTA_LOADED = True


def extract_video_id(url: str) -> str:
    patterns = [
        r"(?:v=)([A-Za-z0-9_-]{11})",
        r"youtu\.be/([A-Za-z0-9_-]{11})",
        r"youtube\.com/embed/([A-Za-z0-9_-]{11})",
        r"youtube\.com/shorts/([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not parse video id from URL: {url}")


def sec_to_ts(seconds: float) -> str:
    whole = int(seconds)
    h = whole // 3600
    m = (whole % 3600) // 60
    s = whole % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def normalize_lines(items: Iterable[dict]) -> list[str]:
    lines: list[str] = []
    for item in items:
        start = float(item.get("start", 0.0))
        text = str(item.get("text", "")).replace("\n", " ").strip()
        if not text:
            continue
        lines.append(f"[{sec_to_ts(start)}] {text}")
    return lines


def try_transcript_api(video_id: str, preferred_languages: list[str]) -> list[str] | None:
    load_transcript_api()

    if YouTubeTranscriptApi is None:
        return None

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        transcript = None
        for lang in preferred_languages:
            try:
                transcript = transcript_list.find_transcript([lang])
                break
            except NoTranscriptFound:
                continue

        if transcript is None:
            for generated in transcript_list:
                if generated.is_generated:
                    transcript = generated
                    break

        if transcript is None:
            return None

        fetched = transcript.fetch()
        return normalize_lines(fetched)
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable):
        return None


def run_cmd(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=False, text=True, capture_output=True)


def fetch_video_meta(url: str) -> dict:
    proc = run_cmd(["yt-dlp", "--dump-single-json", "--no-warnings", url])
    if proc.returncode != 0:
        return {"url": url}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"url": url}


def parse_vtt(vtt_path: Path) -> list[str]:
    lines: list[str] = []
    for raw in vtt_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("WEBVTT"):
            continue
        if "-->" in line:
            continue
        if line.isdigit():
            continue
        line = re.sub(r"<[^>]+>", "", line)
        line = re.sub(r"&nbsp;", " ", line)
        if line:
            lines.append(line)
    deduped: list[str] = []
    prev = ""
    for line in lines:
        if line != prev:
            deduped.append(line)
        prev = line
    return deduped


def try_ytdlp_fallback(url: str, out_dir: Path, video_id: str) -> list[str] | None:
    out_tpl = out_dir / f"{video_id}.%(ext)s"
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--write-auto-subs",
        "--write-subs",
        "--sub-langs",
        "es.*,en.*",
        "--sub-format",
        "vtt",
        "-o",
        str(out_tpl),
        url,
    ]
    proc = run_cmd(cmd)
    if proc.returncode != 0:
        return None

    candidates = sorted(out_dir.glob(f"{video_id}*.vtt"))
    if not candidates:
        return None
    return parse_vtt(candidates[0])


def write_output(out_file: Path, lines: list[str], meta: dict) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "---",
        f"source: {meta.get('webpage_url') or meta.get('url', '')}",
        f"video_id: {meta.get('id', '')}",
        f"title: {json.dumps(meta.get('title', ''), ensure_ascii=False)}",
        f"channel: {json.dumps(meta.get('channel', ''), ensure_ascii=False)}",
        f"fetched_at: {datetime.utcnow().isoformat()}Z",
        "---",
        "",
    ]
    body = "\n".join(lines).strip() + "\n"
    out_file.write_text("\n".join(header) + body, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch transcript from a YouTube URL")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "--langs",
        default="es,en",
        help="Preferred language order, comma separated (default: es,en)",
    )
    parser.add_argument(
        "--outdir",
        default="private/hermes/sources",
        help="Output directory for transcript files",
    )
    args = parser.parse_args()

    preferred = [lang.strip() for lang in args.langs.split(",") if lang.strip()]
    out_dir = Path(args.outdir)

    try:
        video_id = extract_video_id(args.url)
    except ValueError as err:
        print(str(err), file=sys.stderr)
        return 2

    meta = fetch_video_meta(args.url)
    meta.setdefault("id", video_id)
    meta.setdefault("webpage_url", args.url)

    lines = try_transcript_api(video_id, preferred)
    if lines is None:
        lines = try_ytdlp_fallback(args.url, out_dir, video_id)

    if not lines:
        print("Transcript not available via youtube-transcript-api or yt-dlp fallback.", file=sys.stderr)
        return 1

    out_file = out_dir / f"{video_id}.md"
    write_output(out_file, lines, meta)
    print(f"Saved transcript: {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
