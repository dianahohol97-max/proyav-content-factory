"""Generate on-brand lifestyle photos for проЯв carousels with Gemini.

Calls Gemini 2.5 Flash Image ("nano banana") via the REST API directly (no SDK,
so it doesn't depend on google-auth/cryptography). Same model as the
animated-babybook factory. UI screenshots are made separately with headless
Chromium; this script only produces the photographic slides.

Prereqs:
  export GOOGLE_API_KEY=...   # Google AI Studio key (aistudio.google.com/apikey)
Run:
  python generate_photos.py            # only missing files
  python generate_photos.py --force    # regenerate all
  python generate_photos.py --only gallery-hero.jpg
Saved to input/photos/<name> at ~3:4 (cover-fit to 4:5 at render time).
"""
import argparse
import base64
import os
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

import config as C

ROOT = Path(__file__).resolve().parent
PHOTOS_DIR = ROOT / "input" / "photos"
MODEL = "gemini-2.5-flash-image"
API = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

# Shared look so every generated frame reads as one editorial feed.
STYLE = (
    "Editorial documentary photograph, real people, natural window light, "
    "muted filmic color grade with deep shadows, shallow depth of field, 35mm, "
    "premium wedding/portrait photographer aesthetic, calm and elegant, no text, "
    "no logos, no watermark, vertical 4:5 composition with clean negative space."
)


def generate(key, prompt, out_path):
    body = {
        "contents": [{"parts": [{"text": f"{prompt}. {STYLE}"}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": "3:4"},
        },
    }
    r = requests.post(API, headers={"x-goog-api-key": key,
                                    "Content-Type": "application/json"},
                      json=body, timeout=180)
    if r.status_code != 200:
        print(f"  HTTP {r.status_code}: {r.text[:200]}")
        return False
    for cand in r.json().get("candidates", []):
        for part in (cand.get("content", {}) or {}).get("parts", []) or []:
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                raw = base64.b64decode(inline["data"])
                Image.open(BytesIO(raw)).convert("RGB").save(out_path, "JPEG", quality=92)
                return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", default=None)
    args = ap.parse_args()

    prompts = getattr(C, "PHOTO_PROMPTS", {})
    if not prompts:
        raise SystemExit("No PHOTO_PROMPTS in config.py")
    key = os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise SystemExit("GOOGLE_API_KEY not set (Google AI Studio key).")

    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    items = [(args.only, prompts[args.only])] if args.only else list(prompts.items())
    made = 0
    for name, prompt in items:
        out = PHOTOS_DIR / name
        if out.exists() and not args.force:
            print(f"skip (exists): {name}"); continue
        ok = generate(key, prompt, out)
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
        made += int(ok)
    print(f"generated: {made}")


if __name__ == "__main__":
    main()
