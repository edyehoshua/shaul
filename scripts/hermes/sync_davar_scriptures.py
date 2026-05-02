#!/usr/bin/env python3
"""Mirror scripture JSON files from edyhvh/davar into docs/scriptures/."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
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
        "--dry-run",
        action="store_true",
        help="Show which files would be mirrored without writing them.",
    )
    return parser.parse_args()


def fetch_json(url: str) -> object:
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "shaul-scripture-sync",
        },
    )
    with urlopen(request) as response:
        return json.load(response)


def fetch_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "shaul-scripture-sync"})
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
) -> list[tuple[Path, str]]:
    files: list[tuple[Path, str]] = []

    def visit(remote_path: str, relative_root: Path) -> None:
        payload = fetch_json(contents_url(owner, repo, branch, remote_path))
        if isinstance(payload, dict) and payload.get("type") == "file":
            relative_path = relative_root / Path(payload["name"])
            if should_include(relative_path, corpus_name, book):
                files.append((relative_path, payload["path"]))
            return

        for item in payload:
            item_type = item.get("type")
            item_name = item.get("name", "")
            item_path = item.get("path", "")
            item_relative = relative_root / item_name
            if item_type == "file":
                if should_include(item_relative, corpus_name, book):
                    files.append((item_relative, item_path))
            elif item_type == "dir" and config.recursive:
                visit(item_path, item_relative)

    visit(config.upstream_path, Path())
    return files


def mirror_file(owner: str, repo: str, branch: str, source_path: str, destination_path: Path, dry_run: bool) -> str:
    if dry_run:
        return f"dry-run {destination_path}"

    data = fetch_bytes(raw_url(owner, repo, branch, source_path))
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
) -> list[str]:
    remote_files = iter_remote_files(
        owner, repo, branch, corpus_name, config, book)
    results: list[str] = []
    for relative_path, source_path in remote_files:
        destination_path = config.local_path / relative_path
        results.append(mirror_file(owner, repo, branch,
                       source_path, destination_path, dry_run))
    return results


def main() -> int:
    args = parse_args()
    corpora = args.corpus or ["all"]
    selected = [name for name in CORPORA if "all" in corpora or name in corpora]

    try:
        for corpus_name in selected:
            results = sync_corpus(
                args.owner,
                args.repo,
                args.branch,
                corpus_name,
                CORPORA[corpus_name],
                args.book,
                args.dry_run,
            )
            if not results:
                print(
                    f"no files matched for corpus={corpus_name!r} book={args.book!r}")
                continue
            for line in results:
                print(line)
    except (HTTPError, URLError) as exc:
        print(f"sync failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
