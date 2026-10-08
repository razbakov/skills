#!/usr/bin/env bash
# Render a strategy markdown file to an A4 PDF next to it.
#   md-to-pdf.sh docs/qa-strategy.md            -> docs/qa-strategy.pdf
#   md-to-pdf.sh docs/qa-strategy.md out.pdf
# Pipeline: marked (GFM tables + fenced code) -> styled HTML -> headless Chrome print.
# Needs: node/npx and Google Chrome or Chromium. Override the browser with CHROME=/path.
set -euo pipefail

src="${1:?usage: md-to-pdf.sh <file.md> [out.pdf]}"
out="${2:-${src%.*}.pdf}"
[ -f "$src" ] || { echo "not found: $src" >&2; exit 1; }

chrome="${CHROME:-}"
if [ -z "$chrome" ]; then
  for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
           "/Applications/Chromium.app/Contents/MacOS/Chromium" \
           "$(command -v google-chrome || true)" "$(command -v chromium || true)" \
           "$(command -v chromium-browser || true)"; do
    [ -n "$c" ] && [ -x "$c" ] && { chrome="$c"; break; }
  done
fi
[ -n "$chrome" ] || { echo "Chrome/Chromium not found; set CHROME=/path/to/browser" >&2; exit 1; }

title="$(grep -m1 '^# ' "$src" | sed 's/^# //' || true)"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
html="$tmp/doc.html"

{
  cat <<EOF
<!doctype html><html><head><meta charset="utf-8"><title>${title:-Test Strategy}</title>
<style>
  @page { size: A4; margin: 18mm 16mm 20mm; }
  body { font: 10.5pt/1.5 -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; color: #1a1a1a; }
  h1 { font-size: 20pt; margin: 0 0 4pt; }
  h2 { font-size: 11pt; font-weight: 500; color: #555; margin: 0 0 14pt; }
  h3 { font-size: 13pt; margin: 18pt 0 6pt; padding-bottom: 3pt; border-bottom: 1px solid #ddd; break-after: avoid; }
  h4 { font-size: 11pt; margin: 12pt 0 4pt; break-after: avoid; }
  table { border-collapse: collapse; width: 100%; margin: 6pt 0 10pt; font-size: 9pt; break-inside: auto; }
  tr { break-inside: avoid; }
  th, td { border: 1px solid #ccc; padding: 4pt 6pt; text-align: left; vertical-align: top; }
  th { background: #f2f2f2; }
  pre { background: #f6f6f6; padding: 8pt; font-size: 8.5pt; line-height: 1.3; white-space: pre; overflow: hidden; break-inside: avoid; }
  code { font-family: Menlo, Consolas, monospace; font-size: 0.92em; }
  blockquote { border-left: 3px solid #ccc; margin: 6pt 0; padding: 0 10pt; color: #444; }
</style></head><body>
EOF
  npx -y marked@15 --gfm < "$src"
  echo "</body></html>"
} > "$html"

"$chrome" --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$out" "file://$html" >/dev/null 2>&1

[ -s "$out" ] || { echo "PDF render failed" >&2; exit 1; }
echo "$out"
