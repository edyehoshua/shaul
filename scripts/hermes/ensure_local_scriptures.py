#!/usr/bin/env python3
"""Ensure local scriptures corpus is present, syncing from GitHub when needed."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CorpusPath:
    name: str
    local_path: Path


CORPORA: tuple[CorpusPath, ...] = (
    CorpusPath("oe", Path("docs/scriptures/oe/json")),
    CorpusPath("tth", Path("docs/scriptures/tth/json")),
    CorpusPath("delitzsch", Path("docs/scriptures/delitzsch/json")),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Ensure local scriptures are available under docs/scriptures/. "
            "When missing (or forced), run full sync from edyhvh/davar."
        )
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check whether local scripture files exist. Exit 1 if missing.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Always run full sync even when local files are already present.",
    )
    parser.add_argument("--owner", default="edyhvh",
                        help="GitHub owner. Defaults to edyhvh.")
    parser.add_argument("--repo", default="davar",
                        help="GitHub repo. Defaults to davar.")
    parser.add_argument("--branch", default="main",
                        help="Git branch. Defaults to main.")
    parser.add_argument(
        "--token",
        help="GitHub token to pass through to sync script (optional).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Pass --dry-run through to sync script.",
    )
    return parser.parse_args()


def corpus_file_count(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for _ in path.rglob("*.json"))


def find_missing_corpora(repo_root: Path) -> list[str]:
    missing: list[str] = []
    for corpus in CORPORA:
        full_path = repo_root / corpus.local_path
        if corpus_file_count(full_path) == 0:
            missing.append(corpus.name)
    return missing


def print_status(repo_root: Path) -> None:
    for corpus in CORPORA:
        full_path = repo_root / corpus.local_path
        count = corpus_file_count(full_path)
        print(f"[{corpus.name}] local json files: {count}")


def run_sync(args: argparse.Namespace, script_path: Path) -> int:
    command = [
        sys.executable,
        str(script_path),
        "--corpus",
        "all",
        "--owner",
        args.owner,
        "--repo",
        args.repo,
        "--branch",
        args.branch,
    ]
    if args.token:
        command.extend(["--token", args.token])
    if args.dry_run:
        command.append("--dry-run")

    print("running full local scripture sync...")
    result = subprocess.run(command, check=False)
    return result.returncode


def main() -> int:
    args = parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    os.chdir(repo_root)
    sync_script = Path(__file__).with_name("sync_davar_scriptures.py")

    print_status(repo_root)
    missing = find_missing_corpora(repo_root)

    if args.check_only:
        if missing:
            print(f"missing local corpus files for: {', '.join(missing)}")
            return 1
        print("local scripture corpus is ready")
        return 0

    if not args.force and not missing:
        print("local scripture corpus already present; no sync needed")
        return 0

    if missing:
        print(f"missing corpus data detected: {', '.join(missing)}")
    if args.force:
        print("force mode enabled")

    return run_sync(args, sync_script)


if __name__ == "__main__":
    raise SystemExit(main())
