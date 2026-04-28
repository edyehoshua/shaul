#!/usr/bin/env python3
"""Lightweight SQLite index for Hermes sources (YouTube transcripts + articles).

Source of truth stays on disk (private/hermes/sources). This DB is a fast query layer.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path("private/hermes/sources/index.sqlite3")
DEFAULT_SOURCES_DIR = Path("private/hermes/sources")
TRANSCRIPT_LINE_RE = re.compile(r"^\[(\d{2}):(\d{2}):(\d{2})\]\s*(.+)$")


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def file_checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def open_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY,
            source_type TEXT NOT NULL,
            external_id TEXT,
            url TEXT,
            title TEXT,
            author_or_channel TEXT,
            language TEXT,
            published_at TEXT,
            fetched_at TEXT,
            checksum TEXT NOT NULL,
            raw_path TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS segments (
            id INTEGER PRIMARY KEY,
            source_id INTEGER NOT NULL,
            seq INTEGER NOT NULL,
            start_seconds REAL,
            end_seconds REAL,
            text TEXT NOT NULL,
            FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE,
            UNIQUE (source_id, seq)
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS segments_fts USING fts5(
            source_id UNINDEXED,
            raw_path UNINDEXED,
            title,
            text,
            tokenize='unicode61'
        );

        CREATE INDEX IF NOT EXISTS idx_sources_type ON sources(source_type);
        CREATE INDEX IF NOT EXISTS idx_sources_external_id ON sources(external_id);
        CREATE INDEX IF NOT EXISTS idx_segments_source_id ON segments(source_id);
        """
    )
    conn.commit()


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text

    end_marker = "\n---\n"
    end_pos = text.find(end_marker, 4)
    if end_pos == -1:
        return {}, text

    raw_header = text[4:end_pos]
    body = text[end_pos + len(end_marker):]

    meta: dict[str, str] = {}
    for raw_line in raw_header.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        meta[key] = value
    return meta, body


def to_seconds(hours: str, minutes: str, seconds: str) -> int:
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds)


def parse_transcript_segments(body: str) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    seq = 0
    for raw_line in body.splitlines():
        line = raw_line.strip()
        match = TRANSCRIPT_LINE_RE.match(line)
        if not match:
            continue
        h, m, s, text = match.groups()
        text = text.strip()
        if not text:
            continue
        seq += 1
        segments.append(
            {
                "seq": seq,
                "start_seconds": float(to_seconds(h, m, s)),
                "end_seconds": None,
                "text": text,
            }
        )
    return segments


def parse_article_segments(body: str) -> list[dict[str, Any]]:
    parts = re.split(r"\n\s*\n+", body)
    segments: list[dict[str, Any]] = []
    seq = 0
    for part in parts:
        text = " ".join(line.strip() for line in part.splitlines()).strip()
        if not text:
            continue
        if text.startswith("#"):
            continue
        seq += 1
        segments.append(
            {
                "seq": seq,
                "start_seconds": None,
                "end_seconds": None,
                "text": text,
            }
        )
    return segments


def detect_source_type(meta: dict[str, str], body: str) -> str:
    source = meta.get("source", "")
    if meta.get("video_id") or "youtube.com" in source or "youtu.be" in source:
        return "youtube"

    transcript_like = len(parse_transcript_segments(body))
    if transcript_like >= 3:
        return "youtube"

    return "article"


