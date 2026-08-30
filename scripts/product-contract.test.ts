import assert from "node:assert/strict"
import fs from "node:fs/promises"
import path from "node:path"
import { test } from "node:test"

const root = process.cwd()
const read = (p: string) => fs.readFile(path.join(root, p), "utf8")

test("Graph is the home: / is owned by the graph emitter, not the content page", async () => {
  const contentPage = await read("quartz/plugins/emitters/contentPage.tsx")
  assert.match(
    contentPage,
    /slug === "index"\s*\)\s*continue/,
    "ContentPage must skip the root index",
  )
  assert.match(
    contentPage,
    /graph home \(GraphPageEmitter\) owns `\/`/,
    "root index ownership comment must be present",
  )

  const graphPage = await read("quartz/plugins/emitters/graphPage.tsx")
  assert.match(graphPage, /homeSlug = "index"/, "GraphPage must emit at the home slug")
  assert.match(
    graphPage,
    /pageBody: Component\.Graph\(/,
    "home must use the native Quartz Graph component",
  )
  assert.match(graphPage, /showTags: false/, "home graph must hide high-cardinality tag nodes")
})

test("Native Quartz graph used for the home (not a custom reimplementation)", async () => {
  const graphPage = await read("quartz/plugins/emitters/graphPage.tsx")
  assert.match(graphPage, /import \* as Component from "\.\.\/\.\.\/components"/)
  assert.match(
    graphPage,
    /localGraph: \{\s*depth: -1/,
    "home graph must show the full corpus neighborhood",
  )
})

test("Home graph sizes both native graph containers, not only the canvas", async () => {
  const customStyles = await read("quartz/styles/custom.scss")
  assert.match(customStyles, /body\[data-slug="index"\]/)
  assert.match(customStyles, /\.graph-outer[\s\S]*height: clamp\(/)
  assert.match(
    customStyles,
    /\.graph-outer > \.graph-container[\s\S]*height: 100%/,
    "the graph canvas must receive the full homepage container height",
  )
  assert.match(customStyles, /62svh/, "mobile graph height should use the small viewport unit")
})

test("Explorer keeps corpus folders while filtering placeholder files", async () => {
  const explorer = await read("quartz/components/Explorer.tsx")
  assert.match(
    explorer,
    /!node\.isFolder[\s\S]*filePath\.endsWith\("_folder\.md"\)/,
    "_folder.md filtering must not remove its containing folder",
  )
})

test("Tag index renders each tag once (compact, hang-safe) for high-cardinality corpora", async () => {
  const tagContent = await read("quartz/components/pages/TagContent.tsx")
  assert.match(tagContent, /shaul-tag-index/, "compact tag-index markup must exist")
  assert.match(
    tagContent,
    /one link \+ count per tag/,
    "must document why the compact index is required",
  )
  // The index branch must not embed per-tag PageList previews (that caused a ~250k-anchor DOM).
  const indexBranch = tagContent.slice(
    tagContent.indexOf('if (tag === "/")'),
    tagContent.indexOf("} else {"),
  )
  assert.doesNotMatch(indexBranch, /<PageList/, "tag index must not inline per-page listings")
})

test("Concept-atlas loader can never sit stuck in the loading state", async () => {
  const script = await read("quartz/components/scripts/graph-explorer.inline.ts")
  assert.match(script, /preference: "webgl"/, "must fall back to WebGL when WebGPU is unavailable")
  assert.match(
    script,
    /window\.setTimeout/,
    "must install a timeout so the loading state is eventually replaced",
  )
  assert.match(
    script,
    /graph could not be loaded/,
    "fetch/render failures must surface a readable error instead of spinning forever",
  )
})
