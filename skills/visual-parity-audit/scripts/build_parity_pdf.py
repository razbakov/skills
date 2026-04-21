#!/usr/bin/env python3
"""
Build a side-by-side parity PDF from a folder of screenshots.

Expected layout:
  <repo>/docs/images/<audit-name>/a/NN-slug.png   # reference
  <repo>/docs/images/<audit-name>/b/NN-slug.png   # under audit

Output:
  ~/Local/<org>/<project>/<audit-name>-<YYYY-MM-DD>.pdf

Usage: edit ROWS/VERDICT/COVER below, then run:
  python3 build_parity_pdf.py

Requires: python3, tectonic (`brew install tectonic`).
"""
from __future__ import annotations

import subprocess
import sys
from datetime import date
from pathlib import Path

# ==========================================================================
# Configure these for your audit
# ==========================================================================

AUDIT_NAME = "capture-visual-parity"
AUDIT_DATE = date.today().isoformat()

# Absolute paths — edit to match your setup.
IMG_DIR = Path.home() / "Projects/YOUR-REPO/docs/images" / AUDIT_NAME
OUTPUT_PDF = Path.home() / "Local/YOUR-ORG/YOUR-PROJECT" / f"{AUDIT_NAME}-{AUDIT_DATE}.pdf"

TITLE = "Visual Parity Audit"
SUBTITLE = "Reference prototype vs live port"
# Two short lines about the audit (emulated viewport, screen count, etc.)
METHOD_LINE = r"9 screens, 18 screenshots, 420$\times$900 mobile emulation"

# The headline finding. Rendered as a red-bordered callout on page 1.
# Set to "" to hide.
HEADLINE_CALLOUT = (
    r"\textbf{Verdict:} 8 of 9 screens match. One regression surfaced in "
    r"PR \#68 --- fixed in PR \#72."
)

# Per-screen rows.
# Tuple: (n, title, slug, notes_latex)
# `slug` must match the PNG filename: {a,b}/{slug}.png
# `notes_latex` is pre-escaped LaTeX (you can use \textbf, \emph, \#42, etc.)
ROWS: list[tuple[int, str, str, str]] = [
    # (1, "Pin screen", "01-pin", r"Identical copy + color."),
    # (2, "Staff panel", "02-staff", r"\textbf{Regression:} labels shrunk (PR \#68)."),
]

# Verdict summary table: (aspect, status_latex)
# Use the \PASS / \FAIL / \WARN macros (defined in the preamble).
VERDICT: list[tuple[str, str]] = [
    # ("Screen structure", r"\PASS"),
    # ("Label sizing", r"\FAIL{} regression"),
]

# Sections that weren't captured (with reasons).
NOT_CAPTURED = [
    # "Success screen --- requires production DB write",
]

# Action items: (priority, text, status_latex)
ACTIONS: list[tuple[str, str, str]] = [
    # ("P1", "Revert .field-label to 1.5rem/700", r"\PASS{} PR \#72"),
]


# ==========================================================================
# Rendering (don't usually need to change below here)
# ==========================================================================

def esc(text: str) -> str:
    """Escape LaTeX special chars — use on free-form input like screen titles."""
    for old, new in [
        ("\\", "\\textbackslash{}"), ("&", "\\&"), ("%", "\\%"),
        ("$", "\\$"), ("#", "\\#"), ("_", "\\_"),
        ("{", "\\{"), ("}", "\\}"),
        ("~", "\\textasciitilde{}"), ("^", "\\textasciicircum{}"),
    ]:
        text = text.replace(old, new)
    return text


def img_cell(path: Path) -> str:
    """LaTeX for a half-width, height-capped image cell."""
    return (
        r"\begin{minipage}[t]{0.48\textwidth}\centering"
        rf"\includegraphics[width=\linewidth,height=0.52\textheight,keepaspectratio]"
        rf"{{{path.resolve()}}}"
        r"\end{minipage}"
    )


def build_row(n: int, title: str, slug: str, notes: str) -> str:
    a = IMG_DIR / "a" / f"{slug}.png"
    b = IMG_DIR / "b" / f"{slug}.png"
    for p in (a, b):
        if not p.exists():
            print(f"WARNING: missing {p}", file=sys.stderr)
    return (
        rf"\section*{{{n}. {esc(title)}}}" "\n"
        r"\begin{center}" "\n"
        r"\begin{tabular}{@{}cc@{}}" "\n"
        r"\textbf{Reference (A)} & \textbf{Under audit (B)} \\[2pt]" "\n"
        rf"{img_cell(a)} & {img_cell(b)} \\" "\n"
        r"\end{tabular}" "\n"
        r"\end{center}" "\n"
        rf"\noindent {notes}" "\n"
        r"\vspace{0.8em}" "\n"
    )


