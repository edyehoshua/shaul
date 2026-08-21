import fs from "node:fs/promises"
import path from "node:path"
import yaml from "js-yaml"
import {
  ConceptArticle,
  ConceptDefinition,
  ConceptEntity,
  ENTITY_TYPES,
  EntityType,
  KnowledgeCollections,
  KnowledgeEntity,
  Mention,
  Relation,
  isEntityType,
} from "../../knowledge/schema"

export interface KnowledgeIssue {
  file?: string
  message: string
}

export interface LoadedKnowledge extends KnowledgeCollections {
  files: Map<string, string>
  issues: KnowledgeIssue[]
}

const entityDirectories = new Set<string>(ENTITY_TYPES)

async function listYamlFiles(directory: string): Promise<string[]> {
  let entries: { name: string; isDirectory(): boolean }[]
  try {
    entries = (await fs.readdir(directory, { withFileTypes: true })) as unknown as typeof entries
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return []
    throw error
  }

  const files: string[] = []
  for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
    const entryPath = path.join(directory, entry.name)
    if (entry.isDirectory()) {
      files.push(...(await listYamlFiles(entryPath)))
    } else if (/\.(ya?ml)$/i.test(entry.name)) {
      files.push(entryPath)
    }
  }
  return files
}

async function loadYamlFile(filePath: string): Promise<unknown> {
  const source = await fs.readFile(filePath, "utf8")
  return yaml.load(source)
}

const cardConceptIds: Record<string, string> = {
  "ben-hadam": "son-of-man",
  "hijo-elohim": "son-of-god",
  abba: "abba",
  ruaj: "ruach",
  mashiaj: "messiah",
  "torah-y-gracia": "torah",
  reino: "kingdom",
  santidad: "holiness",
  emunah: "emunah",
  arrepentimiento: "repentance",
  resurreccion: "resurrection",
}

interface ConceptCard {
  slug: string
  definition: ConceptDefinition
  articles: ConceptArticle[]
}

interface ConceptTableEntry {
  slug: string
  title: string
}

function stripMarkdown(value: string): string {
  return value
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/`([^`]+)`/g, "$1")
    .trim()
}

function capitalizeLeadingText(value: string): string {
  return value.replace(/^([^\p{L}]*)(\p{Ll})/u, (_match, prefix: string, letter: string) => {
    return `${prefix}${letter.toUpperCase()}`
  })
}

function parseFrontmatterTitle(source: string): string | undefined {
  const match = source.match(/^---\r?\n([\s\S]*?)\r?\n---/)
  if (!match) return undefined
  const titleMatch = match[1].match(/^title:\s*(?:"([^"]+)"|'([^']+)'|(.+))\s*$/m)
  const title = titleMatch?.[1] ?? titleMatch?.[2] ?? titleMatch?.[3]
  return title?.trim() || undefined
}

function articleFromPath(value: string): ConceptArticle | null {
  const match = value.match(/^content\/(.+)\.md$/)
  if (!match) return null
  const pathWithoutExtension = match[1]
  return {
    path: pathWithoutExtension,
    title: pathWithoutExtension.split("/").at(-1)?.replace(/_/g, " ") ?? pathWithoutExtension,
  }
}

async function resolveArticleTitles(
  root: string,
  articles: ConceptArticle[] | undefined,
): Promise<ConceptArticle[] | undefined> {
  if (!articles) return articles
  return Promise.all(
    articles.map(async (article) => {
      try {
        const source = await fs.readFile(path.join(root, "content", `${article.path}.md`), "utf8")
        const title = parseFrontmatterTitle(source)
        if (title) return { ...article, title }
      } catch {
        // Keep the fallback title when the note is missing.
      }
      return { ...article, title: capitalizeLeadingText(article.title) }
    }),
  )
}

function capitalizeDefinition(definition?: ConceptDefinition): ConceptDefinition | undefined {
  if (!definition) return definition
  return {
    ...definition,
    title: capitalizeLeadingText(definition.title),
    paragraphs: definition.paragraphs.map(capitalizeLeadingText),
    ...(definition.caution ? { caution: capitalizeLeadingText(definition.caution) } : {}),
  }
}

function parseConceptTable(source: string): Map<number, ConceptTableEntry> {
  const entries = new Map<number, ConceptTableEntry>()
  for (const line of source.split("\n")) {
    const cells = line
      .split("|")
      .slice(1, -1)
      .map((cell) => cell.trim())
    if (cells.length < 3 || !/^\d+$/.test(cells[0])) continue
    const slug = cells[1].match(/^`([^`]+)`$/)?.[1]
    if (slug) entries.set(Number(cells[0]), { slug, title: stripMarkdown(cells[2]) })
  }
  return entries
}

