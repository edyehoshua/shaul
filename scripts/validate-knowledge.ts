import path from "node:path"
import {
  ENTITY_TYPES,
  canonicalId,
  isRelationStatus,
  isRelationType,
  parseEntityRef,
} from "../knowledge/schema"
import { loadKnowledge } from "./lib/knowledge"

export function validateKnowledgeData(
  knowledge: Awaited<ReturnType<typeof loadKnowledge>>,
): string[] {
  const errors = knowledge.issues.map((issue) => `${issue.file ?? "knowledge"}: ${issue.message}`)
  const entityIds = new Map<string, string>()
  const mentionIds = new Set<string>()
  const relationIds = new Set<string>()

  for (const entity of knowledge.entities) {
    const sourceId = typeof entity.id === "string" ? entity.id : ""
    if (!sourceId || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(sourceId.replace(/^[a-z]+:/, ""))) {
      errors.push(`entity ${String(entity.id)}: id must be kebab-case and non-empty`)
      continue
    }
    const id = canonicalId(entity.type, sourceId)
    const previous = entityIds.get(id)
    if (previous) {
      errors.push(`duplicate entity id ${id} (${previous} and another file)`)
    } else {
      entityIds.set(id, "knowledge")
    }

    if (entity.type === "word") {
      if (!entity.language || !entity.script) {
        errors.push(`${id}: Word entities require language and script`)
      }
    }
    if (entity.type === "verse") {
      if (!Number.isInteger(entity.chapter) || !Number.isInteger(entity.verse)) {
        errors.push(`${id}: Verse entities require integer chapter and verse`)
      }
    }
    if (entity.type === "concept") {
      for (const form of entity.forms ?? []) {
        if (!form || typeof form.word !== "string") {
          errors.push(`${id}: concept form must reference a Word`)
        }
      }
    }
  }

  // A second pass is required because a verse can be declared before its book.
  for (const entity of knowledge.entities) {
    if (entity.type === "verse") {
      assertReference(
        `${canonicalId(entity.type, entity.id)}.book`,
        entity.book,
        "book",
        entityIds,
        errors,
      )
    }
    if (entity.type === "concept") {
      for (const form of entity.forms ?? []) {
        if (typeof form?.word === "string") {
          assertReference(
            `${canonicalId(entity.type, entity.id)}.forms`,
            form.word,
            "word",
            entityIds,
            errors,
          )
        }
      }
      for (const relatedConcept of entity.related_concepts ?? []) {
        assertReference(
          `${canonicalId(entity.type, entity.id)}.related_concepts`,
          relatedConcept,
          "concept",
          entityIds,
          errors,
        )
      }
    }
  }

  for (const mention of knowledge.mentions) {
    if (!mention.id || !mention.note || !mention.text || !Array.isArray(mention.entities)) {
      errors.push(`mention ${String(mention.id)}: requires id, note, text, and entities`)
      continue
    }
    if (mentionIds.has(mention.id)) {
      errors.push(`duplicate mention id ${mention.id}`)
    }
    mentionIds.add(mention.id)
    for (const reference of mention.entities) {
      assertReference(`mention ${mention.id}`, reference, undefined, entityIds, errors)
    }
  }

  for (const relation of knowledge.relations) {
    if (
      !relation.id ||
      typeof relation.source !== "string" ||
      typeof relation.target !== "string"
    ) {
      errors.push(`relation ${String(relation.id)}: requires id, source, and target`)
      continue
    }
    if (relationIds.has(relation.id)) {
      errors.push(`duplicate relation id ${relation.id}`)
    }
    relationIds.add(relation.id)
    if (!isRelationType(relation.type)) {
      errors.push(`relation ${relation.id}: invalid type ${String(relation.type)}`)
    }
    if (!isRelationStatus(relation.status)) {
      errors.push(`relation ${relation.id}: invalid status ${String(relation.status)}`)
    }
    assertReference(`relation ${relation.id}.source`, relation.source, undefined, entityIds, errors)
    assertReference(`relation ${relation.id}.target`, relation.target, undefined, entityIds, errors)
  }

  if (knowledge.entities.length === 0) {
    errors.push("knowledge: no entities found")
  }

  return errors
}

function assertReference(
  context: string,
  value: unknown,
  expectedType: (typeof ENTITY_TYPES)[number] | undefined,
  entityIds: Map<string, string>,
  errors: string[],
) {
  if (typeof value !== "string") {
    errors.push(`${context}: expected a canonical entity reference`)
    return
  }
  const parsed = parseEntityRef(value)
  if (!parsed) {
    errors.push(`${context}: invalid entity reference ${value}`)
    return
  }
  if (expectedType && parsed.type !== expectedType) {
    errors.push(`${context}: expected ${expectedType}, received ${parsed.type}`)
  }
  if (!entityIds.has(parsed.id)) {
    errors.push(`${context}: missing entity ${parsed.id}`)
  }
}

export async function main() {
  const root = path.resolve(process.cwd())
  const knowledge = await loadKnowledge(root)
  const errors = validateKnowledgeData(knowledge)
  if (errors.length > 0) {
    console.error(`Knowledge validation failed with ${errors.length} error(s):`)
    for (const error of errors) console.error(`- ${error}`)
    process.exitCode = 1
    return
  }
  console.log(
    `Knowledge validation passed: ${knowledge.entities.length} entities, ${knowledge.mentions.length} mentions, ${knowledge.relations.length} relations.`,
  )
}

if (import.meta.url === `file://${process.argv[1]}`) {
  await main()
}
