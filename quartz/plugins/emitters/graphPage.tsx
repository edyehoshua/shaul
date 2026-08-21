import fs from "node:fs/promises"
import path from "node:path"
import { render } from "preact-render-to-string"
import GraphHome from "../../components/GraphHome"
import { buildGraph } from "../../../scripts/build-graph"
import { FilePath, FullSlug } from "../../util/path"
import { QuartzEmitterPlugin } from "../types"
import { write } from "./helpers"
// @ts-ignore - Quartz's inline loader turns this source into a bundled string.
import graphExplorerScript from "../../components/scripts/graph-explorer.inline"
// @ts-ignore - Quartz's Sass loader turns this source into CSS text.
import graphHomeStyle from "../../components/styles/graph-home.scss"

const homeSlug = "index" as FullSlug
const graphSlug = "graph" as FullSlug

function renderHomePage(): string {
  const body = render(<GraphHome />)
  return `<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#f4f1e9" />
    <meta name="description" content="Shaul — Escritura conectada por conceptos." />
    <title>Shaul · Escritura conectada.</title>
    <style>${graphHomeStyle}</style>
  </head>
  <body>
    ${body}
    <script type="module">${graphExplorerScript}</script>
  </body>
</html>
`
}

export const GraphPageEmitter: QuartzEmitterPlugin = () => ({
  name: "GraphPage",
  async *emit(ctx, _content, _resources) {
    const { outputPath } = await buildGraph()
    const generatedPath = path.join(ctx.argv.output, "generated", "graph.json")
    await fs.mkdir(path.dirname(generatedPath), { recursive: true })
    await fs.copyFile(outputPath, generatedPath)
    const page = renderHomePage()
    yield generatedPath as FilePath
    yield await write({ ctx, slug: homeSlug, ext: ".html", content: page })
    yield await write({ ctx, slug: graphSlug, ext: ".html", content: page })
  },
  async *partialEmit() {},
})
