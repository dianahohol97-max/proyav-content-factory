"""Editorial renderers for проЯв carousels. Monochrome photography + one cobalt
accent + generous negative space, in the проЯв brand (Unbounded headlines,
Manrope labels/body, cream & coal grounds). Text is drawn by code — zero typos,
exact brand colours. Slides are 4:5 (1080×1350) for Instagram.

Design language (from the reference moodboards, mapped to the brand):
- photos are black & white so the cobalt is the only colour that pops;
- small tracked labels sit in the corners (brand · rubric · index · swipe);
- sticker pills carry the kicker; headlines can accent a *word* in cobalt;
- content alternates full-bleed photo slides with airy paper slides.
Real photos live in input/photos/ (live or generated); an empty pool falls back
to a branded gradient.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import config as C

MARGIN = 84
W, H = C.CAROUSEL_SIZE

PAPER = "#F4F4F1"
COAL = "#12110E"
INK = "#0D0C0A"
MUT_L = "#6F6D66"        # muted on paper
MUT_D = "#9C978C"        # muted on coal / photo
ACC = "#2F55FF"          # cobalt on paper
ACC_D = "#6E8BFF"        # brighter cobalt on dark
WHITE = "#FFFFFF"
SOFT = "#E8E5DE"


def _f(path, size, wght):
    f = ImageFont.truetype(path, size)
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f


def disp(size, wght=600):
    return _f(C.DISPLAY, size, wght)


def body(size, wght=500):
    return _f(C.BODY, size, wght)


def _tw(d, s, f, tr=0):
    return sum(d.textlength(c, font=f) for c in s) + tr * (len(s) - 1) if s else 0


def tracked(d, x, y, s, f, fill, tr=0, anchor="la", shadow=None):
    w = _tw(d, s, f, tr)
    if anchor == "ma":
        x -= w / 2
    elif anchor == "ra":
        x -= w
    if shadow:
        xx = x
        for c in s:
            d.text((xx + 2, y + 2), c, font=f, fill=shadow); xx += d.textlength(c, font=f) + tr
    xx = x
    for c in s:
        d.text((xx, y), c, font=f, fill=fill); xx += d.textlength(c, font=f) + tr


# --- accented headline (words wrapped inside *…* render in cobalt) ----------
def _tokens(text):
    out, acc, cur = [], False, ""
    for ch in text:
        if ch == "*":
            acc = not acc
        elif ch == " ":
            if cur:
                out.append((cur, acc)); cur = ""
        else:
            cur += ch
    if cur:
        out.append((cur, acc))
    return out


def _wrap_tokens(d, toks, f, maxw):
    lines, cur = [], []
    sp = d.textlength(" ", font=f)
    wcur = 0
    for word, a in toks:
        ww = d.textlength(word, font=f)
        add = ww + (sp if cur else 0)
        if cur and wcur + add > maxw:
            lines.append(cur); cur = [(word, a)]; wcur = ww
        else:
            cur.append((word, a)); wcur += add
    if cur:
        lines.append(cur)
    return lines


def _fit_tokens(d, toks, maxw, start, min_size, max_lines, wght=600):
    size = start
    while size >= min_size:
        f = disp(size, wght)
        lines = _wrap_tokens(d, toks, f, maxw)
        if len(lines) <= max_lines and all(
                sum(d.textlength(w, font=f) for w, _ in ln) +
                d.textlength(" ", font=f) * (len(ln) - 1) <= maxw for ln in lines):
            return f, lines
        size -= 3
    f = disp(min_size, wght)
    return f, _wrap_tokens(d, toks, f, maxw)


def _draw_tokens(d, x, y, lines, f, base, accent, lh, shadow=None):
    sp = d.textlength(" ", font=f)
    for ln in lines:
        xx = x
        for word, a in ln:
            col = accent if a else base
            if shadow:
                d.text((xx + 2, y + 3), word, font=f, fill=shadow)
            d.text((xx, y), word, font=f, fill=col)
            xx += d.textlength(word, font=f) + sp
        y += lh
    return y


def wrap(d, text, f, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split(" "):
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= maxw or not cur:
                cur = t
            else:
                lines.append(cur); cur = w
        lines.append(cur)
    return lines


# --- photo helpers ---------------------------------------------------------
def _hex(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _placeholder(w, h, seed):
    """Moody photographic stand-in (tone + grain + vignette) until real photos
    land in input/photos/. Never meant to ship — just to read like a photo."""
    tones = [("#6E6A62", "#171410"), ("#7C8790", "#14181B"),
             ("#8A7F72", "#1A1512"), ("#585C5A", "#0E0F0D")]
    a, b = tones[seed % len(tones)]
    a, b = _hex(a), _hex(b)
    im = Image.new("RGB", (w, h)); px = im.load()
    for y in range(h):
        t = (y / h) ** 1.3
        row = tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))
        for x in range(w):
            fx = 1 - 0.22 * (abs(x - w * 0.42) / w)   # soft directional light
            px[x, y] = tuple(min(255, int(c * fx)) for c in row)
    try:
        grain = Image.effect_noise((w, h), 26).convert("L")
        im = Image.composite(im, Image.new("RGB", (w, h), b),
                             grain.point(lambda v: 150 + v // 4))
    except Exception:
        pass
    im = im.filter(ImageFilter.GaussianBlur(1.4))
    # vignette
    vg = Image.new("L", (w, h), 0); dv = ImageDraw.Draw(vg)
    dv.ellipse([-w * 0.25, -h * 0.22, w * 1.25, h * 1.22], fill=255)
    vg = vg.filter(ImageFilter.GaussianBlur(int(min(w, h) * 0.22)))
    return Image.composite(im, Image.new("RGB", (w, h), (8, 7, 6)), vg)


def _photo(path, w, h, seed=0, mono=False):
    if path and os.path.exists(path):
        try:
            im = Image.open(path).convert("RGB")
            iw, ih = im.size; s = max(w / iw, h / ih)
            im = im.resize((int(iw * s + .5), int(ih * s + .5)), Image.LANCZOS)
            l = (im.size[0] - w) // 2; t = (im.size[1] - h) // 2
            im = im.crop((l, t, l + w, t + h))
        except Exception:
            im = _placeholder(w, h, seed)
    else:
        im = _placeholder(w, h, seed)
    if mono:
        im = ImageOps.grayscale(im)
        im = ImageOps.autocontrast(im, cutoff=1).convert("RGB")
    return im


def _scrim(img, base=60, floor=0.34, peak=228, gamma=1.35, tint=(0, 0, 0)):
    w, h = img.size; mask = Image.new("L", (w, h)); mpx = mask.load(); y0 = h * floor
    for y in range(h):
        a = base + (int((peak - base) * (((y - y0) / (h - y0)) ** gamma)) if y > y0 else 0)
        a = min(245, a)
        for x in range(w):
            mpx[x, y] = a
    return Image.composite(Image.new("RGB", (w, h), tint), img, mask)


def _frame(d, box, col=ACC, tick=26, wdt=4):
    """Editorial corner ticks around a photo inset."""
    x0, y0, x1, y1 = box
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([(cx, cy), (cx + sx * tick, cy)], fill=col, width=wdt)
        d.line([(cx, cy), (cx, cy + sy * tick)], fill=col, width=wdt)


def _pill(d, x, y, text, f, fill, tc, padx=20, pady=11, tr=2):
    tw = _tw(d, text, f, tr); h = f.size + pady * 2
    d.rounded_rectangle([x, y, x + tw + padx * 2, y + h], radius=(h // 2), fill=fill)
    tracked(d, x + padx, y + pady - 2, text, f, tc, tr=tr)
    return x + tw + padx * 2, y + h


# --- corner metadata -------------------------------------------------------
def _meta(d, rubric, index_txt, cue, dark):
    ink = PAPER if dark else INK
    mut = MUT_D if dark else MUT_L
    acc = ACC_D if dark else ACC
    # top-left wordmark
    wf = disp(24, 600)
    x = MARGIN
    for t, col in (("про", ink), ("Я", acc), ("в", ink)):
        d.text((x, 74), t, font=wf, fill=col); x += d.textlength(t, font=wf)
    # top-right rubric + line
    tracked(d, W - MARGIN, 76, C.RUBRIC.get(rubric, "").upper(), body(18, 700), acc, tr=3, anchor="ra")
    tracked(d, W - MARGIN, 102, "УКРАЇНСЬКА ГАЛЕРЕЯ", body(15, 600), mut, tr=3, anchor="ra")
    # bottom-left index
    if index_txt:
        tracked(d, MARGIN, H - 96, index_txt, body(18, 700), acc, tr=3)
    # bottom-right cue
    if cue:
        tracked(d, W - MARGIN, H - 96, cue, body(18, 700), mut, tr=3, anchor="ra")


# --- slides ----------------------------------------------------------------
def cover(car, out_path, photo=None, mono=False):
    img = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(img)
    maxw = W - MARGIN * 2
    # headline (accent words in cobalt)
    toks = _tokens(car["cover"])
    f, lines = _fit_tokens(d, toks, maxw, start=92, min_size=54, max_lines=4)
    lh = int(f.size * 1.08)
    y = 250
    y = _draw_tokens(d, MARGIN, y, lines, f, INK, ACC, lh)
    y += 6
    d.rectangle([MARGIN, y, MARGIN + 96, y + 7], fill=ACC)
    # subtitle
    if car.get("cover_sub"):
        y += 34
        for l in wrap(d, car["cover_sub"], body(31, 500), maxw - 360):
            d.text((MARGIN, y), l, font=body(31, 500), fill=MUT_L); y += 42
    # B&W photo inset, bottom-right
    pw, ph = 400, 500
    px0, py0 = W - MARGIN - pw, H - 150 - ph
    img.paste(_photo(photo, pw, ph, 0, mono), (px0, py0))
    _frame(d, (px0 - 10, py0 - 10, px0 + pw + 10, py0 + ph + 10))
    _meta(d, car["rubric"], "МІНІ-ГАЙД", C.SWIPE_CUE, dark=False)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG"); return out_path


def slide_photo(idx, total, head, text, out_path, kick, photo=None, seed=1, mono=False):
    img = _scrim(_photo(photo, W, H, seed, mono), base=58, floor=0.30, peak=232)
    d = ImageDraw.Draw(img)
    maxw = W - MARGIN * 2
    label = f"{kick} {idx:02d}" if kick else f"{idx:02d} / {total:02d}"
    _pill(d, MARGIN, 150, label, body(19, 700), ACC, WHITE)
    hf, hlines = _fit_tokens(d, _tokens(head), maxw, start=62, min_size=42, max_lines=2)
    bf = body(34, 500); blines = wrap(d, text, bf, maxw)
    hlh = int(hf.size * 1.1); blh = int(bf.size * 1.4)
    block = len(hlines) * hlh + 22 + len(blines) * blh
    y = H - 250 - block
    bar_top = y + 4
    y = _draw_tokens(d, MARGIN, y, hlines, hf, WHITE, ACC_D, hlh, shadow=(0, 0, 0))
    d.rectangle([MARGIN - 30, bar_top, MARGIN - 20, y - int(hf.size * 0.5)], fill=ACC)
    y += 20
    for l in blines:
        tracked(d, MARGIN, y, l, bf, SOFT, shadow=(0, 0, 0)); y += blh
    _meta(d, "", f"{idx:02d} — {total:02d}", C.SWIPE_CUE, dark=True)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG"); return out_path


def slide_paper(idx, total, head, text, out_path, kick, photo=None, seed=1, mono=False):
    img = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(img)
    maxw = W - MARGIN * 2
    label = f"{kick} {idx:02d}" if kick else f"{idx:02d} / {total:02d}"
    _pill(d, MARGIN, 150, label, body(19, 700), INK, PAPER)
    # headline
    hf, hlines = _fit_tokens(d, _tokens(head), maxw, start=60, min_size=40, max_lines=2)
    y = 250
    hlh = int(hf.size * 1.1)
    y = _draw_tokens(d, MARGIN, y, hlines, hf, INK, ACC, hlh)
    d.rectangle([MARGIN, y + 10, MARGIN + 70, y + 16], fill=ACC)
    y += 46
    bf = body(34, 500)
    for l in wrap(d, text, bf, maxw - 40):
        d.text((MARGIN, y), l, font=bf, fill=MUT_L); y += int(bf.size * 1.42)
    # B&W photo band bottom
    pw, ph = maxw, 380
    px0, py0 = MARGIN, H - 170 - ph
    img.paste(_photo(photo, pw, ph, seed, mono), (px0, py0))
    _frame(d, (px0 - 10, py0 - 10, px0 + pw + 10, py0 + ph + 10))
    _meta(d, "", f"{idx:02d} — {total:02d}", C.SWIPE_CUE, dark=False)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG"); return out_path


def cta(car, out_path, photo=None):
    img = Image.new("RGB", (W, H), COAL); d = ImageDraw.Draw(img)
    maxw = W - MARGIN * 2
    _pill(d, MARGIN, 250, "СПРОБУЙ БЕЗКОШТОВНО", body(20, 700), ACC, WHITE)
    cta_lines = car["cta"].split("\n")
    size = 86
    while size >= 48:
        f = disp(size, 600)
        if all(d.textlength(l, font=f) <= maxw for l in cta_lines):
            break
        size -= 3
    y = 380
    for l in cta_lines:
        d.text((MARGIN, y), l, font=f, fill=PAPER); y += int(f.size * 1.12)
    y += 14
    d.rectangle([MARGIN, y, MARGIN + 96, y + 7], fill=ACC); y += 36
    if car.get("cta_sub"):
        for l in wrap(d, car["cta_sub"], body(32, 500), maxw - 200):
            d.text((MARGIN, y), l, font=body(32, 500), fill=MUT_D); y += 44
    tracked(d, MARGIN, H - 330, C.HANDLE, disp(46, 600), ACC_D, tr=1)
    _meta(d, car["rubric"], "", "проЯв.space", dark=True)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG"); return out_path


# --- extra templates (library for varied layouts) --------------------------
def slide_quote(idx, total, head, text, out_path, kick, photo=None, seed=1, mono=False):
    """Coal slide, oversized quote in «» — a scroll-stopping statement."""
    img = Image.new("RGB", (W, H), COAL); d = ImageDraw.Draw(img)
    maxw = W - MARGIN * 2
    _pill(d, MARGIN, 150, f"{kick} {idx:02d}" if kick else f"{idx:02d} / {total:02d}",
          body(19, 700), ACC, WHITE)
    f, lines = _fit_tokens(d, _tokens("«" + head + "»"), maxw, start=98, min_size=50, max_lines=4)
    lh = int(f.size * 1.05)
    y = (H - len(lines) * lh) // 2 - 40
    y = _draw_tokens(d, MARGIN, y, lines, f, WHITE, ACC_D, lh)
    if text:
        y += 26
        for l in wrap(d, text, body(30, 500), maxw - 140):
            d.text((MARGIN, y), l, font=body(30, 500), fill=MUT_D); y += 42
    _meta(d, "", f"{idx:02d} — {total:02d}", C.SWIPE_CUE, dark=True)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG"); return out_path


def slide_uicard(idx, total, head, text, out_path, kick, photo=None, seed=1, mono=False):
    """Paper slide with a headline, a centred framed image (screenshot/graphic),
    and a caption — perfect for UI shots that must match the text."""
    img = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(img)
    maxw = W - MARGIN * 2
    _pill(d, MARGIN, 150, f"{kick} {idx:02d}" if kick else f"{idx:02d} / {total:02d}",
          body(19, 700), INK, PAPER)
    hf, hlines = _fit_tokens(d, _tokens(head), maxw, start=56, min_size=38, max_lines=2)
    y = 232; hlh = int(hf.size * 1.08)
    y = _draw_tokens(d, MARGIN, y, hlines, hf, INK, ACC, hlh)
    y += 22
    pw, ph = maxw, 496
    img.paste(_photo(photo, pw, ph, seed, mono), (MARGIN, y))
    _frame(d, (MARGIN - 10, y - 10, MARGIN + pw + 10, y + ph + 10))
    y2 = y + ph + 32
    if text:
        for l in wrap(d, text, body(30, 500), maxw):
            d.text((MARGIN, y2), l, font=body(30, 500), fill=MUT_L); y2 += 42
    _meta(d, "", f"{idx:02d} — {total:02d}", C.SWIPE_CUE, dark=False)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG"); return out_path


def slide_bigword(idx, total, head, text, out_path, kick, photo=None, seed=1, mono=False):
    """One giant word bleeding off the edge + a small caption (volume-one move)."""
    dark = (seed % 2 == 0)
    img = Image.new("RGB", (W, H), COAL if dark else PAPER); d = ImageDraw.Draw(img)
    ink = WHITE if dark else INK
    maxw = W - MARGIN * 2
    word = (head.split()[0] if head else "").upper()
    f0 = disp(100, 700); w0 = d.textlength(word, font=f0) or 1
    size = min(430, max(150, int(100 * (1.16 * W) / w0)))
    d.text((MARGIN - int(size * 0.04), int(H * 0.33)), word, font=disp(size, 700), fill=ink)
    _pill(d, MARGIN, 150, f"{kick} {idx:02d}" if kick else f"{idx:02d} / {total:02d}",
          body(19, 700), ACC if dark else INK, WHITE if dark else PAPER)
    y = H - 250 - 0
    cap = text or head
    for l in wrap(d, cap, body(33, 500), maxw - 40):
        d.text((MARGIN, y), l, font=body(33, 500), fill=(SOFT if dark else MUT_L)); y += 46
    _meta(d, "", f"{idx:02d} — {total:02d}", C.SWIPE_CUE, dark=dark)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG"); return out_path


TEMPLATES = {
    "photo": slide_photo,     # full-bleed image + overlaid headline
    "paper": slide_paper,     # airy cream slide + image band
    "quote": slide_quote,     # oversized «quote» on coal
    "uicard": slide_uicard,   # centred screenshot/graphic + caption
    "bigword": slide_bigword, # giant word bleeding off the edge
}


def _slide_fields(item):
    if isinstance(item, dict):
        return item.get("head", ""), item.get("body", ""), item.get("tpl")
    return item[0], item[1], None


def carousel(car, out_dir, photos=None, cta_photo=None):
    os.makedirs(out_dir, exist_ok=True)
    photos = photos or []
    kick = car.get("kick")
    mono = car.get("mono", getattr(C, "MONO_PHOTOS", False))
    paths = []
    p = os.path.join(out_dir, "00_cover.png")
    cover(car, p, photo=photos[0] if photos else None, mono=mono); paths.append(p)
    total = len(car["slides"])
    for i, item in enumerate(car["slides"], 1):
        head, text, tpl = _slide_fields(item)
        ph = photos[i] if len(photos) > i else None
        p = os.path.join(out_dir, f"{i:02d}_slide.png")
        fn = TEMPLATES.get(tpl) or (slide_photo if i % 2 == 1 else slide_paper)
        fn(i, total, head, text, p, kick, photo=ph, seed=i, mono=mono)
        paths.append(p)
    p = os.path.join(out_dir, "99_cta.png")
    cta(car, p, photo=cta_photo); paths.append(p)
    return paths
