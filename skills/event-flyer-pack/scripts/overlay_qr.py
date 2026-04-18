"""Overlay a real QR onto a Gemini-generated asset's white placeholder square.

The skill's philosophy: Gemini renders the design (typography, layout, imagery),
we just replace its fake QR placeholder with a real scannable one. This script
is intentionally thin — it does not build layouts.

Usage:
    python3 overlay_qr.py <gemini_png> <qr_png> <output_png> \
        [--x X --y Y --size S]   # manual placement (pixel coords, top-left)
        [--auto-detect]          # find the largest pure-white square

    python3 overlay_qr.py <gemini_png> <qr_png> <output_png> --verify <expected_url>

Dependencies: Pillow, opencv-python-headless (for auto-detect + verify).
Run via: uvx --with Pillow --with opencv-python-headless --with numpy python3 overlay_qr.py ...
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

from PIL import Image


def find_white_square(img_path: Path) -> tuple[int, int, int]:
    """Find the largest near-pure-white square in the image. Returns (x, y, side)."""
    import cv2
    import numpy as np
    img = cv2.imread(str(img_path))
    if img is None:
        raise RuntimeError(f"Cannot read {img_path}")
    # Threshold to near-white (all channels >= 245)
    mask = cv2.inRange(img, (245, 245, 245), (255, 255, 255))
    # Find contours, pick the largest roughly-square one
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best = None
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w < 80 or h < 80:  # too small
            continue
        aspect = w / h if h else 0
        if not (0.8 <= aspect <= 1.25):  # not square enough
            continue
        area = w * h
        if best is None or area > best[3]:
            best = (x, y, min(w, h), area)
    if best is None:
        raise RuntimeError("No white square placeholder detected. Pass --x/--y/--size manually.")
    x, y, side, _ = best
    return x, y, side


def composite(gemini_path: Path, qr_path: Path, out_path: Path,
              x: int | None, y: int | None, size: int | None,
              auto: bool) -> tuple[int, int, int]:
    base = Image.open(gemini_path).convert("RGBA")
    qr = Image.open(qr_path).convert("RGBA")
    if auto or (x is None or y is None or size is None):
        x, y, size = find_white_square(gemini_path)
    # Keep a small quiet-zone margin — inset the QR inside the placeholder.
    pad = max(6, size // 18)
    qr_side = size - 2 * pad
    qr = qr.resize((qr_side, qr_side), Image.NEAREST)
    base.alpha_composite(qr, (x + pad, y + pad))
    base.convert("RGB").save(out_path)
    return x, y, size


def verify(out_path: Path, expected: str) -> tuple[bool, str]:
    import cv2
    img = cv2.imread(str(out_path))
    data, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
    return (data == expected), data or "NO DECODE"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gemini_png")
    ap.add_argument("qr_png")
    ap.add_argument("output_png")
    ap.add_argument("--x", type=int); ap.add_argument("--y", type=int); ap.add_argument("--size", type=int)
    ap.add_argument("--auto-detect", action="store_true")
    ap.add_argument("--verify", help="Expected URL; assert the composite decodes to this")
    args = ap.parse_args()
    x, y, size = composite(Path(args.gemini_png), Path(args.qr_png), Path(args.output_png),
                           args.x, args.y, args.size, args.auto_detect)
    print(f"Placed QR at ({x}, {y}) size {size}px")
    if args.verify:
        ok, val = verify(Path(args.output_png), args.verify)
        print(f"Verify: {'OK' if ok else 'FAIL'} -> {val}")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
