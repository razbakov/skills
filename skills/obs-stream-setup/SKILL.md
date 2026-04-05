---
name: obs-stream-setup
description: Generate OBS stream overlay assets (background, overlay, starting-soon, BRB screens) and configure OBS scenes via WebSocket. Use when the user asks to set up OBS, create stream overlays, design a live stream layout, make their stream look nicer, or mentions OBS scenes/sources. Also trigger when the user says "set up my stream", "create stream graphics", "OBS overlay", or wants branded live stream assets.
---

# OBS Stream Setup

Generate a complete OBS stream package: HTML/CSS overlay assets rendered to PNG, then programmatically configure OBS scenes via WebSocket API.

## What this skill produces

1. **4 HTML source files** (editable, re-renderable):
   - `overlay.html` — transparent overlay with top bar, camera frame, lower third, LIVE badge, social handles
   - `background.html` — dark gradient background with geometric grid pattern
   - `starting-soon.html` — pre-stream waiting screen
   - `brb.html` — break screen

2. **4 PNG assets** (1920x1080):
   - `obs-overlay.png` — transparent PNG for layering
   - `obs-background.png` — solid background
   - `obs-starting-soon.png` — starting soon screen
   - `obs-brb.png` — BRB screen

3. **3 OBS scenes** (configured via WebSocket):
   - **Starting Soon** — single image source
   - **Live** — layered: background → screen capture → camera → overlay (browser source)
   - **BRB** — single image source

## Inputs to gather from the user

Before generating, ask for (or use defaults):

| Input | Example | Default |
|-------|---------|---------|
| Stream title | User-specified | required |
| Streamer name | From CLAUDE.md Personal Info | required |
| Subtitle | User-specified | required |
| Social handle | From CLAUDE.md Personal Info | required |
| Platform labels | "YouTube", "GitHub" | YouTube, GitHub |
| Color scheme | dark blue/purple | `#0a0a14` → `#1a1a3e`, accent `#7c4dff` |
| Layout split | 65/35 | 65% screen, 35% camera |

## Process

### Step 1: Create output directory

```bash
mkdir -p <project>/obs-assets
```

### Step 2: Generate HTML files

Create 4 HTML files using the templates below. Replace placeholders with user inputs.

**Key layout dimensions (1920x1080 canvas):**
```
Top bar:     y=0,   h=56
Screen area: x=16,  y=66, w=1224, h=940
Camera area: x=1264, y=66, w=640,  h=940
Bottom bar:  y=1032, h=48
```

#### overlay.html template

Transparent background (`background: transparent`). Contains:
- Top bar with stream title (gradient background, border-bottom)
- Red LIVE badge (top-right, pulsing animation)
- Screen capture frame (left, subtle border)
- Camera frame (right, border with glow)
- Lower third on camera (gradient fade, accent line, name + subtitle)
- Bottom bar with platform labels and social handle

The overlay uses `background: transparent` on body so it renders as a transparent PNG and works as an OBS Browser Source.

#### background.html template

Dark gradient background with:
- Grid pattern (60px grid, very subtle purple lines)
- Diagonal accent lines
- 3 radial glow spots for depth

#### starting-soon.html template

Centered layout with:
- Stream title (small, uppercase, above)
- "Starting Soon" (large, bold)
- Streamer name (subtitle)
- Animated dots (pulse animation)
- Bottom bar with handles

#### brb.html template

Same as starting-soon but with:
- Coffee cup icon (&#9749;) with float animation
- "Be Right Back" main text
- "Taking a short break" subtitle

### Step 3: Install dependencies and render to PNG

```bash
cd <project>/obs-assets
npm install --no-save puppeteer obs-websocket-js
```

Create `render.mjs`:
```javascript
import puppeteer from 'puppeteer';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

async function render(htmlFile, outputFile, transparent = false) {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  await page.goto(`file://${join(__dirname, htmlFile)}`, { waitUntil: 'networkidle0' });
  await page.screenshot({
    path: join(__dirname, outputFile),
    omitBackground: transparent,
    fullPage: false,
  });
  await browser.close();
  console.log(`Rendered: ${outputFile} (transparent: ${transparent})`);
}

await render('overlay.html', 'obs-overlay.png', true);
await render('background.html', 'obs-background.png', false);
await render('starting-soon.html', 'obs-starting-soon.png', false);
await render('brb.html', 'obs-brb.png', false);
console.log('Done!');
```

Run: `node render.mjs`

The `omitBackground: true` flag is critical for the overlay — it produces a transparent PNG that OBS can layer on top of video sources.

### Step 4: Set up OBS scenes via WebSocket

OBS 28+ has a built-in WebSocket server. The setup script needs the password from the OBS config.

**Read the password:**
```bash
cat ~/Library/Application\ Support/obs-studio/plugin_config/obs-websocket/config.json
```

If the WebSocket server isn't enabled, tell the user: "In OBS, go to Tools → WebSocket Server Settings → Enable WebSocket Server"

Create `setup-obs.mjs` that:
1. Connects to `ws://127.0.0.1:4455` with the password
2. Creates 3 scenes: "Starting Soon", "Live", "BRB"
3. For "Live", layers sources bottom-to-top:
   - Background (image_source) — `obs-background.png`, stretched to 1920x1080
   - Screen capture (reuse existing `macOS Screen Capture`) — positioned at x=16,y=66, bounded 1224x940
   - Camera (reuse existing `Camera`) — positioned at x=1264,y=66, bounded 640x940
   - Stream Overlay (browser_source) — `overlay.html`, 1920x1080 (browser source enables CSS animations like LIVE badge pulse)
4. For "Starting Soon" and "BRB", add single image sources stretched to canvas
5. Switches to the "Live" scene

The script is idempotent — running it again updates transforms instead of duplicating sources.

### Step 5: Verify

Open the generated PNGs for the user to preview. Show the overlay and background separately so they can confirm the layout before applying to OBS.

## Design system

### Colors
| Role | Value |
|------|-------|
| Background dark | `#0a0a14` |
| Background mid | `#1a1a3e` |
| Background light | `#2d1b4e` |
| Accent | `#7c4dff` |
| Accent light | `#b388ff` |
| Text primary | `#e0e0f0` |
| Text muted | `rgba(180, 170, 220, 0.8)` |
| LIVE badge | `#e53935` |
| Borders | `rgba(120, 80, 220, 0.3-0.5)` |

### Typography
- Font: Inter, Segoe UI, system-ui (system sans-serif stack)
- Top bar title: 20px, 600 weight, 4px letter-spacing, uppercase
- Lower third name: 22px, 600 weight
- Lower third subtitle: 14px, 400 weight, 1px letter-spacing
- Big screen text (Starting Soon/BRB): 64px, 700 weight

## Customizing after setup

Edit the HTML files and re-render:
```bash
node render.mjs
```

The overlay in OBS uses a Browser Source pointing to `overlay.html`, so changes to the HTML take effect after refreshing the browser source in OBS (right-click → Refresh cache).
