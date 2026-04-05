#!/usr/bin/env python3
"""Generate video with Google Veo via Gemini API.

Usage:
  # Text-to-video
  python3 generate.py "A dancer spinning in a bright room" -o output.mp4

  # Image-to-video
  python3 generate.py "The dancer begins to spin gracefully" -i input.png -o output.mp4

  # With model override
  python3 generate.py "prompt" -o output.mp4 -m veo-2.0-generate-001
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.request
import urllib.error

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("Error: GEMINI_API_KEY not set", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "veo-3.1-generate-preview"


def start_generation(prompt, image_path=None, model=DEFAULT_MODEL, duration=8, aspect_ratio="16:9"):
    """Start async video generation, return operation name."""
    instance = {"prompt": prompt}

    if image_path:
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()
        mime = "image/jpeg" if image_path.lower().endswith((".jpg", ".jpeg")) else "image/png"
        instance["image"] = {"bytesBase64Encoded": image_b64, "mimeType": mime}

    payload = {
        "instances": [instance],
        "parameters": {
            "aspectRatio": aspect_ratio,
            "sampleCount": 1,
            "durationSeconds": duration,
        },
    }

    url = f"{BASE_URL}/models/{model}:predictLongRunning"
    print(f"Starting video generation with {model}...")
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"x-goog-api-key": API_KEY, "Content-Type": "application/json"},
    )

    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read())
    op = result.get("name")
    print(f"Operation: {op}")
    return op


def poll_until_done(operation_name, timeout_seconds=300):
    """Poll operation until done, return response dict."""
    print("Polling for completion...")
    start = time.time()
    poll_count = 0
    while time.time() - start < timeout_seconds:
        time.sleep(5)
        poll_count += 1
        req = urllib.request.Request(
            f"{BASE_URL}/{operation_name}",
            headers={"x-goog-api-key": API_KEY},
        )
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read())
        done = result.get("done", False)
        print(f"  Poll {poll_count}: done={done}")

        if done:
            error = result.get("error")
            if error:
                print(f"Error: {json.dumps(error, indent=2)}", file=sys.stderr)
                sys.exit(1)
            return result.get("response", {})

    print("Timeout waiting for video generation", file=sys.stderr)
    sys.exit(1)


def download_video(response, output_path):
    """Extract video from response and save to file."""
    samples = response.get("generateVideoResponse", {}).get("generatedSamples", [])
    if not samples:
        samples = response.get("videos", [])
    if not samples:
        print(f"No videos in response: {json.dumps(response, indent=2)}", file=sys.stderr)
        sys.exit(1)

    video = samples[0].get("video", {})

    # Try inline base64 first
    b64 = video.get("bytesBase64Encoded")
    if b64:
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(b64))
        print(f"Video saved: {output_path} ({os.path.getsize(output_path)} bytes)")
        return

    # Try URI download
    uri = video.get("uri")
    if uri:
        print(f"Downloading from URI...")
        req = urllib.request.Request(uri, headers={"x-goog-api-key": API_KEY})
        # Follow redirects manually
        try:
            resp = urllib.request.urlopen(req, timeout=60)
            # If we get a redirect (302), the response body may contain the redirect URL
            with open(output_path, "wb") as f:
                f.write(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 302:
                redirect_url = e.headers.get("Location", uri)
                resp = urllib.request.urlopen(redirect_url, timeout=60)
                with open(output_path, "wb") as f:
                    f.write(resp.read())
            else:
                raise

        size = os.path.getsize(output_path)
        if size < 1000:
            # Likely got a redirect page, retry with curl-style redirect following
            import subprocess
            subprocess.run(
                ["curl", "-s", "-L", "-o", output_path, "-H", f"x-goog-api-key: {API_KEY}", uri],
                check=True,
                timeout=60,
            )
            size = os.path.getsize(output_path)

        print(f"Video saved: {output_path} ({size} bytes)")
        return

    print(f"No video data found: {json.dumps(video, indent=2)}", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate video with Google Veo")
    parser.add_argument("prompt", help="Video description prompt")
    parser.add_argument("-i", "--image", help="Input image for image-to-video")
    parser.add_argument("-o", "--output", default="/tmp/veo-output.mp4", help="Output path")
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL, help="Model name")
    parser.add_argument("-d", "--duration", type=int, default=8, choices=[4, 5, 6, 7, 8], help="Duration in seconds")
    parser.add_argument("-a", "--aspect-ratio", default="16:9", help="Aspect ratio (16:9 or 9:16)")
    parser.add_argument("-t", "--timeout", type=int, default=300, help="Max wait time in seconds")
    args = parser.parse_args()

    try:
        op = start_generation(args.prompt, args.image, args.model, args.duration, args.aspect_ratio)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        if args.model == DEFAULT_MODEL:
            print("Retrying with veo-2.0-generate-001...", file=sys.stderr)
            op = start_generation(args.prompt, args.image, "veo-2.0-generate-001", args.duration, args.aspect_ratio)
        else:
            sys.exit(1)

    response = poll_until_done(op, args.timeout)
    download_video(response, args.output)


if __name__ == "__main__":
    main()
