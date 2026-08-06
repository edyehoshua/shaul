# Verse-addressable notes and static API contract

## Purpose

Shaul keeps Markdown notes as its canonical, reviewable knowledge base. The verse index is a generated read model for Bible readers, search UIs, and future API wrappers. It must never replace the note, its comparison sheet, its source links, or its `Pendiente de verificar` safeguards.

The current static endpoint is generated under `static/api/v1/verse-notes/`. Quartz copies `static/` to the published site, so a deployment exposes, for example:

- `/api/v1/verse-notes/index.json`
- `/api/v1/verse-notes/juan_1_29.json`
- `/api/v1/verse-notes/chapters/juan_1.json`

A future HTTP service should use these documents as a read-only baseline rather than adding a second manually maintained database.

## Canonical authoring model

Each note remains a Markdown document under `content/`. Its frontmatter owns the machine-readable relationship to Scripture and sources:

```yaml
---
title: "Human-readable title, not a raw verse"
description: "The question this note answers"
date: YYYY-MM-DD
tags: []
references:
  - "#juan_1_29"
  - "#juan_1_32-34"
sources:
  - "https://www.youtube.com/watch?v=VIDEO_ID"
  - "docs/scriptures/tth/json/juan.json"
source_ids:
  - "youtube:VIDEO_ID"
---
```

Rules:

- `references` is the authoritative Scripture address list for API discovery.
- Verse tags use lowercase ASCII Spanish book slugs (`#juan_1_29`, `#genesis_1_1`, `#isaias_53_5`) so references and generated URLs have one stable naming convention.
- Use `#book_chapter_verse` for a verse and `#book_chapter_start-end` only for an inclusive range in one chapter.
- Use `#book_chapter` only when the whole chapter is the actual anchor. It generates a chapter endpoint, not a false verse-level claim.
- Do not put Talmud, midrash, Zohar, or commentator shorthand in new `references`. Keep their precise citations in `Referencias judías y fuentes externas`, and use a dedicated field later only if a real bibliographic schema is needed.
- `sources` stays human-readable; `source_ids` is stable and machine-oriented. Current YouTube form: `youtube:<11-character video id>`.
- A note that depends on a verse includes the actual local corpus text in `Hoja de comparación`; the index deliberately stores metadata and links, not a duplicate scripture corpus.

Legacy notes can contain older non-scriptural shorthand in `references`; the generator leaves those notes untouched and excludes that shorthand from Bible endpoints. New notes must follow the model above.

## Generated document shape

One verse document is deliberately small:

```json
{
  "schema_version": 1,
  "verse": {
    "tag": "#juan_1_29",
    "book": "juan",
    "chapter": 1,
    "verse": 29
  },
  "notes": [
    {
      "id": "content/besorah/yojanan_1_testigo_cordero",
      "path": "content/besorah/yojanan_1_testigo_cordero.md",
      "url": "/content/besorah/yojanan_1_testigo_cordero/",
      "title": "Yojanán 1: el testigo que presenta al Cordero",
      "description": "...",
      "tags": ["yojanan", "testimonio"],
      "sources": ["https://www.youtube.com/watch?v=2C6YJnz5fKs"],
      "source_ids": ["youtube:2C6YJnz5fKs"]
    }
  ]
}
```

The aggregate `index.json` contains all verse and chapter documents. Per-verse documents are preferred by a Bible UI because they avoid downloading the full index for a single reference.

## Build and validation

```bash
npm run scriptures:ensure
npm run verse-index:test
npm run verse-index:build
```

`verse-index:build` is deterministic and overwrites only `static/api/v1/verse-notes/`. It expands same-chapter verse ranges into individual verse endpoints, deduplicates repeated references in one note, and rejects descending ranges. It does not use transcript text directly, so private transcripts remain private.

Before merging a note batch, run:

```bash
npm run content:check-frontmatter
npm run verse-index:test
npm run verse-index:build
npm run test
npm run check
npm run build
```

## Scalable transcript-to-note pipeline

1. Keep the transcript in `private/transcripts/<channel>/<video-id>.md`; this is source evidence, not published note content.
2. Create one **source card / class note** per coherent video or tightly bounded passage. Include the video URL, stable `source_ids`, a timestamp route, and only claims supported by that transcript.
3. Anchor every directly discussed biblical verse in `references`, then populate the comparison sheet from the local OE/TTH/Delitzsch corpus.
4. Split only when the video contains genuinely independent arguments. A chapter note can link to focused topic or lexical notes; avoid copying the same exposition into each note.
5. Preserve claims from the teacher as the teacher's argument. Cotejable secondary material—Talmud, Zohar, targum, grammar, history, manuscript claims—must have a traceable citation or a checkbox in `Pendiente de verificar`.
6. Generate the read model and use the per-verse JSON as the intake for future search, API, or Bible-reader integration.

This gives fast batch throughput without treating unverified verbal claims as settled reference data.
