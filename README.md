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
python3 scripts/hermes/fetch_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

Dependencies:

```bash
python3 -m pip install -r requirements-hermes.txt
```

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
