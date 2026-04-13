#!/usr/bin/env python3
"""Generate an image using Gemini via REST API, with optional reference images."""

import argparse
import base64
import json
import os
import subprocess
import sys
import urllib.request


def get_api_key() -> str:
    """Get GEMINI_API_KEY from env, falling back to sourcing ~/.zshrc."""
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key

    for profile in ["~/.zshrc", "~/.bashrc", "~/.bash_profile", "~/.zprofile"]:
        path = os.path.expanduser(profile)
        if os.path.exists(path):
            result = subprocess.run(
                ["bash", "-c", f"source {path} 2>/dev/null && echo $GEMINI_API_KEY"],
                capture_output=True, text=True,
            )
            key = result.stdout.strip()
            if key:
                return key

    print("Error: GEMINI_API_KEY not found in environment or shell profiles.", file=sys.stderr)
    print("Set it with: export GEMINI_API_KEY=your-key-here", file=sys.stderr)
    sys.exit(1)


def generate_image(prompt: str, output_path: str, model: str = "gemini-3.1-flash-image-preview", input_images: list = None) -> str:
    """Call Gemini API to generate an image, optionally with reference images."""
    api_key = get_api_key()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    parts = []
    for img_path in (input_images or []):
        with open(img_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        ext = os.path.splitext(img_path)[1].lower().lstrip(".")
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}.get(ext, "image/png")
        parts.append({"inlineData": {"mimeType": mime, "data": img_b64}})

    parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    }

    data = json.dumps(payload).encode()

    # Use urllib for large payloads (curl fails with big base64 images)
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    try:
        resp = urllib.request.urlopen(req, timeout=180)
        result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"API Error ({e.code}): {body[:500]}", file=sys.stderr)
        sys.exit(1)

    if "error" in result:
        print(f"API Error: {result['error']['message']}", file=sys.stderr)
        sys.exit(1)

    text_response = None
    image_saved = False

    for part in result["candidates"][0]["content"]["parts"]:
        if "inlineData" in part:
            img_bytes = base64.b64decode(part["inlineData"]["data"])
            with open(output_path, "wb") as f:
                f.write(img_bytes)
            image_saved = True
            print(f"Image saved: {output_path} ({len(img_bytes)} bytes)")
        elif "text" in part:
            text_response = part["text"]

    if text_response:
        print(f"Model notes: {text_response}")

    if not image_saved:
        print("Error: No image was returned by the API.", file=sys.stderr)
        print(f"Full response: {json.dumps(result, indent=2)[:500]}", file=sys.stderr)
        sys.exit(1)

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate images with Gemini API")
    parser.add_argument("prompt", help="Image generation prompt")
    parser.add_argument("-o", "--output", default="generated_image.png", help="Output file path")
    parser.add_argument("-m", "--model", default="gemini-3.1-flash-image-preview", help="Model name")
    parser.add_argument("-i", "--input", action="append", default=None, help="Reference image(s) — can be repeated: -i photo1.jpg -i photo2.jpg")
    args = parser.parse_args()

    generate_image(args.prompt, args.output, args.model, args.input)


if __name__ == "__main__":
    main()
