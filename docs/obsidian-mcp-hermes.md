---
title: Obsidian MCP + Hermes
description: Baseline integration to let Hermes read/write notes in this vault
---

# Obsidian MCP + Hermes

This guide sets a practical baseline for using Hermes with Obsidian notes inside this repository.

## 1) Obsidian vault target

Use this folder as the vault content root:

- content/

## 2) Enable Obsidian REST access

In Obsidian:

1. Install and enable an API plugin that exposes local note operations.
2. Generate an API key.
3. Restrict access to local loopback when possible.

## 3) MCP server config (example)

Copy and adapt:

- .mcp/obsidian-mcp.example.json

Set:

- OBSIDIAN_VAULT_PATH to your local absolute path ending in /shaul/content
- OBSIDIAN_API_KEY to your local key

## 4) Hermes working contract

Hermes should:

1. Read the target note if it exists.
2. Accept raw notes from the user as direct input context.
3. Create/update one note or multiple linked notes based on the user's request.
4. Preserve frontmatter fields: title, description, date, tags, references, sources.
5. Use verse tags to keep graph connections discoverable.
6. Append reusable insights to private/hermes/learning-log.md.

## 4.1) Raw notes workflow (new)

Use this when you pass rough notes directly to Hermes:

1. Paste your raw notes.
2. Specify mode: edit-existing | single-note | multi-note.
3. Specify target path(s) in content/ when known.
4. Hermes reorganizes content using the Shaul structure conventions.
5. Hermes returns final note file(s) plus a short changelog.

## 5) Transcript ingestion support

Use:

python3 scripts/hermes/fetch_transcript.py "<youtube-url>"

Output is stored in:

- private/hermes/sources/

## 6) Suggested prompt shape for Hermes

- Topic:
- Mode: edit-existing | single-note | multi-note
- Raw notes:
- Source preference: blog | video | web
- Output path in content/:
- Required verse links:
- Constraints (length, tone, sections):

## 7) Review checklist

- Title is clear (not only a verse string).
- יהוה is used where the divine name appears.
- References are explicit and linked.
- Sources are included.
- No invented quotations.
