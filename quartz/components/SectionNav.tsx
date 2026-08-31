import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { classNames } from "../util/lang"
import { FullSlug, resolveRelative } from "../util/path"

type NavItem = { label: string; slug: FullSlug }

const defaultNav: NavItem[] = [
  { label: "Inicio", slug: "index" as FullSlug },
  { label: "Tanaj", slug: "tanaj/index" as FullSlug },
  { label: "Besorah", slug: "besorah/index" as FullSlug },
  { label: "Temas", slug: "temas/index" as FullSlug },
  // The graph is the home page; the old standalone /graph HTML is no longer emitted.
  { label: "Grafo", slug: "index" as FullSlug },
  { label: "Tags", slug: "tags/index" as FullSlug },
]

interface Options {
  items?: NavItem[]
}

export default ((userOpts?: Partial<Options>) => {
  const opts: Options = { items: defaultNav, ...userOpts }

  const SectionNav: QuartzComponent = ({ fileData, displayClass }: QuartzComponentProps) => {
    const current = fileData.slug as FullSlug
    return (
      <nav class={classNames(displayClass, "section-nav")} aria-label="Secciones">
        {(opts.items ?? defaultNav).map((item) => (
          <a key={item.slug} href={resolveRelative(current, item.slug)}>
            {item.label}
          </a>
        ))}
      </nav>
    )
  }

  SectionNav.css = `
  .section-nav {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    align-items: center;
    gap: 1rem;
    font-size: 0.9rem;
  }
  .section-nav a {
    color: var(--darkgray);
    text-decoration: none;
    padding: 0.2rem 0;
    border-bottom: 2px solid transparent;
  }
  .section-nav a:hover {
    color: var(--secondary);
    border-bottom-color: var(--secondary);
  }
  @media (max-width: 600px) {
    .section-nav {
      gap: 0.75rem;
    }
  }
  `

  return SectionNav
}) satisfies QuartzComponentConstructor
