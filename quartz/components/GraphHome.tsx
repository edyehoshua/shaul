import { JSX } from "preact"

const filters: Array<{ type: string; label: string }> = [{ type: "concept", label: "Concepts" }]

export default function GraphHome(): JSX.Element {
  return (
    <div class="shaul-home">
      <header class="shaul-header">
        <button
          class="shaul-corner-control shaul-reset"
          type="button"
          data-graph-reset
          aria-label="Reset graph"
        >
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
        </button>

        <a class="shaul-brand" href="./" aria-label="Shaul home">
          SHAUL
        </a>

        <a class="shaul-legacy-link" href="./tags/besorah.html">
          Legacy site <span aria-hidden="true">↗</span>
        </a>

        <nav class="shaul-nav" aria-label="Graph filters">
          {filters.map((filter) => (
            <button
              type="button"
              data-graph-filter={filter.type}
              aria-pressed={filter.type === "concept"}
            >
              {filter.label}
            </button>
          ))}
        </nav>
      </header>

      <main class="shaul-main">
        <section class="shaul-graph-panel" aria-label="Interactive knowledge graph">
          <div id="shaul-graph" class="shaul-graph-canvas">
            <div class="shaul-graph-loading">Loading graph…</div>
          </div>
          <div class="shaul-graph-meta" aria-hidden="true">
            <span>Drag · zoom · select</span>
            <span>יהוה</span>
          </div>
        </section>

        <aside id="shaul-graph-details" class="shaul-details" data-open="false" aria-live="polite">
          <button
            class="shaul-details-close"
            type="button"
            data-graph-details-close
            aria-label="Close details"
          >
            ×
          </button>
          <div id="shaul-graph-details-content" class="shaul-details-content">
            <div class="shaul-details-empty">
              <span>Select a node</span>
            </div>
          </div>
        </aside>
      </main>
    </div>
  )
}
