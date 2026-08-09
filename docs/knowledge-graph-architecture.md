# Arquitectura inicial del grafo de conocimiento

Esta primera etapa introduce el grafo de conocimiento en paralelo con Quartz. Las notas existentes siguen siendo la fuente documental publicada; no se migran ni se reemplazan en esta etapa.

## Arquitectura actual

Quartz toma Markdown desde `content/`, lo transforma y emite HTML estático. El grafo experimental se incorpora como un emisor adicional: los archivos YAML bajo `knowledge/` se validan, se compilan a `generated/graph.json` y se copian al sitio junto con `graph.html`. El servidor de Quartz y el despliegue estático siguen funcionando sin un backend.

## Modelo

- `Entity`: una entidad canónica con ID estable y tipo (`concept`, `word`, `verse`, `person` o `book`).
- `Word`: una expresión léxica con idioma, escritura y transliteración opcional.
- `Concept`: una idea scriptural que puede asociar varias formas lingüísticas mediante `forms`.
- `Verse`: una referencia canónica a un libro, capítulo y versículo.
- `Person`: una persona que puede relacionarse con conceptos.
- `Book`: un libro que contiene versos.
- `Mention`: un fragmento de una nota que contribuye contexto a una o más entidades; no es una afirmación semántica automática.
- `Relation`: una relación explícita entre dos entidades. Las relaciones usan `confirmed` o `proposed`.

Los IDs de los archivos son locales a su colección (`son-of-man.yml`), pero el compilador produce IDs tipo-seguros como `concept:son-of-man` y `word:bar-enash-ar`. Así, `Word` y `Concept` nunca se almacenan como el mismo objeto.

Las Mentions no son nodos visibles del grafo. Se compilan en `entityMentions` para que la interfaz pueda seleccionar un Concepto y recuperar sus fragmentos y notas originales sin llenar la visualización con nodos documentales.

## Datos piloto

El conjunto inicial contiene 25 Conceptos, 12 Words, 6 Verses, 5 Persons, 5 Books, 6 Mentions y 25 Relations. El caso más profundo es `concept:son-of-man`, conectado con `concept:son`, `word:bar-enash-ar` y `word:ben-ha-adam-he`, además de Daniel 7, Marcos 14, el Mesías y el Anciano de Días. `concept:torah` y `word:torah-he` prueban explícitamente la separación entre concepto y forma léxica.

## Compilación y validación

```bash
npm run graph:validate
npm run graph:build
```

El validador detecta YAML inválido, tipos de colección incorrectos, IDs duplicados, IDs mal formados, referencias inexistentes, formas Concepto → Word inválidas, libros inexistentes para Verses y tipos/status de Relation no admitidos. El compilador falla si la validación falla.

## Ruta experimental

La portada nueva de Shaul se emite como HTML estático propio en `index.html`; `/graph` conserva un alias directo a la misma experiencia. La página no usa el layout ni los scripts globales de Quartz. Carga `generated/graph.json`, crea el grafo con Graphology y lo renderiza con Sigma.js. Permite seleccionar nodos, filtrar por tipo y ver formas lingüísticas, vecinos y Mentions. Quartz permanece como capa legacy para las notas.

## Compatibilidad y límites

- El grafo se genera como archivos estáticos y es compatible con GitHub Pages; no requiere Node en producción, servidor, base de datos ni autenticación.
- El compilador es una etapa de build y el JSON generado se conserva en Git para que el artefacto sea revisable.
- Las relaciones interpretativas no se infieren con un LLM. `proposed` permite sugerencias futuras sin convertirlas en conocimiento autoritativo.
- Las entidades `Verse` conservan la referencia canónica; el texto bíblico sigue viniendo del corpus local y no se duplica en este piloto.
- El conjunto no intenta representar toda la Biblia, todo el léxico ni todos los contenidos existentes.
