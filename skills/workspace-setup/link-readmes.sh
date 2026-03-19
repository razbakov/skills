#!/bin/bash
# Create CLAUDE.md and AGENTS.md as symlinks to README.md
# Scans root and 1st-level folders

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

link_readme() {
  local dir="$1"
  local readme="$dir/README.md"

  if [ -f "$readme" ]; then
    for target in CLAUDE.md AGENTS.md; do
      local dest="$dir/$target"
      if [ ! -e "$dest" ]; then
        ln -s README.md "$dest"
        echo "Linked $dest -> README.md"
      else
        echo "Skipped $dest (already exists)"
      fi
    done
  fi
}

# Root
link_readme "$ROOT"

# 1st-level folders
for dir in "$ROOT"/*/; do
  [ -d "$dir" ] && link_readme "${dir%/}"
done
