import {
  SimulationLinkDatum,
  SimulationNodeDatum,
  forceCenter,
  forceCollide,
  forceLink,
  forceManyBody,
  forceRadial,
  forceSimulation,
  select,
  zoom,
  zoomIdentity,
  drag,
} from "d3"
import { Application, Circle, Container, Graphics, Text } from "pixi.js"
import { Group as TweenGroup, Tween as Tweened } from "@tweenjs/tween.js"

type EntityType = "concept" | "word" | "verse" | "person" | "book"

interface GraphNode {
  id: string
  type: EntityType
  label: string
  names?: Record<string, string>
  aliases?: string[]
  forms?: { word: string; role: string }[]
  summary?: { what_it_is?: string; what_it_is_not?: string }
  articles?: { path: string; title: string }[]
  related_concepts?: string[]
  language?: string
  script?: string
  transliteration?: string
  book?: string
  chapter?: number
  verse?: number
  text?: string
  description?: string
}

interface GraphEdge {
  id: string
  source: string
  target: string
  type: string
  status: string
}

interface Mention {
  id: string
  note: string
  entities: string[]
  location?: { heading?: string; anchor?: string }
  text: string
}

interface GraphDocument {
  nodes: GraphNode[]
  edges: GraphEdge[]
  mentions: Mention[]
  entityMentions: Record<string, string[]>
}

type RenderNode = GraphNode & SimulationNodeDatum
type RenderLink = Omit<GraphEdge, "source" | "target"> &
  SimulationLinkDatum<RenderNode> & {
    source: RenderNode
    target: RenderNode
  }

type NodeRenderData = {
  simulationData: RenderNode
  gfx: Graphics
  label: Text
  active: boolean
}

type LinkRenderData = {
  simulationData: RenderLink
  gfx: Graphics
  active: boolean
  alpha: number
  color: number
}

const colors: Record<EntityType, number> = {
  concept: 0x202327,
  word: 0xc87078,
  verse: 0x8fa6b4,
  person: 0xb2a2b5,
  book: 0xd1b36d,
}

