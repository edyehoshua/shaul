import { QuartzEmitterPlugin } from "../types"
import { i18n } from "../../i18n"
import { unescapeHTML } from "../../util/escape"
import { FullSlug, getFileExtension, isAbsoluteURL, joinSegments, QUARTZ } from "../../util/path"
import { ImageOptions, SocialImageOptions, defaultImage, getSatoriFonts } from "../../util/og"
import { loadEmoji, getIconCode } from "../../util/emoji"
import { Readable } from "stream"
import { write } from "./helpers"
import { BuildCtx } from "../../util/ctx"
import { QuartzPluginData } from "../vfile"
import fs from "node:fs/promises"
import { createRequire } from "node:module"
import { styleText } from "util"

const require = createRequire(import.meta.url)

const defaultOptions: SocialImageOptions = {
  colorScheme: "lightMode",
  width: 1200,
  height: 630,
  imageStructure: defaultImage,
  excludeRoot: false,
}

type OgHeadPageData = QuartzPluginData & {
  filePath?: string
  slug?: string
  frontmatter?: {
    socialImage?: string
  }
}

type OgFonts = Awaited<ReturnType<typeof getSatoriFonts>>
type PreactFactory = {
  h: (type: unknown, props: Record<string, string> | null, ...children: unknown[]) => unknown
  Fragment: unknown
}

function getPreactFactory(): PreactFactory {
  const preactModuleName = "preact"
  return require(preactModuleName) as PreactFactory
}

function renderOgHeadTags(
  userDefinedOgImagePath: string | undefined,
  ogImagePath: string,
  ogImageMimeType: string,
  fullOptions: SocialImageOptions,
) {
  const { h, Fragment } = getPreactFactory()
  const tags: unknown[] = []

  if (!userDefinedOgImagePath) {
    tags.push(
      h("meta", { property: "og:image:width", content: fullOptions.width.toString() }),
      h("meta", { property: "og:image:height", content: fullOptions.height.toString() }),
    )
  }

  tags.push(
    h("meta", { property: "og:image", content: ogImagePath }),
    h("meta", { property: "og:image:url", content: ogImagePath }),
    h("meta", { name: "twitter:image", content: ogImagePath }),
    h("meta", { property: "og:image:type", content: ogImageMimeType }),
  )

  return h(Fragment, null, ...tags)
}

async function renderWebp(svg: string): Promise<Readable> {
  try {
    const sharpModuleName = "sharp"
    const sharpModule = await import(sharpModuleName)
    return sharpModule.default(Buffer.from(svg)).webp({ quality: 40 })
  } catch {
    throw new Error(
      "CustomOgImages requires the optional 'sharp' package. Install it before enabling this emitter.",
    )
  }
}

async function renderSvg(
  svgInput: ImageOptions["fileData"] extends never
    ? never
    : ReturnType<SocialImageOptions["imageStructure"]>,
  options: {
    width: number
    height: number
    fonts: OgFonts
  },
): Promise<string> {
  const satoriModuleName = "satori"
  const { default: satori } = await import(satoriModuleName)

  return satori(svgInput, {
    width: options.width,
    height: options.height,
    fonts: options.fonts,
    loadAdditionalAsset: async (languageCode: string, segment: string) => {
      if (languageCode === "emoji") {
        return await loadEmoji(getIconCode(segment))
      }

      return languageCode
    },
  })
}

/**
 * Generates social image (OG/twitter standard) and saves it as `.webp` inside the public folder
 * @param opts options for generating image
 */
async function generateSocialImage(
  { cfg, description, fonts, title, fileData }: ImageOptions,
  userOpts: SocialImageOptions,
): Promise<Readable> {
  const { width, height } = userOpts
  const customIconPath = joinSegments("design", "logo.png")
  const defaultIconPath = joinSegments(QUARTZ, "static", "icon.png")
  let iconPath = defaultIconPath
  let iconBase64: string | undefined = undefined
  try {
    await fs.access(customIconPath)
    iconPath = customIconPath
  } catch {
    // Fall back to the default Quartz icon when no custom logo is present.
  }

  try {
    const iconData = await fs.readFile(iconPath)
    iconBase64 = `data:image/png;base64,${iconData.toString("base64")}`
  } catch (err) {
    console.warn(styleText("yellow", `Warning: Could not find icon at ${iconPath}`))
  }

  const imageComponent = userOpts.imageStructure({
    cfg,
    userOpts,
    title,
    description,
    fonts,
    fileData,
    iconBase64,
  })

  const svg = await renderSvg(imageComponent, { width, height, fonts })

  return renderWebp(svg)
}

