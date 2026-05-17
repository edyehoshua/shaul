import path from "path"
import { readFile, writeFile } from "fs/promises"
import type { Root as HTMLRoot } from "hast"
import type { Root as MDRoot } from "remark-parse/lib"
import cfg from "../quartz.config"
import { glob } from "../quartz/util/glob"
import { joinSegments, slugifyFilePath, type FilePath } from "../quartz/util/path"
import { createHtmlProcessor, createMdProcessor } from "../quartz/processors/parse"
import { filterContent } from "../quartz/processors/filter"
import { getStaticResourcesFromPlugins } from "../quartz/plugins"

function expectTree<T>(tree: T | undefined, stage: string): T {
  if (!tree) {
    throw new Error(`${stage} returned no syntax tree`)
  }

  return tree
}

const targetRelative = "temas/ben_hijo_titulos_mesias.md" as FilePath
const targetFullPath = joinSegments("content", targetRelative) as FilePath

const argv = {
  directory: "content",
  output: "public",
  verbose: false,
  watch: false,
  serve: false,
  baseDir: "",
  port: 8080,
  wsPort: 3001,
  remoteDevHost: "",
  bundleInfo: false,
}

const allFiles = await glob("**/*.*", argv.directory, cfg.configuration.ignorePatterns)
const ctx = {
  buildId: "trace-ben-hijo",
  argv,
  cfg,
  allFiles,
  allSlugs: allFiles.map((fp) => slugifyFilePath(fp)),
  incremental: false,
}

const report: Record<string, unknown> = {
  targetRelative,
  targetSlug: slugifyFilePath(targetRelative),
  discoveredByGlob: allFiles.includes(targetRelative),
  publicExistsBeforeProbe: false,
}

report.publicExistsBeforeProbe = await readFile(
  path.join("public", "temas", "ben_hijo_titulos_mesias.html"),
  "utf8",
)
  .then(() => true)
  .catch(() => false)

try {
  const raw = await readFile(targetFullPath, "utf8")
  let transformed = raw.trim()
  for (const plugin of cfg.plugins.transformers.filter((plugin) => plugin.textTransform)) {
    transformed = plugin.textTransform!(ctx as never, transformed)
  }

  report.textLoaded = true
  report.textLength = transformed.length

  const vfile = {
    value: transformed,
    path: targetFullPath,
    stem: path.basename(targetFullPath, path.extname(targetFullPath)),
    data: {
      filePath: targetFullPath,
      relativePath: targetRelative,
      slug: slugifyFilePath(targetRelative),
    },
  }

  const mdProcessor = createMdProcessor(ctx as never)
  const mdAst = expectTree(
    mdProcessor.parse(vfile as never) as MDRoot | undefined,
    "Markdown parse",
  )
  const mdTree = expectTree(
    (await mdProcessor.run(mdAst, vfile as never)) as MDRoot | undefined,
    "Markdown transform",
  )
  report.markdownParsed = true
  report.frontmatter = (vfile.data as Record<string, unknown>).frontmatter ?? null

  const htmlProcessor = createHtmlProcessor(ctx as never)
  const htmlTree = expectTree(
    (await htmlProcessor.run(mdTree, vfile as never)) as HTMLRoot | undefined,
    "HTML transform",
  )
  report.htmlProcessed = true

  const filtered = filterContent(ctx as never, [[htmlTree, vfile as never]])
  report.filteredCount = filtered.length
  report.filteredOut = filtered.length === 0

  if (filtered.length > 0) {
    const staticResources = getStaticResourcesFromPlugins(ctx as never)
    const contentPage = cfg.plugins.emitters.find((emitter) => emitter.name === "ContentPage")
    if (contentPage) {
      const emitted = await contentPage.emit(ctx as never, filtered, staticResources)
      const emittedPaths: string[] = []
      if (Symbol.asyncIterator in emitted) {
        for await (const file of emitted) {
          emittedPaths.push(file)
        }
      } else {
        emittedPaths.push(...emitted)
      }
      report.contentPageEmitted = emittedPaths
    }
  }
} catch (error) {
  report.error = {
    message: error instanceof Error ? error.message : String(error),
    stack: error instanceof Error ? error.stack : null,
  }
}

await writeFile(".quartz-trace-ben-hijo.json", JSON.stringify(report, null, 2) + "\n")