const graphContainer = document.getElementById("shaul-graph")
if (graphContainer) {
  const detailsPanel = document.getElementById("shaul-graph-details")
  const details = document.getElementById("shaul-graph-details-content")
  const resetButton = document.querySelector<HTMLButtonElement>("[data-graph-reset]")
  const closeDetailsButton = document.querySelector<HTMLButtonElement>("[data-graph-details-close]")
  const graphFilters = [...document.querySelectorAll<HTMLButtonElement>("[data-graph-filter]")]

  let graphData: GraphDocument
  let selectedId: string | null = null
  let hoveredNodeId: string | null = null
  let activeFilter: EntityType | "all" = "concept"
  let currentTransform = zoomIdentity
  let simulation: ReturnType<typeof forceSimulation<RenderNode>>
  let renderPixiFromD3: () => void = () => {}
  let selectNode: (nodeId: string) => void = () => {}

  const nodeById = (id: string) => graphData.nodes.find((node) => node.id === id)

  const addText = (parent: HTMLElement, tag: string, value: unknown, className?: string) => {
    const element = document.createElement(tag)
    if (className) element.className = className
    element.textContent = String(value ?? "")
    parent.append(element)
    return element
  }

  const renderDetails = (nodeId: string) => {
    if (!details) return
    const node = nodeById(nodeId)
    if (!node) return

    details.replaceChildren()
    addText(details, "h2", node.label)

    if (node.type === "word") {
      const lexical = document.createElement("dl")
      addText(lexical, "dt", "Language")
      addText(lexical, "dd", node.language)
      addText(lexical, "dt", "Script")
      addText(lexical, "dd", node.script)
      if (node.transliteration) {
        addText(lexical, "dt", "Transliteration")
        addText(lexical, "dd", node.transliteration)
      }
      details.append(lexical)
    }

    if (node.type === "concept" && node.summary?.what_it_is) {
      addText(details, "h3", "Qué es")
      addText(details, "p", node.summary.what_it_is, "graph-details-summary")
    }

    if (node.type === "concept" && node.summary?.what_it_is_not) {
      addText(details, "h3", "Qué no es")
      addText(details, "p", node.summary.what_it_is_not, "graph-details-summary graph-details-not")
    }

    if (node.type === "concept" && node.related_concepts?.length) {
      addText(details, "h3", "Conceptos relacionados")
      const list = document.createElement("ul")
      for (const relatedId of node.related_concepts) {
        const related = nodeById(relatedId)
        if (!related) continue
        const item = document.createElement("li")
        const button = document.createElement("button")
        button.type = "button"
        button.className = "shaul-related-node"
        button.textContent = related.label
        button.addEventListener("click", () => selectNode(related.id))
        item.append(button)
        list.append(item)
      }
      details.append(list)
    }

    if (node.type === "concept" && node.forms?.length) {
      addText(details, "h3", "Formas lingüísticas")
      const list = document.createElement("ul")
      for (const form of node.forms) {
        const word = nodeById(form.word)
        const item = document.createElement("li")
        addText(item, "strong", word?.script ?? form.word)
        const language =
          word?.language === "aramaic"
            ? "Arameo"
            : word?.language === "hebrew"
              ? "Hebreo"
              : form.role
        addText(
          item,
          "span",
          ` · ${word?.transliteration ?? word?.label ?? form.role} · ${language}`,
        )
        list.append(item)
      }
      details.append(list)
    }

    if (node.type === "concept" && node.articles?.length) {
      addText(details, "h3", "Notas relacionadas")
      const list = document.createElement("ul")
      for (const article of node.articles) {
        const item = document.createElement("li")
        const link = document.createElement("a")
        link.href = `./${article.path}.html`
        link.textContent = article.title
        item.append(link)
        list.append(item)
      }
      details.append(list)
    }
  }

  const render = async () => {
    try {
      const response = await fetch("generated/graph.json")
      if (!response.ok) throw new Error(`Graph request failed (${response.status})`)
      graphData = (await response.json()) as GraphDocument

      const width = graphContainer?.offsetWidth ?? 0
      const height = Math.max(graphContainer?.offsetHeight ?? 0, 250)
      const degree = new Map(graphData.nodes.map((node) => [node.id, 0]))
      graphData.edges.forEach((edge) => {
        degree.set(edge.source, (degree.get(edge.source) ?? 0) + 1)
        degree.set(edge.target, (degree.get(edge.target) ?? 0) + 1)
      })

      const nodes: RenderNode[] = graphData.nodes.map((node, index) => {
        const angle = index * Math.PI * (3 - Math.sqrt(5))
        const radius = 60 + Math.sqrt(index / graphData.nodes.length) * 300
        return {
          ...node,
          x: Math.cos(angle) * radius,
          y: Math.sin(angle) * radius,
        }
      })
      const nodeMap = new Map(nodes.map((node) => [node.id, node]))
      const links: RenderLink[] = graphData.edges
        .filter((edge) => nodeMap.has(edge.source) && nodeMap.has(edge.target))
        .map((edge) => ({
          ...edge,
          source: nodeMap.get(edge.source)!,
          target: nodeMap.get(edge.target)!,
        }))

      simulation = forceSimulation<RenderNode>(nodes)
        .force("charge", forceManyBody<RenderNode>().strength(-115))
        .force("center", forceCenter<RenderNode>(0, 0).strength(0.22))
        .force("link", forceLink<RenderNode, RenderLink>(links).distance(110).strength(0.62))
        .force("radial", forceRadial(Math.max(230, Math.min(width, height) * 0.31)).strength(0.1))
        .force(
          "collide",
          forceCollide<RenderNode>((node) => 3 + Math.sqrt(degree.get(node.id) ?? 0)).iterations(3),
        )
        .alphaDecay(0.025)
        .velocityDecay(0.42)

      const renderer = await createPixiRenderer({
        width,
        height,
        nodes,
        links,
        degree,
      })

      renderPixiFromD3 = renderer.renderPixiFromD3
      selectNode = (nodeId: string) => {
        selectedId = nodeId
        renderDetails(nodeId)
        if (detailsPanel) detailsPanel.dataset.open = "true"
        renderPixiFromD3()
      }

      renderer.bindInteractions()
      simulation.on("tick", () => {
        renderer.syncPositions()
        renderer.renderFrame()
      })

      const closeDetails = () => {
        selectedId = null
        if (detailsPanel) detailsPanel.dataset.open = "false"
        renderPixiFromD3()
      }

      closeDetailsButton?.addEventListener("click", closeDetails)
      resetButton?.addEventListener("click", () => {
        activeFilter = "concept"
        graphFilters.forEach((candidate) => {
          candidate.setAttribute(
            "aria-pressed",
            String(candidate.dataset.graphFilter === "concept"),
          )
        })
        selectedId = null
        if (detailsPanel) detailsPanel.dataset.open = "false"
        renderer.resetView()
        simulation.alpha(0.8).restart()
        renderPixiFromD3()
      })
      graphFilters.forEach((button) => {
        button.addEventListener("click", () => {
          activeFilter = (button.dataset.graphFilter ?? "concept") as EntityType
          graphFilters.forEach((candidate) => {
            candidate.setAttribute("aria-pressed", String(candidate === button))
          })
          renderPixiFromD3()
        })
      })

      document.querySelector(".shaul-graph-loading")?.remove()
      renderer.start()
      if (graphData.nodes.some((node) => node.id === "concept:son-of-man")) {
        selectNode("concept:son-of-man")
      }
    } catch (error) {
      console.error(error)
      document
        .querySelector(".shaul-graph-loading")
        ?.replaceChildren(document.createTextNode("The graph could not be loaded."))
    }
  }

  async function createPixiRenderer({
    width,
    height,
    nodes,
    links,
    degree,
  }: {
    width: number
    height: number
    nodes: RenderNode[]
    links: RenderLink[]
    degree: Map<string, number>
  }) {
    const css = getComputedStyle(document.documentElement)
    const ink = css.getPropertyValue("--shaul-ink").trim() || "#202327"
    const tweenMap = new Map<string, { update: (time: number) => void; stop: () => void }>()
    const nodeRenderData: NodeRenderData[] = []
    const linkRenderData: LinkRenderData[] = []
    let dragging = false
    let stopAnimation = false

    const app = new Application()
    await app.init({
      width,
      height,
      antialias: true,
      autoStart: false,
      autoDensity: true,
      backgroundAlpha: 0,
      preference: "webgpu",
      resolution: window.devicePixelRatio,
      eventMode: "static",
    })
    graphContainer!.appendChild(app.canvas)

    const stage = app.stage
    const linksContainer = new Container<Graphics>({ zIndex: 1, isRenderGroup: true })
    const nodesContainer = new Container<Graphics>({ zIndex: 2, isRenderGroup: true })
    const labelsContainer = new Container<Text>({ zIndex: 3, isRenderGroup: true })
    stage.addChild(linksContainer, nodesContainer, labelsContainer)

    const nodeRadius = (node: RenderNode) =>
      (node.type === "concept" ? 5 : 3) + Math.sqrt(degree.get(node.id) ?? 0)

    for (const node of nodes) {
      const radius = nodeRadius(node)
      const label = new Text({
        interactive: false,
        eventMode: "none",
        text: node.label,
        alpha: 0,
        anchor: { x: 0.5, y: 1.25 },
        style: {
          fontSize: 11,
          fill: ink,
          fontFamily: "Helvetica Neue, Helvetica, Arial, sans-serif",
        },
        resolution: window.devicePixelRatio * 3,
      })

      const gfx = new Graphics({
        interactive: true,
        eventMode: "static",
        label: node.id,
        hitArea: new Circle(0, 0, radius + 6),
        cursor: "pointer",
      })
        .circle(0, 0, radius)
        .fill({ color: colors[node.type] })
        .on("pointerover", (event) => {
          hoveredNodeId = event.target.label as string
          updateHoverInfo()
          renderPixiFromD3()
        })
        .on("pointerleave", () => {
          hoveredNodeId = null
          updateHoverInfo()
          if (!dragging) renderPixiFromD3()
        })
        .on("pointertap", () => selectNode(node.id))

      nodesContainer.addChild(gfx)
      labelsContainer.addChild(label)
      nodeRenderData.push({ simulationData: node, gfx, label, active: false })
    }

    for (const link of links) {
      const gfx = new Graphics({ interactive: false, eventMode: "none" })
      linksContainer.addChild(gfx)
      linkRenderData.push({
        simulationData: link,
        gfx,
        active: false,
        alpha: 1,
        color: 0xdfe3e3,
      })
    }

    function updateHoverInfo() {
      for (const node of nodeRenderData) {
        node.active = Boolean(
          hoveredNodeId &&
          links.some(
            (link) =>
              (link.source.id === hoveredNodeId && link.target.id === node.simulationData.id) ||
              (link.target.id === hoveredNodeId && link.source.id === node.simulationData.id),
          ),
        )
      }
      for (const link of linkRenderData) {
        link.active = Boolean(
          hoveredNodeId &&
          (link.simulationData.source.id === hoveredNodeId ||
            link.simulationData.target.id === hoveredNodeId),
        )
      }
    }

    function renderNodes() {
      tweenMap.get("nodes")?.stop()
      const tweenGroup = new TweenGroup()
      for (const node of nodeRenderData) {
        const filtered = activeFilter !== "all" && node.simulationData.type !== activeFilter
        const focused =
          hoveredNodeId === null || node.active || node.simulationData.id === hoveredNodeId
        const alpha = filtered ? 0.08 : hoveredNodeId && !focused ? 0.18 : 1
        tweenGroup.add(new Tweened<Graphics>(node.gfx).to({ alpha }, 180))
      }
      tweenGroup.getAll().forEach((tween) => tween.start())
      tweenMap.set("nodes", {
        update: tweenGroup.update.bind(tweenGroup),
        stop: () => tweenGroup.getAll().forEach((tween) => tween.stop()),
      })
    }

    function renderLinks() {
      tweenMap.get("links")?.stop()
      const tweenGroup = new TweenGroup()
      for (const link of linkRenderData) {
        const isConceptRelation =
          link.simulationData.type === "related_to" &&
          link.simulationData.source.type === "concept" &&
          link.simulationData.target.type === "concept"
        const filtered =
          activeFilter !== "all" &&
          link.simulationData.source.type !== activeFilter &&
          link.simulationData.target.type !== activeFilter
        const alpha = filtered
          ? 0.04
          : hoveredNodeId
            ? link.active
              ? 1
              : 0.16
            : isConceptRelation
              ? 0.9
              : 0.7
        link.color = link.active ? 0x8a8f92 : isConceptRelation ? 0xc87078 : 0xdfe3e3
        tweenGroup.add(new Tweened<LinkRenderData>(link).to({ alpha }, 180))
      }
      tweenGroup.getAll().forEach((tween) => tween.start())
      tweenMap.set("links", {
        update: tweenGroup.update.bind(tweenGroup),
        stop: () => tweenGroup.getAll().forEach((tween) => tween.stop()),
      })
    }

    function renderLabels() {
      tweenMap.get("labels")?.stop()
      const tweenGroup = new TweenGroup()
      const zoomOpacity = Math.max((currentTransform.k - 1) / 3.75, 0)
      for (const node of nodeRenderData) {
        const active =
          node.active ||
          node.simulationData.id === hoveredNodeId ||
          node.simulationData.id === selectedId
        const filtered = activeFilter !== "all" && node.simulationData.type !== activeFilter
        const conceptVisible = activeFilter === "concept" && node.simulationData.type === "concept"
        const alpha = filtered ? 0 : active ? 1 : conceptVisible ? 0.72 : zoomOpacity
        node.label.scale.set(1 / currentTransform.k)
        tweenGroup.add(new Tweened<Text>(node.label).to({ alpha }, 120))
      }
      tweenGroup.getAll().forEach((tween) => tween.start())
      tweenMap.set("labels", {
        update: tweenGroup.update.bind(tweenGroup),
        stop: () => tweenGroup.getAll().forEach((tween) => tween.stop()),
      })
    }

    renderPixiFromD3 = () => {
      renderNodes()
      renderLinks()
      renderLabels()
    }

    function syncPositions() {
      for (const node of nodeRenderData) {
        const { x = 0, y = 0 } = node.simulationData
        node.gfx.position.set(x + width / 2, y + height / 2)
        node.label.position.set(x + width / 2, y + height / 2)
      }
      for (const link of linkRenderData) {
        const source = link.simulationData.source
        const target = link.simulationData.target
        link.gfx.clear()
        link.gfx
          .moveTo((source.x ?? 0) + width / 2, (source.y ?? 0) + height / 2)
          .lineTo((target.x ?? 0) + width / 2, (target.y ?? 0) + height / 2)
          .stroke({ alpha: link.alpha, width: 1, color: link.color })
      }
    }

    function renderFrame(time = 0) {
      tweenMap.forEach((tween) => tween.update(time))
      app.renderer.render(stage)
    }

    function bindInteractions() {
      select<HTMLCanvasElement, RenderNode | undefined>(app.canvas).call(
        drag<HTMLCanvasElement, RenderNode | undefined>()
          .container(() => app.canvas)
          .subject(() => nodes.find((node) => node.id === hoveredNodeId))
          .on("start", (event) => {
            if (!event.active) simulation.alphaTarget(0.25).restart()
            event.subject.fx = event.subject.x
            event.subject.fy = event.subject.y
            event.subject.__dragStartedAt = Date.now()
            dragging = true
          })
          .on("drag", (event) => {
            event.subject.fx = event.x - width / 2
            event.subject.fy = event.y - height / 2
          })
          .on("end", (event) => {
            if (!event.active) simulation.alphaTarget(0)
            event.subject.fx = null
            event.subject.fy = null
            dragging = false
            if (Date.now() - (event.subject.__dragStartedAt ?? 0) < 350)
              selectNode(event.subject.id)
          }),
      )

      select<HTMLCanvasElement, RenderNode>(app.canvas).call(
        zoom<HTMLCanvasElement, RenderNode>()
          .extent([
            [0, 0],
            [width, height],
          ])
          .scaleExtent([0.35, 4])
          .on("zoom", ({ transform }) => {
            currentTransform = transform
            stage.scale.set(transform.k, transform.k)
            stage.position.set(transform.x, transform.y)
            renderLabels()
          }),
      )
    }

    function resetView() {
      currentTransform = zoomIdentity
      stage.scale.set(1, 1)
      stage.position.set(0, 0)
    }

    function start() {
      const animate = (time: number) => {
        if (stopAnimation) return
        syncPositions()
        tweenMap.forEach((tween) => tween.update(time))
        app.renderer.render(stage)
        requestAnimationFrame(animate)
      }
      renderPixiFromD3()
      requestAnimationFrame(animate)
    }

    return {
      bindInteractions,
      renderFrame,
      renderPixiFromD3,
      resetView,
      start,
      syncPositions,
    }
  }

  void render()
}
