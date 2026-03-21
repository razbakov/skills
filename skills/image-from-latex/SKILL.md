---
name: image-from-latex
description: "Generate images from LaTeX/TikZ compiled with Tectonic and converted to PNG via ImageMagick. Use when the user wants vector-quality graphics, thumbnails, diagrams, or visual assets with precise typography and geometric elements from code."
---

# LaTeX-to-Image Technique

Generate high-quality images from LaTeX/TikZ source, compiled to PDF with Tectonic and rasterized to PNG with ImageMagick.

## When to use

- You need precise geometric shapes, gradients, and text positioning
- Thumbnails (YouTube 16:9, Shorts 9:16) with bold typography
- Diagrams, infographics, or stylized graphics with exact control
- Output must be vector-sharp at any resolution

## When NOT to use

- Complex layouts with many HTML-like elements → use **image-from-html**
- Photo-realistic or illustrative imagery → use **image-from-gemini**
- Multi-page documents → use **latex-pdf** skill directly

## Requirements

- `tectonic`: `brew install tectonic` (auto-downloads LaTeX packages)
- `magick` (ImageMagick): `brew install imagemagick`
- `python3` (standard library only)

## Workflow

### 1. Write a Python script that builds TikZ source

```python
import subprocess
from pathlib import Path

PREAMBLE = r"""
\documentclass[tikz,border=0pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{tikz}
\usetikzlibrary{calc,positioning,fadings}
\usepackage{xcolor}
\begin{document}
"""
POST = r"\end{document}"

F = r"\sffamily\bfseries"  # bold sans-serif shorthand
```

### 2. Compile with Tectonic

```python
def compile_tex(tex_content, name, out_dir):
    p = Path(out_dir) / f"{name}.tex"
    p.write_text(tex_content)
    r = subprocess.run(["tectonic", str(p)], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FAIL {name}: {r.stderr[:500]}")
        return False
    print(f"OK {name}")
    return True
```

### 3. Convert PDF to PNG

```bash
# 16:9 landscape (1280x720)
magick -density 300 output.pdf -resize 1280x720! -quality 95 output.png

# 9:16 vertical (1080x1920)
magick -density 300 output.pdf -resize 1080x1920! -quality 95 output.png

# A4 print (300 DPI)
magick -density 300 output.pdf -quality 95 output.png
```

### 4. Display the result

Use the **Read tool** on the generated PNG to show it inline.

## Helpers

### Shadow text (drop shadow for depth)

```python
def st(x, y, text, size, color, anchor="west", sop=0.5, ox=0.12, oy=-0.12):
    fs = rf"{F}\fontsize{{{size}}}{{{size+2}}}\selectfont"
    return (
        rf"  \node[anchor={anchor}, font={fs}, text=black, opacity={sop}] at ({x+ox},{y+oy}) {{{text}}};" "\n"
        rf"  \node[anchor={anchor}, font={fs}, text={color}] at ({x},{y}) {{{text}}};"
    )

def stc(x, y, text, size, color, sop=0.5, ox=0.08, oy=-0.08):
    return st(x, y, text, size, color, anchor="center", sop=sop, ox=ox, oy=oy)
```

### LaTeX text escaping

```python
def esc(text):
    for old, new in [
        ("\\", "\\textbackslash{}"), ("&", "\\&"), ("%", "\\%"),
        ("$", "\\$"), ("#", "\\#"), ("_", "\\_"),
        ("{", "\\{"), ("}", "\\}"),
        ("~", "\\textasciitilde{}"), ("^", "\\textasciicircum{}"),
    ]:
        text = text.replace(old, new)
    return text
```

## Canvas dimensions

| Format              | Width (cm) | Height (cm) | PNG size    |
| ------------------- | ---------- | ------------ | ----------- |
| 16:9 landscape      | 25.6       | 14.4         | 1280x720    |
| 9:16 vertical       | 10.8       | 19.2         | 1080x1920   |

## Design tips

- Font sizes: 70-95pt title, 18-24pt subtitle
- Always use `\usepackage{lmodern}` for large font sizes
- Use `\sffamily\bfseries` for bold sans-serif
- Gradient backgrounds: `\shade[top color=X, bottom color=Y]`
- Subtle depth: `\fill[black, opacity=0.12]` triangle in a corner
- Accent underline: thin `\fill` rectangle (0.15cm) below title
- 2-3 colors max: bg gradient + 1-2 accent colors
- Escape `%` as `\%` and `$` as `\$` in text nodes
