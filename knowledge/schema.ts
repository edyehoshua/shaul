export const ENTITY_TYPES = ["concept", "word", "verse", "person", "book"] as const
export type EntityType = (typeof ENTITY_TYPES)[number]

export const RELATION_TYPES = [
  "contains",
  "expresses",
  "mentions",
  "related_to",
  "associated_with",
  "alludes_to",
] as const
export type RelationType = (typeof RELATION_TYPES)[number]

export const RELATION_STATUSES = ["proposed", "confirmed"] as const
export type RelationStatus = (typeof RELATION_STATUSES)[number]

export type CanonicalId = `${EntityType}:${string}`

export interface BaseEntity {
  id: string
  type: EntityType
  names?: Record<string, string>
  aliases?: string[]
  description?: string
}

export interface ConceptForm {
  word: string
  role: string
}

export interface ConceptSummary {
  what_it_is?: string
  what_it_is_not?: string
}

export interface ConceptArticle {
  path: string
  title: string
}

export interface ConceptEntity extends BaseEntity {
  type: "concept"
  forms?: ConceptForm[]
  summary?: ConceptSummary
  articles?: ConceptArticle[]
  related_concepts?: string[]
}

export interface WordEntity extends BaseEntity {
  type: "word"
  language: string
  script: string
  transliteration?: string
}

export interface VerseEntity extends BaseEntity {
  type: "verse"
  book: string
  chapter: number
  verse: number
  text?: string
}

export interface PersonEntity extends BaseEntity {
  type: "person"
}

export interface BookEntity extends BaseEntity {
  type: "book"
}

export type KnowledgeEntity = ConceptEntity | WordEntity | VerseEntity | PersonEntity | BookEntity

export interface MentionLocation {
  heading?: string
  anchor?: string
}

export interface Mention {
  id: string
  note: string
  entities: string[]
  location?: MentionLocation
  text: string
}

export interface Relation {
  id: string
  source: string
  target: string
  type: RelationType
  status: RelationStatus
}

export interface KnowledgeCollections {
  entities: KnowledgeEntity[]
  mentions: Mention[]
  relations: Relation[]
}

export interface GraphNode extends Record<string, unknown> {
  id: CanonicalId
  type: EntityType
  label: string
}

export interface GraphEdge extends Record<string, unknown> {
  id: string
  source: CanonicalId
  target: CanonicalId
  type: RelationType
  status: RelationStatus
}

export interface GraphDocument {
  version: 1
  nodes: GraphNode[]
  edges: GraphEdge[]
  mentions: Mention[]
  entityMentions: Record<string, string[]>
}

export function isEntityType(value: unknown): value is EntityType {
  return typeof value === "string" && ENTITY_TYPES.includes(value as EntityType)
}

export function isRelationType(value: unknown): value is RelationType {
  return typeof value === "string" && RELATION_TYPES.includes(value as RelationType)
}

export function isRelationStatus(value: unknown): value is RelationStatus {
  return typeof value === "string" && RELATION_STATUSES.includes(value as RelationStatus)
}

export function canonicalId(type: EntityType, id: string): CanonicalId {
  const prefix = `${type}:`
  return (id.startsWith(prefix) ? id : `${prefix}${id}`) as CanonicalId
}

export function parseEntityRef(value: string): { type: EntityType; id: CanonicalId } | null {
  const separator = value.indexOf(":")
  if (separator <= 0) return null
  const type = value.slice(0, separator)
  const id = value.slice(separator + 1)
  if (!isEntityType(type) || !id) return null
  return { type, id: canonicalId(type, id) }
}

export function displayLabel(entity: KnowledgeEntity): string {
  if (entity.type === "word") {
    return entity.script || entity.transliteration || entity.names?.es || entity.id
  }
  if (entity.type === "verse") {
    const book = entity.book.replace(/^book:/, "")
    return `${book} ${entity.chapter}:${entity.verse}`
  }
  return entity.names?.es ?? entity.names?.en ?? entity.id
}
