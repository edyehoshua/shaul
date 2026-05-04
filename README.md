# shaul

https://shaul.vercel.app

A digital workspace for midrash-style scripture study: connecting Tanaj and Besorah around the Messiah with traceable notes.

## V2 Direction

This repository now uses a lighter, agent-ready workflow:

- Quartz as static publishing engine
- Obsidian-first authoring model
- Hermes research workflow baseline
- Transcript ingestion tooling (youtube-transcript-api + yt-dlp fallback)
- No Dependabot (manual dependency review)

## Quick Start

```bash
git clone https://github.com/edyhvh/shaul.git
cd shaul
npm install
npm start
```

Site runs at http://localhost:8080

## Build

```bash
npm run build
```

Generated output is in public/.

## Hermes Transcript Tool

```bash
npm run hermes:transcript -- "https://www.youtube.com/watch?v=VIDEO_ID"
```

Dependencies:

```bash
npm run hermes:setup
```

## Local Scriptures Sync (Hermes Prerequisite)

Hermes note and verse-sheet workflows are local-first and use the in-repo corpus under `docs/scriptures/`.

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

One-shot Hermes prep (Python deps + local scriptures + DB init):

```bash
npm run hermes:prepare
```

## Hermes Source DB (Transcripts + Articles)

Hermes includes a lightweight SQLite index for source files under `private/hermes/sources`.

Initialize DB schema:

```bash
npm run hermes:db:init
```

Reindex all source files (`.md`, `.txt`, `.html`) from `private/hermes/sources`:

```bash
npm run hermes:db:reindex
```

Search indexed content:

```bash
npm run hermes:db:search -- "messiah"
```

Show DB health summary (counts and latest indexed files):

```bash
npm run hermes:db:stats
```

When you run transcript ingestion, the output is automatically indexed unless `--no-index` is passed.

## Notes Authoring

See:

- content/guide.md
- content/templates/topic-v2.md
- .github/instructions/shaul.instructions.md
- .github/skill/obsidian/SKILL.md

## Acknowledgments

Built with Quartz v4.5.2:

- https://quartz.jzhao.xyz
- https://github.com/jackyzha0/quartz

SHALOM
