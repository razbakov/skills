#!/usr/bin/env python3
"""Send a poster + caption bundle to Telegram Saved Messages via Telethon.

Usage:
    send-to-telegram.py <image-path> <caption-md-path> [--chat me] [--section Primary]

Sends two messages:
  1. The image (as a photo, not a document)
  2. The extracted "## Primary" section of caption.md (or a different section
     specified via --section)

Both go to the user's Saved Messages (`me`) by default. Pass `--chat <username-or-id>`
to send elsewhere — but Saved Messages is the canonical review surface for these
bundles before publishing to IG.

Requires:
- Telethon ≥ 1.43 in the venv at ~/.config/telegram/venv/
- Authenticated session at ~/.config/telegram/session.session
- TELEGRAM_API_ID, TELEGRAM_API_HASH in ~/.config/telegram/.env

Common error: `ValueError: too many values to unpack (expected 5)` means the venv's
Telethon is older than the session-file schema. Fix:

    /Users/$USER/.config/telegram/venv/bin/python3.13 -m pip install \\
        --upgrade --force-reinstall "telethon>=1.43"

(Use the python3.13 binary specifically — the venv has multiple python versions
and `python3` may resolve to the wrong one.)
"""
import argparse
import asyncio
import os
import sys
from pathlib import Path


def load_env(env_file: Path):
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def extract_section(caption_md: str, section_name: str) -> str:
    """Extract a `## <Section>` block from caption.md, stripping the heading line.

    Sections are delimited by `---` (or end of file). Returns the body text.
    """
    needle = f"## {section_name}"
    if needle not in caption_md:
        raise ValueError(f"Section '{section_name}' not found in caption.md")
    start = caption_md.index(needle)
    rest = caption_md[start:]
    # End at next `---` (separator) or end of file
    if "\n---" in rest:
        rest = rest[: rest.index("\n---")]
    # Drop the heading line itself
    lines = rest.split("\n", 2)
    body = lines[2] if len(lines) > 2 else ""
    return body.strip()


async def send(image_path: str, body: str, chat: str, as_file: bool):
    from telethon import TelegramClient

    api_id = int(os.environ["TELEGRAM_API_ID"])
    api_hash = os.environ["TELEGRAM_API_HASH"]
    session = str(Path.home() / ".config" / "telegram" / "session")

    async with TelegramClient(session, api_id, api_hash) as client:
        sent_img = await client.send_file(chat, image_path, force_document=as_file)
        kind = "file" if as_file else "photo"
        print(f"image ({kind}) msg_id={sent_img.id}")
        sent_txt = await client.send_message(chat, body, link_preview=False)
        print(f"caption msg_id={sent_txt.id} ({len(body)} chars)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", help="Path to schedule.png")
    parser.add_argument("caption", help="Path to caption.md")
    parser.add_argument(
        "--chat",
        default="me",
        help="Telegram chat target (default: me = Saved Messages)",
    )
    parser.add_argument(
        "--section",
        default="Primary",
        help="Caption section to send (default: Primary)",
    )
    parser.add_argument(
        "--as-file",
        action="store_true",
        help="Send the image as a document/file (uncompressed) instead of a "
             "Telegram photo. Use this when the recipient will re-upload the "
             "image elsewhere (e.g. Instagram) and needs the original quality.",
    )
    args = parser.parse_args()

    load_env(Path.home() / ".config" / "telegram" / ".env")

    image_path = Path(args.image).expanduser().resolve()
    if not image_path.exists():
        sys.exit(f"image not found: {image_path}")

    caption_md = Path(args.caption).expanduser().read_text()
    body = extract_section(caption_md, args.section)
    if not body:
        sys.exit(f"section '{args.section}' is empty")

    asyncio.run(send(str(image_path), body, args.chat, args.as_file))


if __name__ == "__main__":
    main()
