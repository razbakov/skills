"""
Batch-generate Instagram grid posts via the Gemini API.

This template generates multiple 1:1 square posts in a single script run,
which is dramatically faster than sequential /image-from-gemini calls and
also avoids the per-call shell overhead.

Customize the `prompts` dict per launch. Output filenames encode the grid
position so a reader can see at a glance which file maps to which cell.

Per content-publishing.md framework rule: flyers, posters, social posts,
and event graphics must use Gemini. Never use the HTML/headless-Chrome path.

USAGE:
  cd ~/Local/<Org>/instagram/grid-launch-N/
  source ~/.zshrc                    # load GEMINI_API_KEY
  python3 generate.py                # outputs post-A3-*.png, post-B1-*.png, ...
"""
import base64
import json
import os
import urllib.request


def generate(prompts: dict[str, str], model: str = "gemini-3.1-flash-image-preview") -> None:
    """
    Generate one PNG per prompt entry. Saves to current working directory.

    Args:
        prompts: dict mapping cell-label-and-slug -> prompt text.
                 e.g. {"A3-tagline-card": "Square 1:1 ..."}
        model:   Gemini model id. Default is flash-image-preview (fast, good quality).
                 Use gemini-3-pro-image-preview for higher quality (slower, costlier).
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY not set. Run: source ~/.zshrc")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    for name, prompt in prompts.items():
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            resp = urllib.request.urlopen(req, timeout=240)
            result = json.loads(resp.read())
            saved = False
            for candidate in result.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    if "inlineData" in part:
                        img_data = base64.b64decode(part["inlineData"]["data"])
                        fp = f"post-{name}.png"
                        with open(fp, "wb") as f:
                            f.write(img_data)
                        print(f"OK {fp} ({len(img_data)} bytes)")
                        saved = True
                        break
                if saved:
                    break
            if not saved:
                # Gemini sometimes refuses on first try; consider retrying with a softer prompt.
                # Common refusal triggers: real-people likeness w/o reference photo, brand-name overlap, ambiguous safety hits.
                print(f"NO IMAGE for {name} — consider retry with softened prompt")
        except Exception as e:
            print(f"ERROR {name}: {e}")


# ────────────────────────────────────────────────────────────────────
# EXAMPLE — replace this dict for your launch.
# Naming convention: "<GridCell>-<short-slug>" so output is post-A3-tagline-card.png.
# Cells that REUSE an existing asset (flyer, logo, etc.) should be `cp`'d
# into this folder before this script runs — don't generate what already exists.
# ────────────────────────────────────────────────────────────────────

prompts = {
    "A3-tagline-card": """Square 1:1 Instagram post (1080x1080). Pure typographic design on cream off-white background.
Top: massive bold sans-serif typography all caps: 'BRAND NAME'.
Middle: thin terracotta divider.
Bottom: smaller type with tagline and key details.
Spell every word exactly. Use apostrophes and ampersands as written, not their word equivalents.""",
    # Add 5-6 more cells here for your launch...
}


if __name__ == "__main__":
    generate(prompts)
