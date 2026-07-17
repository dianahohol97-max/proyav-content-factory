"""Renderers for проЯв carousels. Full-bleed photo + code-drawn text overlaid on
the image — zero typos, exact brand fonts. Slides are 4:5 (1080×1350) for IG.

Layout language: the photo fills the slide; a bottom-weighted scrim keeps text
legible on any image; text is white with a cobalt accent; a fixed wordmark
footer keeps the feed coherent. Real photos live in input/photos/ (drop live
shots or generated images); an empty pool falls back to a branded gradient.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import config as C

MARGIN = 96
WHITE = "#FFFFFF"
SOFT = "#E8E5DE"          # slightly warm white for body
ACC = "#6E8BFF"           # brighter cobalt — reads on dark photo


def font(path, size, wght=500):
    f = ImageFont.truetype(path, size)
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f


def disp(size, wght=600):
    return font(C.DISPLAY, size, wght)


def body(size, wght=500):
    return font(C.BODY, size, wght)


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _tw(d, s, f, tr=0):
    return sum(d.textlength(c, font=f) for c in s) + tr * (len(s) - 1) if s else 0


def _shadow(d, x, y, s, f, fill, tr=0, anchor="la", sh=(0, 0, 0)):
    """Draw text with a soft dark shadow for legibility on photos."""
    w = _tw(d, s, f, tr)
    if anchor == "ma":
        x -= w / 2
    for dx, dy in ((2, 3),):
        xx = x
        for c in s:
            d.text((xx + dx, y + dy), c, font=f, fill=sh)
            xx += d.textlength(c, font=f) + tr
    xx = x
    for c in s:
        d.text((xx, y), c, font=f, fill=fill)
        xx += d.textlength(c, font=f) + tr


def wrap(d, text, f, max_w):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split(" "):
            trial = (cur + " " + w).strip()
            if d.textlength(trial, font=f) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur); cur = w
        lines.append(cur)
    return lines


def fit_lines(d, text, f_factory, max_w, start, min_size=42, max_lines=2, wght=600):
    size = start
    while size >= min_size:
        f = f_factory(size, wght)
        lines = wrap(d, text, f, max_w)
        if len(lines) <= max_lines and all(d.textlength(l, font=f) <= max_w for l in lines):
            return f, lines
        size -= 3
    f = f_factory(min_size, wght)
    return f, wrap(d, text, f, max_w)


# --- photo + scrim ---------------------------------------------------------
def _placeholder(w, h, seed=0):
    top = _hex(C.ACCENT_SOFT if seed % 2 else C.ACCENT)
    bot = _hex(C.COAL)
    base = Image.new("RGB", (w, h)); px = base.load()
    for y in range(h):
        t = y / h
        row = tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3))
        for x in range(w):
            px[x, y] = row
    return base.filter(ImageFilter.GaussianBlur(3))


def _cover_fit(im, w, h):
    iw, ih = im.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale + 0.5), int(ih * scale + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    return im.crop((left, top, left + w, top + h))


def _photo(photo_path, seed=0):
    W, H = C.CAROUSEL_SIZE
    if photo_path and os.path.exists(photo_path):
        try:
            return _cover_fit(Image.open(photo_path).convert("RGB"), W, H)
        except Exception:
            pass
    return _placeholder(W, H, seed)


def _scrim(img, tint=(0, 0, 0), base=70, floor=0.34, peak=232, gamma=1.35):
    """Darken the photo with a bottom-weighted gradient so text stays legible.
    `base` = constant darken over the whole frame; the gradient ramps from
    `floor` (fraction of height) to `peak` alpha at the bottom. `tint` lets the
    CTA use a cobalt wash instead of black."""
    W, H = img.size
    mask = Image.new("L", (W, H), 0)
    mpx = mask.load()
    y0 = H * floor
    for y in range(H):
        a = base
        if y > y0:
            a += int((peak - base) * (((y - y0) / (H - y0)) ** gamma))
        a = min(245, a)
        for x in range(W):
            mpx[x, y] = a
    overlay = Image.new("RGB", (W, H), tint)
    return Image.composite(overlay, img, mask)


# --- wordmark / eyebrow (on photo) -----------------------------------------
def _wordmark(d, W, y):
    d.line([(W / 2 - 60, y), (W / 2 + 60, y)], fill="#B9C0D8", width=2)
    f = disp(28, 600)
    parts = [("про", WHITE), ("Я", ACC), ("в", WHITE)]
    total = sum(d.textlength(t, font=f) for t, _ in parts)
    x = W / 2 - total / 2
    for t, col in parts:
        d.text((x, y + 24), t, font=f, fill=col); x += d.textlength(t, font=f)
    _shadow(d, W / 2, y + 72, C.TAGLINE, body(17, 600), "#C9CEDC", tr=3, anchor="ma")


def _eyebrow(d, x, y, rubric):
    d.ellipse([x, y + 5, x + 12, y + 17], fill=ACC)
    _shadow(d, x + 26, y, f"{C.RUBRIC.get(rubric, '').upper()}   ·   {C.BRAND.upper()}",
            body(19, 700), WHITE, tr=3)


# --- slides ----------------------------------------------------------------
def cover(car, out_path, photo=None):
    W, H = C.CAROUSEL_SIZE
    img = _scrim(_photo(photo, 0), base=64, floor=0.30, peak=224)
    d = ImageDraw.Draw(img)
    maxw = W - MARGIN * 2
    _eyebrow(d, MARGIN, 150, car["rubric"])
    # bottom-anchored title block
    f, lines = fit_lines(d, car["cover"], disp, maxw, start=80, min_size=52, max_lines=3, wght=600)
    sub_lines = wrap(d, car.get("cover_sub", ""), body(33, 500), maxw) if car.get("cover_sub") else []
    lh = int(f.size * 1.14)
    block_h = len(lines) * lh + (16 + 6) + (len(sub_lines) * 42 if sub_lines else 0)
    y = H - 300 - block_h
    for l in lines:
        _shadow(d, MARGIN, y, l, f, WHITE); y += lh
    y += 14
    d.rectangle([MARGIN, y, MARGIN + 90, y + 6], fill=ACC); y += 22
    for l in sub_lines:
        _shadow(d, MARGIN, y, l, body(33, 500), SOFT); y += 42
    _shadow(d, MARGIN, H - 250, C.SWIPE_CUE, body(26, 700), ACC, tr=4)
    _wordmark(d, W, H - 168)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


def content_slide(idx, total, head, text, out_path, photo=None, seed=1):
    W, H = C.CAROUSEL_SIZE
    img = _scrim(_photo(photo, seed), base=58, floor=0.30, peak=230)
    d = ImageDraw.Draw(img)
    maxw = W - MARGIN * 2
    _shadow(d, MARGIN, 148, f"{idx:02d}  /  {total:02d}", body(23, 700), ACC, tr=3)
    hf, hlines = fit_lines(d, head, disp, maxw, start=58, min_size=40, max_lines=2, wght=600)
    bf = body(34, 500)
    blines = wrap(d, text, bf, maxw)
    hlh = int(hf.size * 1.15); blh = int(bf.size * 1.4)
    block_h = len(hlines) * hlh + 20 + len(blines) * blh
    y = H - 250 - block_h
    bar_top = y + 4
    for l in hlines:
        _shadow(d, MARGIN, y, l, hf, WHITE); y += hlh
    d.rectangle([MARGIN - 34, bar_top, MARGIN - 23, y - int(hf.size * 0.34)], fill=ACC)
    y += 20
    for l in blines:
        _shadow(d, MARGIN, y, l, bf, SOFT); y += blh
    _wordmark(d, W, H - 168)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


def cta(car, out_path, photo=None):
    """Closing slide: photo under a cobalt wash so it reads as the brand close."""
    W, H = C.CAROUSEL_SIZE
    img = _scrim(_photo(photo, 9), tint=_hex(C.ACCENT_DEEP), base=150, floor=0.0, peak=232, gamma=1.0)
    d = ImageDraw.Draw(img)
    maxw = W - MARGIN * 2
    _shadow(d, W / 2, 322, "ЗБЕРЕЖИ  ·  ПОДІЛИСЯ", body(22, 700), "#D3DAFF", tr=6, anchor="ma")
    cta_lines = car["cta"].split("\n")
    size = 82
    while size >= 48:
        f = disp(size, 600)
        if all(d.textlength(l, font=f) <= maxw for l in cta_lines):
            break
        size -= 3
    y = 410
    for l in cta_lines:
        _shadow(d, W / 2, y, l, f, WHITE, anchor="ma"); y += int(f.size * 1.16)
    y += 18
    d.rectangle([W / 2 - 46, y, W / 2 + 46, y + 6], fill=WHITE); y += 42
    if car.get("cta_sub"):
        for l in wrap(d, car["cta_sub"], body(33, 500), maxw - 80):
            _shadow(d, W / 2, y, l, body(33, 500), "#D3DAFF", anchor="ma"); y += 44
    _shadow(d, W / 2, H - 300, C.HANDLE, disp(38, 600), WHITE, tr=1, anchor="ma")
    _wordmark(d, W, H - 168)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


def carousel(car, out_dir, photos=None):
    os.makedirs(out_dir, exist_ok=True)
    photos = photos or []
    paths = []
    p = os.path.join(out_dir, "00_cover.png")
    cover(car, p, photo=photos[0] if len(photos) > 0 else None); paths.append(p)
    total = len(car["slides"])
    for i, (head, text) in enumerate(car["slides"], 1):
        p = os.path.join(out_dir, f"{i:02d}_slide.png")
        ph = photos[i] if len(photos) > i else None
        content_slide(i, total, head, text, p, photo=ph, seed=i); paths.append(p)
    p = os.path.join(out_dir, "99_cta.png")
    cta(car, p, photo=photos[-1] if photos else None); paths.append(p)
    return paths
