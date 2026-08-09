import fs from "node:fs"
import http from "node:http"
import path from "node:path"
import process from "node:process"
import handler from "serve-handler"

const output = path.resolve(process.cwd(), "public")
const portIndex = process.argv.indexOf("--port")
const port = Number(portIndex >= 0 ? process.argv[portIndex + 1] : 8480)

if (!Number.isInteger(port) || port < 1 || port > 65535) {
  console.error("Invalid port. Use --port followed by a number between 1 and 65535.")
  process.exit(1)
}

if (!fs.existsSync(path.join(output, "index.html"))) {
  console.error("No production build found in public/. Run `npm run build` first.")
  process.exit(1)
}

const server = http.createServer(async (request, response) => {
  try {
    await handler(request, response, {
      public: output,
      directoryListing: false,
      headers: [
        {
          source: "**/*.*",
          headers: [{ key: "Content-Disposition", value: "inline" }],
        },
      ],
    })
  } catch (error) {
    console.error(error)
    if (!response.headersSent) response.writeHead(500)
    response.end("Unable to serve the built site.")
  }
})

server.listen(port, () => {
  console.log(`Serving the existing public/ build at http://localhost:${port}`)
  console.log("Run `npm run build` when you want to regenerate the site.")
})
