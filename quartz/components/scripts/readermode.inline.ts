const STORAGE_KEY = "shaul-reader-mode"
const LONG_NOTE_THRESHOLD_WORDS = 2500

const emitReaderModeChangeEvent = (mode: "on" | "off") => {
  const event: CustomEventMap["readermodechange"] = new CustomEvent("readermodechange", {
    detail: { mode },
  })
  document.dispatchEvent(event)
}

function storedPreference(): "on" | "off" | null {
  try {
    const value = window.localStorage.getItem(STORAGE_KEY)
    return value === "on" || value === "off" ? value : null
  } catch {
    return null
  }
}

function savePreference(value: "on" | "off"): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, value)
  } catch {
    // Reader mode still works for the current SPA session when storage is unavailable.
  }
}

function isLongNote(): boolean {
  const article = document.querySelector("article")
  if (!article) return false
  const words = (article.textContent ?? "").trim().split(/\s+/).filter(Boolean).length
  return words >= LONG_NOTE_THRESHOLD_WORDS
}

// Start from the first page's length; an explicit preference persists across SPA navigation.
let isReaderMode = false
let hasExplicitPreference = false

document.addEventListener("nav", () => {
  const apply = () => {
    document.documentElement.setAttribute("reader-mode", isReaderMode ? "on" : "off")
  }

  const switchReaderMode = () => {
    isReaderMode = !isReaderMode
    const newMode = isReaderMode ? "on" : "off"
    hasExplicitPreference = true
    savePreference(newMode)
    emitReaderModeChangeEvent(newMode)
    apply()
  }

  for (const readerModeButton of document.getElementsByClassName("readermode")) {
    readerModeButton.addEventListener("click", switchReaderMode)
    window.addCleanup(() => readerModeButton.removeEventListener("click", switchReaderMode))
  }

  // No explicit preference yet: let each page default by its own length.
  const preference = storedPreference()
  if (preference !== null) {
    hasExplicitPreference = true
    isReaderMode = preference === "on"
  } else if (!hasExplicitPreference) {
    isReaderMode = isLongNote()
  }
  apply()
})
