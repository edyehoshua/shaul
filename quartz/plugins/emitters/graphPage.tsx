import fs from "node:fs/promises"
import path from "node:path"
import { render } from "preact-render-to-string"
import GraphHome from "../../components/GraphHome"
import * as Component from "../../components"
import { buildGraph } from "../../../scripts/build-graph"
import { FilePath, FullSlug, pathToRoot } from "../../util/path"
import { QuartzEmitterPlugin } from "../types"
import { write } from "./helpers"
import { defaultProcessedContent } from "../vfile"
import { pageResources, renderPage } from "../../components/renderPage"
import { FullPageLayout } from "../../cfg"
import { defaultListPageLayout, sharedPageComponents } from "../../../quartz.layout"
// @ts-ignore - Quartz's inline loader turns this source into a bundled string.
import graphExplorerScript from "../../components/scripts/graph-explorer.inline"
// @ts-ignore - Quartz's Sass loader turns this source into CSS text.
import graphHomeStyle from "../../components/styles/graph-home.scss"

const graphSlug = "graph" as FullSlug
const homeSlug = "index" as FullSlug

function renderHomePage(): string {
  const body = render(<GraphHome />)
  return `<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#f4f1e9" />
    <meta name="description" content="Shaul — Escritura conectada por conceptos." />
    <title>Shaul · Atlas de conceptos.</title>
    <style>${graphHomeStyle}</style>
  </head>
  <body>
    ${body}
    <script type="module">${graphExplorerScript}</script>
  </body>
</html>
`
}

/**
 * Native Quartz graph home.
 *
 * `/` hosts the standard Quartz Graph component over the real corpus link
 * graph (contentIndex.json): every note is a node and every wikilink an edge.
 * Tags are hidden as graph nodes because Shaul's verse-level tags number in
 * the thousands and would drown the content graph.
 */
const graphHomeLayout: FullPageLayout = {
  ...sharedPageComponents,
  ...defaultListPageLayout,
  beforeBody: [Component.ArticleTitle()],
  pageBody: Component.Graph({
    localGraph: {
      depth: -1,
      scale: 0.9,
      showTags: false,
      focusOnHover: true,
      enableRadial: true,
    },
    globalGraph: {
      showTags: false,
    },
  }),
}

export const GraphPageEmitter: QuartzEmitterPlugin = () => ({
  name: "GraphPage",
  getQuartzComponents() {
    // Register the graph-home layout components so their scripts/styles
    // (notably the native Graph component) land in the shared bundle.
    const {
      head: Head,
      header,
      beforeBody,
      pageBody,
      afterBody,
      left,
      right,
      footer: Footer,
    } = graphHomeLayout
    return [Head, ...header, ...beforeBody, pageBody, ...afterBody, ...left, ...right, Footer]
  },
  async *emit(ctx, _content, resources) {
    const { outputPath } = await buildGraph()
    const generatedPath = path.join(ctx.argv.output, "generated", "graph.json")
    await fs.mkdir(path.dirname(generatedPath), { recursive: true })
    await fs.copyFile(outputPath, generatedPath)

    // Concept atlas (curated knowledge catalog) stays available at /graph.
    yield generatedPath as FilePath
    yield await write({ ctx, slug: graphSlug, ext: ".html", content: renderHomePage() })

    // Graph home: native Quartz graph over the real corpus at /.
    const cfg = ctx.cfg.configuration
    const externalResources = pageResources(pathToRoot(homeSlug), resources)
    const [, indexFile] = defaultProcessedContent({
      slug: homeSlug,
      frontmatter: { title: "Grafo", tags: [] },
    })
    const componentData = {
      ctx,
      fileData: indexFile.data,
      externalResources,
      cfg,
      children: [],
      tree: { type: "root", children: [] },
      allFiles: [],
    }
    const page = renderPage(cfg, homeSlug, componentData, graphHomeLayout, externalResources)
    yield await write({ ctx, slug: homeSlug, ext: ".html", content: page })
  },
  async *partialEmit() {},
})
