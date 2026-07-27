#!/usr/bin/env python3
"""Inventory a YouTube channel and fetch its public video transcripts.

The channel manifest is the durable inventory. Transcript files remain the raw
source of truth, while the SQLite database is updated as a query index.
The command is deliberately resumable: an existing transcript is skipped
unless --force is supplied.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHANNEL = "https://www.youtube.com/@EricdeJes%C3%BAsRodr%C3%ADguezMendoza"
DEFAULT_ARCHIVE = ROOT / "data" / "inventories"
VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_transcript  # noqa: E402
import source_index_db  # noqa: E402


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def run_yt_dlp(url: str) -> dict[str, Any] | None:
    command = [
        "yt-dlp",
        "--skip-download",
        "--flat-playlist",
        "--dump-single-json",
        "--ignore-errors",
        "--no-warnings",
        url,
    ]
    process = subprocess.run(command, capture_output=True, text=True, check=False)
    if process.returncode != 0 or not process.stdout.strip():
        return None
    try:
        return json.loads(process.stdout)
    except json.JSONDecodeError:
        return None


def channel_root(url: str) -> str:
    parsed = urlsplit(url)
    path = parsed.path.rstrip("/")
    for suffix in ("/playlists", "/videos", "/streams", "/featured", "/community"):
        if path.endswith(suffix):
            path = path[: -len(suffix)]
            break
    return urlunsplit((parsed.scheme or "https", parsed.netloc, path, "", ""))


def absolute_entry_url(entry: dict[str, Any], kind: str) -> str:
    value = entry.get("webpage_url") or entry.get("url") or ""
    entry_id = str(entry.get("id") or "")
    if value.startswith("http"):
        return value
    if kind == "video" and VIDEO_ID_RE.match(entry_id):
        return f"https://www.youtube.com/watch?v={entry_id}"
    if kind == "playlist" and entry_id:
        return f"https://www.youtube.com/playlist?list={entry_id}"
    return value


def classify_entry(entry: dict[str, Any]) -> tuple[str, str] | None:
    entry_id = str(entry.get("id") or "")
    value = str(entry.get("webpage_url") or entry.get("url") or "")
    ie_key = str(entry.get("ie_key") or entry.get("extractor_key") or "").lower()
    entry_type = str(entry.get("_type") or "")

    if "playlist" in ie_key or "playlist?list=" in value or entry_type == "playlist":
        return "playlist", entry_id
    if VIDEO_ID_RE.match(entry_id) or "watch?v=" in value or "/shorts/" in value:
        return "video", entry_id
    return None


def collect_page(url: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    payload = run_yt_dlp(url)
    if not payload:
        return [], []

    videos: list[dict[str, Any]] = []
    playlists: list[dict[str, Any]] = []
    entries = payload.get("entries") or []
    for raw_entry in entries:
        if not isinstance(raw_entry, dict):
            continue
        classified = classify_entry(raw_entry)
        if not classified:
            continue
        kind, entry_id = classified
        if not entry_id:
            continue
        item = {
            "id": entry_id,
            "title": raw_entry.get("title") or "",
            "url": absolute_entry_url(raw_entry, kind),
            "channel": payload.get("channel") or payload.get("uploader") or "",
            "channel_id": payload.get("channel_id") or "",
            "playlist": payload.get("title") or "",
        }
        if kind == "video":
            videos.append(item)
        else:
            playlists.append(item)
    return videos, playlists


def archive_slug(channel_url: str) -> str:
    parsed = urlsplit(channel_url)
    handle = unquote(parsed.path.strip("/").split("/")[0])
    handle = handle.removeprefix("@") or "youtube-channel"
    return re.sub(r"[^A-Za-z0-9_-]+", "-", handle).strip("-").lower()


def archive_dir(channel_url: str, archive_root: Path) -> Path:
    return archive_root / archive_slug(channel_url)


def inventory(channel_url: str, archive_root: Path) -> Path:
    root = channel_root(channel_url)
    archive_root.mkdir(parents=True, exist_ok=True)

    videos_by_id: dict[str, dict[str, Any]] = {}
    playlists_by_id: dict[str, dict[str, Any]] = {}

    page_urls = [f"{root}/videos", f"{root}/playlists"]
    for page_url in page_urls:
        videos, playlists = collect_page(page_url)
        for item in videos:
            videos_by_id.setdefault(item["id"], item)
        for item in playlists:
            playlists_by_id.setdefault(item["id"], item)

    # Playlist pages may expose videos that are not returned by the uploads tab.
    for playlist in list(playlists_by_id.values()):
        videos, nested_playlists = collect_page(playlist["url"])
        for item in videos:
            item["playlist_id"] = playlist["id"]
            item["playlist_title"] = playlist.get("title") or ""
            # A video already discovered on /videos lacks its playlist ownership.
            # Keep that canonical entry but enrich it with the playlist metadata;
            # otherwise whole playlists are falsely counted as one video.
            existing = videos_by_id.get(item["id"])
            if existing is None:
                videos_by_id[item["id"]] = item
            elif not existing.get("playlist_id"):
                existing.update({
                    "playlist_id": item["playlist_id"],
                    "playlist_title": item["playlist_title"],
                })
        for item in nested_playlists:
            playlists_by_id.setdefault(item["id"], item)

    payload = {
        "schema_version": 1,
        "channel_url": root,
        "channel_slug": archive_slug(root),
        "generated_at": utc_now(),
        "playlists": sorted(playlists_by_id.values(), key=lambda item: item.get("title", "").lower()),
        "videos": sorted(
            videos_by_id.values(),
            key=lambda item: (item.get("title") or "").lower(),
        ),
    }
    path = archive_root / f"{archive_slug(root)}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Inventory: {path}")
    print(f"Videos: {len(payload['videos'])}; playlists: {len(payload['playlists'])}")
    return path


def load_inventory(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_transcript(path: Path, item: dict[str, Any], lines: list[str], source: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "source": item.get("url") or f"https://www.youtube.com/watch?v={item['id']}",
        "video_id": item["id"],
        "title": item.get("title") or item["id"],
        "channel": item.get("channel") or "Eric de Jesús Rodríguez Mendoza",
        "transcript_source": source,
        "fetched_at": utc_now(),
    }
    header = ["---"]
    for key, value in metadata.items():
        header.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    header.extend(["---", ""])
    path.write_text("\n".join(header) + "\n".join(lines).strip() + "\n", encoding="utf-8")


def fetch_one(item: dict[str, Any], transcript_dir: Path, force: bool) -> dict[str, Any]:
    video_id = item["id"]
    output = transcript_dir / f"{video_id}.md"
    result: dict[str, Any] = {
        "video_id": video_id,
        "title": item.get("title") or "",
        "url": item.get("url") or f"https://www.youtube.com/watch?v={video_id}",
        "started_at": utc_now(),
    }
    if not item.get("title"):
        result.update({"status": "unavailable", "error": "Inventory entry has no public title"})
        return result
    if output.exists() and not force:
        result.update({"status": "skipped", "path": str(output)})
        return result

    url = result["url"]
    preferred = ["es", "es-419", "en"]
    try:
        lines = fetch_transcript.try_ytdlp_fallback(url, transcript_dir, video_id)
        source = "yt-dlp-subtitles"
        if lines is None:
            try:
                lines = fetch_transcript.try_transcript_api(video_id, preferred)
            except Exception as exc:
                result["transcript_api_error"] = f"{type(exc).__name__}: {exc}"
                lines = None
            source = "youtube-transcript-api"
        for temporary in transcript_dir.glob(f"{video_id}*.vtt"):
            temporary.unlink(missing_ok=True)
        if not lines:
            result.update({"status": "unavailable", "error": result.get("transcript_api_error", "No Spanish/English transcript available")})
            return result
        write_transcript(output, item, lines, source)
        result.update({"status": "fetched", "source": source, "path": str(output), "segments": len(lines)})
    except Exception as exc:  # keep the batch resumable when one video fails
        result.update({"status": "error", "error": f"{type(exc).__name__}: {exc}"})
    return result


def transcripts(
    inventory_path: Path,
    workers: int,
    limit: int | None,
    force: bool,
    transcript_dir: Path | None,
    status_path: Path | None,
) -> None:
    data = load_inventory(inventory_path)
    target = inventory_path.parent.parent
    transcript_dir = transcript_dir or ROOT / "private" / "transcripts" / inventory_path.stem
    transcript_dir.mkdir(parents=True, exist_ok=True)
    status_path = status_path or target / "status" / f"{inventory_path.stem}.ytdlp.jsonl"
    status_path.parent.mkdir(parents=True, exist_ok=True)
    items = data.get("videos") or []
    if limit:
        items = items[:limit]
    print(f"Fetching {len(items)} videos with {workers} workers")

    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = [pool.submit(fetch_one, item, transcript_dir, force) for item in items]
        for index, future in enumerate(as_completed(futures), start=1):
            result = future.result()
            results.append(result)
            with status_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
            print(f"[{index}/{len(futures)}] {result['status']}: {result['video_id']} {result.get('title', '')}")

    db_path = ROOT / "private" / "sources" / "index.sqlite3"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    source_index_db.init_db(db_path)
    for result in results:
        if result.get("status") != "fetched":
            continue
        source_index_db.index_file(db_path, Path(result["path"]).resolve(), ROOT)

    counts: dict[str, int] = {}
    for result in results:
        counts[result["status"]] = counts.get(result["status"], 0) + 1
    print("Transcript summary: " + ", ".join(f"{key}={value}" for key, value in sorted(counts.items())))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    inventory_parser = subparsers.add_parser("inventory", help="discover channel videos and playlists")
    inventory_parser.add_argument("channel_url", nargs="?", default=DEFAULT_CHANNEL)
    inventory_parser.add_argument("--archive-root", type=Path, default=DEFAULT_ARCHIVE)

    transcript_parser = subparsers.add_parser("transcripts", help="fetch transcripts from an inventory")
    transcript_parser.add_argument("inventory", type=Path)
    transcript_parser.add_argument("--workers", type=int, default=2)
    transcript_parser.add_argument("--limit", type=int)
    transcript_parser.add_argument("--force", action="store_true")
    transcript_parser.add_argument("--transcript-dir", type=Path)
    transcript_parser.add_argument("--status-file", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "inventory":
        inventory(args.channel_url, args.archive_root)
        return 0
    transcripts(args.inventory, args.workers, args.limit, args.force, args.transcript_dir, args.status_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
