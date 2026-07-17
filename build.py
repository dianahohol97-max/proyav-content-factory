"""Build step (run locally or by GitHub Actions).

Renders every carousel in config.CAROUSELS to output/carousels/<id>/ and writes
queue/carousel_queue.json with raw-CDN image URLs. The Make carousel poster
reads the queue and dedups by `id` in its Data Store, so re-running is safe.
"""
import json
import os
import glob
import config as C
import render as R

ROOT = os.path.dirname(os.path.abspath(__file__))
CARS_DIR = os.path.join(ROOT, "output", "carousels")
PHOTOS_DIR = os.path.join(ROOT, "input", "photos")
Q_DIR = os.path.join(ROOT, "queue")


def raw(path_from_root):
    return f"{C.RAW}/{path_from_root.replace(os.sep, '/')}"


def _photo_pool():
    pool = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"):
        pool += glob.glob(os.path.join(PHOTOS_DIR, ext))
    return sorted(pool)


def build_carousels():
    items = []
    pool = _photo_pool()
    cursor = 0
    for car in C.CAROUSELS:
        out_dir = os.path.join(CARS_DIR, car["id"])
        # a carousel needs 1 cover photo + 1 per content slide; explicit
        # per-carousel photos win, otherwise draw from the pool round-robin.
        need = 1 + len(car["slides"])
        if car.get("photos"):
            photos = [os.path.join(PHOTOS_DIR, p) for p in car["photos"]]
        elif pool:
            photos = [pool[(cursor + i) % len(pool)] for i in range(need)]
            cursor += need
        else:
            photos = []
        paths = R.carousel(car, out_dir, photos=photos)
        slides = [raw(os.path.relpath(p, ROOT)) for p in paths]
        caption = car["caption"] + C.CAPTION_FOOTER.format(brand=C.BRAND)
        items.append({
            "id": car["id"],
            "channels": ["instagram_carousel"],
            "format": "carousel",
            "rubric": car["rubric"],
            "caption": caption,
            "hashtags": car.get("hashtags", ""),
            "slides": slides,          # ordered image URLs — export JPEG for IG
            "status": "ready",
        })
    return items


def main():
    os.makedirs(Q_DIR, exist_ok=True)
    car_items = build_carousels()
    with open(os.path.join(Q_DIR, "carousel_queue.json"), "w") as f:
        json.dump(car_items, f, indent=2, ensure_ascii=False)
    total_slides = sum(len(i["slides"]) for i in car_items)
    print(f"carousels: {len(car_items)}  slides: {total_slides}")


if __name__ == "__main__":
    main()