def normalize_source_record(file_path: Path, content: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    meta, body = parse_frontmatter(content)
    source_type = detect_source_type(meta, body)

    if source_type == "youtube":
        segments = parse_transcript_segments(body)
    else:
        segments = parse_article_segments(body)

    if not segments:
        segments = parse_article_segments(body)

    source = meta.get("source") or meta.get("url") or ""
    title = meta.get("title") or file_path.stem
    author_or_channel = meta.get("channel") or meta.get("author") or ""
    external_id = meta.get("video_id") or ""

    record: dict[str, Any] = {
        "source_type": source_type,
        "external_id": external_id,
        "url": source,
        "title": title,
        "author_or_channel": author_or_channel,
        "language": meta.get("language", ""),
        "published_at": meta.get("published_at", ""),
        "fetched_at": meta.get("fetched_at", ""),
        "segments": segments,
    }
    return record, segments


def upsert_source(conn: sqlite3.Connection, raw_path: str, checksum: str, record: dict[str, Any]) -> int:
    now = utc_now_iso()
    row = conn.execute(
        "SELECT id FROM sources WHERE raw_path = ?", (raw_path,)).fetchone()
    if row is None:
        cur = conn.execute(
            """
            INSERT INTO sources (
                source_type, external_id, url, title, author_or_channel, language,
                published_at, fetched_at, checksum, raw_path, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["source_type"],
                record["external_id"],
                record["url"],
                record["title"],
                record["author_or_channel"],
                record["language"],
                record["published_at"],
                record["fetched_at"],
                checksum,
                raw_path,
                now,
                now,
            ),
        )
        source_id = int(cur.lastrowid)
    else:
        source_id = int(row[0])
        conn.execute(
            """
            UPDATE sources
            SET source_type = ?, external_id = ?, url = ?, title = ?, author_or_channel = ?,
                language = ?, published_at = ?, fetched_at = ?, checksum = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                record["source_type"],
                record["external_id"],
                record["url"],
                record["title"],
                record["author_or_channel"],
                record["language"],
                record["published_at"],
                record["fetched_at"],
                checksum,
                now,
                source_id,
            ),
        )

    conn.execute("DELETE FROM segments_fts WHERE source_id = ?", (source_id,))
    conn.execute("DELETE FROM segments WHERE source_id = ?", (source_id,))

    for segment in record["segments"]:
        cur = conn.execute(
            """
            INSERT INTO segments (source_id, seq, start_seconds, end_seconds, text)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                source_id,
                segment["seq"],
                segment["start_seconds"],
                segment["end_seconds"],
                segment["text"],
            ),
        )
        segment_id = int(cur.lastrowid)
        conn.execute(
            """
            INSERT INTO segments_fts (rowid, source_id, raw_path, title, text)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                segment_id,
                source_id,
                raw_path,
                record["title"],
                segment["text"],
            ),
        )

    conn.commit()
    return source_id


def index_file(db_path: Path, file_path: Path, workspace_root: Path) -> tuple[int, int]:
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    record, segments = normalize_source_record(file_path, content)
    checksum = file_checksum(file_path)
    raw_path = str(file_path.relative_to(workspace_root)) if file_path.is_relative_to(
        workspace_root) else str(file_path)

    conn = open_db(db_path)
    try:
        init_schema(conn)
        source_id = upsert_source(conn, raw_path, checksum, record)
    finally:
        conn.close()

    return source_id, len(segments)


def reindex_sources(db_path: Path, sources_dir: Path, workspace_root: Path) -> tuple[int, int]:
    conn = open_db(db_path)
    try:
        init_schema(conn)
        conn.execute("DELETE FROM segments_fts")
        conn.execute("DELETE FROM segments")
        conn.execute("DELETE FROM sources")
        conn.commit()
    finally:
        conn.close()

    files = sorted(
        [
            p
            for p in sources_dir.rglob("*")
            if p.is_file() and p.suffix.lower() in {".md", ".txt", ".html", ".htm"}
        ]
    )

    indexed_sources = 0
    indexed_segments = 0
    for path in files:
        _, count = index_file(db_path, path, workspace_root)
        indexed_sources += 1
        indexed_segments += count

    return indexed_sources, indexed_segments


def search(db_path: Path, query: str, limit: int) -> list[sqlite3.Row]:
    conn = open_db(db_path)
    conn.row_factory = sqlite3.Row
    try:
        init_schema(conn)
        rows = conn.execute(
            """
            SELECT
                s.source_type,
                f.raw_path,
                COALESCE(s.title, '') AS title,
                COALESCE(s.url, '') AS url,
                seg.start_seconds,
                seg.seq,
                snippet(segments_fts, 3, '[', ']', ' ... ', 14) AS snippet,
                bm25(segments_fts) AS score
            FROM segments_fts AS f
            JOIN segments AS seg ON seg.id = f.rowid
            JOIN sources AS s ON s.id = f.source_id
            WHERE segments_fts MATCH ?
            ORDER BY score ASC
            LIMIT ?
            """,
            (query, limit),
        ).fetchall()
    finally:
        conn.close()
    return rows


