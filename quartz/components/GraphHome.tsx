import { JSX } from "preact"

const filters: Array<{ type: string; label: string }> = [{ type: "concept", label: "Conceptos" }]

export default function GraphHome(): JSX.Element {
  return (
    <div class="shaul-home">
      <header class="shaul-header">
        <button
          class="shaul-corner-control shaul-reset"
          type="button"
          data-graph-reset
          aria-label="Reiniciar grafo"
        >
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
        </button>

        <a class="shaul-brand" href="./" aria-label="Inicio">
          SHAUL
        </a>

        <nav class="shaul-nav" aria-label="Filtros del grafo">
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
        <section class="shaul-graph-panel" aria-label="Grafo de conceptos interactivo">
          <div id="shaul-graph" class="shaul-graph-canvas">
            <div class="shaul-graph-loading">Cargando grafo…</div>
          </div>
          <div class="shaul-graph-meta" aria-hidden="true">
            <span>Arrastrar · zoom · seleccionar</span>
            <span>יהוה</span>
          </div>
        </section>

        <aside id="shaul-graph-details" class="shaul-details" data-open="false" aria-live="polite">
          <button
            class="shaul-details-close"
            type="button"
            data-graph-details-close
            aria-label="Cerrar detalles"
          >
            ×
          </button>
          <div id="shaul-graph-details-content" class="shaul-details-content">
            <div class="shaul-details-empty">
              <span>Selecciona un nodo</span>
            </div>
          </div>
        </aside>
      </main>
    </div>
  )
}
