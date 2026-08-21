import fs from "node:fs/promises"
import path from "node:path"
import {
  GraphDocument,
  GraphEdge,
  GraphNode,
  canonicalId,
  displayLabel,
  parseEntityRef,
} from "../knowledge/schema"
import { loadKnowledge } from "./lib/knowledge"
import { validateKnowledgeData } from "./validate-knowledge"

export function compileGraph(knowledge: Awaited<ReturnType<typeof loadKnowledge>>): GraphDocument {
  const errors = validateKnowledgeData(knowledge)
  if (errors.length > 0) {
    throw new Error(
      `Cannot compile invalid knowledge:\n${errors.map((error) => `- ${error}`).join("\n")}`,
    )
  }

  const nodes: GraphNode[] = knowledge.entities.map((entity) => {
    const node = {
      ...entity,
      id: canonicalId(entity.type, entity.id),
      type: entity.type,
      label: displayLabel(entity),
    } as GraphNode
    return node
  })

  const edges: GraphEdge[] = knowledge.relations.map((relation) => {
    const source = parseEntityRef(relation.source)!
    const target = parseEntityRef(relation.target)!
    return {
      ...relation,
      id: relation.id,
      source: source.id,
      target: target.id,
      type: relation.type,
      status: relation.status,
    }
  })

  const entityMentions: Record<string, string[]> = {}
  for (const mention of knowledge.mentions) {
    for (const reference of mention.entities) {
      const entityId = parseEntityRef(reference)!.id
      entityMentions[entityId] ??= []
      entityMentions[entityId].push(mention.id)
    }
  }

  return {
    version: 1,
    nodes,
    edges,
    mentions: knowledge.mentions,
    entityMentions,
  }
}

export async function buildGraph(root = process.cwd()) {
  const knowledge = await loadKnowledge(root)
  const graph = compileGraph(knowledge)
  const outputPath = path.join(root, "generated", "graph.json")
  await fs.mkdir(path.dirname(outputPath), { recursive: true })
  await fs.writeFile(outputPath, `${JSON.stringify(graph, null, 2)}\n`, "utf8")
  return { graph, outputPath }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const { graph, outputPath } = await buildGraph()
  console.log(
    `Graph compiled to ${path.relative(process.cwd(), outputPath)}: ${graph.nodes.length} nodes, ${graph.edges.length} edges, ${graph.mentions.length} mentions.`,
  )
}
