import assert from "node:assert/strict"
import { test } from "node:test"
import { compileGraph } from "./build-graph"
import { loadKnowledge } from "./lib/knowledge"

test("pilot knowledge compiles into one typed graph", async () => {
  const knowledge = await loadKnowledge()
  const graph = compileGraph(knowledge)

  assert.equal(graph.nodes.filter((node) => node.type === "concept").length, 25)
  assert.ok(graph.nodes.some((node) => node.id === "word:bar-enash-ar"))
  assert.ok(graph.nodes.some((node) => node.id === "concept:son-of-man"))
  assert.ok(graph.edges.some((edge) => edge.source === "word:bar-enash-ar"))
  assert.ok(graph.entityMentions["concept:son-of-man"]?.length >= 2)
})