def build_verdict_table() -> str:
    if not VERDICT:
        return ""
    rows = "\n".join(rf"{aspect} & {status} \\" for aspect, status in VERDICT)
    return (
        r"\section*{Verdict}" "\n"
        r"\begin{center}\renewcommand{\arraystretch}{1.3}" "\n"
        r"\begin{tabular}{@{}p{0.62\textwidth}@{}p{0.35\textwidth}@{}}" "\n"
        r"\toprule \textbf{Area} & \textbf{Parity} \\ \midrule" "\n"
        f"{rows}" "\n"
        r"\bottomrule \end{tabular}\end{center}" "\n"
    )


def build_not_captured() -> str:
    if not NOT_CAPTURED:
        return ""
    items = "\n".join(rf"\item {line}" for line in NOT_CAPTURED)
    return (
        r"\section*{Screens not captured}" "\n"
        r"\begin{itemize}\setlength{\itemsep}{2pt}" "\n"
        f"{items}\n"
        r"\end{itemize}" "\n"
    )


def build_actions() -> str:
    if not ACTIONS:
        return ""
    rows = "\n".join(
        rf"\textbf{{{p}}} & {item} & {status} \\" for p, item, status in ACTIONS
    )
    return (
        r"\section*{Action items}" "\n"
        r"\begin{center}\renewcommand{\arraystretch}{1.3}" "\n"
        r"\begin{tabular}{@{}p{0.12\textwidth}p{0.58\textwidth}p{0.25\textwidth}@{}}" "\n"
        r"\toprule \textbf{Priority} & \textbf{Item} & \textbf{Status} \\ \midrule" "\n"
        f"{rows}" "\n"
        r"\bottomrule \end{tabular}\end{center}" "\n"
    )


PREAMBLE = r"""\documentclass[10pt,a4paper]{article}
\usepackage[margin=18mm,headheight=14pt]{geometry}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{xcolor}
\usepackage{fancyhdr}
\usepackage{tcolorbox}
\usepackage{pifont}
\usepackage[hidelinks]{hyperref}
\usepackage{titlesec}

\definecolor{accentRed}{HTML}{C62828}
\definecolor{accentGreen}{HTML}{2E7D32}
\definecolor{accentAmber}{HTML}{F9A825}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small __HEADER_LEFT__}
\fancyhead[R]{\small __HEADER_RIGHT__}
\fancyfoot[C]{\small\thepage}
\renewcommand{\headrulewidth}{0.3pt}

\titleformat{\section}{\large\bfseries}{\thesection}{1em}{}
\setlength{\parindent}{0pt}
\setlength{\parskip}{4pt plus 1pt}

\newcommand{\PASS}{\textcolor{accentGreen}{\ding{51}}}
\newcommand{\FAIL}{\textcolor{accentRed}{\ding{55}}}
\newcommand{\WARN}{\textcolor{accentAmber}{$\sim$}}

\begin{document}
"""


def build_cover() -> str:
    lines = [
        r"\begin{center}",
        rf"{{\Huge\bfseries\color{{accentRed}} {esc(TITLE)}}}\\[6pt]",
        rf"{{\Large {esc(SUBTITLE)}}}\\[4pt]",
        rf"{{\today \hspace{{1em}} $\cdot$ \hspace{{1em}} {METHOD_LINE}}}",
        r"\end{center}",
        r"\vspace{0.5em}",
    ]
    if HEADLINE_CALLOUT:
        lines += [
            r"\begin{tcolorbox}[colback=accentRed!6,colframe=accentRed,boxrule=0.6pt,left=10pt,right=10pt]",
            HEADLINE_CALLOUT,
            r"\end{tcolorbox}",
        ]
    return "\n".join(lines)


def main() -> None:
    IMG_DIR.parent.parent.mkdir(parents=True, exist_ok=True)  # noqa: ensure parent exists
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    tex_path = OUTPUT_PDF.with_suffix(".tex")

    preamble = (
        PREAMBLE
        .replace("__HEADER_LEFT__", esc(TITLE))
        .replace("__HEADER_RIGHT__", AUDIT_DATE)
    )

    body_parts = [build_cover(), build_verdict_table()]
    if ROWS:
        body_parts.append(r"\section*{Side-by-side screenshots}")
        body_parts.extend(build_row(n, t, s, notes) for n, t, s, notes in ROWS)
    body_parts.append(build_not_captured())
    body_parts.append(build_actions())

    tex = preamble + "\n".join(p for p in body_parts if p) + "\n\\end{document}\n"
    tex_path.write_text(tex)
    print(f"wrote {tex_path} ({len(tex)} chars)")

    result = subprocess.run(
        ["tectonic", str(tex_path)],
        capture_output=True, text=True, cwd=tex_path.parent,
    )
    if result.returncode != 0:
        print("tectonic stderr:\n" + result.stderr, file=sys.stderr)
        sys.exit(1)
    print(f"built {OUTPUT_PDF} ({OUTPUT_PDF.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
