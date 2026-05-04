#!/usr/bin/env python3
"""Mirror scripture JSON files from edyhvh/davar into docs/scriptures/."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class CorpusConfig:
    upstream_path: str
    local_path: Path
    recursive: bool


CORPORA: dict[str, CorpusConfig] = {
    "oe": CorpusConfig("data/oe", Path("docs/scriptures/oe/json"), True),
    "tth": CorpusConfig("data/tth_2/json", Path("docs/scriptures/tth/json"), False),
    "delitzsch": CorpusConfig("data/delitzsch", Path("docs/scriptures/delitzsch/json"), False),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Mirror scripture JSON files from edyhvh/davar into docs/scriptures/."
    )
    parser.add_argument(
        "--corpus",
        choices=["oe", "tth", "delitzsch", "all"],
        action="append",
        help="Corpus to sync. Repeat for multiple corpora. Defaults to all.",
    )
    parser.add_argument(
        "--book",
        help=(
            "Optional book filter. For oe this is a book folder like genesis. "
            "For tth or delitzsch this is the JSON stem like bereshit or romanos."
        ),
    )
    parser.add_argument("--owner", default="edyhvh",
                        help="GitHub owner. Defaults to edyhvh.")
    parser.add_argument("--repo", default="davar",
                        help="GitHub repo. Defaults to davar.")
    parser.add_argument("--branch", default="main",
                        help="Git branch. Defaults to main.")
    parser.add_argument(
        "--token",
        help=(
            "GitHub token for authenticated API requests. "
            "Defaults to env GITHUB_TOKEN or GH_TOKEN."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which files would be mirrored without writing them.",
    )
    return parser.parse_args()


def request_headers(token: str | None, accept_json: bool) -> dict[str, str]:
    headers = {"User-Agent": "shaul-scripture-sync"}
    if accept_json:
        headers["Accept"] = "application/vnd.github+json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_json(url: str, token: str | None) -> Any:
    request = Request(
        url,
        headers=request_headers(token, accept_json=True),
    )
    with urlopen(request) as response:
        return json.load(response)


def fetch_bytes(url: str, token: str | None) -> bytes:
    request = Request(url, headers=request_headers(token, accept_json=False))
    with urlopen(request) as response:
        return response.read()


def contents_url(owner: str, repo: str, branch: str, path: str) -> str:
    return f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"


def raw_url(owner: str, repo: str, branch: str, path: str) -> str:
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"


def should_include(relative_path: Path, corpus_name: str, book: str | None) -> bool:
    if relative_path.suffix != ".json":
        return False
    if book is None:
        return True
    if corpus_name == "oe":
        return relative_path.parts[0] == book
    return relative_path.stem == book


def iter_remote_files(
    owner: str,
    repo: str,
    branch: str,
    corpus_name: str,
    config: CorpusConfig,
    book: str | None,
    token: str | None,
) -> list[tuple[Path, str]]:
    files: list[tuple[Path, str]] = []

    def visit(remote_path: str, relative_root: Path) -> None:
        payload = fetch_json(contents_url(
            owner, repo, branch, remote_path), token)
        if isinstance(payload, dict) and payload.get("type") == "file":
            item_name = payload.get("name")
            item_path = payload.get("path")
            if not isinstance(item_name, str) or not isinstance(item_path, str):
                return
            relative_path = relative_root / Path(item_name)
            if should_include(relative_path, corpus_name, book):
                files.append((relative_path, item_path))
            return

        if not isinstance(payload, list):
            raise ValueError(
                f"Unexpected payload type for {remote_path}: {type(payload).__name__}")

        for item in payload:
            if not isinstance(item, dict):
                continue
            item_type = item.get("type")
            item_name = item.get("name")
            item_path = item.get("path")
            if not isinstance(item_name, str):
                continue
            item_relative = relative_root / item_name
            if item_type == "file":
                if not isinstance(item_path, str):
                    continue
                if should_include(item_relative, corpus_name, book):
                    files.append((item_relative, item_path))
            elif item_type == "dir" and config.recursive:
                if not isinstance(item_path, str):
                    continue
                visit(item_path, item_relative)

    visit(config.upstream_path, Path())
    return files


def mirror_file(
    owner: str,
    repo: str,
    branch: str,
    source_path: str,
    destination_path: Path,
    dry_run: bool,
    token: str | None,
) -> str:
    if dry_run:
        return f"dry-run {destination_path}"

    data = fetch_bytes(raw_url(owner, repo, branch, source_path), token=token)
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    if destination_path.exists() and destination_path.read_bytes() == data:
        return f"unchanged {destination_path}"
    destination_path.write_bytes(data)
    return f"updated {destination_path}"


def sync_corpus(
    owner: str,
    repo: str,
    branch: str,
    corpus_name: str,
    config: CorpusConfig,
    book: str | None,
    dry_run: bool,
    token: str | None,
) -> tuple[int, int]:
    remote_files = iter_remote_files(
        owner, repo, branch, corpus_name, config, book, token)
    total = len(remote_files)
    print(f"[{corpus_name}] discovered {total} file(s)", flush=True)

    changed = 0
    for idx, (relative_path, source_path) in enumerate(remote_files, start=1):
        destination_path = config.local_path / relative_path
        status = mirror_file(
            owner,
            repo,
            branch,
            source_path,
            destination_path,
            dry_run,
            token,
        )
        if status.startswith("updated"):
            changed += 1
        print(f"[{corpus_name}] {idx}/{total} {status}", flush=True)
    return total, changed


def main() -> int:
    args = parse_args()
    corpora = args.corpus or ["all"]
    selected = [name for name in CORPORA if "all" in corpora or name in corpora]
    token = args.token or os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")

    try:
        for corpus_name in selected:
            total, changed = sync_corpus(
                args.owner,
                args.repo,
                args.branch,
                corpus_name,
                CORPORA[corpus_name],
                args.book,
                args.dry_run,
                token,
            )
            if total == 0:
                print(
                    f"no files matched for corpus={corpus_name!r} book={args.book!r}")
                continue
            print(
                f"[{corpus_name}] summary: {changed} updated, {total - changed} unchanged",
                flush=True,
            )
    except HTTPError as exc:
        if exc.code == 403:
            remaining = exc.headers.get("X-RateLimit-Remaining", "unknown")
            reset = exc.headers.get("X-RateLimit-Reset", "unknown")
            print(
                (
                    "sync failed: GitHub API rate limit exceeded. "
                    f"remaining={remaining} reset={reset}. "
                    "Set GITHUB_TOKEN (or pass --token) and retry."
                ),
                file=sys.stderr,
            )
            return 1
        print(f"sync failed: {exc}", file=sys.stderr)
        return 1
    except URLError as exc:
        print(f"sync failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
