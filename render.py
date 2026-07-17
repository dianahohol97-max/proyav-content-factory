"""Renderers for проЯв carousels. Photo + code-drawn text — zero typos, exact
brand colours, brand fonts. Slides are 4:5 (1080×1350) for Instagram.

Layout language (per brand book): a full-bleed photo panel on top, a cream text
zone below, one cobalt accent, a fixed wordmark footer. The CTA slide is solid
cobalt for a strong close. Real photos live in input/photos/ (drop live shots or
generated images there); if the pool is empty, a branded gradient stands in.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import config as C

MARGIN = 96


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


def tracked(d, x, y, s, f, fill, tr=0, anchor="la"):
    w = _tw(d, s, f, tr)
    if anchor == "ma":
        x -= w / 2
    for c in s:
        d.text((x, y), c, font=f, fill=fill)
        x += d.textlength(c, font=f) + tr


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


def fit_lines(d, text, f_factory, max_w, start, min_size=44, max_lines=2, wght=600):
    size = start
    while size >= min_size:
        f = f_factory(size, wght)
        lines = wrap(d, text, f, max_w)
        if len(lines) <= max_lines and all(d.textlength(l, font=f) <= max_w for l in lines):
            return f, lines
        size -= 3
    f = f_factory(min_size, wght)
    return f, wrap(d, text, f, max_w)


# --- photo panel -----------------------------------------------------------
def _placeholder(w, h, seed=0):
    """Branded gradient stand-in when no photo is supplied."""
    top = _hex(C.ACCENT_SOFT if seed % 2 else C.ACCENT)
    bot = _hex(C.COAL)
    base = Image.new("RGB", (w, h))
    px = base.load()
    for y in range(h):
        t = y / h
        px_row = tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3))
        for x in range(w):
            px[x, y] = px_row
    try:
        noise = Image.effect_noise((w, h), 22).convert("L")
        base = Image.composite(base, Image.new("RGB", (w, h), bot),
                               noise.point(lambda v: 90 + v // 3))
    except Exception:
        pass
    return base.filter(ImageFilter.GaussianBlur(2))


def _cover_fit(im, w, h):
    """Center-crop a photo to exactly fill w×h."""
    iw, ih = im.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale + 0.5), int(ih * scale + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    return im.crop((left, top, left + w, top + h))


def _photo_panel(img, box, photo_path, seed=0):
    """Paste a photo (or placeholder) into box=(x,y,w,h); cobalt seam at bottom."""
    x, y, w, h = box
    if photo_path and os.path.exists(photo_path):
        try:
            ph = _cover_fit(Image.open(photo_path).convert("RGB"), w, h)
        except Exception:
            ph = _placeholder(w, h, seed)
    else:
        ph = _placeholder(w, h, seed)
    img.paste(ph, (x, y))
    d = ImageDraw.Draw(img)
    d.rectangle([x, y + h - 5, x + w, y + h], fill=C.ACCENT)   # cobalt seam


def _base():
    W, H = C.CAROUSEL_SIZE
    img = Image.new("RGB", (W, H), C.BG)
    return img, ImageDraw.Draw(img), W, H


def _wordmark(d, W, y, ink=None, muted=None):
    ink = ink or C.INK
    muted = muted or C.MUTED
    d.line([(W / 2 - 60, y), (W / 2 + 60, y)], fill=(muted if muted != C.MUTED else C.HAIR), width=2)
    f = disp(28, 600)
    parts = [("про", ink), ("Я", C.ACCENT if ink == C.INK else ink), ("в", ink)]
    total = sum(d.textlength(t, font=f) for t, _ in parts)
    x = W / 2 - total / 2
    for t, col in parts:
        d.text((x, y + 24), t, font=f, fill=col)
        x += d.textlength(t, font=f)
    tracked(d, W / 2, y + 72, C.TAGLINE, body(17, 600), muted, tr=3, anchor="ma")


def _eyebrow(d, x, y, rubric, fill=None):
    d.ellipse([x, y + 5, x + 12, y + 17], fill=C.ACCENT)
    tracked(d, x + 26, y, f"{C.RUBRIC.get(rubric, '').upper()}   ·   {C.BRAND.upper()}",
            body(19, 700), fill or C.MUTED, tr=3)


# --- slides ----------------------------------------------------------------
def cover(car, out_path, photo=None):
    img, d, W, H = _base()
    PH = 700
    _photo_panel(img, (0, 0, W, PH), photo, seed=0)
    d = ImageDraw.Draw(img)
    maxw = W - MARGIN * 2
    _eyebrow(d, MARGIN, PH + 50, car["rubric"])
    f, lines = fit_lines(d, car["cover"], disp, maxw, start=64, min_size=42, max_lines=2, wght=600)
    y = PH + 92
    for l in lines:
        d.text((MARGIN, y), l, font=f, fill=C.INK); y += int(f.size * 1.16)
    y += 8
    d.rectangle([MARGIN, y, MARGIN + 90, y + 6], fill=C.ACCENT)
    if car.get("cover_sub"):
        y += 32
        sf = body(32, 500)
        for l in wrap(d, car["cover_sub"], sf, maxw):
            d.text((MARGIN, y), l, font=sf, fill=C.MUTED); y += int(sf.size * 1.28)
    tracked(d, MARGIN, H - 238, C.SWIPE_CUE, body(26, 700), C.ACCENT, tr=4)
    _wordmark(d, W, H - 168)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


def content_slide(idx, total, head, text, out_path, photo=None, seed=1):
    img, d, W, H = _base()
    PH = 600
    _photo_panel(img, (0, 0, W, PH), photo, seed=seed)
    d = ImageDraw.Draw(img)
    maxw = W - MARGIN * 2
    tracked(d, MARGIN, PH + 52, f"{idx:02d}  /  {total:02d}", body(23, 700), C.ACCENT, tr=3)
    hf, hlines = fit_lines(d, head, disp, maxw, start=58, min_size=40, max_lines=2, wght=600)
    y = PH + 98
    bar_top = y + 4
    for l in hlines:
        d.text((MARGIN, y), l, font=hf, fill=C.INK); y += int(hf.size * 1.15)
    d.rectangle([MARGIN - 34, bar_top, MARGIN - 23, y - int(hf.size * 0.34)], fill=C.ACCENT)
    y += 18
    bf = body(34, 500)
    for l in wrap(d, text, bf, maxw):
        d.text((MARGIN, y), l, font=bf, fill=C.INK); y += int(bf.size * 1.4)
    _wordmark(d, W, H - 168)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


def cta(car, out_path):
    """Solid cobalt closing slide — the one bold moment."""
    W, H = C.CAROUSEL_SIZE
    img = Image.new("RGB", (W, H), C.ACCENT)
    d = ImageDraw.Draw(img)
    white = "#FFFFFF"
    soft = "#C9D3FF"
    maxw = W - MARGIN * 2
    tracked(d, W / 2, 300, "ЗБЕРЕЖИ  ·  ПОДІЛИСЯ", body(22, 700), soft, tr=6, anchor="ma")
    cta_lines = car["cta"].split("\n")
    size = 82
    while size >= 48:
        f = disp(size, 600)
        if all(d.textlength(l, font=f) <= maxw for l in cta_lines):
            break
        size -= 3
    y = 392
    for l in cta_lines:
        d.text((W / 2, y), l, font=f, fill=white, anchor="ma"); y += int(f.size * 1.16)
    y += 18
    d.rectangle([W / 2 - 46, y, W / 2 + 46, y + 6], fill=white)
    if car.get("cta_sub"):
        y += 42
        sf = body(33, 500)
        for l in wrap(d, car["cta_sub"], sf, maxw - 80):
            tracked(d, W / 2, y, l, sf, soft, anchor="ma"); y += int(sf.size * 1.32)
    tracked(d, W / 2, H - 300, C.HANDLE, disp(38, 600), white, tr=1, anchor="ma")
    # white wordmark
    d.line([(W / 2 - 60, H - 168), (W / 2 + 60, H - 168)], fill=soft, width=2)
    wf = disp(28, 600)
    wm = "проЯв"
    tw = sum(d.textlength(c, font=wf) for c in wm)
    d.text((W / 2 - tw / 2, H - 144), wm, font=wf, fill=white)
    tracked(d, W / 2, H - 96, C.TAGLINE, body(17, 600), soft, tr=3, anchor="ma")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


def carousel(car, out_dir, photos=None):
    """Render a full carousel. `photos` = ordered paths: [cover, slide1, slide2, …].
    Missing entries fall back to a branded gradient."""
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
    cta(car, p); paths.append(p)
    return paths
