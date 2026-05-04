# Shaul Instructions (v2)

## Purpose

This repository is a study workspace to connect Scripture with Scripture in the same line of reasoning modeled by the apostles, centered on the Messiah.

## Language Policy

- Use English for repository operations, coding tasks, commit or PR text, and agent process communication.
- Write human-facing note prose in Spanish.
- Keep scripture quotations in their source language (for example, Hebrew text remains Hebrew).

## Core Style Rules

- Always use the Tetragrammaton as יהוה in note content where the divine name is written.
- Use clear, human-readable note titles. Do not use a raw verse as the main title.
- Store verse references in metadata and content, not as the full note title.
- Prefer Hebrew without nikud for verse text by default.
- Use Hebrew with nikud only when it is strictly needed for disambiguation.
- For Tanaj Hebrew and Delitzsch/TTH references, use shafan.xyz as the primary textual source.
- Use topic-specific structure. Do not force one rigid template for all notes.

## Source Priority for Research

- Local scripture library under docs/scriptures/ mirrored from edyhvh/davar JSON datasets
- https://yehoshuamaranata.blogspot.com
- https://www.youtube.com/@EricdeJes%C3%BAsRodr%C3%ADguezMendoza
- https://www.youtube.com/@SomosElCuerpodelMesias
- Additional web research only when needed to support context

## Obsidian + Quartz Authoring Rules

- Keep notes under content/ in thematic folders.
- Keep references discoverable with inline verse tags like #bereshit_1_1.
- Keep frontmatter field names in English schema keys, but write human-facing note content in Spanish.
- Prefer the local in-repo scripture corpus in docs/scriptures/ before remote scripture fetches when the passage already exists locally.
- Local scripture layout is docs/scriptures/oe/json/, docs/scriptures/tth/json/, and docs/scriptures/delitzsch/json/.
- Use Davar JSON sources: data/oe/<book>/<chapter>.json, data/tth_2/json/<book>.json, and data/delitzsch/\*.json.
- For TTH, prefer data/tth_2/json rather than the older data/tth tree.
- If a note directly discusses a verse, extract the verse into a comparison sheet from the local corpus when available; use shafan.xyz only as fallback when the local corpus is missing that passage.
- Add frontmatter fields:
  - title
  - description
  - date
  - tags
  - references
  - sources
- In YAML frontmatter, use spaces for indentation, never tabs.
- Keep tables and comparison sheets concise and scannable.
- Prefer links between notes over duplicated explanation blocks.

## Hermes Agent Workflow

1. Receive a topic request.
2. Detect request mode: raw notes organization, source-based research, or mixed.
3. Decide source path: user raw notes, article, video transcript, or web context.
4. Ingest source material and normalize it into structured points.
5. Execute the requested output shape: edit existing notes, create one consolidated note, or create several linked notes.
6. Add/refresh verse links and cross references.
7. Append learning summary to private/hermes/learning-log.md.

## Raw Notes Workflow

- Accept rough user notes as authoritative input context unless they conflict with explicit scripture text.
- Preserve the user's core ideas, but reorganize for clarity and traceability.
- If the user asks for one note: merge by single thesis and keep concise sections.
- If the user asks for multiple notes: split by topic or argument boundary and add links between generated notes.
- If the user asks to edit existing notes: update in place and keep existing metadata conventions.

## Transcript Tooling

- Primary transcript API: youtube-transcript-api.
- Fallback method: yt-dlp auto subtitles.
- Use scripts/hermes/fetch_transcript.py for ingestion.

## Local Scripture Workflow

1. Mirror scripture JSON from edyhvh/davar into docs/scriptures/.
2. Keep translation families separated under oe/json/, tth/json/, and delitzsch/json/.
3. OE stays chapter-oriented by book folder; TTH and Delitzsch stay book-oriented JSON files.
4. Treat docs/scriptures/ as the fast local source for Hermes and note normalization work.
5. Use npm run scriptures:ensure before scripture-dependent Hermes or note work.
6. Use npm run scriptures:sync -- --corpus <name> (or --corpus all) for explicit refreshes.

## Safety and Quality

- Do not invent quotes from sources.
- Mark uncertain claims as pending verification.
- Keep doctrinal conclusions tied to explicit passages and references.
