import assert from "node:assert/strict"
import fs from "node:fs/promises"
import path from "node:path"
import { test } from "node:test"

const root = process.cwd()

async function readPackage() {
  return JSON.parse(await fs.readFile(path.join(root, "package.json"), "utf8")) as {
    engines?: { node?: string; npm?: string }
    scripts?: Record<string, string>
  }
}

test("README npm run commands reference existing package scripts", async () => {
  const [readme, packageJson] = await Promise.all([
    fs.readFile(path.join(root, "README.md"), "utf8"),
    readPackage(),
  ])
  const commands = new Set(
    [...readme.matchAll(/npm run ([A-Za-z0-9:_-]+)/g)].map((match) => match[1]),
  )

  for (const command of commands) {
    assert.ok(packageJson.scripts?.[command], `README references missing npm script: ${command}`)
  }
})

test("Docker uses the declared Node major and canonical start script", async () => {
  const [dockerfile, packageJson] = await Promise.all([
    fs.readFile(path.join(root, "Dockerfile"), "utf8"),
    readPackage(),
  ])
  const expectedMajor = packageJson.engines?.node?.match(/^\d+/)?.[0]
  assert.ok(expectedMajor, "package.json must declare a Node major")

  const imageMajors = [...dockerfile.matchAll(/^FROM node:(\d+)(?:[-\s]|$)/gm)].map(
    (match) => match[1],
  )
  assert.ok(imageMajors.length > 0, "Dockerfile must declare at least one Node image")
  assert.deepEqual(
    [...new Set(imageMajors)],
    [expectedMajor],
    `Dockerfile Node majors must match package.json (${expectedMajor})`,
  )
  assert.match(dockerfile, /^CMD \["npm", "start"\]$/m)
  assert.match(
    dockerfile,
    /apt-get install[^\n]*python3/,
    "Docker runtime must install Python for verse-index:build",
  )
})

test("Docker context excludes local dependencies and private state", async () => {
  const dockerignore = await fs.readFile(path.join(root, ".dockerignore"), "utf8")
  const patterns = new Set(
    dockerignore
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter((line) => line && !line.startsWith("#")),
  )

  for (const requiredPattern of [".git/", ".venv/", "node_modules/", "private/", "data/"]) {
    assert.ok(patterns.has(requiredPattern), `.dockerignore must exclude ${requiredPattern}`)
  }
})

test("package-lock records the manifest engines", async () => {
  const [packageJson, packageLock] = await Promise.all([
    readPackage(),
    fs.readFile(path.join(root, "package-lock.json"), "utf8").then(
      (source) =>
        JSON.parse(source) as {
          packages?: { ""?: { engines?: { node?: string; npm?: string } } }
        },
    ),
  ])

  assert.deepEqual(packageLock.packages?.[""]?.engines, packageJson.engines)
})
