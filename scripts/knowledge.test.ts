import assert from "node:assert/strict"
import fs from "node:fs/promises"
import path from "node:path"
import { test } from "node:test"
import { compileGraph } from "./build-graph"
import { loadKnowledge } from "./lib/knowledge"
import { validateKnowledgeData } from "./validate-knowledge"

test("pilot knowledge compiles into one typed graph", async () => {
  const knowledge = await loadKnowledge()
  const graph = compileGraph(knowledge)

  const concepts = graph.nodes.filter((node) => node.type === "concept")
  assert.equal(concepts.length, 69)
  assert.equal(concepts.filter((node) => Array.isArray(node.definition?.paragraphs)).length, 64)
  assert.ok(graph.nodes.some((node) => node.id === "word:bar-enash-ar"))
  assert.ok(graph.nodes.some((node) => node.id === "concept:son-of-man"))
  assert.ok(graph.nodes.some((node) => node.id === "concept:torah"))
  assert.ok(graph.nodes.some((node) => node.id === "concept:ruach"))
  assert.ok(graph.edges.some((edge) => edge.source === "word:bar-enash-ar"))
  assert.ok(graph.entityMentions["concept:son-of-man"]?.length >= 2)

  const sonOfMan = concepts.find((node) => node.id === "concept:son-of-man")
  const definitionText = [
    ...(sonOfMan?.definition?.paragraphs ?? []),
    sonOfMan?.definition?.caution ?? "",
  ].join(" ")
  assert.doesNotMatch(definitionText, /la clase|Eric |Natanael/i)
  assert.ok(
    (sonOfMan?.articles ?? []).every((article: { title: string }) =>
      /^\p{Lu}/u.test(article.title),
    ),
  )

  const articlePaths = new Set(
    concepts.flatMap((concept) => concept.articles?.map((article) => article.path) ?? []),
  )
  for (const articlePath of articlePaths) {
    await assert.doesNotReject(
      fs.access(path.join(process.cwd(), "content", `${articlePath}.md`)),
      `missing concept article: ${articlePath}`,
    )
  }
})

test("knowledge validation rejects an unknown related concept", async () => {
  const knowledge = await loadKnowledge()
  const concept = knowledge.entities.find((entity) => entity.type === "concept")
  assert.ok(concept)
  concept.related_concepts = ["concept:not-in-the-graph"]

  assert.ok(
    validateKnowledgeData(knowledge).some((error) =>
      error.includes("missing entity concept:not-in-the-graph"),
    ),
  )
})
