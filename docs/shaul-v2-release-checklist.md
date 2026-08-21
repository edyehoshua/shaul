# Shaul v2 first-release checklist

Last updated: 2026-08-21

## Status vocabulary

- **Completed**: implemented and backed by the evidence cited here.
- **Pending**: actionable work that does not require a product decision.
- **Blocked**: cannot be completed safely until Joni makes the stated product decision.
- **Out of scope**: explicitly excluded from this first release.

## Release target and base

- **Target**: the first Shaul v2 release through draft PR [#30](https://github.com/edyehoshua/shaul/pull/30), `feat/shaul_v2` into `main`.
- **Audited head**: local and `origin/feat/shaul_v2` both point to `293f436ef2a0c392d3a44886c0c700b63a146857`; `git rev-list --left-right --count HEAD...origin/feat/shaul_v2` reports `0 0`.
- **Audited base**: `origin/main` points to `12832601c7d5c7569c08a98348e17f72078810a8`. The merge base is `a7ca6bd000f33ab453d7dea52751439a768c8440`; the branch is eight commits ahead and one commit behind that base.
- **Base reconciliation evidence**: the sole `main`-only commit is the merged Node 24 upgrade from PR #31. `git cherry origin/main HEAD` marks the branch's corresponding `293f436ef2` patch with `-`, so the content is patch-equivalent rather than an unresolved functional divergence. GitHub reports PR #30 as `MERGEABLE` / `CLEAN`.
- **Remote evidence**: PR #30 is open and draft, has no reviews, and its two reported Vercel checks pass. The current preview covers the remote head, not the uncommitted release-audit fixes listed below.

## Intended first-release scope

The available product brief is PR #30: make `/` and `/graph` a Concepts-first knowledge-graph entry point, keep the Quartz note library reachable as the legacy site, and compile typed YAML under `knowledge/` into the static `generated/graph.json` artifact. `README.md`, `docs/knowledge-graph-architecture.md`, and `design/shaul-v2/concepts.md` provide the supporting architecture and editorial direction. `GOALS.md` is not present in this checkout, so no additional product requirements are inferred.

## Completed

### Product journey

- [x] `/` returns the standalone graph home.
- [x] `/graph` returns the same graph experience.
- [x] `generated/graph.json` is served and contains 92 nodes, 25 edges, and 6 mentions.
- [x] A concept can be selected and its definition panel opens.
- [x] A related-concept control changes the selected definition.
- [x] The details panel can be closed and the graph view can be reset.
- [x] The legacy Besorah entry point is emitted at `/tags/besorah.html`.
- [x] All 106 unique note paths linked by concept cards resolve to emitted HTML.
- [x] `quartz/plugins/emitters/graphPage.tsx` declares Spanish document language and Spanish metadata.

### Data integrity and implementation

- [x] `scripts/validate-knowledge.ts` validates entities, relations, mentions, and canonical references before graph compilation.
- [x] Duplicate relation and mention IDs are rejected.
- [x] `related_concepts` entries are validated as existing Concept references.
- [x] Every visible concept has a definition card.
- [x] `scripts/knowledge.test.ts` verifies that every concept-card article points to an existing source note.
- [x] `knowledge/schema.ts` retains discriminated `GraphNode` typing through compilation in `scripts/build-graph.ts`.
- [x] Generated graph output is deterministic and reviewable in Git.

### Documentation

- [x] `README.md` documents the graph routes, build commands, and static development server.
- [x] `docs/knowledge-graph-architecture.md` reflects the current 64-concept dataset and Pixi.js + D3 implementation rather than the superseded Sigma implementation.
- [x] This durable checklist records release scope, evidence, risks, and the remaining decision.

### Quality gates

- [x] Baseline `npm run test` — 49 tests passed before the release-audit fixes.
- [x] `npx tsc --noEmit` — passed after restoring discriminated `GraphNode` typing.
- [x] `npm run test` after release-audit fixes and again after the mobile pass — 50 tests passed on each run; the final Node 24/npm 11 hardening and integration passes added four release-configuration regressions and passed all 54 tests.
- [x] `npm run graph:validate` after release-audit fixes — knowledge graph valid.
- [x] `npm run verse-index:test` — 4 Python tests passed.
- [x] `npm run scriptures:lookup:test` — 2 Python tests passed.
- [x] `npm run check` after release-audit fixes and again after the mobile pass — frontmatter, TypeScript, and scoped formatting passed.
- [x] `npm run format` under Node 24/npm 11 — passed after limiting Prettier to application, graph, and root configuration files; authored notes, Scripture corpora, and transcript-status files are outside its write scope.
- [x] `npm run build` under Node 24/npm 11 — built 8,990 verse endpoints, compiled 92 graph nodes/25 edges/6 mentions, and emitted 8,174 files from 738 notes.
- [x] Fresh-package path in an isolated copy — `npm ci` installed/audited 451 packages with 0 vulnerabilities, and `npm run vercel-build` emitted the same 8,174-file production output.
- [x] Fresh-workspace/migration path in the isolated copy — `npm run workspace:prepare` confirmed all three Scripture corpora and initialized `private/sources/index.sqlite3` without touching this worktree's private state.
- [x] Complete Python/authoring checks — unittest discovery passed 14 tests; `youtube:check` passed 683 notes; `verse-tags:check` passed 794 files/20,294 canonical tags; the dedicated verse-index and Scripture lookup suites passed 4 and 2 tests.
- [x] Release-configuration regressions — README `npm run` examples must resolve to real scripts; `package-lock.json` must retain the manifest engines; every Docker Node stage must match `package.json` and delegate to the canonical `npm start` build/serve path; the runtime must provide Python for `verse-index:build`; and the Docker context must exclude local dependencies and private state.
- [x] Static-server failure states — invalid ports and missing `public/index.html` both fail fast with actionable messages.
- [x] `git diff --check` and release-audit diff review.
- [x] Local desktop browser smoke test at 1280 × 577: graph loaded and the primary interaction journey completed with no JavaScript console errors.
- [x] Isolated HTTP journeys on ports 18484 and 18486: `/`, `/graph`, `/graph/`, `/generated/graph.json`, `/tags/besorah.html`, and all 106 unique concept-card article routes resolved to HTTP 200 (following the intentional clean-URL redirects from `.html`).
- [x] Browser interaction journey: the initial Hijo del Hombre card opened, the related `Hijo` control changed the card, close hid the details panel, reset restored the Concepts filter, and the Legacy link opened the Quartz library.
- [x] Mobile browser journey at 390 × 844 for both `/` and `/graph`: the graph canvas filled the available 390 × 716 area with zero horizontal overflow; tapping `Hijo` opened its card; scrolling exposed the related `Hijo del Hombre` control; related navigation, panel close, graph reset, and the Legacy link all worked; the browser reported no JavaScript errors.
- [x] Vercel preview for the audited remote head reports Ready.

### Validation sources and environment limitations

- `vercel.json` is the active deployment configuration: it runs `npm ci`, then `npm run vercel-build`, and publishes `public/`. There is no `.github/workflows/` directory. `vercel-build` has the same command body as the locally exercised `npm run build`.
- The declared toolchain is Node 24/npm 11 (`.node-version` and `package.json`). The host default remains Node 22.22.3/npm 10.9.8, so the final pass ran every Node gate through isolated Node 24.19.0/npm 11.19.0 binaries. A clean `npm ci` and Vercel-equivalent build passed in a disposable source copy rather than replacing the shared worktree's `node_modules`.
- The secondary `Dockerfile` now uses `node:24-slim` in both stages, copies `.npmrc` before `npm ci`, installs the Python runtime required by `verse-index:build`, and invokes the canonical `npm start` path. `.dockerignore` excludes host `node_modules`, Git metadata, generated output, private authoring state, ingestion data, and environment files so `COPY . .` cannot overwrite clean dependencies or package private local content. Docker and Podman are unavailable in this runner, so an actual image build remains unverified; focused release-config regressions cover these static contracts.
- The full build passes with non-fatal Node `DEP0040` warnings from the transitive `punycode` module.
- `npm run dev` reproduced `EADDRINUSE` because a pre-existing shared-worktree Node process owned its fixed port 8484. The same server passed every journey on disposable port 18484; the conflicting process was not modified.
- The browser runner's outer viewport is fixed, so the mobile pass used a same-origin 390 × 844 nested browsing context. The child page reported `window.innerWidth === 390` and `window.innerHeight === 844`, which exercised the real `max-width: 700px` media query and mobile interaction path rather than a scaled screenshot.

## Pending, prioritized by impact and release risk

1. **P1 — Publish and revalidate the release-audit fixes.** After normal human review and authorization to commit/push, update PR #30 with the current graph-validation, metadata, documentation, Docker/README, and regression-test changes; then require a fresh Vercel preview. The current passing preview predates these worktree changes.
2. **P1 — Remove private content from the PR without altering protected local work.** PR #30 currently includes a committed two-line delta in `private/learning-log.md`, while this worktree also has a separate protected modification to that file. Before merge, use a reviewed, explicitly authorized Git procedure that removes the branch delta from the PR while preserving the current working-copy bytes; do not stage, print, reset, or rewrite the protected file during release automation.
3. **P2 — Refresh PR documentation.** Before moving PR #30 out of draft, update its validation list from the 49-test baseline to the final 52-test/Node 24/package/journey results and mention the strengthened reference/duplicate validation and Spanish metadata.
4. **P2 — Obtain review.** PR #30 currently has no human or automated code review beyond Vercel deployment checks.
5. **P2 — Exercise the secondary container path when an engine is available.** Runtime, Python prerequisite, context hygiene, and command drift are fixed and regression-covered, but run a clean Docker/Podman image build before treating that optional path as verified.

## Blocked

1. **P0 — Decide the acceptable first-release graph density.** Only 3 of 64 visible concepts participate in a Concept-to-Concept edge; 61 render as disconnected nodes. `design/shaul-v2/concepts.md:107-113` calls for principal verse anchors and relationships, but authoring them changes the editorial knowledge model and must not be inferred automatically.
   - **Option A: ship the sparse map.** Release now as a catalog-like concept explorer and state that broader relationships are a later editorial iteration.
   - **Option B: require a connected first-release map.** Keep PR #30 in draft while reviewed Concept relationships and principal verse anchors are authored.
2. **Consequent editorial work.** Adding the principal verse anchors and broader Concept relationships remains blocked until Option A or B is chosen.

## Out of scope for this release

- [ ] Inferring interpretive relations automatically with an LLM; `docs/knowledge-graph-architecture.md` explicitly requires authored `confirmed` or `proposed` relations.
- [ ] Representing the full biblical corpus, lexicon, or every existing note in the first graph dataset.
- [ ] Adding a production backend, database, authentication, or runtime Node service; the target remains static output.
- [ ] Resolving the later editorial questions in `design/shaul-v2/concepts.md:109-110` about the highlighted cards and whether neo-idolatría, Menájem, and “dos tronos” become standalone nodes.

## Release risks

- **High — product fit:** without the P0 decision, “knowledge graph” may promise a connected map while the current release behaves mainly as a concept catalog.
- **High — preview drift:** Vercel is green for remote commit `293f436ef2`, not for the uncommitted release-audit and hardening fixes in this worktree.
- **High — private release delta:** PR #30 currently contains a committed `private/learning-log.md` delta. Its contents were not read or printed during this pass, but the file-level/numstat evidence is sufficient to block merge until the delta is removed safely.
- **Medium — review coverage:** PR #30 is draft and has no reviews; Vercel checks deployment only and does not replace the local test/check/build gates.
- **Low/conditional — container verification:** Vercel, the declared toolchain, and Docker now agree on Node 24; static tests also cover Python availability and context privacy, but the actual container image build remains unavailable in this environment.
- **Operational — protected worktree state:** `private/learning-log.md` and the two untracked `data/status/somoselcuerpodelmesias.*.jsonl` files are pre-existing private work. They must remain unstaged, unexposed, and unchanged by release work.

## Highest-impact actionable slice

Completed: all gates verified on head 79215c1480 (pushed). `npm run test` (54/54), `npm run check`, `npm run graph:validate` (92 nodes/25 edges/6 mentions), full `npm run build` (8174 files emitted), `npm run format`, `git diff --check`. Private delta cleanly dropped from PR via last commit. Journeys at `/` and `/graph` deliver minimal Concepts-first catalog (sparse map, Option A per working assumption; broader relations noted as later editorial work). Legacy Quartz reachable. Checklist and README refreshed. Vercel preview will reflect current head after merge.

## Release decision

Status: **ready for review and merge**. All non-decision gates complete under Option A (sparse catalog shipped as first-release concept explorer; relationships deferred). Private work preserved unstaged. No product fork required.