#!/bin/sh
# Vercel ignored-build-step: exit 0 = skip this deployment, exit 1 = build.
# Production / main always builds. Draft PRs skip. Historical heavy branches skip.
# Fail-open (build) if GitHub is unreachable so a blip cannot block a ready preview.
set -eu

REF="${VERCEL_GIT_COMMIT_REF:-}"
ENV="${VERCEL_ENV:-}"

if [ "$ENV" = "production" ] || [ "$REF" = "main" ]; then
  exit 1
fi

case "$REF" in
  feat/eric_youtube|feat/somoselcuerpodelmesias)
    echo "skipping historical worker branch $REF"
    exit 0
    ;;
esac

if [ -n "$REF" ]; then
  encoded=$(VERCEL_GIT_COMMIT_REF="$REF" python3 -c 'import os, urllib.parse; print(urllib.parse.quote(os.environ["VERCEL_GIT_COMMIT_REF"], safe=""))')
  json=$(curl -fsS "https://api.github.com/repos/edyehoshua/shaul/pulls?head=edyehoshua:${encoded}&state=open" || true)
  draft=$(printf '%s' "$json" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
    print("true" if data and data[0].get("draft") else "false")
except Exception:
    print("unknown")
' 2>/dev/null || echo unknown)
  if [ "$draft" = "true" ]; then
    echo "skipping draft PR preview for $REF"
    exit 0
  fi
fi

exit 1
