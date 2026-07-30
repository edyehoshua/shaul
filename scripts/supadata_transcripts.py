#!/usr/bin/env python3
"""Fetch timestamped YouTube transcripts through Supadata.

This provider intentionally uses Supadata's ``native`` mode only. It fetches
existing captions without asking Supadata to generate an AI transcript, which
keeps this first pass inexpensive. Videos without native captions are recorded
as unavailable and can be retried later through the VPS/yt-dlp fallback.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://api.supadata.ai/v1"
DEFAULT_LANGUAGE = "es"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import channel_archive  # noqa: E402
import source_index_db  # noqa: E402


class SupadataError(RuntimeError):
    """An API or transcript-processing failure."""


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def configured_api_key() -> str | None:
    """Read the key from the environment or the documented local config file."""
    if value := os.environ.get("SUPADATA_API_KEY"):
        return value
    config_path = Path.home() / ".config" / "shaul" / "supadata.env"
    if not config_path.is_file():
        return None
    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or not line.startswith("SUPADATA_API_KEY="):
            continue
        value = line.split("=", 1)[1].strip().strip("'\"")
        if value:
            return value
    return None


def request_json(
    path: str,
    api_key: str,
    params: dict[str, str] | None = None,
    timeout: int = 90,
) -> tuple[int, dict[str, Any]]:
    query = urllib.parse.urlencode(params or {})
    url = f"{BASE_URL}/{path.lstrip('/')}"
    if query:
        url = f"{url}?{query}"
    request = urllib.request.Request(
        url,
        headers={"x-api-key": api_key, "accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            status = response.status
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        status = exc.code
    try:
        payload = json.loads(body) if body else {}
    except json.JSONDecodeError as exc:
        raise SupadataError(f"Supadata returned invalid JSON ({status}): {body[:300]}") from exc
    if not isinstance(payload, dict):
        raise SupadataError(f"Supadata returned an unexpected response ({status})")
    return status, payload


def fetch_transcript(
    api_key: str,
    video_url: str,
    language: str,
    poll_timeout: int,
) -> tuple[int, dict[str, Any]]:
    status, payload = request_json(
        "/transcript",
        api_key,
        {
            "url": video_url,
            "lang": language,
            "text": "false",
            "mode": "native",
        },
    )
    job_id = payload.get("jobId")
    if status != 202 and not job_id:
        return status, payload
    if not job_id:
        raise SupadataError(f"Supadata returned HTTP {status} without a job ID")

    deadline = time.monotonic() + poll_timeout
    while time.monotonic() < deadline:
        time.sleep(1)
        job_status, job = request_json(f"/transcript/{job_id}", api_key)
        current = str(job.get("status") or "").lower()
        if current == "completed":
            return job_status, job
        if current == "failed":
            raise SupadataError(str(job.get("error") or "Supadata job failed"))
    raise SupadataError(f"Supadata job timed out after {poll_timeout} seconds: {job_id}")


def timestamp(milliseconds: Any) -> str:
    total_seconds = max(0, int(float(milliseconds or 0) / 1000))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"[{hours:02d}:{minutes:02d}:{seconds:02d}]"


def transcript_lines(payload: dict[str, Any]) -> list[str]:
    content = payload.get("content")
    if content is None and isinstance(payload.get("result"), dict):
        content = payload["result"].get("content")
    if isinstance(content, list):
        lines: list[str] = []
        for segment in content:
            if not isinstance(segment, dict):
                continue
            text = re.sub(r"\s+", " ", str(segment.get("text") or "")).strip()
            if text:
                lines.append(f"{timestamp(segment.get('offset'))} {text}")
        return lines
    if isinstance(content, str) and content.strip():
        # Supadata normally returns timestamped chunks with text=false. Keep a
        # defensive plain-text fallback without fabricating timestamps.
        return [line.strip() for line in content.splitlines() if line.strip()]
    return []


def fetch_one(
    item: dict[str, Any],
    transcript_dir: Path,
    api_key: str,
    language: str,
    poll_timeout: int,
    force: bool,
) -> dict[str, Any]:
    video_id = str(item["id"])
    output = transcript_dir / f"{video_id}.md"
    result: dict[str, Any] = {
        "video_id": video_id,
        "title": item.get("title") or "",
        "url": item.get("url") or f"https://www.youtube.com/watch?v={video_id}",
        "started_at": utc_now(),
        "provider": "supadata-native",
    }
    if output.exists() and not force:
        result.update({"status": "skipped", "path": str(output)})
        return result
    if not item.get("title"):
        result.update({"status": "unavailable", "error": "Inventory entry has no public title"})
        return result
    try:
        http_status, payload = fetch_transcript(api_key, result["url"], language, poll_timeout)
        lines = transcript_lines(payload)
        if http_status == 206 or not lines:
            result.update({"status": "unavailable", "http_status": http_status, "error": payload.get("error", "No native transcript available")})
            return result
        channel_archive.write_transcript(output, item, lines, "supadata-native")
        result.update({"status": "fetched", "http_status": http_status, "path": str(output), "segments": len(lines), "language": payload.get("lang", language)})
    except Exception as exc:  # keep the batch resumable when one video fails
        result.update({"status": "error", "error": f"{type(exc).__name__}: {exc}"})
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--status-file", type=Path)
    parser.add_argument("--language", default=DEFAULT_LANGUAGE)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--poll-timeout", type=int, default=900)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--video-id", action="append", dest="video_ids")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    api_key = configured_api_key()
    if not api_key:
        print("SUPADATA_API_KEY is not set", file=sys.stderr)
        return 2

    data = json.loads(args.inventory.read_text(encoding="utf-8"))
    items = data.get("videos") or []
    if args.video_ids:
        selected = set(args.video_ids)
        items = [item for item in items if item.get("id") in selected]
    if args.limit:
        items = items[: args.limit]

    data_root = args.inventory.parent.parent
    transcript_dir = args.output_dir or ROOT / "private" / "transcripts" / args.inventory.stem
    status_path = args.status_file or data_root / "status" / f"{args.inventory.stem}.supadata.jsonl"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    status_path.parent.mkdir(parents=True, exist_ok=True)
    db_path = ROOT / "private" / "sources" / "index.sqlite3"
    source_index_db.init_db(db_path)

    print(f"Fetching {len(items)} videos with {max(1, args.workers)} workers in native mode", flush=True)
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [
            pool.submit(fetch_one, item, transcript_dir, api_key, args.language, args.poll_timeout, args.force)
            for item in items
        ]
        for index, future in enumerate(as_completed(futures), start=1):
            result = future.result()
            with status_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
            if result.get("status") == "fetched":
                source_index_db.index_file(db_path, Path(result["path"]).resolve(), ROOT)
            print(f"[{index}/{len(futures)}] {result['status']}: {result['video_id']} {result.get('title', '')}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
