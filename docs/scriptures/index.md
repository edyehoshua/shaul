---
title: Local Scriptures Library
description: In-repo scripture corpus for fast note integration and verse-sheet extraction
---

# Local Scriptures Library

This directory is the local scripture corpus for Shaul.

Its purpose is to keep the scripture JSON inside the repository so note work can extract verse sheets quickly without depending on remote fetches for every passage.

## Source of truth

- Mirror from `edyhvh/davar` into this repository.
- Treat this folder as the first source for scripture extraction during note work.
- Use shafan.xyz only when the needed passage has not yet been copied here.

## Layout

- [oe](./oe/)
- [tth](./tth/)
- [delitzsch](./delitzsch/)

## Working convention

- Keep scripture files in their Davar JSON shape.
- Keep the text close to source wording; do not paraphrase.
- When a study note discusses a verse directly, copy the Hebrew and translation from this local corpus into the note's comparison sheet.
- Keep translation families separated rather than mixing them in one file.

## Suggested expansion pattern

- `docs/scriptures/oe/json/<book>/<chapter>.json`
- `docs/scriptures/tth/json/<book>.json`
- `docs/scriptures/delitzsch/json/<book>.json`

## Upstream Davar mapping

- `data/oe/<book>/<chapter>.json` -> `docs/scriptures/oe/json/<book>/<chapter>.json`
- `data/tth_2/json/<book>.json` -> `docs/scriptures/tth/json/<book>.json`
- `data/delitzsch/<book>.json` -> `docs/scriptures/delitzsch/json/<book>.json`

## Sync helper

Use:

```shell
npm run scriptures:ensure
npm run scriptures:sync -- --corpus tth
npm run scriptures:sync -- --corpus oe --book genesis
npm run scriptures:sync -- --corpus delitzsch
```

- `scriptures:ensure` checks whether local corpus files already exist and syncs only when missing.
- `scriptures:sync` mirrors selected Davar JSON files into this repository.