function parseConceptCards(
  cardsSource: string,
  tableEntries: Map<number, ConceptTableEntry>,
): ConceptCard[] {
  const headings = [...cardsSource.matchAll(/^## (\d+)\.\s+(.+)$/gm)]
  const cards: ConceptCard[] = []

  for (let index = 0; index < headings.length; index++) {
    const heading = headings[index]
    const start = (heading.index ?? 0) + heading[0].length
    const end = headings[index + 1]?.index ?? cardsSource.length
    const body = cardsSource.slice(start, end).trim()
    const number = Number(heading[1])
    const title = stripMarkdown(heading[2])
    const tableEntry = tableEntries.get(number)
    if (!tableEntry) continue

    const cautionMatch = body.match(/^\*\*Cuidado de lectura:\*\*\s*(.+)$/m)
    const notesMatch = body.match(/^\*\*Notas de entrada:\*\*\s*(.+)$/m)
    const definitionEnd = Math.min(
      cautionMatch?.index ?? body.length,
      notesMatch?.index ?? body.length,
    )
    const paragraphs = body
      .slice(0, definitionEnd)
      .split(/\n\s*\n/)
      .map(stripMarkdown)
      .filter(Boolean)

    const articles = notesMatch
      ? [...notesMatch[1].matchAll(/`([^`]+)`/g)]
          .map((match) => articleFromPath(match[1]))
          .filter((article): article is ConceptArticle => article !== null)
      : []

    cards.push({
      slug: tableEntry.slug,
      definition: {
        title: capitalizeLeadingText(title),
        paragraphs: paragraphs.map(capitalizeLeadingText),
        ...(cautionMatch ? { caution: capitalizeLeadingText(stripMarkdown(cautionMatch[1])) } : {}),
      },
      articles,
    })
  }

  return cards
}

async function loadConceptCards(root: string): Promise<ConceptCard[]> {
  try {
    const [cardsSource, tableSource] = await Promise.all([
      fs.readFile(path.join(root, "design/shaul-v2/cards-50.md"), "utf8"),
      fs.readFile(path.join(root, "design/shaul-v2/concepts.md"), "utf8"),
    ])
    return parseConceptCards(cardsSource, parseConceptTable(tableSource))
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return []
    throw error
  }
}

function mergeArticles(
  current: ConceptArticle[] | undefined,
  additions: ConceptArticle[],
): ConceptArticle[] | undefined {
  const articles = [...(current ?? []), ...additions]
  if (articles.length === 0) return current
  const map = new Map<string, ConceptArticle>()
  for (const article of articles) {
    if (!map.has(article.path)) map.set(article.path, article)
  }
  return [...map.values()]
}

async function mergeConceptCards(root: string, entities: KnowledgeEntity[]) {
  const cards = await loadConceptCards(root)
  const concepts = new Map(
    entities
      .filter((entity): entity is ConceptEntity => entity.type === "concept")
      .map((entity) => [entity.id, entity]),
  )

  for (const card of cards) {
    const id = cardConceptIds[card.slug] ?? card.slug
    const existing = concepts.get(id)
    if (existing) {
      existing.definition = capitalizeDefinition(card.definition)
      existing.articles = mergeArticles(existing.articles, card.articles)
      continue
    }

    const concept: ConceptEntity = {
      id,
      type: "concept",
      names: { es: card.definition.title },
      definition: capitalizeDefinition(card.definition),
      articles: card.articles,
    }
    entities.push(concept)
    concepts.set(id, concept)
  }

  for (const concept of concepts.values()) {
    concept.definition = capitalizeDefinition(concept.definition)
    concept.articles = await resolveArticleTitles(root, concept.articles)
  }
}

export async function loadKnowledge(root = process.cwd()): Promise<LoadedKnowledge> {
  const knowledgeRoot = path.join(root, "knowledge")
  const entities: KnowledgeEntity[] = []
  const mentions: Mention[] = []
  const relations: Relation[] = []
  const files = new Map<string, string>()
  const issues: KnowledgeIssue[] = []

  for (const collectionName of [...ENTITY_TYPES, "mentions", "relations"]) {
    const directoryName =
      collectionName === "mentions" || collectionName === "relations"
        ? collectionName
        : `${collectionName}s`
    const directory = path.join(knowledgeRoot, directoryName)
    const filePaths = await listYamlFiles(directory)
    for (const filePath of filePaths) {
      const relativePath = path.relative(root, filePath)
      files.set(relativePath, filePath)
      let parsed: unknown
      try {
        parsed = await loadYamlFile(filePath)
      } catch (error) {
        issues.push({ file: relativePath, message: `invalid YAML: ${(error as Error).message}` })
        continue
      }

      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
        issues.push({ file: relativePath, message: "expected a YAML object" })
        continue
      }

      const value = parsed as Record<string, unknown>
      if (collectionName === "mentions") {
        mentions.push(value as unknown as Mention)
      } else if (collectionName === "relations") {
        relations.push(value as unknown as Relation)
      } else {
        const entity = value as unknown as KnowledgeEntity
        if (!isEntityType(entity.type)) {
          issues.push({
            file: relativePath,
            message: `invalid entity type: ${String(entity.type)}`,
          })
        }
        if (entity.type !== collectionName) {
          issues.push({
            file: relativePath,
            message: `entity type ${String(entity.type)} does not match collection ${collectionName}`,
          })
        }
        entities.push(entity)
      }
    }
  }

  await mergeConceptCards(root, entities)

  return { entities, mentions, relations, files, issues }
}

export function expectedEntityDirectory(type: EntityType): string {
  return `${type}s`
}

export function isEntityCollectionName(value: string): value is EntityType {
  return entityDirectories.has(value)
}
