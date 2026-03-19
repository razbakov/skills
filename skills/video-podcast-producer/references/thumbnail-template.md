# Thumbnail TikZ Template

## Python Boilerplate

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

F = r"\sffamily\bfseries"  # font prefix for bold sans-serif

def compile(tex, name, out_dir):
    p = out_dir / f"{name}.tex"
    p.write_text(tex)
    r = subprocess.run(["tectonic", str(p)], capture_output=True, text=True)
    p.unlink(missing_ok=True)
    if r.returncode != 0:
        print(f"FAIL {name}: {r.stderr[:500]}")
        return False
    print(f"OK {name}")
    return True
```

## Shadow Text Helper

Creates text with a drop shadow for depth:

```python
def st(x, y, text, size, color, anchor="west", sop=0.5, ox=0.12, oy=-0.12):
    """Shadow text node. sop=shadow opacity, ox/oy=shadow offset."""
    fs = rf"{F}\fontsize{{{size}}}{{{size+2}}}\selectfont"
    return (
        rf"  \node[anchor={anchor}, font={fs}, text=black, opacity={sop}] at ({x+ox},{y+oy}) {{{text}}};" "\n"
        rf"  \node[anchor={anchor}, font={fs}, text={color}] at ({x},{y}) {{{text}}};"
    )

def stc(x, y, text, size, color, sop=0.5, ox=0.08, oy=-0.08):
    """Center-anchored shadow text."""
    return st(x, y, text, size, color, anchor="center", sop=sop, ox=ox, oy=oy)
```

## Canvas Dimensions

```python
# 16:9 landscape (YouTube thumbnail)
W_LANDSCAPE = 25.6  # cm
H_LANDSCAPE = 14.4

# 9:16 vertical (Shorts thumbnail)
W_VERTICAL = 10.8
H_VERTICAL = 19.2
```

## Landscape Thumbnail Pattern (16:9)

```python
def make_landscape_thumbnail(title_lines, subtitle, colors, out_dir, name):
    """
    title_lines: list of (text, color) tuples, top to bottom
    subtitle: string
    colors: dict with 'bg1', 'bg2', 'accent', 'subtitle'
    """
    W, H = 25.6, 14.4

    color_defs = "\n".join(
        rf"\definecolor{{{k}}}{{HTML}}{{{v}}}"
        for k, v in colors.items()
    )

    # Stack title lines from top
    title_nodes = ""
    y = H * 0.78
    spacing = H * 0.2
    for text, color in title_lines:
        title_nodes += st(1.2, y, text, 80, color) + "\n"
        y -= spacing

    tex = PREAMBLE + rf"""
{color_defs}
\begin{{tikzpicture}}
  \shade[top color=bg1, bottom color=bg2] (0,0) rectangle ({W},{H});
  \fill[black, opacity=0.12] ({W*0.45},0) -- ({W},{H*0.6}) -- ({W},0) -- cycle;
{title_nodes}
  \fill[accent] (1.2,{y + spacing - 1.2}) rectangle (10.0,{y + spacing - 1.05});
  \node[anchor=west, font={F}\fontsize{{22}}{{24}}\selectfont, text=subtitle, opacity=0.85]
    at (1.2,{y + spacing - 2.0}) {{{subtitle}}};
\end{{tikzpicture}}
""" + POST
    return compile(tex, name, out_dir)
```

## Vertical Thumbnail Pattern (9:16)

Same design principles but centered text, stacked vertically with graphic elements in the bottom half.

```python
def make_vertical_thumbnail(title_lines, subtitle, colors, out_dir, name):
    W, H = 10.8, 19.2
    CX = W / 2

    color_defs = "\n".join(
        rf"\definecolor{{{k}}}{{HTML}}{{{v}}}"
        for k, v in colors.items()
    )

    title_nodes = ""
    y = H * 0.82
    spacing = H * 0.13
    for text, color in title_lines:
        title_nodes += stc(CX, y, text, 58, color) + "\n"
        y -= spacing

    tex = PREAMBLE + rf"""
{color_defs}
\begin{{tikzpicture}}
  \shade[top color=bg1, bottom color=bg2] (0,0) rectangle ({W},{H});
{title_nodes}
  \fill[accent, opacity=0.8] (1.5,{y + spacing - 1.0}) rectangle ({W-1.5},{y + spacing - 0.85});
  \node[anchor=center, font={F}\fontsize{{20}}{{22}}\selectfont, text=subtitle, opacity=0.8]
    at ({CX},{y + spacing - 1.8}) {{{subtitle}}};
\end{{tikzpicture}}
""" + POST
    return compile(tex, name, out_dir)
```

## PDF to PNG Conversion

```bash
# Landscape 16:9
magick -density 300 thumb.pdf -resize 1280x720! -quality 95 thumb.png

# Vertical 9:16
magick -density 300 thumb.pdf -resize 1080x1920! -quality 95 thumb.png
```

## Design Tips

- Font sizes: 70-95pt for main title, 18-24pt for subtitle
- Always use `\usepackage{lmodern}` — required for large font sizes
- Use `\sffamily\bfseries` not `\helvet` for large text rendering
- Gradient backgrounds: `\shade[top color=X, bottom color=Y]`
- Subtle depth: dark triangle `\fill[black, opacity=0.12]` in a corner
- Accent underline: thin `\fill` rectangle (0.15cm height) below title
- Color palettes should use 2-3 colors max: bg gradient + 1-2 accent colors
- Escape `%` as `\%` and `$` as `\$` in text nodes

## Graphic Element Patterns

### Terminal Window (for code/tech topics)
```latex
\fill[termbg, rounded corners=10pt] (x0,y0) rectangle (x1,y1);
\draw[termborder, line width=2pt, rounded corners=10pt] (x0,y0) rectangle (x1,y1);
% Traffic light dots
\fill[red!70!black] (x0+0.8, y1-0.6) circle (0.22cm);
\fill[yellow!70!black] (x0+1.5, y1-0.6) circle (0.22cm);
\fill[green!70!black] (x0+2.2, y1-0.6) circle (0.22cm);
```

### Pricing Cards (for tool comparisons)
```latex
\fill[cardbg, rounded corners=12pt] (x0,y0) rectangle (x1,y1);
\draw[accent, line width=2.5pt, rounded corners=12pt] (x0,y0) rectangle (x1,y1);
\fill[accent] (x0, y0+0.3) rectangle (x0+0.4, y1-0.3);  % left bar
```

### Prohibition Sign
```latex
\draw[red, line width=6pt] (cx,cy) circle (R);
\draw[red, line width=6pt] (cx-R*0.707, cy+R*0.707) -- (cx+R*0.707, cy-R*0.707);
```

### Crossed-Out Text/Number
```latex
\node[...] at (x,y) {TEXT};
\draw[red, line width=5pt] (x-w,y) -- (x+w,y);  % horizontal strike
% or X cross:
\draw[red, line width=7pt] (x-w,y+h) -- (x+w,y-h);
\draw[red, line width=7pt] (x-w,y-h) -- (x+w,y+h);
```
