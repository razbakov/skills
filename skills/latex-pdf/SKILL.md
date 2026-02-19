---
name: latex-pdf
description: Generate high-quality, professionally styled PDF documents and reports using Python-generated LaTeX compiled with Tectonic. Use when the user asks to create a PDF, generate a report, build a PDF document, produce a printable report, or needs a polished multi-page document with tables, color coding, or statistical formatting.
---

# LaTeX PDF Generator

Generate professional PDF documents by writing a Python script that constructs LaTeX source strings and compiles them to PDF using Tectonic. No TeX distribution installation required — Tectonic auto-downloads packages on first use.

## Approach

1. **Python script** builds LaTeX content as a string using f-strings/concatenation
2. Write the string to a `.tex` file
3. Compile with `tectonic <file>.tex` → produces `.pdf` in the same directory

This approach is preferred over HTML-to-PDF or JS-based PDF libraries because LaTeX produces typographically superior output with precise control over layout, tables, math, headers/footers, and page breaks.

## Prerequisites

- Python 3 (standard library only — no pip packages needed)
- Tectonic: `brew install tectonic` (macOS) or `cargo install tectonic`

## Quick Start

```python
import subprocess
from pathlib import Path

def generate_report(data: dict, output_path: Path):
    tex = build_latex(data)
    tex_path = output_path.with_suffix(".tex")
    tex_path.write_text(tex)
    result = subprocess.run(
        ["tectonic", str(tex_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"tectonic failed:\n{result.stderr}")
```

## Essential LaTeX Helpers

Always include these in the Python script:

```python
def esc(text: str) -> str:
    """Escape LaTeX special characters."""
    for old, new in [
        ("\\", "\\textbackslash{}"), ("&", "\\&"), ("%", "\\%"),
        ("$", "\\$"), ("#", "\\#"), ("_", "\\_"),
        ("{", "\\{"), ("}", "\\}"),
        ("~", "\\textasciitilde{}"), ("^", "\\textasciicircum{}"),
    ]:
        text = text.replace(old, new)
    return text

def pct(v: float, decimals: int = 1) -> str:
    """Format a 0-1 value as a LaTeX percentage."""
    return f"{v * 100:.{decimals}f}\\%"
```

## Document Structure

## Key Patterns

### Compile with Tectonic

```python
result = subprocess.run(
    ["tectonic", str(tex_path)],
    capture_output=True, text=True,
)
if result.returncode != 0:
    print(result.stderr)
    sys.exit(1)
```

Tectonic downloads LaTeX packages automatically on first run. No `tlmgr` or TeX Live needed. It produces the PDF in the same directory as the `.tex` file.
