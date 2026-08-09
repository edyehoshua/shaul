import fs from "node:fs/promises"
import path from "node:path"
import yaml from "js-yaml"
import {
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

  return { entities, mentions, relations, files, issues }
}

export function expectedEntityDirectory(type: EntityType): string {
  return `${type}s`
}

export function isEntityCollectionName(value: string): value is EntityType {
  return entityDirectories.has(value)
}
