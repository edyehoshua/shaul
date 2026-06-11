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
- Alcance de la nota (fuente, pasaje base, avisos de verificación)
- Texto base
- Hoja de comparación
- Hoja léxica / Léxico clave / Léxico base
- Referencias judías y fuentes externas
- Bloques temáticos de argumento
- Conexiones principales
- Conclusión
- Pendiente de verificar
- Ver también

Para la especificación completa que usan los agentes (Grok, Cursor, Codex, Hermes), ver [docs/note-authoring.md](../docs/note-authoring.md).

## Comparación de textos

Cuando el tema lo amerite, usar una tabla corta y legible:

| Referencia     | Hebreo | Traducción ES (TTH) | Observación                |
| -------------- | ------ | ------------------- | -------------------------- |
| #tehilim_2_7   | ...    | ...                 | Filiación mesiánica        |
| #matiyahu_3_17 | ...    | ...                 | Eco y expansión apostólica |

En notas de clase o Besorah también sirve esta variante:

| Referencia | Texto local | Función en la clase |
| --- | --- | --- |
| #iojanan_11_4 | extracto TTH / Delitzsch | Clave interpretativa del pasaje |

## Hoja léxica (griego, hebreo, arameo)

Usar cuando la traducción o la equivalencia entre idiomas sostiene el argumento.

| Término | Transliteración | Sentido en la nota | Raíz o base | Observación |
| --- | --- | --- | --- | --- |
| **(אמן)** | emun | afirmarse, fidelidad | אמן | No reducir a "fe" emocional |
| **(πιστεύω)** | pisteuo | afirmarse | πιστ- | Aproximación, no equivalencia perfecta |

Reglas:

- Escribir la forma en su escritura original: **(אבא)**, **(πνεῦμα)**
- Hebreo sin nikud por defecto
- Distinguir equivalencia exacta, aproximación interpretativa o analogía pedagógica
- Si el cotejo léxico no está hecho, mover el punto a `Pendiente de verificar`

## Referencias judías y otras fuentes

Cuando la clase o el estudio mencione Talmud, midrash, targum, comentaristas o historiadores, registrar la referencia de forma trazable:

| Tipo | Formato | Ejemplo |
| --- | --- | --- |
| Talmud Bavli | tratado + daf | b. Sanhedrin 37a |
| Midrash | colección + referencia | Bereishit Rabbah 44:7 |
| Targum | nombre + pasaje | Targum Onkelos, Bereshit 1:1 |
| Comentarista | autor + pasaje | Ibn Ezra, Bereshit 1:1 |
| Historiador | obra + cita | Josefo, Ant. 18.23 |

Si la cita exacta no está confirmada, conservar la idea en la nota y añadir una casilla en `Pendiente de verificar`. No inventar referencias.

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
