# Note Authoring Spec (All LLM Agents)

Canonical rules for Grok Build, Cursor, Codex, Hermes, and any other agent that creates or edits notes in this repository.

Human-facing note prose stays in Spanish. Agent process communication stays in English.

## When to Read This

Read this document before:

- Creating a new note from raw notes, a video transcript, or web research
- Expanding an existing note in the Yojanan series or similar class-based notes
- Adding lexical tables, Jewish literature references, or comparison sheets

Companion docs:

- [content/guide.md](../content/guide.md) — Spanish overview for human authors
- [content/templates/topic-v2.md](../content/templates/topic-v2.md) — starter template
- [docs/obsidian-mcp-hermes.md](./obsidian-mcp-hermes.md) — Hermes + Obsidian integration
- [AGENTS.md](../AGENTS.md) — short agent entry point

## Prerequisites

Before scripture-dependent work:

```bash
npm run scriptures:ensure
```

Use local corpus paths under `docs/scriptures/` first. Fall back to shafan.xyz only when the passage is missing locally.

## Note Modes

| Mode | Input | Output |
| --- | --- | --- |
| `raw-notes` | User rough notes | One or more reorganized notes |
| `transcript` | YouTube URL or `private/hermes/sources/*.txt` | One consolidated note or a linked series |
| `thematic` | Topic + scripture anchors | One focused note under `content/temas/` |
| `edit-existing` | Target path + new material | Update in place, preserve metadata conventions |

Detect mode from the user request. Default to `edit-existing` when a target path is named.

## Required Frontmatter

```yaml
---
title: "Clear human title, not a bare verse"
description: "What question this note answers"
date: YYYY-MM-DD
tags: []
references: []
sources: []
---
```

Rules:

- YAML uses spaces only, never tabs
- `references` holds verse tags like `#iojanan_10_11`
- `sources` holds URLs, transcript paths, or internal docs like `docs/benhaelohim.md`
- Optional: `translation: "[TTH, Delitzsch]"` when multiple corpora are cited

## Section Vocabulary

Use topic-specific structure. Do not force every section on every note. Pick only what the argument needs.

| Section | When to use |
| --- | --- |
| `# Tesis` | Always — one tight paragraph with the main claim |
| `## Alcance de la nota` | Transcript/class notes — source, scope, verification disclaimer |
| `## Contexto de lectura` | Historical or literary framing needed before exposition |
| `## Texto base` | Short list of anchor verses when helpful before tables |
| `## Hoja de comparación` | Note directly discusses verses — include actual text from local corpus |
| `## Hoja léxica` / `## Léxico base` / `## Léxico clave` | Word-study or translation-sensitive argument |
| `## Referencias judías y fuentes externas` | Talmud, midrash, targum, commentators, historians cited or implied |
| Thematic `##` headings | Argument blocks named by idea, not by rigid template |
| `## Conexiones principales` | Cross-links between verses and related notes |
| `## Pendiente de verificar` | Unverified lexical, rabbinic, or historical claims |
| `## Conclusión` | Short closing synthesis |
| `## Ver también` | Links to related notes in `content/` |

Recent high-quality examples:

- `content/besorah/yojanan_10_puerta_pastor_abba.md`
- `content/besorah/yojanan_14_abba_menajem_nombre.md`
- `content/temas/ben_hijo_titulos_mesias.md`
- `content/temas/elohim_aba.md`

## Comparison Sheets

When a note discusses a verse, extract text from the local corpus instead of leaving only a bare tag or paraphrase.

### Standard Tanaj + TTH

| Referencia | Hebreo (sin nikud) | TTH (ES) | Observación |
| --- | --- | --- | --- |
| #bereshit_1_1 | ... | ... | ... |

### Besorah / mixed local corpora

| Referencia | Texto local | Función en la clase |
| --- | --- | --- |
| #iojanan_11_4 | Delitzsch / TTH excerpt | Why this verse matters in the argument |

Corpus priority:

1. OE Hebrew — `docs/scriptures/oe/json/<book>/<chapter>.json`
2. TTH — `docs/scriptures/tth/json/<book>.json` (prefer `data/tth_2/json`)
3. Delitzsch — `docs/scriptures/delitzsch/json/*.json`

If a verse is missing in TTH, say so explicitly and use Delitzsch or OE where available.

## Lexical Sheets (Greek–Hebrew–Aramaic)

Add a lexical sheet when the argument depends on terms that must not be flattened into Spanish or modern theological English.

### Full cross-language sheet

Use for Besorah notes with semitic background or word-study notes:

| Término | Transliteración | Sentido en la nota | Raíz o base | Observación |
| --- | --- | --- | --- | --- |
| **(אמן)** | emun / aman | afirmarse, fidelidad | אמן | No reducir a "fe" emocional |
| **(πιστεύω)** | pisteuo | afirmarse, mostrar fidelidad | πιστ- | Cotejar con אמן, no asumir equivalencia total |
| **(ψυχή)** | psuche | nefesh, vida expuesta | ψυχ- | La clase lo acerca a nefesh; marcar si es pedagógico |

Formatting rules:

- Put source script in bold parentheses: **(אבא)**, **(πνεῦμα)**, **(ܐܒܐ)** when citing forms
- Prefer Hebrew without nikud unless disambiguation requires vowels
- Keep Greek and Aramaic in source script, not only transliteration
- State whether the link is exact equivalence, approximate translation, or pedagogical analogy
- Never claim perfect equivalence between Greek, Hebrew, Aramaic, and Spanish without qualification

### Compact approximation sheet

