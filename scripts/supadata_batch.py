#!/usr/bin/env python3
"""Fetch many YouTube transcripts through Supadata's paid batch endpoint."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import channel_archive
import source_index_db
import supadata_transcripts as api


def post_json(path: str, api_key: str, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(
        f"{api.BASE_URL}/{path.lstrip('/')}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"x-api-key": api_key, "accept": "application/json", "content-type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {"error": body[:500]}
        return exc.code, payload


def get_json(path: str, api_key: str) -> tuple[int, dict[str, Any]]:
    return api.request_json(path, api_key, timeout=90)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--status-file", type=Path)
    parser.add_argument("--language", default="es")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--poll-seconds", type=int, default=5)
    parser.add_argument("--result-file", type=Path, help="Process a previously downloaded completed batch response")
    parser.add_argument("--job-id", help="Job ID to record when processing --result-file")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    api_key = api.configured_api_key()
    if not api_key:
        print("SUPADATA_API_KEY is not configured")
        return 2

    data = json.loads(args.inventory.read_text(encoding="utf-8"))
    data_root = args.inventory.parent.parent
    transcript_dir = args.output_dir or api.ROOT / "private" / "transcripts" / args.inventory.stem
    status_path = args.status_file or data_root / "status" / f"{args.inventory.stem}.supadata-batch.jsonl"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    status_path.parent.mkdir(parents=True, exist_ok=True)
    items = [item for item in data.get("videos", []) if args.force or not (transcript_dir / f"{item['id']}.md").exists()]
    if args.limit:
        items = items[: args.limit]
    if not items:
        print("No missing transcripts to process")
        return 0

    video_ids = [item["id"] for item in items]
    if args.result_file:
        result = json.loads(args.result_file.read_text(encoding="utf-8"))
        job_id = args.job_id or "recovered-batch"
        if str(result.get("status") or "").lower() != "completed":
            print(f"Saved Supadata result is not completed: {result.get('status')}")
            return 1
        print(f"Processing saved Supadata batch result for {len(items)} videos", flush=True)
    else:
        status, response = post_json(
            "/youtube/transcript/batch",
            api_key,
            {"videoIds": video_ids, "lang": args.language, "text": False},
        )
        if status != 200 or not response.get("jobId"):
            print(f"Supadata batch request failed (HTTP {status}): {response.get('error', response.get('message', response))}")
            return 1

        job_id = response["jobId"]
        print(f"Started Supadata batch job {job_id} for {len(items)} videos", flush=True)
        while True:
            time.sleep(max(1, args.poll_seconds))
            status, result = get_json(f"/youtube/batch/{job_id}", api_key)
            job_status = str(result.get("status") or "").lower()
            print(f"Batch status: {job_status or status}", flush=True)
            if job_status == "completed":
                break
            if job_status == "failed":
                print(f"Supadata batch failed: {result.get('error', result)}")
                return 1

    item_by_id = {item["id"]: item for item in items}
    db_path = api.ROOT / "private" / "sources" / "index.sqlite3"
    source_index_db.init_db(db_path)
    results = result.get("results") or []
    with status_path.open("a", encoding="utf-8") as handle:
        for entry in results:
            video_id = str(entry.get("videoId") or "")
            item = item_by_id.get(video_id)
            if not item:
                continue
            transcript = entry.get("transcript")
            output = transcript_dir / f"{video_id}.md"
            row = {
                "video_id": video_id,
                "title": item.get("title") or "",
                "url": item.get("url") or f"https://www.youtube.com/watch?v={video_id}",
                "started_at": api.utc_now(),
                "provider": "supadata-batch",
                "batch_job_id": job_id,
            }
            if transcript:
                lines = api.transcript_lines(transcript)
                if lines:
                    channel_archive.write_transcript(output, item, lines, "supadata-batch")
                    row.update({"status": "fetched", "path": str(output), "segments": len(lines), "language": transcript.get("lang", args.language)})
                    source_index_db.index_file(db_path, output.resolve(), api.ROOT)
                else:
                    row.update({"status": "unavailable", "error": "Empty transcript"})
            else:
                row.update({"status": "unavailable", "error": entry.get("errorCode", "Transcript unavailable")})
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(f"{row['status']}: {video_id} {row['title']}", flush=True)
    stats = result.get("stats") or {}
    print(f"Batch complete: total={stats.get('total', len(results))} succeeded={stats.get('succeeded', 0)} failed={stats.get('failed', 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
