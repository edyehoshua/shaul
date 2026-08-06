# Pipeline de Somos El Cuerpo del Mesías

## Alcance inicial

Esta lane incorpora seis playlists del canal [Somos El Cuerpo del Mesías](https://www.youtube.com/@SomosElCuerpodelMesias/playlists):

- Carta a los Efesios — 9 videos
- Carta a los Gálatas — 11 videos
- Carta a los Romanos — 29 videos
- Doctrinas de Ha'Satán — 4 videos
- Proverbios - Mishlei — 100 videos
- Neoidolatría, Israel y el legado de las naciones — 35 videos

El inventario contiene **188 videos deduplicados por ID de YouTube**. La fuente durable es `data/inventories/somoselcuerpodelmesias.json`; la propiedad exclusiva de lanes está en `data/inventories/somoselcuerpodelmesias.lanes.json`.

## Cuatro workers

| Worker                                          | Playlists                           | Videos | Criterio                            |
| ----------------------------------------------- | ----------------------------------- | -----: | ----------------------------------- |
| `somoselcuerpodelmesias-efesios-galatas`        | Efesios, Gálatas                    |     20 | Epístolas de formación y libertad   |
| `somoselcuerpodelmesias-romanos`                | Romanos                             |     29 | Argumento de Romanos en secuencia   |
| `somoselcuerpodelmesias-proverbios`             | Proverbios - Mishlei                |    100 | Sabiduría, vocabulario y conexiones |
| `somoselcuerpodelmesias-doctrinas-neoidolatria` | Doctrinas de Ha'Satán, Neoidolatría |     39 | Discernimiento, Israel y naciones   |

Cada worker tiene ownership exclusivo de sus playlists y `source_id`. Ningún worker debe editar una fuente o una nota perteneciente a otra lane.

## Flujo eficiente

1. Inventariar y deduplicar videos por ID.
2. Recuperar transcripciones en paralelo, manteniéndolas bajo `private/transcripts/somoselcuerpodelmesias/`.
3. Procesar por lotes pequeños y reanudables; un fallo individual no bloquea el resto.
4. Crear una nota por exposición coherente, no una nota artificial por cada fragmento.
5. Escribir la prosa humana en español y conservar las citas bíblicas en su idioma fuente.
6. Usar `docs/scriptures/` como fuente primaria para los textos bíblicos.
7. Incluir título humano, tesis, alcance, hoja de comparación, conexiones, pendientes, conclusión, créditos públicos y `source_ids` únicos.
8. Validar cada lote antes de que el integrador canónico lo incorpore a `feat/somoselcuerpodelmesias`.

## Gates de publicación

```bash
npm run content:check-frontmatter
npm run youtube:check
npm run verse-tags:check
python3 scripts/check_transcript_note_quality.py
npm run verse-index:test
npm run scriptures:lookup:test
git diff --check
npm run authoring:coverage
```

Las transcripciones privadas son evidencia de trabajo y nunca deben enlazarse desde una nota pública. Las notas deben mostrar el crédito del canal y la URL pública del video, sin inventar citas ni completar silencios del transcript con especulación.

## Estado y siguiente lote

La rama se abre como una integración reanudable: primero queda fijado el inventario y el ownership; luego los cuatro workers producen lotes de notas, y un único integrador selecciona cambios efectivos, ejecuta los gates y publica. La cobertura nueva se debe distinguir de remediaciones sobre notas ya existentes.