Use for introductory notes or glossaries of loaded terms:

| Forma | Aproximación usual | Matiz que hay que preservar |
| --- | --- | --- |
| **(רבי)** | maestro | Título relacional del siglo I; no agota el uso cultural |
| **(משיח)** | cristo | No absorbe la densidad de unción y función mesiánica |

### Hebrew-only root sheet

Use for Tanaj-heavy notes:

| Hebreo | Transliteración (es) | Significado | Raíz | Sentido de la raíz | Observación |
| --- | --- | --- | --- | --- | --- |
| **(ימלט)** | imalet | escapar | מלט | escapar, librarse | El que libra es יהוה |

## External Literature References

Jewish, patristic, historical, and lexical sources appear often in class notes. Treat them in two layers:

1. **In prose** — short contextual mention tied to the argument
2. **In a dedicated section or checklist** — precise-enough citation for later verification

### Citation format

Use this pattern in Spanish prose and in `## Referencias judías y fuentes externas`:

| Source type | Format | Example |
| --- | --- | --- |
| Talmud Bavli | `Nombre del tratado` + daf | b. Sanhedrin 37a |
| Talmud Yerushalmi | `y.` + tratado + capítulo/página | y. Berakhot 1:1 |
| Midrash | Colección + referencia interna | Bereishit Rabbah 44:7 |
| Targum | Nombre + pasaje bíblico | Targum Onkelos, Bereshit 1:1 |
| Commentator | Autor + obra + pasaje | Ibn Ezra, Bereshit 1:1 |
| Mishnah | Tratado + capítulo:mishná | m. Shabbat 7:2 |
| Zohar | Sección + folio if known | Zohar 1:134b — mark dating as pending if uncertain |
| Historian | Author + work + citation | Josefo, Ant. 18.23 |
| Lexicon / grammar | Title + entry or page | BDB, אמן; Jastrow, אַבָּא |

When the source is mentioned in a transcript but the exact reference is unknown:

- Keep the idea in prose
- Add a checkbox under `## Pendiente de verificar`
- Do not invent daf, chapter, or page numbers

Example pending item:

```markdown
- [ ] Localizar la referencia talmúdica exacta del pastor que entrega una oveja al lobo (b. ? ?a)
```

### Section template

```markdown
## Referencias judías y fuentes externas

| Fuente | Referencia | Uso en la nota | Estado |
| --- | --- | --- | --- |
| Talmud Bavli | b. Sanhedrin 37a | Contexto sobre ... | Pendiente de verificar |
| Ibn Ezra | Bereshit 1:1 | Setenta nombres / ancianos | Pendiente de verificar |
| Targum Onkelos | Bereshit 1:1 | ... | Cotejado |
```

`Estado` values: `Cotejado`, `Pendiente de verificar`, `Mención indirecta en la clase`

## Verification Policy

Class transcripts and raw notes are authoritative for the teacher's argument, but secondary claims must stay traceable.

Always mark as pending when not directly checked:

- Exact Talmud / midrash / Zohar citations
- Lexical equations across Greek, Hebrew, and Aramaic
- Historical claims (Yamnia, movements, calendars, Nicea, etc.)
- Commentator attributions (Ibn Ezra, Rashi, Ramban, etc.)
- Manuscript or syriac transmission claims

Never:

- Invent quotations from scripture, Talmud, midrash, or videos
- Present pedagogical wordplay as settled lexicography without a checkbox
- Close a doctrinal conclusion on an unverified rabbinic citation

## Linking and Tags

- Inline verse tags: `#iojanan_10_11`, `#bereshit_1_1`
- Related notes: prefer `## Ver también` with relative links or wikilinks
- Both styles are acceptable:
  - `[Yojanán 10](./yojanan_10_puerta_pastor_abba.md)`
  - `[[yojanan_10_puerta_pastor_abba|Yojanán 10: la puerta]]`
- Prefer linking over duplicating long explanations across notes

## Agent Workflow (Any LLM)

1. Read target note if editing; read 1–2 nearby notes in the same series for convention matching
2. Run `npm run scriptures:ensure` when verses are needed
3. Detect mode: raw-notes | transcript | thematic | edit-existing
4. Ingest source material without inventing quotes
5. Build only the sections the topic needs
6. Pull verse text from local corpus into comparison sheets
7. Add lexical sheets when words carry the argument
8. Record external literature in citation format or pending checklist
9. Refresh `references`, `sources`, and cross-links
10. Append a short learning entry to `private/hermes/learning-log.md` when Hermes-style work is done

## Suggested User Prompt (Copy/Paste)

```text
Topic:
Mode: edit-existing | single-note | multi-note | thematic
Output path(s) in content/:
Source: raw notes | youtube URL | transcript path | web
Required verse links:
Include lexical sheet? yes/no
Include Jewish/external references? yes/no
Constraints:
```

## Agent Review Checklist

- [ ] Title is human-readable, not only a verse reference
- [ ] `# Tesis` states one clear claim
- [ ] `## Alcance de la nota` present for transcript/class notes
- [ ] Discussed verses appear in a comparison sheet with local corpus text
- [ ] Greek–Hebrew–Aramaic terms use a lexical sheet when translation shapes the argument
- [ ] Talmud, midrash, targum, and commentator mentions are cited precisely or marked pending
- [ ] יהוה used where the divine name appears
- [ ] Hebrew without nikud unless disambiguation requires vowels
- [ ] `## Pendiente de verificar` lists unchecked secondary claims
- [ ] `## Ver también` links related notes
- [ ] No invented quotations