#!/usr/bin/env python3
"""Generate an image using Gemini 3.1 Flash Image Preview via REST API."""

import argparse
import base64
import json
import os
import subprocess
import sys


def get_api_key() -> str:
    """Get GEMINI_API_KEY from env, falling back to sourcing ~/.zshrc."""
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key

    # Try sourcing from shell profile
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


def generate_image(prompt: str, output_path: str, model: str = "gemini-3.1-flash-image-preview") -> str:
    """Call Gemini API to generate an image from a text prompt."""
    api_key = get_api_key()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    }

    result = subprocess.run(
        ["curl", "-s", url, "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=120,
    )

    if result.returncode != 0:
        print(f"Error: curl failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(result.stdout)

    if "error" in data:
        print(f"API Error: {data['error']['message']}", file=sys.stderr)
        sys.exit(1)

    # Extract image and optional text from response
    text_response = None
    image_saved = False

    for part in data["candidates"][0]["content"]["parts"]:
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
        print(f"Full response: {json.dumps(data, indent=2)[:500]}", file=sys.stderr)
        sys.exit(1)

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate images with Gemini API")
    parser.add_argument("prompt", help="Image generation prompt")
    parser.add_argument("-o", "--output", default="generated_image.png", help="Output file path (default: generated_image.png)")
    parser.add_argument("-m", "--model", default="gemini-3.1-flash-image-preview", help="Model name")
    args = parser.parse_args()

    generate_image(args.prompt, args.output, args.model)


if __name__ == "__main__":
    main()
