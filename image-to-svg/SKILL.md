---
name: image-to-svg
description: Convert raster images (JPEG, PNG) to SVG vector graphics using Potrace. Use when the user asks to vectorize an image, convert a logo to SVG, trace a bitmap, or create vector graphics from a raster image.
---

# Image to SVG Conversion

Convert logos and icons from raster formats to clean SVG vectors using Potrace.

## Prerequisites

```bash
# macOS
brew install potrace imagemagick

# Ubuntu/Debian
sudo apt install potrace imagemagick
```

## Quick Workflow

### 1. Prepare the image

Convert to PBM (portable bitmap) format for Potrace:

```bash
# For clean logos with solid colors
magick input.jpg -colorspace Gray -threshold 50% output.pbm

# Adjust threshold (0-100%) based on image:
# - Lower values: more black, captures finer details
# - Higher values: more white, cleaner shapes
```

### 2. Trace to SVG

```bash
potrace output.pbm -s -o output.svg
```

**Potrace options:**
| Option | Effect |
|--------|--------|
| `-s` | Output SVG format |
| `-t 5` | Suppress speckles smaller than 5 pixels |
| `-a 1.0` | Smoother curves (0=polygon, 1.34=default) |
| `-O 0.2` | Optimize paths (0=least, 1=most) |

### 3. Add colors (optional)

Potrace outputs monochrome SVG. To add colors:

1. Open the SVG and identify path groups
2. Change `fill="#000000"` to desired colors
3. For multi-color logos, separate paths into `<g>` groups with different fills

**Example color edit:**

```xml
<!-- Before -->
<g fill="#000000">
  <path d="...lips..."/>
  <path d="...hand..."/>
</g>

<!-- After: separate groups with colors -->
<g fill="#C21E1E">  <!-- Red for lips -->
  <path d="...lips..."/>
</g>
<g fill="#FFFFFF">  <!-- White for hand -->
  <path d="...hand..."/>
</g>
```

## Multi-Color Logos

For logos with distinct color regions:

1. Create separate masks for each color
2. Trace each mask individually
3. Combine into single SVG with color groups

```bash
# Extract red channel (for red elements)
magick input.jpg -channel R -separate -threshold 50% red.pbm
potrace red.pbm -s -o red.svg

# Combine manually or use SVG editor
```

## Troubleshooting

| Issue               | Solution                                            |
| ------------------- | --------------------------------------------------- |
| Too much noise      | Increase threshold or use `-t` to suppress speckles |
| Missing details     | Decrease threshold value                            |
| Jagged edges        | Use `-a 1.5` for smoother curves                    |
| File too large      | Use `-O 1` for maximum optimization                 |
| Background included | Use `-k 0.5` to set black level cutoff              |

## Output Verification

Always verify the SVG renders correctly:

1. Open in browser to check appearance
2. Test at different sizes (SVG should scale cleanly)
3. Verify on both light and dark backgrounds if needed
