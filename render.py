"""Editorial renderers for проЯв carousels — moodboard aesthetic, brand DNA kept.

Type: Playfair Display for headlines (with *italic* accent words) — the editorial
elegance from the references; Manrope for body and tracked small-caps labels;
Unbounded reserved for the проЯв wordmark (brand anchor). Palette stays neutral
(cream & coal); cobalt appears sparingly — the wordmark Я, the index, one CTA
button. Photos can be colour or black-&-white. Slides are 4:5 (1080×1350).
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import config as C

MARGIN = 88
W, H = C.CAROUSEL_SIZE

PAPER = "#F4F4F1"
COAL = "#14130F"
INK = "#111014"
MUT_L = "#6F6D66"
MUT_D = "#A9A49A"
HAIR_L = "#D9D6CE"
HAIR_D = "#3A382F"
ACC = "#2F55FF"
ACC_D = "#7C93FF"
WHITE = "#FBFAF7"
SOFT = "#E7E3DB"


def _f(path, size, wght):
    f = ImageFont.truetype(path, size)
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f


def serif(size, wght=560):
    return _f(C.SERIF, size, wght)


def serif_it(size, wght=560):
    return _f(C.SERIF_IT, size, wght)


def body(size, wght=500):
    return _f(C.BODY, size, wght)


def wm_font(size, wght=600):
    return _f(C.WORDMARK, size, wght)


def _hex(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _tw(d, s, f, tr=0):
    return sum(d.textlength(c, font=f) for c in s) + tr * (len(s) - 1) if s else 0


def tracked(d, x, y, s, f, fill, tr=0, anchor="la", shadow=None):
    s = s
    w = _tw(d, s, f, tr)
    if anchor == "ma":
        x -= w / 2
    elif anchor == "ra":
        x -= w
    if shadow:
        xx = x
        for c in s:
            d.text((xx + 1.5, y + 1.5), c, font=f, fill=shadow); xx += d.textlength(c, font=f) + tr
    xx = x
    for c in s:
        d.text((xx, y), c, font=f, fill=fill); xx += d.textlength(c, font=f) + tr


# --- accented serif headline (words in *…* become italic) ------------------
def _tokens(text):
    out, acc, cur = [], False, ""
    for ch in text:
        if ch == "*":
            if cur:
                out.append((cur, acc)); cur = ""
            acc = not acc
        elif ch == " ":
            if cur:
                out.append((cur, acc)); cur = ""
        else:
            cur += ch
    if cur:
        out.append((cur, acc))
    return out


def _fw(size):
    return serif(size), serif_it(size)


def _wrap_tokens(d, toks, size, maxw):
    rf, itf = _fw(size)
    sp = d.textlength(" ", font=rf)
    lines, cur, wcur = [], [], 0
    for word, a in toks:
        f = itf if a else rf
        ww = d.textlength(word, font=f)
        add = ww + (sp if cur else 0)
        if cur and wcur + add > maxw:
            lines.append(cur); cur = [(word, a)]; wcur = ww
        else:
            cur.append((word, a)); wcur += add
    if cur:
        lines.append(cur)
    return lines


def _fit_tokens(d, toks, maxw, start, min_size, max_lines):
    size = start
    while size >= min_size:
        lines = _wrap_tokens(d, toks, size, maxw)
        rf, itf = _fw(size); sp = d.textlength(" ", font=rf)
        ok = all(sum(d.textlength(w, font=(itf if a else rf)) for w, a in ln) +
                 sp * (len(ln) - 1) <= maxw for ln in lines)
        if len(lines) <= max_lines and ok:
            return size, lines
        size -= 3
    return min_size, _wrap_tokens(d, toks, min_size, maxw)


def _draw_tokens(d, x, y, lines, size, base, lh, shadow=None):
    rf, itf = _fw(size); sp = d.textlength(" ", font=rf)
    for ln in lines:
        xx = x
        for word, a in ln:
            f = itf if a else rf
            if shadow:
                d.text((xx + 1.5, y + 2), word, font=f, fill=shadow)
            d.text((xx, y), word, font=f, fill=base)
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


# --- photo -----------------------------------------------------------------
def _placeholder(w, h, seed):
    tones = [("#B9B2A6", "#4B463D"), ("#A7ADB0", "#3C4044"), ("#C3B4A6", "#5A4B41")]
    a, b = tones[seed % len(tones)]
    a, b = _hex(a), _hex(b)
    im = Image.new("RGB", (w, h)); px = im.load()
    for y in range(h):
        t = (y / h) ** 1.2
        row = tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))
        for x in range(w):
            px[x, y] = row
    try:
        im = Image.composite(im, Image.new("RGB", (w, h), b),
                             Image.effect_noise((w, h), 14).point(lambda v: 150 + v // 5))
    except Exception:
        pass
    return im.filter(ImageFilter.GaussianBlur(4))


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
        im = ImageOps.autocontrast(ImageOps.grayscale(im), cutoff=1).convert("RGB")
    return im


def _scrim(img, base=48, floor=0.40, peak=214, gamma=1.5):
    w, h = img.size; mask = Image.new("L", (w, h)); mpx = mask.load(); y0 = h * floor
    for y in range(h):
        a = base + (int((peak - base) * (((y - y0) / (h - y0)) ** gamma)) if y > y0 else 0)
        for x in range(w):
            mpx[x, y] = min(240, a)
    return Image.composite(Image.new("RGB", (w, h), (10, 9, 7)), img, mask)


def _inset(img, box, photo, seed, mono, hair):
    x0, y0, x1, y1 = box
    img.paste(_photo(photo, x1 - x0, y1 - y0, seed, mono), (x0, y0))
    ImageDraw.Draw(img).rectangle([x0, y0, x1 - 1, y1 - 1], outline=hair, width=2)


# --- shared chrome ---------------------------------------------------------
def _wordmark_corner(d, dark):
    ink = WHITE if dark else INK
    x = MARGIN
    f = wm_font(23, 600)
    for t, col in (("про", ink), ("Я", ACC_D if dark else ACC), ("в", ink)):
        d.text((x, 70), t, font=f, fill=col); x += d.textlength(t, font=f)


def _label(d, x, y, text, color, rule_color):
    """Small-caps tracked label with a short leading rule (editorial)."""
    d.line([(x, y + 9), (x + 26, y + 9)], fill=rule_color, width=2)
    tracked(d, x + 40, y, text.upper(), body(17, 700), color, tr=3)


def _meta(d, rubric, index_txt, cue, dark):
    ink = WHITE if dark else INK
    mut = MUT_D if dark else MUT_L
    _wordmark_corner(d, dark)
    if rubric:
        tracked(d, W - MARGIN, 72, C.RUBRIC.get(rubric, "").upper(), body(16, 700), mut, tr=3, anchor="ra")
        tracked(d, W - MARGIN, 96, "УКРАЇНСЬКА ГАЛЕРЕЯ", body(14, 600), mut, tr=3, anchor="ra")
    if index_txt:
        tracked(d, MARGIN, H - 92, index_txt, body(16, 700), ACC_D if dark else ACC, tr=3)
    if cue:
        tracked(d, W - MARGIN, H - 92, cue, body(16, 700), mut, tr=3, anchor="ra")


# --- slides ----------------------------------------------------------------
def cover(car, out_path, photo=None, mono=False):
    img = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(img)
    maxw = W - MARGIN * 2
    _meta(d, car["rubric"], "МІНІ-ГАЙД", C.SWIPE_CUE, dark=False)
    if car.get("kick") or True:
        _label(d, MARGIN, 168, car.get("kick_label", "РОЗБІР"), INK, ACC)
    size, lines = _fit_tokens(d, _tokens(car["cover"]), maxw, start=98, min_size=56, max_lines=4)
    y = 236
    lh = int(size * 1.02)
    y = _draw_tokens(d, MARGIN, y, lines, size, INK, lh)
    if car.get("cover_sub"):
        y += 26
        for l in wrap(d, car["cover_sub"], body(30, 500), maxw - 380):
            d.text((MARGIN, y), l, font=body(30, 500), fill=MUT_L); y += 42
    pw, ph = 408, 512
    _inset(img, (W - MARGIN - pw, H - 150 - ph, W - MARGIN, H - 150), photo, 0, mono, HAIR_L)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG"); return out_path


def slide_photo(idx, total, head, text, out_path, kick, photo=None, seed=1, mono=False):
    img = _scrim(_photo(photo, W, H, seed, mono))
    d = ImageDraw.Draw(img)
    maxw = W - MARGIN * 2
    _label(d, MARGIN, 150, f"{kick} {idx:02d}" if kick else f"РОЗДІЛ {idx:02d}", WHITE, ACC_D)
    size, hlines = _fit_tokens(d, _tokens(head), maxw, start=72, min_size=46, max_lines=2)
    bf = body(33, 500); blines = wrap(d, text, bf, maxw)
    hlh = int(size * 1.04); blh = int(bf.size * 1.42)
    block = len(hlines) * hlh + 22 + len(blines) * blh
    y = H - 240 - block
    y = _draw_tokens(d, MARGIN, y, hlines, size, WHITE, hlh, shadow=(8, 7, 5))
    y += 22
    for l in blines:
        tracked(d, MARGIN, y, l, bf, SOFT, shadow=(8, 7, 5)); y += blh
    _meta(d, "", f"{idx:02d} — {total:02d}", C.SWIPE_CUE, dark=True)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG"); return out_path


def slide_paper(idx, total, head, text, out_path, kick, photo=None, seed=1, mono=False):
    img = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(img)
    maxw = W - MARGIN * 2
    _label(d, MARGIN, 150, f"{kick} {idx:02d}" if kick else f"РОЗДІЛ {idx:02d}", INK, ACC)
    size, hlines = _fit_tokens(d, _tokens(head), maxw, start=68, min_size=44, max_lines=2)
    y = 232
    hlh = int(size * 1.04)
    y = _draw_tokens(d, MARGIN, y, hlines, size, INK, hlh)
    y += 24
    bf = body(33, 500)
    for l in wrap(d, text, bf, maxw - 40):
        d.text((MARGIN, y), l, font=bf, fill=MUT_L); y += int(bf.size * 1.44)
    pw, ph = maxw, 372
    _inset(img, (MARGIN, H - 168 - ph, MARGIN + pw, H - 168), photo, seed, mono, HAIR_L)
    _meta(d, "", f"{idx:02d} — {total:02d}", C.SWIPE_CUE, dark=False)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG"); return out_path


def cta(car, out_path, photo=None):
    img = Image.new("RGB", (W, H), COAL); d = ImageDraw.Draw(img)
    maxw = W - MARGIN * 2
    _label(d, MARGIN, 236, "ЗБЕРЕЖИ · ПОДІЛИСЯ", MUT_D, ACC_D)
    size, lines = _fit_tokens(d, _tokens(car["cta"].replace("\n", " ")), maxw, start=94, min_size=54, max_lines=3)
    y = 300
    lh = int(size * 1.05)
    y = _draw_tokens(d, MARGIN, y, lines, size, WHITE, lh)
    if car.get("cta_sub"):
        y += 24
        for l in wrap(d, car["cta_sub"], body(31, 500), maxw - 220):
            d.text((MARGIN, y), l, font=body(31, 500), fill=MUT_D); y += 44
    # single cobalt moment — the CTA button
    y += 30
    bf = body(20, 700); btxt = "СПРОБУЙ БЕЗКОШТОВНО  →"
    bw = _tw(d, btxt, bf, 2) + 56; bh = 68
    d.rounded_rectangle([MARGIN, y, MARGIN + bw, y + bh], radius=34, fill=ACC)
    tracked(d, MARGIN + 28, y + 22, btxt, bf, WHITE, tr=2)
    # handle in elegant italic
    d.text((MARGIN, H - 150 - 60), C.HANDLE, font=serif_it(46, 560), fill=WHITE)
    _meta(d, car["rubric"], "", "проЯв.space", dark=True)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG"); return out_path


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
        head, text = item[0], item[1]
        ph = photos[i] if len(photos) > i else None
        p = os.path.join(out_dir, f"{i:02d}_slide.png")
        if i % 2 == 1:
            slide_photo(i, total, head, text, p, kick, photo=ph, seed=i, mono=mono)
        else:
            slide_paper(i, total, head, text, p, kick, photo=ph, seed=i, mono=mono)
        paths.append(p)
    p = os.path.join(out_dir, "99_cta.png")
    cta(car, p, photo=cta_photo); paths.append(p)
    return paths
