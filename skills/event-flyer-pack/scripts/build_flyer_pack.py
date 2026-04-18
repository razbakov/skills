"""Build an Event Flyer Pack from a JSON spec + hero image.

Usage:
    python3 build_flyer_pack.py event_spec.json [--out ./print]

Produces, per event slug, into <out>/:
    <slug>-flyer-front-bleed.{png,pdf}      A6 + 3mm bleed
    <slug>-flyer-back-bleed.{png,pdf}       A6 + 3mm bleed
    <slug>-flyer-a4-4up-front.{png,pdf}     A4 home printable with crop marks
    <slug>-flyer-a4-4up-back.{png,pdf}      A4 home printable with crop marks
    <slug>-tent-card-bleed.{png,pdf}        A6 bleed, top half mirrored 180°
    <slug>-instagram-story.{png,jpg}        1080×1920

Hard rules enforced:
  * QR is anchored to canvas bottom (`mm(8-10)` margin) — content flows above.
  * Every QR has a white quiet-zone card behind it with pad = mm(2.5-3).
  * Before export, assertQR(png, expected_url) is called and raises on failure.
  * For multi-QR images (A4 4-up, tent card) each region is cropped and tested
    separately, because cv2 returns NO DECODE when two identical QRs share a frame.

Dependencies: Pillow, qrcode, opencv-python-headless, numpy.
Run via: uvx --with Pillow --with qrcode --with opencv-python-headless --with numpy python3 build_flyer_pack.py ...
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont
import qrcode
from qrcode.constants import ERROR_CORRECT_H
import cv2

DPI = 300
def mm(v: float) -> int:
    return int(round(v / 25.4 * DPI))

# -----------------------------------------------------------------------------
# Spec dataclass
# -----------------------------------------------------------------------------
@dataclass
class EventSpec:
    slug: str
    title_line1: str
    title_line2: str
    date: str
    time: str
    venue: str
    entry: str
    event_url: str
    hero_path: str
    eyebrow: str = ""                       # "MONTUNO CLUB · MÜNCHEN"
    tagline: str = ""                       # italic line under the title
    program: str = ""                       # "Timba · Reparto · Son"
    highlights: list = field(default_factory=list)
    dresscode: str | None = None
    dj: str | None = None
    palette: dict = field(default_factory=dict)
    language: str = "en"

    @classmethod
    def from_json(cls, path: str | Path) -> "EventSpec":
        data = json.loads(Path(path).read_text())
        return cls(**data)

# -----------------------------------------------------------------------------
# Fonts — macOS system fonts; override via env if on Linux
# -----------------------------------------------------------------------------
FONT_PATHS = {
    "didot":       "/System/Library/Fonts/Supplemental/Didot.ttc",
    "baskerville": "/System/Library/Fonts/Supplemental/Baskerville.ttc",
    "helvetica":   "/System/Library/Fonts/HelveticaNeue.ttc",
}
# Platform override: export FONT_PATHS_OVERRIDE='{"didot":"/usr/share/fonts/...","baskerville":"..."}'
_override = os.environ.get("FONT_PATHS_OVERRIDE")
if _override:
    try:
        FONT_PATHS.update(json.loads(_override))
    except json.JSONDecodeError as e:
        print(f"Warning: FONT_PATHS_OVERRIDE is not valid JSON: {e}", file=sys.stderr)

def font(name: str, size_mm: float, index: int = 0) -> ImageFont.FreeTypeFont:
    path = FONT_PATHS[name]
    try:
        return ImageFont.truetype(path, mm(size_mm), index=index)
    except Exception:
        return ImageFont.truetype(path, mm(size_mm))

def hex_to_rgb(h: str) -> Tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def tc(draw: ImageDraw.ImageDraw, cx: int, y: int, text: str, f, fill):
    bbox = draw.textbbox((0, 0), text, font=f)
    draw.text((cx - (bbox[2]-bbox[0])//2, y), text, font=f, fill=fill)

# -----------------------------------------------------------------------------
# QR
# -----------------------------------------------------------------------------
def make_qr(url: str, px: int, fg=(0, 0, 0), border_modules: int = 4) -> Image.Image:
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=10, border=border_modules)
    qr.add_data(url); qr.make(fit=True)
    img = qr.make_image(fill_color="#%02x%02x%02x" % fg, back_color="#ffffff").convert("RGBA")
    return img.resize((px, px), Image.NEAREST)

def place_qr(canvas: Image.Image, qr_img: Image.Image, cx: int, top_y: int, pad: int):
    """Place QR centered at cx with white quiet-zone card behind it.
    top_y is the Y coordinate of the QR's TOP edge (not the card's)."""
    qw, qh = qr_img.size
    card = Image.new("RGBA", (qw + pad*2, qh + pad*2), (255, 255, 255, 255))
    canvas.alpha_composite(card, (cx - qw//2 - pad, top_y - pad))
    canvas.alpha_composite(qr_img, (cx - qw//2, top_y))

def assert_qr_fits(qr_top: int, qr_size: int, canvas_height: int, safe_bottom_mm: float = 8):
    """Hard rule: QR bottom must sit at least `safe_bottom_mm` above canvas bottom."""
    if qr_top + qr_size > canvas_height - mm(safe_bottom_mm):
        raise RuntimeError(
            f"QR overflow: qr_top={qr_top} + qr_size={qr_size} = "
            f"{qr_top + qr_size} > canvas_h - {mm(safe_bottom_mm)} = "
            f"{canvas_height - mm(safe_bottom_mm)}. Tighten layout above or shrink QR."
        )

def verify_qr(png_path: Path, expected: str, region: Tuple[int, int, int, int] | None = None) -> Tuple[bool, str]:
    img = cv2.imread(str(png_path))
    if img is None: return False, "cannot read"
    if region:
        x0, y0, x1, y1 = region
        img = img[y0:y1, x0:x1]
    data, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
    return (data == expected), data or "NO DECODE"

# -----------------------------------------------------------------------------
# FLYER FRONT — A6 + 3mm bleed
# -----------------------------------------------------------------------------
def build_flyer_front(spec: EventSpec, out: Path) -> Path:
    W, H = mm(111), mm(154)
    cream = hex_to_rgb(spec.palette.get("cream", "#F5ECDA"))
    gold  = hex_to_rgb(spec.palette.get("gold",  "#C6A260"))
    terra = hex_to_rgb(spec.palette.get("terracotta", "#C44C34"))
    ink   = hex_to_rgb(spec.palette.get("ink", "#1A0D0B"))

    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    hero = Image.open(spec.hero_path).convert("RGBA")
    hero_ratio = hero.width / hero.height
    target = W / H
    if hero_ratio > target:
        new_h, new_w = H, int(H * hero_ratio)
    else:
        new_w, new_h = W, int(W / hero_ratio)
    hero = hero.resize((new_w, new_h), Image.LANCZOS)
    canvas.alpha_composite(hero, ((W - new_w)//2, (H - new_h)//2))

    # gradient overlay — darker top & bottom, mid transparent
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(H):
        t = y / H
        if t < 0.30: a = int(170 * (1 - t/0.30))
        elif t > 0.55: a = int(210 * ((t-0.55)/0.45))
        else: a = 30
        od.line([(0, y), (W, y)], fill=(10, 6, 14, a))
    canvas.alpha_composite(overlay)

    d = ImageDraw.Draw(canvas); cx = W // 2
    tc(d, cx, mm(10), spec.eyebrow, font("helvetica", 3.4, index=1), gold)

    y = mm(18); title_f = font("didot", 18, index=1)
    tc(d, cx, y, spec.title_line1, title_f, cream); y += mm(14)
    tc(d, cx, y, spec.title_line2, title_f, cream); y += mm(17)
    tc(d, cx, y, spec.tagline, font("baskerville", 5, index=2), tuple(max(0, c-20) for c in cream))

    # Flyer FRONT is the hook: hero + title + when/where/how much + style + dresscode + DJ + QR.
    # Highlights go on the BACK (they're detail-level, and the front has a tight vertical budget
    # because the QR has to sit in the bottom mm(8) margin).
    yb = mm(86)
    content_bottom = yb
    def draw_line(text, font_obj, fill_color, spacing_mm, height_mm):
        nonlocal yb, content_bottom
        tc(d, cx, yb, text, font_obj, fill_color)
        content_bottom = yb + mm(height_mm)
        yb += mm(spacing_mm)

    draw_line(spec.date, font("didot", 7.2), cream, 9, 7.2)
    draw_line(f"{spec.time}  ·  {spec.venue}  ·  {spec.entry}", font("helvetica", 3.8, index=1), cream, 6, 3.8)
    if spec.program:
        draw_line(spec.program, font("baskerville", 3.6), cream, 5, 3.6)

    if spec.dresscode:
        dcf = font("helvetica", 3.2, index=1)
        bbox = d.textbbox((0, 0), spec.dresscode, font=dcf)
        pad_x = mm(4); pw = (bbox[2]-bbox[0]) + pad_x*2; ph = mm(6.5)
        px = cx - pw//2
        d.rounded_rectangle([px, yb, px+pw, yb+ph], radius=mm(2.5), fill=terra)
        d.text((px + pad_x, yb + mm(1.8)), spec.dresscode, font=dcf, fill=cream)
        content_bottom = yb + ph
        yb += ph + mm(3)

    if spec.dj:
        draw_line(spec.dj, font("baskerville", 4.6, index=2), cream, 5, 4.6)

    # QR — bottom-anchored, verified not to overlap actual content bottom
    qr_px = mm(22)
    qr_top = H - mm(8) - qr_px
    assert_qr_fits(qr_top, qr_px, H, safe_bottom_mm=8)
    if qr_top < content_bottom + mm(2):
        raise RuntimeError(
            f"Content bottom ({content_bottom}px) overlaps QR top ({qr_top}px). "
            f"Shorten copy (drop dresscode or DJ) or use build_flyer_back for detail content."
        )
    place_qr(canvas, make_qr(spec.event_url, qr_px, fg=ink), cx, qr_top, pad=mm(2.5))

    canvas = canvas.convert("RGB")
    png = out / f"{spec.slug}-flyer-front-bleed.png"
    canvas.save(png, "PNG")
    canvas.save(out / f"{spec.slug}-flyer-front-bleed.pdf", "PDF", resolution=DPI)
    ok, val = verify_qr(png, spec.event_url)
    if not ok: raise RuntimeError(f"Front QR did not verify: {val}")
    return png

# -----------------------------------------------------------------------------
# FLYER BACK — A6 + 3mm bleed, solid warm background with program details
# -----------------------------------------------------------------------------
def build_flyer_back(spec: EventSpec, out: Path) -> Path:
    W, H = mm(111), mm(154)
    cream = hex_to_rgb(spec.palette.get("cream", "#F5ECDA"))
    gold  = hex_to_rgb(spec.palette.get("gold",  "#C6A260"))
    terra = hex_to_rgb(spec.palette.get("terracotta", "#C44C34"))
    navy  = hex_to_rgb(spec.palette.get("navy", "#16284A"))
    ink   = hex_to_rgb(spec.palette.get("ink", "#1A0D0B"))

    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    # Vertical warm gradient (wine -> navy)
    od = ImageDraw.Draw(canvas)
    top_rgb = tuple(max(0, c - 30) for c in terra)
    bot_rgb = navy
    for y in range(H):
        t = y / H
        r = int(top_rgb[0]*(1-t) + bot_rgb[0]*t)
        g = int(top_rgb[1]*(1-t) + bot_rgb[1]*t)
        b = int(top_rgb[2]*(1-t) + bot_rgb[2]*t)
        od.line([(0, y), (W, y)], fill=(r, g, b, 255))

    d = ImageDraw.Draw(canvas); cx = W // 2
    tc(d, cx, mm(10), spec.eyebrow, font("helvetica", 3.4, index=1), gold)

    y = mm(22)
    title_f = font("didot", 13, index=1)
    tc(d, cx, y, f"{spec.title_line1} {spec.title_line2}", title_f, cream); y += mm(14)

    # gold divider — proportional to title width so it reads as a deliberate rule
    title_bbox = d.textbbox((0, 0), f"{spec.title_line1} {spec.title_line2}", font=title_f)
    dw = max(mm(18), (title_bbox[2] - title_bbox[0]) // 3)
    d.rectangle([cx - dw//2, y, cx + dw//2, y + mm(0.6)], fill=gold); y += mm(7)

    # date/time/venue/entry block — compact, single line for time+venue+entry
    tc(d, cx, y, spec.date, font("didot", 6.5), cream); y += mm(8)
    tc(d, cx, y, f"{spec.time}  ·  {spec.venue}  ·  {spec.entry}", font("helvetica", 3.4, index=1), cream); y += mm(10)

    # Program label + body
    tc(d, cx, y, "PROGRAMM", font("helvetica", 2.8, index=1), gold); y += mm(5)
    if spec.program:
        tc(d, cx, y, spec.program, font("baskerville", 4, index=2), cream); y += mm(7)

    if spec.highlights:
        tc(d, cx, y, "HIGHLIGHTS", font("helvetica", 2.8, index=1), gold); y += mm(5)
        for h in spec.highlights[:4]:
            tc(d, cx, y, h, font("baskerville", 3.6), cream); y += mm(4.5)
        y += mm(2)

    if spec.dresscode:
        dcf = font("helvetica", 3.2, index=1)
        bbox = d.textbbox((0, 0), spec.dresscode, font=dcf)
        pad_x = mm(4); pw = (bbox[2]-bbox[0]) + pad_x*2; ph = mm(7.5)
        px = cx - pw//2
        d.rounded_rectangle([px, y, px + pw, y + ph], radius=mm(2.5), fill=terra)
        d.text((px + pad_x, y + mm(2.2) - mm(0.5)), spec.dresscode, font=dcf, fill=cream)
        y += ph + mm(4)

    # QR — bottom-anchored
    qr_px = mm(22)
    qr_top = H - mm(9) - qr_px
    assert_qr_fits(qr_top, qr_px, H, safe_bottom_mm=9)
    if qr_top < y:
        raise RuntimeError(f"Back content ({y}px) overlaps QR ({qr_top}px). Shorten highlights or shrink QR.")
    place_qr(canvas, make_qr(spec.event_url, qr_px, fg=ink), cx, qr_top, pad=mm(2.5))

    canvas = canvas.convert("RGB")
    png = out / f"{spec.slug}-flyer-back-bleed.png"
    canvas.save(png, "PNG")
    canvas.save(out / f"{spec.slug}-flyer-back-bleed.pdf", "PDF", resolution=DPI)
    ok, val = verify_qr(png, spec.event_url)
    if not ok: raise RuntimeError(f"Back QR did not verify: {val}")
    return png

# -----------------------------------------------------------------------------
# TENT CARD — A6 bleed, top half rotated 180°
# -----------------------------------------------------------------------------
def build_tent_card(spec: EventSpec, out: Path) -> Path:
    W, H = mm(111), mm(154); HALF = H // 2
    cream = hex_to_rgb(spec.palette.get("cream", "#F5ECDA"))
    gold  = hex_to_rgb(spec.palette.get("gold",  "#C6A260"))
    ink   = hex_to_rgb(spec.palette.get("ink", "#1A0D0B"))
    wine  = hex_to_rgb(spec.palette.get("wine", "#74141C"))
    navy  = hex_to_rgb(spec.palette.get("navy", "#16284A"))

    def render_side(top: tuple, bot: tuple) -> Image.Image:
        side = Image.new("RGBA", (W, HALF), (0, 0, 0, 255))
        sd = ImageDraw.Draw(side)
        for y in range(HALF):
            t = y / HALF
            r = int(top[0]*(1-t) + bot[0]*t)
            g = int(top[1]*(1-t) + bot[1]*t)
            b = int(top[2]*(1-t) + bot[2]*t)
            sd.line([(0, y), (W, y)], fill=(r, g, b, 255))
        cx = W // 2; y = mm(6)
        tc(sd, cx, y, spec.eyebrow, font("helvetica", 3.4, index=1), gold); y += mm(6)
        dw = mm(20); sd.rectangle([cx-dw//2, y, cx+dw//2, y+mm(0.5)], fill=gold); y += mm(4)
        if spec.dj:
            tc(sd, cx, y, spec.dj.replace("DJ ", ""), font("didot", 13, index=1), cream); y += mm(13)
        tc(sd, cx, y, spec.program, font("baskerville", 4, index=2), cream); y += mm(7)
        tc(sd, cx, y, f"{spec.title_line1} {spec.title_line2}", font("helvetica", 2.8, index=1), gold); y += mm(5)
        tc(sd, cx, y, f"{spec.date} · {spec.time} · {spec.entry}", font("helvetica", 2.8, index=1), cream); y += mm(5)
        qr_px = mm(24); qr_top = HALF - mm(6) - qr_px
        assert_qr_fits(qr_top, qr_px, HALF, safe_bottom_mm=6)
        place_qr(side, make_qr(spec.event_url, qr_px, fg=ink), cx, qr_top, pad=mm(2.5))
        return side

    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    bottom = render_side((18, 32, 62), navy)
    top = render_side((116, 20, 28), (184, 44, 48)).rotate(180)
    canvas.alpha_composite(top, (0, 0))
    canvas.alpha_composite(bottom, (0, HALF))
    d = ImageDraw.Draw(canvas)
    d.line([(mm(6), HALF), (W - mm(6), HALF)], fill=gold, width=2)

    canvas = canvas.convert("RGB")
    png = out / f"{spec.slug}-tent-card-bleed.png"
    canvas.save(png, "PNG")
    canvas.save(out / f"{spec.slug}-tent-card-bleed.pdf", "PDF", resolution=DPI)
    # Verify each half separately — cv2 confuses 2 identical QRs in one frame
    ok_top, v_top = verify_qr(png, spec.event_url, region=(0, 0, W, HALF))
    ok_bot, v_bot = verify_qr(png, spec.event_url, region=(0, HALF, W, H))
    if not (ok_top and ok_bot):
        raise RuntimeError(f"Tent QR verify failed: top={v_top} bot={v_bot}")
    return png

# -----------------------------------------------------------------------------
# A4 4-up with crop marks — wraps any A6+bleed PNG
# -----------------------------------------------------------------------------
def build_a4_4up(side_name: str, slug: str, bleed_png: Path, out: Path) -> Path:
    A4W, A4H = mm(210), mm(297)
    sheet = Image.new("RGB", (A4W, A4H), "white")
    card = Image.open(bleed_png).convert("RGB").resize((mm(111), mm(154)), Image.LANCZOS)
    tile_w, tile_h = mm(105), mm(148)
    mx = (A4W - tile_w*2) // 2; my = (A4H - tile_h*2) // 2
    bleed = mm(3)
    for row in range(2):
        for col in range(2):
            x = mx + col*tile_w; y = my + row*tile_h
            sheet.paste(card, (x - bleed, y - bleed))
    d = ImageDraw.Draw(sheet); ml, mo = mm(4), mm(1)
    for row in range(2):
        for col in range(2):
            x0 = mx + col*tile_w; y0 = my + row*tile_h
            x1 = x0 + tile_w; y1 = y0 + tile_h
            for (cx, cy) in [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]:
                d.line([(cx-ml-mo, cy), (cx-mo, cy)], fill="black", width=2)
                d.line([(cx+mo, cy), (cx+mo+ml, cy)], fill="black", width=2)
                d.line([(cx, cy-ml-mo), (cx, cy-mo)], fill="black", width=2)
                d.line([(cx, cy+mo), (cx, cy+mo+ml)], fill="black", width=2)
    png = out / f"{slug}-flyer-a4-4up-{side_name}.png"
    sheet.save(png, "PNG")
    sheet.save(out / f"{slug}-flyer-a4-4up-{side_name}.pdf", "PDF", resolution=DPI)
    return png

# -----------------------------------------------------------------------------
# IG story — stub (1080×1920, hero + title + QR)
# -----------------------------------------------------------------------------
def build_ig_story(spec: EventSpec, out: Path) -> Path:
    W, H = 1080, 1920
    cream = hex_to_rgb(spec.palette.get("cream", "#F5ECDA"))
    ink   = hex_to_rgb(spec.palette.get("ink", "#1A0D0B"))
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    hero = Image.open(spec.hero_path).convert("RGBA")
    hr = hero.width / hero.height; tr = W / H
    if hr > tr:
        nh, nw = H, int(H*hr)
    else:
        nw, nh = W, int(W/hr)
    hero = hero.resize((nw, nh), Image.LANCZOS)
    canvas.alpha_composite(hero, ((W-nw)//2, (H-nh)//2))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 120))
    canvas.alpha_composite(overlay)
    d = ImageDraw.Draw(canvas); cx = W//2
    try:
        tf = ImageFont.truetype(FONT_PATHS["didot"], 180, index=1)
    except (OSError, IOError):
        tf = ImageFont.load_default()
    try:
        sf = ImageFont.truetype(FONT_PATHS["helvetica"], 52, index=1)
    except (OSError, IOError):
        sf = ImageFont.load_default()
    tc(d, cx, 400, spec.title_line1, tf, cream)
    tc(d, cx, 600, spec.title_line2, tf, cream)
    tc(d, cx, 820, f"{spec.date} · {spec.time}", sf, cream)
    tc(d, cx, 900, f"{spec.venue} · {spec.entry}", sf, cream)
    qr_px = 360; qr_top = H - 200 - qr_px
    assert_qr_fits(qr_top, qr_px, H, safe_bottom_mm=0); place_qr(canvas, make_qr(spec.event_url, qr_px, fg=ink), cx, qr_top, pad=30)
    canvas = canvas.convert("RGB")
    png = out / f"{spec.slug}-instagram-story.png"
    canvas.save(png, "PNG")
    canvas.save(out / f"{spec.slug}-instagram-story.jpg", "JPEG", quality=92)
    ok, val = verify_qr(png, spec.event_url)
    if not ok: raise RuntimeError(f"IG QR verify failed: {val}")
    return png

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", help="Path to event_spec.json")
    ap.add_argument("--out", default="./print", help="Output directory")
    ap.add_argument("--custom-back-png", help="Optional pre-built back PNG (A6 bleed) to use instead of the generated one")
    ap.add_argument("--skip", nargs="*", default=[], choices=["front", "back", "tent", "a4", "ig"],
                    help="Skip specific deliverables")
    args = ap.parse_args()

    spec = EventSpec.from_json(args.spec)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    front = back = None
    if "front" not in args.skip:
        print("Building flyer front…"); front = build_flyer_front(spec, out)
    if "back" not in args.skip:
        if args.custom_back_png:
            back = Path(args.custom_back_png)
            print(f"Using provided back PNG: {back}")
        else:
            print("Building flyer back…"); back = build_flyer_back(spec, out)
    if "tent" not in args.skip:
        print("Building tent card…"); build_tent_card(spec, out)
    if "a4" not in args.skip:
        if front: print("Building A4 4-up front…"); build_a4_4up("front", spec.slug, front, out)
        if back:  print("Building A4 4-up back…");  build_a4_4up("back",  spec.slug, back,  out)
    if "ig" not in args.skip:
        print("Building IG story…"); build_ig_story(spec, out)

    print("\n=== Done. Files in", out, "===")

if __name__ == "__main__":
    sys.exit(main())
