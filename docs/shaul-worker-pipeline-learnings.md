# Aprendizajes del pipeline de workers de Shaul

## Propósito

Este documento conserva las decisiones, fallos y procedimientos aprendidos durante el trabajo de integración de fuentes de Eric de Jesús Rodríguez Mendoza. Debe servir como guía para abrir otra lane o repetir el proceso con otro canal sin volver a consumir tokens en ciclos vacíos, duplicar fuentes o mezclar worktrees de forma insegura.

## Arquitectura que funcionó

- Mantener una sola rama canónica de publicación: `feat/eric_youtube`.
- Mantener un único integrador con autoridad para publicar.
- Usar un worktree y una rama por lane:
  - `worker/shaul-yojanan`
  - `worker/shaul-epistles`
  - `worker/shaul-efesios`
  - `worker/shaul-haftarot`
  - `worker/shaul-tanaj`
- Mantener el recuperador de transcripciones separado: nunca debe editar notas públicas, hacer commits canónicos ni hacer push.
- Usar `gpt-5.6-luna` mediante `openai-codex`. El intento con `grok-4.5` no fue viable porque el proveedor devolvió HTTP 403 por límite de gasto/créditos.
- El integrador debe hacer `fetch`/rebase antes de revisar candidatos y debe publicar únicamente después de validar.

## Regla fundamental: propiedad de lanes

Cada fuente debe tener una única autoridad. No se debe reasignar una fuente a otra lane solo para igualar cantidades.

Antes de integrar un cambio:

1. Comparar el `source_id` contra todo `content/`.
2. Confirmar que la fuente pertenece a la lane del worker.
3. Rechazar cambios que dupliquen un `source_id`.
4. Rechazar cambios que editen una nota canónica bajo propiedad de otra lane.
5. Integrar únicamente el resultado efectivo, no todos los commits históricos de una rama.

Una rama de worker puede estar cientos de commits por delante y aun así contener trabajo ya integrado, reversiones, remediaciones obsoletas o cambios de otras lanes. Nunca se debe fusionar completa a ciegas.

## Fuentes y cobertura

Separar siempre estas categorías:

- **Cobertura nueva:** reduce el número de fuentes pendientes.
- **Remediación:** mejora una nota ya cubierta, pero no aumenta cobertura.
- **Clasificación:** marca una fuente como musical, no expositiva, no disponible o faltante.
- **Fuente bloqueada:** no tiene transcript local recuperable o la red/proveedor impide obtenerlo.
- **Fuente no reasignable:** tiene ownership exclusivo de otra lane.

El contador de cobertura no es una medida suficiente de productividad. Un ciclo puede producir commits válidos y seguir en el mismo porcentaje porque solo hizo remediaciones.

## Modo de cierre recomendado

Cuando la cobertura supera aproximadamente 95%:

1. Cambiar los autores a **cobertura nueva solamente**.
2. No remediar notas ya cubiertas salvo que la reparación sea indispensable para aceptar una fuente todavía pendiente.
3. Si no hay una fuente nueva elegible, responder exactamente `[SILENT]`.
4. No reintentar indefinidamente fuentes musicales, no expositivas o sin transcript.
5. Pausar el recuperador cuando no haya una fuente alternativa concreta.
6. Pausar un lane después de ciclos silenciosos confirmados.
7. Pausar el integrador cuando todos los autores estén silenciosos.

El error más costoso de esta ejecución fue mantener autores activos reparando notas ya cubiertas. La corrección de cobertura-nueva produjo inmediatamente dos integraciones nuevas; después todos los autores respondieron `[SILENT]`, confirmando que no quedaban candidatos automáticos claros.

## Reparto y velocidad

El reparto debe ser equitativo dentro de las restricciones de ownership, no artificialmente igual en número.

- Si una lane tiene más fuentes, verificar primero si realmente son procesables.
- Una cola grande puede estar compuesta casi totalmente por música, introducciones, faltantes o material sin transcript.
- No poner dos autores sobre el mismo lane sin dividir explícitamente los `source_id` y sin un mecanismo de exclusión.
- La frecuencia nominal no equivale a throughput: el integrador llegó a tardar varios minutos por ciclo. Un schedule cada minuto produjo consumo y ciclos vacíos; cada cinco minutos fue más estable.
- Medir el progreso por cambios de cobertura canónica, no por número de commits de workers.

## Criterios de una nota integrable

Cada nota nueva o consolidada debe conservar:

- frontmatter válido;
- título humano, no un verso crudo;
- prosa humana en español;
- `source_id` único;
- crédito público de Eric y URL pública del video;
- ausencia de rutas privadas de transcript;
- texto bíblico desde `docs/scriptures/` cuando exista;
- perícopas en orden;
- léxico argumental con forma fuente, transliteración, sentido, fuerza contextual y relación cualificada;
- `## Mapa de la enseñanza de Eric` con al menos tres entradas trazables;
- distinción entre observación de Eric, apoyo textual, inferencia y pendiente de verificar;
- hebreo sin barras de segmentación morfológica;
- enlaces Quartz válidos.

No inventar transcript, citas, referencias rabínicas ni argumentos que no se puedan atribuir o verificar. Las afirmaciones inciertas deben quedar como `Pendiente de verificar`.

