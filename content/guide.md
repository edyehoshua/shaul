---
title: "Guía v2 para Notas en Shaul"
description: "Reglas prácticas para crear notas bíblicas con Obsidian + Quartz + Hermes"
date: 2026-04-27
tags: [guia, obsidian, quartz, hermes, notas]
references: []
sources: []
---

# Guía v2 para Notas en Shaul

Esta guía define un marco simple para crear notas bíblicas conectadas entre sí, con estructura flexible por tema.

## Principios

- Enfocar toda nota en una pregunta o tesis concreta.
- Conectar pasajes entre sí de forma trazable.
- Priorizar claridad sobre volumen.
- Mantener fidelidad textual en citas y fuentes.

## Reglas de escritura

- Usar יהוה cuando se escriba el Nombre.
- Usar títulos claros y humanos (no solo una referencia de versículo).
- Mantener referencias de versículos en `references` y en el cuerpo (ejemplo: `#ieshaiahu_53_5`).
- Usar hebreo sin nikud por defecto.
- Usar hebreo con nikud solo cuando haga falta para desambiguar.

## Frontmatter recomendado

```yaml
---
title: ""
description: ""
date: YYYY-MM-DD
tags: []
references: []
sources: []
---
```

## Estructura flexible por tema

No hay plantilla fija obligatoria. Usa solo las secciones que el tema necesita:

- Tesis
- Texto base
- Hoja de comparación
- Conexiones Tanaj <-> Besorah
- Observaciones lingüísticas
- Conclusión
- Pendientes de verificación

## Comparación de textos

Cuando el tema lo amerite, usar una tabla corta y legible:

| Referencia     | Hebreo | Traducción ES (TTH) | Observación                |
| -------------- | ------ | ------------------- | -------------------------- |
| #tehilim_2_7   | ...    | ...                 | Filiación mesiánica        |
| #matiyahu_3_17 | ...    | ...                 | Eco y expansión apostólica |

## Fuentes para investigación

Prioridad:

1. https://yehoshuamaranata.blogspot.com
2. https://www.youtube.com/@EricdeJes%C3%BAsRodr%C3%ADguezMendoza
3. https://www.youtube.com/@SomosElCuerpodelMesias
4. Investigación adicional cuando haga falta contexto

## Flujo con Hermes

1. Definir tema.
2. Buscar fuente principal (blog o video).
3. Extraer transcripción (API o fallback).
4. Crear/actualizar nota en `content/`.
5. Enlazar versículos y notas relacionadas.
6. Registrar aprendizaje en `private/hermes/learning-log.md`.

## Herramientas para transcripción

```bash
python3 scripts/hermes/fetch_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

Si no hay transcripción directa, el script usa fallback con `yt-dlp`.
