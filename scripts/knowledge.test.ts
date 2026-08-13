import assert from "node:assert/strict"
import { test } from "node:test"
import { compileGraph } from "./build-graph"
import { loadKnowledge } from "./lib/knowledge"

test("pilot knowledge compiles into one typed graph", async () => {
  const knowledge = await loadKnowledge()
  const graph = compileGraph(knowledge)

  const concepts = graph.nodes.filter((node) => node.type === "concept")
  assert.equal(concepts.length, 64)
  assert.equal(concepts.filter((node) => Array.isArray(node.definition?.paragraphs)).length, 64)
  assert.ok(graph.nodes.some((node) => node.id === "word:bar-enash-ar"))
  assert.ok(graph.nodes.some((node) => node.id === "concept:son-of-man"))
  assert.ok(graph.nodes.some((node) => node.id === "concept:torah"))
  assert.ok(graph.nodes.some((node) => node.id === "concept:ruach"))
  assert.ok(graph.edges.some((edge) => edge.source === "word:bar-enash-ar"))
  assert.ok(graph.entityMentions["concept:son-of-man"]?.length >= 2)
})
