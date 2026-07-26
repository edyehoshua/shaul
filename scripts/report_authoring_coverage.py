#!/usr/bin/env python3
"""Report deterministic coverage and review samples for Eric de Jesús transcript notes."""
from __future__ import annotations
import argparse, collections, hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "data/inventories/ericdejes.json"
LANES = ROOT / "data/authoring-lanes.json"
CONTENT = ROOT / "content"
OUT = ROOT / "data/authoring-coverage.json"
REVIEW = ROOT / "data/authoring-quality-review.md"
ID_RE = re.compile(r"youtube:([\w-]+)")

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    inv = json.loads(INVENTORY.read_text())
    lanes = json.loads(LANES.read_text())["lanes"]
    assigned = {p: lane for lane, cfg in lanes.items() for p in cfg["playlists_in_order"]}
    classified_groups = [
        (lane, group)
        for lane, cfg in lanes.items()
        for group in cfg.get("source_groups", [])
    ]
    notes = []
    seen = collections.defaultdict(list)
    for path in sorted(CONTENT.rglob("*.md")):
        text = path.read_text(errors="replace")
        ids = list(dict.fromkeys(ID_RE.findall(text)))
        if ids:
            rel = str(path.relative_to(ROOT))
            notes.append({"path": rel, "ids": ids, "credits": "## Créditos" in text})
            for video_id in ids:
                seen[video_id].append(rel)
    videos = inv["videos"]
    inventory_ids = {v["id"] for v in videos}
    covered = set(seen) & inventory_ids
    by_playlist = {}
    playlist_ids = set()
    for playlist in inv.get("playlists", []):
        title = playlist["title"]
        ids = set(playlist.get("video_ids", []))
        playlist_ids.update(ids)
        by_playlist[title] = {
            "total": playlist.get("video_count", len(ids)),
            "covered": len(ids & covered),
            "lane": assigned.get(title),
        }
    # Explicitly classified uploads retain their source-level ownership even
    # when YouTube's channel inventory does not expose a playlist.
    for lane, group in classified_groups:
        ids = {source.removeprefix("youtube:") for source in group["source_ids"]}
        playlist_ids.update(ids)
        by_playlist[group["title"]] = {
            "total": len(ids),
            "covered": len(ids & covered),
            "lane": lane,
        }
    # The uploads tab also contains videos not assigned to any playlist.
    uncategorized = inventory_ids - playlist_ids
    if uncategorized:
        by_playlist["Uncategorized"] = {
            "total": len(uncategorized),
            "covered": len(uncategorized & covered),
            "lane": None,
        }
    report = {
        "inventory_videos": len(videos), "covered_videos": len(covered),
        "pending_videos": len(videos) - len(covered),
        "transcript_notes": len(notes),
        "notes_missing_visible_credits": [n["path"] for n in notes if not n["credits"]],
        "duplicate_source_ids": {k: v for k, v in seen.items() if len(v) > 1},
        "playlists": dict(sorted(by_playlist.items())),
        "completion": len(covered) == len(videos) and not any(not n["credits"] for n in notes) and not any(len(v) > 1 for v in seen.values()),
    }
    # Stable 10-note audit sample; changes only as content changes.
    sample = sorted(notes, key=lambda n: hashlib.sha256(n["path"].encode()).hexdigest())[:10]
    if args.write:
        OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        lines = ["# Muestreo de calidad de autoría", "", "Revisar esta muestra antes de cada hito de 25 integraciones.", ""]
        for n in sample:
            lines.append(f"- [ ] `{n['path']}` — fuentes: {', '.join('youtube:' + i for i in n['ids'])}; créditos visibles: {'sí' if n['credits'] else 'NO'}.")
        REVIEW.write_text("\n".join(lines) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__": main()
