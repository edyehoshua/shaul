import { readdir, readFile } from "node:fs/promises"
import path from "node:path"

const contentRoot = path.resolve("content")

async function walk(dir) {
  const entries = await readdir(dir, { withFileTypes: true })
  const files = await Promise.all(
    entries.map(async (entry) => {
      const fullPath = path.join(dir, entry.name)
      if (entry.isDirectory()) {
        return walk(fullPath)
      }

      if (entry.isFile() && entry.name.endsWith(".md")) {
        return [fullPath]
      }

      return []
    }),
  )

  return files.flat()
}

function findFrontmatterTabIssues(text) {
  const lines = text.split(/\r?\n/)
  if (lines[0] !== "---") {
    return []
  }

  const issues = []
  for (let i = 1; i < lines.length; i += 1) {
    const line = lines[i]
    if (line === "---" || line === "...") {
      break
    }

    if (line.includes("\t")) {
      issues.push({
        lineNumber: i + 1,
        line,
      })
    }
  }

  return issues
}

function formatLine(line) {
  return line.replace(/\t/g, "\\t")
}

async function main() {
  const markdownFiles = await walk(contentRoot)
  const issues = []

  for (const filePath of markdownFiles) {
    const text = await readFile(filePath, "utf8")
    const fileIssues = findFrontmatterTabIssues(text)
    for (const issue of fileIssues) {
      issues.push({ filePath, ...issue })
    }
  }

  if (issues.length === 0) {
    console.log("Frontmatter tab check passed.")
    return
  }

  console.error("Found tab characters in YAML frontmatter. Use spaces for indentation.")
  for (const issue of issues) {
    const relativePath = path.relative(process.cwd(), issue.filePath)
    console.error(`- ${relativePath}:${issue.lineNumber} -> ${formatLine(issue.line)}`)
  }

  process.exitCode = 1
}

main().catch((error) => {
  console.error(error)
  process.exitCode = 1
})