async function processOgImage(
  ctx: BuildCtx,
  fileData: QuartzPluginData,
  fonts: OgFonts,
  fullOptions: SocialImageOptions,
) {
  const cfg = ctx.cfg.configuration
  const slug = fileData.slug!
  const titleSuffix = cfg.pageTitleSuffix ?? ""
  const title =
    (fileData.frontmatter?.title ?? i18n(cfg.locale).propertyDefaults.title) + titleSuffix
  const description =
    fileData.frontmatter?.socialDescription ??
    fileData.frontmatter?.description ??
    unescapeHTML(fileData.description?.trim() ?? i18n(cfg.locale).propertyDefaults.description)

  const stream = await generateSocialImage(
    {
      title,
      description,
      fonts,
      cfg,
      fileData,
    },
    fullOptions,
  )

  return write({
    ctx,
    content: stream,
    slug: `${slug}-og-image` as FullSlug,
    ext: ".webp",
  })
}

export const CustomOgImagesEmitterName = "CustomOgImages"
export const CustomOgImages: QuartzEmitterPlugin<Partial<SocialImageOptions>> = (userOpts) => {
  const fullOptions = { ...defaultOptions, ...userOpts }

  return {
    name: CustomOgImagesEmitterName,
    getQuartzComponents() {
      return []
    },
    async *emit(ctx, content, _resources) {
      const cfg = ctx.cfg.configuration
      const headerFont = cfg.theme.typography.header
      const bodyFont = cfg.theme.typography.body
      const fonts = await getSatoriFonts(headerFont, bodyFont)

      for (const [_tree, vfile] of content) {
        if (vfile.data.frontmatter?.socialImage !== undefined) continue
        yield processOgImage(ctx, vfile.data, fonts, fullOptions)
      }
    },
    async *partialEmit(ctx, _content, _resources, changeEvents) {
      const cfg = ctx.cfg.configuration
      const headerFont = cfg.theme.typography.header
      const bodyFont = cfg.theme.typography.body
      const fonts = await getSatoriFonts(headerFont, bodyFont)

      // find all slugs that changed or were added
      for (const changeEvent of changeEvents) {
        if (!changeEvent.file) continue
        if (changeEvent.file.data.frontmatter?.socialImage !== undefined) continue
        if (changeEvent.type === "add" || changeEvent.type === "change") {
          yield processOgImage(ctx, changeEvent.file.data, fonts, fullOptions)
        }
      }
    },
    externalResources: (ctx) => {
      if (!ctx.cfg.configuration.baseUrl) {
        return {}
      }

      const baseUrl = ctx.cfg.configuration.baseUrl
      return {
        additionalHead: [
          (pageData: OgHeadPageData) => {
            const isRealFile = pageData.filePath !== undefined
            let userDefinedOgImagePath = pageData.frontmatter?.socialImage

            if (userDefinedOgImagePath) {
              userDefinedOgImagePath = isAbsoluteURL(userDefinedOgImagePath)
                ? userDefinedOgImagePath
                : `https://${baseUrl}/static/${userDefinedOgImagePath}`
            }

            const generatedOgImagePath = isRealFile
              ? `https://${baseUrl}/${pageData.slug!}-og-image.webp`
              : undefined
            const defaultOgImagePath = `https://${baseUrl}/static/og-image.png`
            const ogImagePath = userDefinedOgImagePath ?? generatedOgImagePath ?? defaultOgImagePath
            const ogImageMimeType = `image/${getFileExtension(ogImagePath) ?? "png"}`
            return renderOgHeadTags(
              userDefinedOgImagePath,
              ogImagePath,
              ogImageMimeType,
              fullOptions,
            ) as never
          },
        ],
      }
    },
  }
}