def stats(db_path: Path, latest_limit: int) -> dict[str, Any]:
    conn = open_db(db_path)
    conn.row_factory = sqlite3.Row
    try:
        init_schema(conn)

        total_sources = int(
            conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0])
        total_segments = int(
            conn.execute("SELECT COUNT(*) FROM segments").fetchone()[0])

        type_rows = conn.execute(
            """
            SELECT source_type, COUNT(*) AS count
            FROM sources
            GROUP BY source_type
            ORDER BY count DESC, source_type ASC
            """
        ).fetchall()
        by_type = {str(row["source_type"]): int(row["count"])
                   for row in type_rows}

        latest_rows = conn.execute(
            """
            SELECT raw_path, source_type, title, updated_at
            FROM sources
            ORDER BY datetime(updated_at) DESC
            LIMIT ?
            """,
            (latest_limit,),
        ).fetchall()

        latest: list[dict[str, str]] = []
        for row in latest_rows:
            latest.append(
                {
                    "raw_path": str(row["raw_path"]),
                    "source_type": str(row["source_type"]),
                    "title": str(row["title"] or ""),
                    "updated_at": str(row["updated_at"]),
                }
            )

    finally:
        conn.close()

    return {
        "total_sources": total_sources,
        "total_segments": total_segments,
        "by_type": by_type,
        "latest": latest,
    }


def cmd_init(args: argparse.Namespace) -> int:
    conn = open_db(Path(args.db))
    try:
        init_schema(conn)
    finally:
        conn.close()
    print(f"Initialized DB: {args.db}")
    return 0


def cmd_index_file(args: argparse.Namespace) -> int:
    workspace_root = Path(args.workspace_root).resolve()
    file_path = Path(args.file).resolve()
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return 2

    source_id, segment_count = index_file(
        Path(args.db), file_path, workspace_root)
    print(
        f"Indexed file: {file_path} (source_id={source_id}, segments={segment_count})")
    return 0


def cmd_reindex(args: argparse.Namespace) -> int:
    workspace_root = Path(args.workspace_root).resolve()
    sources_dir = Path(args.sources_dir).resolve()
    if not sources_dir.exists():
        print(f"Sources dir not found: {sources_dir}")
        return 2

    source_count, segment_count = reindex_sources(
        Path(args.db), sources_dir, workspace_root)
    print(f"Reindexed sources: {source_count}, segments: {segment_count}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    rows = search(Path(args.db), args.query, args.limit)
    if not rows:
        print("No results")
        return 0

    for row in rows:
        ts = ""
        if row["start_seconds"] is not None:
            ts = f" t={int(row['start_seconds'])}s"
        print(f"[{row['source_type']}] {row['raw_path']}#{row['seq']}{ts}")
        if row["title"]:
            print(f"  title: {row['title']}")
        if row["url"]:
            print(f"  url: {row['url']}")
        print(f"  {row['snippet']}")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    data = stats(Path(args.db), args.latest)
    print(f"DB: {args.db}")
    print(f"Sources: {data['total_sources']}")
    print(f"Segments: {data['total_segments']}")

    print("By type:")
    if data["by_type"]:
        for source_type, count in data["by_type"].items():
            print(f"  {source_type}: {count}")
    else:
        print("  none")

    print(f"Latest files (max {args.latest}):")
    if data["latest"]:
        for item in data["latest"]:
            line = f"  [{item['source_type']}] {item['raw_path']}"
            if item["title"]:
                line += f" | {item['title']}"
            line += f" | updated: {item['updated_at']}"
            print(line)
    else:
        print("  none")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Hermes source SQLite index")
    parser.set_defaults(func=None)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--db", default=str(DEFAULT_DB_PATH),
                        help="SQLite DB path")
    common.add_argument(
        "--workspace-root",
        default=".",
        help="Workspace root used to store relative source file paths",
    )

    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser(
        "init", parents=[common], help="Initialize DB schema")
    p_init.set_defaults(func=cmd_init)

    p_index = sub.add_parser(
        "index-file", parents=[common], help="Index one source file")
    p_index.add_argument("file", help="Path to source file")
    p_index.set_defaults(func=cmd_index_file)

    p_reindex = sub.add_parser(
        "reindex", parents=[common], help="Rebuild DB from source directory")
    p_reindex.add_argument(
        "--sources-dir",
        default=str(DEFAULT_SOURCES_DIR),
        help="Directory with transcript/article files",
    )
    p_reindex.set_defaults(func=cmd_reindex)

    p_search = sub.add_parser("search", parents=[common], help="FTS search")
    p_search.add_argument("query", help="FTS query string")
    p_search.add_argument("--limit", type=int, default=20,
                          help="Max rows to return")
    p_search.set_defaults(func=cmd_search)

    p_stats = sub.add_parser(
        "stats", parents=[common], help="Show index health and summary stats"
    )
    p_stats.add_argument(
        "--latest",
        type=int,
        default=10,
        help="How many recently updated files to show",
    )
    p_stats.set_defaults(func=cmd_stats)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if not args.func:
        parser.print_help()
        return 2
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
