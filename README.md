# shaul

https://shaul.vercel.app

A digital workspace for midrash-style scripture study: connecting Tanaj and Besorah around the Messiah with traceable notes.

## V2 Direction

This repository now uses a lighter, agent-ready workflow:

- Quartz as static publishing engine
- Obsidian-first authoring model
- agent research workflow baseline
- Transcript ingestion tooling (youtube-transcript-api + yt-dlp fallback)
- No Dependabot (manual dependency review)

## Quick Start

```bash
git clone https://github.com/edyhvh/shaul.git
cd shaul
npm install
npm run build
npm run dev
```

The Shaul v2 site runs at http://localhost:8484. `npm run dev` serves the existing
`public/` build without rebuilding it; run `npm run build` again after changing notes,
graph data, or site code.

## Build

```bash
npm run build
```

Generated output is in public/.

The Shaul v2 graph home runs at `http://localhost:8484` during development. Quartz remains
the legacy note publisher, and the graph is also available at `/graph`. Its source data lives
under `knowledge/` and can be validated or compiled independently:

```bash
npm run graph:validate
npm run graph:build
```

## Transcript Tool

```bash
npm run transcript -- "https://www.youtube.com/watch?v=VIDEO_ID"
```

Dependencies:

```bash
npm run setup
```

## Local Scriptures Sync (Prerequisite)

Note and verse-sheet workflows are local-first and use the in-repo corpus under `docs/scriptures/`.

Ensure local scriptures are present (sync only when missing):

```bash
npm run scriptures:ensure
```

Force a refresh from `edyhvh/davar`:

```bash
npm run scriptures:ensure -- --force
```

Manual corpus sync examples:

```bash
npm run scriptures:sync -- --corpus all
npm run scriptures:sync -- --corpus oe --book genesis
```

One-shot preparation (Python deps + local scriptures + DB init):

```bash
npm run prepare
```

## Source DB (Transcripts + Articles)

The project includes a lightweight SQLite index for source files under `private/sources`.

Initialize DB schema:

```bash
npm run sources:db:init
```

Reindex all source files (`.md`, `.txt`, `.html`) from `private/sources`:

```bash
npm run sources:db:reindex
```

Search indexed content:

```bash
npm run sources:db:search -- "messiah"
```

Show DB health summary (counts and latest indexed files):

```bash
npm run sources:db:stats
```

When you run transcript ingestion, the output is automatically indexed unless `--no-index` is passed.

## Notes Authoring

See:

- docs/note-authoring.md (canonical spec for Grok, Cursor, and Codex)
- AGENTS.md
- content/guide.md
- content/templates/topic-v2.md
- .github/instructions/shaul.instructions.md
- .github/skill/obsidian/SKILL.md

## Acknowledgments

Built with Quartz v4.5.2:

- https://quartz.jzhao.xyz
- https://github.com/jackyzha0/quartz

SHALOM