## Gates obligatorios antes de publicar

Desde `/home/david/shaul`:

```bash
npm run scriptures:ensure
python3 scripts/check_transcript_note_quality.py
npm run content:check-frontmatter
npm run youtube:check
npm run verse-tags:check
npm run verse-index:test
npm run scriptures:lookup:test
git diff --check
npm run authoring:coverage
```

Para una integración concreta, revisar también:

```bash
git status --short --branch
git diff --stat origin/feat/eric_youtube...HEAD
git log --oneline --decorate -n 10
```

Los checks esenciales son:

- `quality_failures=0`;
- cero `source_id` duplicados;
- cero rutas privadas expuestas;
- cero segmentaciones hebreas inválidas;
- créditos públicos visibles;
- frontmatter sin tabs;
- índice bíblico regenerable;
- `git diff --check` limpio;
- rama canónica sincronizada con `origin`.

## Integración de worktrees

Procedimiento seguro:

1. Auditar la rama canónica y todos los worktrees.
2. Comparar cada worker con `feat/eric_youtube` usando `git diff` y `git log`.
3. Excluir worktrees `candidate-*` y `validate-run-*` antiguos salvo revisión explícita: pueden tener conflictos o estados intermedios.
4. Revisar los cambios efectivos por archivo y por `source_id`.
5. Integrar en lotes pequeños.
6. Ejecutar los gates después de cada lote.
7. Hacer push de `feat/eric_youtube`.
8. Leer de nuevo el estado remoto antes de mergear el PR.

No se debe afirmar que “todo fue integrado” solo porque una rama fue mergeada. Debe existir un reporte de qué se integró, qué se omitió y por qué.

## Recuperación de transcripciones

- El recuperador no debe escribir notas públicas.
- Debe guardar solo el material permitido en `private/` y actualizar los inventarios correspondientes.
- Un fallo de Supadata o YouTube bloqueado no debe producir una nota especulativa.
- Después de un retry corto sin resultado, clasificar la fuente como faltante y detener reintentos automáticos.
- Nunca exponer secretos, tokens, cookies ni rutas privadas en notas públicas o mensajes del repositorio.

## Fallos y correcciones aprendidas

### Demasiadas remediaciones

**Síntoma:** muchos commits, pero cobertura casi inmóvil.

**Causa:** los autores priorizaban reparar notas cubiertas.

**Corrección:** modo cobertura nueva solamente y `[SILENT]` cuando no haya candidato.

### Conflicto entre owners

**Síntoma:** el integrador rechaza cambios aunque la nota parezca correcta.

**Causa:** un worker intenta editar una fuente de otra lane o duplicar un `source_id`.

**Corrección:** una autoridad por lane, revisión global del inventario y rechazo explícito.

### Mezcla de ramas históricas

**Síntoma:** cientos de archivos modificados, duplicados o reversiones inesperadas.

**Causa:** fusionar una rama de worker acumulada durante muchas integraciones.

**Corrección:** seleccionar cambios efectivos por archivo/source ID, no hacer merge masivo.

### Prettier destructivo para Quartz

Algunas referencias Quartz con guion bajo se refluían de manera incompatible cuando se aplicaba Prettier masivamente. Usar Prettier dirigido y conservar el marcado canónico cuando la reescritura lo corrompa. `git diff --check` y las validaciones semánticas tienen prioridad sobre una limpieza cosmética global.

### Cambio de modelo

No cambiar el modelo de los jobs individualmente sin:

1. pausar todos los jobs;
2. cambiar los pins de todos;
3. ejecutar ciclos reales de verificación;
4. confirmar `last_status`, `execution_success` y logs;
5. reanudar solo después de comprobar el resultado.

## Estado de cierre de esta ejecución

Al finalizar la integración final:

- inventario: 958 videos;
- cobertura canónica: 932;
- pendientes: 26;
- notas transcriptivas: 485;
- `quality_failures=0`;
- IDs duplicados: 0;
- rutas privadas expuestas: 0;
- rama `feat/eric_youtube` limpia y sincronizada;
- el PR existente es `#25` hacia `main`.

Las diferencias históricas restantes de Yojanán no se integraron automáticamente porque incluían 205 archivos de divergencia, trabajo ya presente, reversiones o remediaciones capaces de sobrescribir contenido canónico mejor. Esa omisión es deliberada y debe repetirse como criterio de seguridad en otro canal.

## Checklist para un canal nuevo

- [ ] Crear inventario de playlists y `source_id`.
- [ ] Asignar lanes exclusivas.
- [ ] Preparar corpus bíblico local.
- [ ] Crear worktree separado por lane.
- [ ] Configurar un único integrador.
- [ ] Validar primero una nota por lane.
- [ ] Medir cobertura canónica y no solo commits.
- [ ] Clasificar música/no expositivo/faltante temprano.
- [ ] Pasar a cobertura nueva solamente al superar 95%.
- [ ] Pausar jobs silenciosos.
- [ ] Integrar selectivamente, nunca ramas completas a ciegas.
- [ ] Ejecutar todos los gates.
- [ ] Crear o actualizar un único PR de cierre.
- [ ] Mergear solo después de leer de nuevo CI, rama, PR y remoto.
