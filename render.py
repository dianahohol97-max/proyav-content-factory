"""Renderers for проЯв carousels. Text is drawn by code — zero typos, exact
brand colours, brand fonts. Slides are 4:5 (1080×1350) for Instagram.

Layout language (per brand book): off-white paper, one cobalt accent, generous
air, Unbounded for headlines, Manrope for body, a fixed wordmark footer so the
feed reads as one system.
"""
import os
from PIL import Image, ImageDraw, ImageFont
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


def _tw(d, s, f, tr=0):
    return sum(d.textlength(c, font=f) for c in s) + tr * (len(s) - 1) if s else 0


def tracked(d, x, y, s, f, fill, tr=0, anchor="la"):
    """Letter-spaced text. anchor 'la' left, 'ma' centred on x."""
    w = _tw(d, s, f, tr)
    if anchor == "ma":
        x -= w / 2
    for c in s:
        d.text((x, y), c, font=f, fill=fill)
        x += d.textlength(c, font=f) + tr


def wrap(d, text, f, max_w):
    """Greedy word-wrap to a pixel width. Returns list of lines."""
    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for w in words:
            trial = (cur + " " + w).strip()
            if d.textlength(trial, font=f) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def fit_lines(d, text, f_factory, max_w, start, min_size=44, wght=600):
    """Shrink a headline until it fits max_w in <=2 lines. Returns (font, lines)."""
    size = start
    while size >= min_size:
        f = f_factory(size, wght)
        lines = wrap(d, text, f, max_w)
        if len(lines) <= 2 and all(d.textlength(l, font=f) <= max_w for l in lines):
            return f, lines
        size -= 3
    f = f_factory(min_size, wght)
    return f, wrap(d, text, f, max_w)


def _base():
    W, H = C.CAROUSEL_SIZE
    img = Image.new("RGB", (W, H), C.BG)
    return img, ImageDraw.Draw(img), W, H


def _wordmark(d, W, y):
    """проЯв wordmark with cobalt Я, centred, + tagline under a hairline."""
    d.line([(W / 2 - 60, y), (W / 2 + 60, y)], fill=C.HAIR, width=2)
    f = disp(30, 600)
    parts = [("про", C.INK), ("Я", C.ACCENT), ("в", C.INK)]
    total = sum(d.textlength(t, font=f) for t, _ in parts)
    x = W / 2 - total / 2
    yb = y + 26
    for t, col in parts:
        d.text((x, yb), t, font=f, fill=col)
        x += d.textlength(t, font=f)
    tracked(d, W / 2, y + 78, C.TAGLINE, body(18, 600), C.MUTED, tr=3, anchor="ma")


def _eyebrow(d, x, y, rubric):
    """Cobalt dot + tracked rubric label + brand."""
    d.ellipse([x, y + 6, x + 13, y + 19], fill=C.ACCENT)
    tracked(d, x + 28, y, f"{C.RUBRIC.get(rubric, '').upper()}   ·   {C.BRAND.upper()}",
            body(20, 700), C.MUTED, tr=3)


def cover(car, out_path):
    img, d, W, H = _base()
    _eyebrow(d, MARGIN, 150, car["rubric"])
    # big hook headline, up to 3 lines, left-aligned
    maxw = W - MARGIN * 2
    f, lines = fit_lines(d, car["cover"], disp, maxw, start=96, min_size=56, wght=600)
    # allow 3 lines for the cover specifically
    f2 = f
    lines = wrap(d, car["cover"], f2, maxw)
    while len(lines) > 3 and f2.size > 52:
        f2 = disp(f2.size - 3, 600)
        lines = wrap(d, car["cover"], f2, maxw)
    y = 300
    lh = int(f2.size * 1.14)
    for l in lines:
        d.text((MARGIN, y), l, font=f2, fill=C.INK)
        y += lh
    # cobalt short rule
    y += 14
    d.rectangle([MARGIN, y, MARGIN + 96, y + 6], fill=C.ACCENT)
    # subtitle
    if car.get("cover_sub"):
        y += 40
        sub_f = body(36, 500)
        for l in wrap(d, car["cover_sub"], sub_f, maxw):
            d.text((MARGIN, y), l, font=sub_f, fill=C.MUTED)
            y += int(sub_f.size * 1.3)
    # swipe cue bottom-left
    tracked(d, MARGIN, H - 300, C.SWIPE_CUE, body(28, 600), C.ACCENT, tr=4)
    _wordmark(d, W, H - 200)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


def content_slide(idx, total, head, text, out_path):
    img, d, W, H = _base()
    maxw = W - MARGIN * 2
    # index
    tracked(d, MARGIN, 150, f"{idx:02d}  /  {total:02d}", body(24, 700), C.ACCENT, tr=3)
    # cobalt accent bar left of headline
    hf, hlines = fit_lines(d, head, disp, maxw - 8, start=68, min_size=44, wght=600)
    y = 250
    bar_top = y + 6
    for l in hlines:
        d.text((MARGIN, y), l, font=hf, fill=C.INK)
        y += int(hf.size * 1.16)
    d.rectangle([MARGIN - 34, bar_top, MARGIN - 22, y - int(hf.size * 0.32)], fill=C.ACCENT)
    # body text
    y += 26
    bf = body(37, 500)
    for l in wrap(d, text, bf, maxw):
        d.text((MARGIN, y), l, font=bf, fill=C.INK)
        y += int(bf.size * 1.42)
    _wordmark(d, W, H - 200)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


def cta(car, out_path):
    img, d, W, H = _base()
    maxw = W - MARGIN * 2
    tracked(d, W / 2, 300, "ЗБЕРЕЖИ  ·  ПОДІЛИСЯ", body(22, 700), C.MUTED, tr=6, anchor="ma")
    f, _ = fit_lines(d, car["cta"].replace("\n", " "), disp, maxw, start=86, min_size=56)
    y = 400
    for l in car["cta"].split("\n"):
        d.text((W / 2, y), l, font=f, fill=C.INK, anchor="ma")
        y += int(f.size * 1.16)
    y += 20
    d.rectangle([W / 2 - 48, y, W / 2 + 48, y + 6], fill=C.ACCENT)
    if car.get("cta_sub"):
        y += 44
        sf = body(34, 500)
        for l in wrap(d, car["cta_sub"], sf, maxw - 80):
            tracked(d, W / 2, y, l, sf, C.MUTED, anchor="ma")
            y += int(sf.size * 1.34)
    tracked(d, W / 2, H - 320, C.HANDLE, disp(40, 600), C.ACCENT, tr=1, anchor="ma")
    _wordmark(d, W, H - 200)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


def carousel(car, out_dir):
    """Render a full carousel (cover + content slides + CTA). Returns ordered paths."""
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    p = os.path.join(out_dir, "00_cover.png"); cover(car, p); paths.append(p)
    total = len(car["slides"])
    for i, (head, text) in enumerate(car["slides"], 1):
        p = os.path.join(out_dir, f"{i:02d}_slide.png")
        content_slide(i, total, head, text, p); paths.append(p)
    p = os.path.join(out_dir, "99_cta.png"); cta(car, p); paths.append(p)
    return paths
