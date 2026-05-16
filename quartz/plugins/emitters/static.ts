import { FilePath, QUARTZ, joinSegments } from "../../util/path"
import { QuartzEmitterPlugin } from "../types"
import fs from "fs"
import { glob } from "../../util/glob"
import { dirname } from "path"

export const Static: QuartzEmitterPlugin = () => ({
  name: "Static",
  async *emit({ argv, cfg }) {
    const staticPath = joinSegments(QUARTZ, "static")
    const customIconPath = joinSegments("design", "logo.png") as FilePath
    const fps = await glob("**", staticPath, cfg.configuration.ignorePatterns)
    const outputStaticPath = joinSegments(argv.output, "static")
    await fs.promises.mkdir(outputStaticPath, { recursive: true })
    for (const fp of fps) {
      const src = joinSegments(staticPath, fp) as FilePath
      const dest = joinSegments(outputStaticPath, fp) as FilePath
      await fs.promises.mkdir(dirname(dest), { recursive: true })
      await fs.promises.copyFile(src, dest)
      yield dest
    }

    try {
      await fs.promises.access(customIconPath, fs.constants.R_OK)
      const outputIconPath = joinSegments(outputStaticPath, "icon.png") as FilePath
      await fs.promises.copyFile(customIconPath, outputIconPath)
      yield outputIconPath
    } catch {
      // Keep the default Quartz icon when no custom logo is provided.
    }
  },
  async *partialEmit() {},
})
