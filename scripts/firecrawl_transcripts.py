#!/usr/bin/env python3
"""Fetch YouTube transcripts through Firecrawl's scrape + interact workflow.

Firecrawl returns the transcript from YouTube's dynamically opened transcript
panel. This provider is deliberately sequential and resumable because browser
sessions are billed by duration and should be stopped immediately after each
transcript is captured.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import channel_archive  # noqa: E402
import source_index_db  # noqa: E402


SCRAPE_ID_RE = re.compile(r"Scrape ID:\s*([0-9a-f-]{36})", re.IGNORECASE)
TRANSCRIPT_LINE_RE = re.compile(r"^\s*(\d+:\d{2}(?::\d{2})?)\s+(.+?)\s*$")
PROMPT = (
    "Click the YouTube button labeled Show transcript. Then return the complete "
    "transcript text with every timestamp and spoken line. Do not summarize, "
    "omit, or invent any content. If the transcript cannot be opened, return "
    "exactly TRANSCRIPT_UNAVAILABLE."
)


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def run(command: list[str], timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False, timeout=timeout)


def normalize_timestamp(value: str) -> str:
    parts = [int(part) for part in value.split(":")]
    if len(parts) == 2:
        hours, minutes, seconds = 0, parts[0], parts[1]
    else:
        hours, minutes, seconds = parts
    return f"[{hours:02d}:{minutes:02d}:{seconds:02d}]"


def normalize_transcript(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        match = TRANSCRIPT_LINE_RE.match(raw)
        if not match:
            continue
        spoken = re.sub(r"\s+", " ", match.group(2)).strip()
        if spoken:
            lines.append(f"{normalize_timestamp(match.group(1))} {spoken}")
    return lines


def scrape_id_from_output(stdout: str) -> str | None:
    match = SCRAPE_ID_RE.search(stdout)
    return match.group(1) if match else None


def interaction_text(payload: dict[str, Any]) -> str:
    """Support the CLI's prompt and code response field names."""
    for key in ("output", "result"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def stop_session(scrape_id: str) -> None:
    run(["firecrawl", "interact", "stop", scrape_id], timeout=30)


def fetch_one(item: dict[str, Any], transcript_dir: Path, force: bool) -> dict[str, Any]:
    video_id = item["id"]
    output = transcript_dir / f"{video_id}.md"
    result: dict[str, Any] = {
        "video_id": video_id,
        "title": item.get("title") or "",
        "url": item.get("url") or f"https://www.youtube.com/watch?v={video_id}",
        "started_at": utc_now(),
        "provider": "firecrawl-interact",
    }
    if output.exists() and not force:
        result.update({"status": "skipped", "path": str(output)})
        return result
    if not item.get("title"):
        result.update({"status": "unavailable", "error": "Inventory entry has no public title"})
        return result

    with tempfile.TemporaryDirectory(prefix=f"shaul-firecrawl-{video_id}-") as temp_dir:
        page_path = Path(temp_dir) / "page.md"
        interaction_path = Path(temp_dir) / "interaction.json"
        try:
            scrape = run(
                [
                    "firecrawl",
                    "scrape",
                    result["url"],
                    "--format",
                    "markdown",
                    "--only-main-content",
                    "--wait-for",
                    "3000",
                    "-o",
                    str(page_path),
                ],
                timeout=180,
            )
        except subprocess.TimeoutExpired:
            result.update({"status": "timeout", "error": "Firecrawl scrape timed out"})
            return result
        scrape_id = scrape_id_from_output(scrape.stdout + "\n" + scrape.stderr)
        if not scrape_id:
            result.update({"status": "error", "error": f"No scrape ID: {scrape.stderr[-500:]}"})
            return result

        try:
            try:
                interaction = run(
                    [
                        "firecrawl",
                        "interact",
                        "-s",
                        scrape_id,
                        "--prompt",
                        PROMPT,
                        "--timeout",
                        "120",
                        "--json",
                        "-o",
                        str(interaction_path),
                    ],
                    timeout=240,
                )
            except subprocess.TimeoutExpired:
                result.update({"status": "timeout", "error": "Firecrawl interaction timed out"})
                return result
            if not interaction_path.exists():
                result.update({"status": "error", "error": f"No interaction output: {interaction.stderr[-500:]}"})
                return result
            payload = json.loads(interaction_path.read_text(encoding="utf-8"))
            raw_text = interaction_text(payload)
            lines = normalize_transcript(raw_text)
            if not lines:
                result.update({"status": "unavailable", "error": raw_text[:500] or "No timestamped transcript returned"})
                return result
            channel_archive.write_transcript(output, item, lines, "firecrawl-interact")
            result.update({"status": "fetched", "path": str(output), "segments": len(lines), "scrape_id": scrape_id})
            return result
        finally:
            stop_session(scrape_id)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--video-id", action="append", dest="video_ids")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = json.loads(args.inventory.read_text(encoding="utf-8"))
    items = data.get("videos") or []
    if args.video_ids:
        selected = set(args.video_ids)
        items = [item for item in items if item.get("id") in selected]
    if args.limit:
        items = items[: args.limit]

    transcript_dir = args.inventory.parent / "transcripts"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    status_path = args.inventory.parent / "firecrawl-transcript-status.jsonl"
    db_path = ROOT / "private" / "sources" / "index.sqlite3"
    source_index_db.init_db(db_path)

    for index, item in enumerate(items, start=1):
        result = fetch_one(item, transcript_dir, args.force)
        with status_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False) + "\n")
        if result.get("status") == "fetched":
            source_index_db.index_file(db_path, Path(result["path"]).resolve(), ROOT)
        print(f"[{index}/{len(items)}] {result['status']}: {result['video_id']} {result.get('title', '')}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
