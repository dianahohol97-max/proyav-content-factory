# проЯв — Content Factory

Code-rendered carousel factory for **проЯв** (українська галерея для фотографів).
Text is drawn by code (Pillow) → zero typos, exact brand colours, brand fonts.
GitHub Actions renders on a schedule and writes a JSON **queue** that a Make
poster consumes. Same architecture as the VistelaCo / bloom focus factories.

```
config.py   brand tokens (cobalt #2F55FF, Unbounded + Manrope) + carousel library
render.py   Pillow renderers — 4:5 (1080×1350) educational carousels
build.py    renders everything + writes queue/carousel_queue.json (raw-CDN URLs)
output/     generated slides, served free via raw.githubusercontent (CDN)
queue/      carousel_queue.json  <- the Make carousel poster reads this
.github/workflows/build.yml   weekly cron + manual run
```

## What it produces
Educational IG carousels (cover + content slides + CTA), on-brand per the проЯв
brand book. Add a carousel = append to `CAROUSELS` in `config.py`.

## Handoff (Make poster)
Clone the proven bloom carousel poster (Make scenario **9418390**): read
`queue/carousel_queue.json`, post the next un-posted `id`, **export slides as
JPEG** for Instagram, dedup by `id` in a Data Store (`proyav-posted`).

## Run locally
```
pip install -r requirements.txt
mkdir -p fonts
curl -sSLg -o fonts/Unbounded.ttf "https://raw.githubusercontent.com/google/fonts/main/ofl/unbounded/Unbounded%5Bwght%5D.ttf"
curl -sSLg -o fonts/Manrope.ttf   "https://raw.githubusercontent.com/google/fonts/main/ofl/manrope/Manrope%5Bwght%5D.ttf"
python build.py
```
