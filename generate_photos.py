"""Generate on-brand lifestyle photos for проЯв carousels with Gemini.

Uses Gemini 2.5 Flash Image ("nano banana") via the google-genai SDK — the same
setup as the animated-babybook factory. UI screenshots are made separately with
headless Chromium (make_screenshots.py); this script only produces the
photographic slides (cover / CTA / human moments).

Prereqs:
  pip install google-genai
  export GOOGLE_API_KEY=...   # Google AI Studio key (aistudio.google.com/apikey)

Run:
  python generate_photos.py            # only missing files
  python generate_photos.py --force    # regenerate all
  python generate_photos.py --only gallery-hero.jpg
Saved to input/photos/<name> at 3:4 (cover-fit to 4:5 at render time).
"""
import argparse
import os
import sys
from io import BytesIO
from pathlib import Path

import config as C

ROOT = Path(__file__).resolve().parent
PHOTOS_DIR = ROOT / "input" / "photos"
MODEL = "gemini-2.5-flash-image"

# Shared look so every generated frame reads as one editorial feed.
STYLE = (
    "Editorial documentary photograph, real people, natural window light, "
    "muted filmic color grade with deep shadows, shallow depth of field, 35mm, "
    "premium wedding/portrait photographer aesthetic, calm and elegant, no text, "
    "no logos, no watermark, vertical 4:5 composition with clean negative space."
)


def _bytes(response):
    for cand in (response.candidates or []):
        if not cand.content or not cand.content.parts:
            continue
        for part in cand.content.parts:
            inline = getattr(part, "inline_data", None)
            if inline and inline.data and (inline.mime_type or "").startswith("image/"):
                return inline.data
    return b""


def generate(client, types, prompt, out_path):
    resp = client.models.generate_content(
        model=MODEL,
        contents=[f"{prompt}. {STYLE}"],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="3:4"),
        ),
    )
    data = _bytes(resp)
    if not data:
        return False
    from PIL import Image
    Image.open(BytesIO(data)).convert("RGB").save(out_path, "JPEG", quality=92)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", default=None, help="single filename to generate")
    args = ap.parse_args()

    prompts = getattr(C, "PHOTO_PROMPTS", {})
    if not prompts:
        raise SystemExit("No PHOTO_PROMPTS in config.py")
    if not os.environ.get("GOOGLE_API_KEY"):
        raise SystemExit("GOOGLE_API_KEY not set (Google AI Studio key).")

    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    items = prompts.items() if not args.only else [(args.only, prompts[args.only])]
    made = 0
    for name, prompt in items:
        out = PHOTOS_DIR / name
        if out.exists() and not args.force:
            print(f"skip (exists): {name}"); continue
        ok = generate(client, types, prompt, out)
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
        made += int(ok)
    print(f"generated: {made}")


if __name__ == "__main__":
    main()
