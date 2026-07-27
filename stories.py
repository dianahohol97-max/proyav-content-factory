"""Instagram Stories renderer for проЯв highlights (закріплені сторіс).

Vertical 9:16 frames (1080×1920) on the same brand as the carousels — cobalt
accent, Unbounded headlines, Manrope body, cream & coal grounds. Content lives
in config.STORIES; this module draws the frames. Text is drawn by code (zero
typos, exact brand colours).

Layout keeps a safe zone: Instagram overlays its UI on the top ~250px and the
bottom ~240px, so all content sits between them and reads on any phone.
"""
import os
from PIL import Image, ImageDraw
import config as C
import render as R  # reuse the carousel drawing helpers (fonts, tokens, photo)

W, H = C.STORY_SIZE            # 1080 × 1920
MARGIN = 96
TOP_SAFE = 300                 # IG avatar/close sit above this
BOT_SAFE = H - 300             # IG reply bar sits below this

PAPER = R.PAPER
COAL = R.COAL
INK = R.INK
MUT_L = R.MUT_L
MUT_D = R.MUT_D
ACC = R.ACC
ACC_D = R.ACC_D
WHITE = R.WHITE
SOFT = R.SOFT


def _wordmark(d, x, y, size=30, dark=False):
    """проЯв wordmark with the cobalt Я, top-left anchor."""
    ink = PAPER if dark else INK
    acc = ACC_D if dark else ACC
    wf = R.disp(size, 600)
    for t, col in (("про", ink), ("Я", acc), ("в", ink)):
        d.text((x, y), t, font=wf, fill=col)
        x += d.textlength(t, font=wf)
    return x


def _footer(d, dark=False, index=None):
    """Corner meta: wordmark top-left, site bottom-left, index bottom-right."""
    _wordmark(d, MARGIN, TOP_SAFE - 96, 30, dark)
    mut = MUT_D if dark else MUT_L
    acc = ACC_D if dark else ACC
    R.tracked(d, MARGIN, BOT_SAFE + 70, C.SITE, R.body(24, 700), acc, tr=2)
    if index:
        R.tracked(d, W - MARGIN, BOT_SAFE + 70, index, R.body(22, 700), mut, tr=3, anchor="ra")


def frame_cover(story, out_path):
    """Highlight cover — giant проЯв on coal, doubles as the highlight icon."""
    img = Image.new("RGB", (W, H), COAL)
    d = ImageDraw.Draw(img)
    R.tracked(d, W // 2, TOP_SAFE + 40, "УКРАЇНСЬКА ГАЛЕРЕЯ ДЛЯ ФОТОГРАФІВ",
              R.body(22, 700), MUT_D, tr=4, anchor="ma")
    # wordmark, centered, oversized
    wf = R.disp(180, 700)
    parts = (("про", PAPER), ("Я", ACC_D), ("в", PAPER))
    tot = sum(d.textlength(t, font=wf) for t, _ in parts)
    x = (W - tot) // 2
    y = H // 2 - 190
    for t, col in parts:
        d.text((x, y), t, font=wf, fill=col)
        x += d.textlength(t, font=wf)
    # accent rule
    d.rectangle([(W - 120) // 2, y + 250, (W + 120) // 2, y + 260], fill=ACC_D)
    for i, line in enumerate(("Галерея для клієнтів", "замість архіву в Drive")):
        R.tracked(d, W // 2, y + 300 + i * 52, line, R.body(34, 500), SOFT, anchor="ma")
    R.tracked(d, W // 2, BOT_SAFE + 70, C.SITE, R.disp(34, 600), PAPER, anchor="ma")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


PHOTO_DIR = os.path.join("input", "photos")


def frame_feature(story, fr, idx, total, out_path):
    """Paper feature frame: eyebrow pill, accented headline, body, and — when a
    `photo` is given — a framed image band from the проЯв site at the bottom."""
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    maxw = W - MARGIN * 2
    photo = fr.get("photo")
    has_photo = bool(photo and os.path.exists(os.path.join(PHOTO_DIR, photo)))
    # eyebrow pill
    label = f"{fr.get('kick', 'ФУНКЦІЯ')} · {idx:02d}"
    R._pill(d, MARGIN, TOP_SAFE + 20, label, R.body(22, 700), ACC, WHITE, tr=2)
    # headline (accent word in cobalt) — a touch smaller when a photo shares the frame
    hstart = 92 if has_photo else 104
    hmax_lines = 3 if has_photo else 4
    hf, hlines = R._fit_tokens(d, R._tokens(fr["head"]), maxw, start=hstart, min_size=54, max_lines=hmax_lines)
    hlh = int(hf.size * 1.06)
    y = TOP_SAFE + 150
    y = R._draw_tokens(d, MARGIN, y, hlines, hf, INK, ACC, hlh)
    # rule
    y += 22
    d.rectangle([MARGIN, y, MARGIN + 100, y + 8], fill=ACC)
    y += 50
    # body
    bf = R.body(38, 500)
    for l in R.wrap(d, fr["body"], bf, maxw):
        d.text((MARGIN, y), l, font=bf, fill=MUT_L)
        y += int(bf.size * 1.42)
    # photo band from the site, filling the space down to the safe zone
    if has_photo:
        band_top = max(y + 40, H - 300 - 720)
        ph = BOT_SAFE - band_top - 20
        if ph > 300:
            pth = os.path.join(PHOTO_DIR, photo)
            img.paste(R._photo(pth, maxw, ph, seed=idx, mono=False), (MARGIN, band_top))
            R._frame(d, (MARGIN - 10, band_top - 10, MARGIN + maxw + 10, band_top + ph + 10))
    _footer(d, dark=False, index=f"{idx:02d} — {total:02d}")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


def frame_price(story, idx, total, out_path):
    """Coal price frame — free tier headline + the real tier ladder."""
    img = Image.new("RGB", (W, H), COAL)
    d = ImageDraw.Draw(img)
    maxw = W - MARGIN * 2
    R._pill(d, MARGIN, TOP_SAFE + 20, C.PRICE_EYEBROW, R.body(22, 700), ACC_D, COAL, tr=3)
    y = TOP_SAFE + 140
    # free tier — the hero number
    d.text((MARGIN, y), C.PRICE_FREE_BIG, font=R.disp(150, 700), fill=PAPER)
    y += 178
    for l in R.wrap(d, C.PRICE_FREE_SUB, R.body(34, 500), maxw):
        d.text((MARGIN, y), l, font=R.body(34, 500), fill=ACC_D)
        y += 46
    y += 34
    d.rectangle([MARGIN, y, W - MARGIN, y + 2], fill="#2A2824")
    y += 44
    # tier ladder
    nf = R.disp(40, 600)
    for name, price, note in C.PRICE_TIERS:
        d.text((MARGIN, y), name, font=R.body(34, 700), fill=PAPER)
        R.tracked(d, W - MARGIN, y - 4, price, nf, ACC_D, anchor="ra")
        y += 48
        for l in R.wrap(d, note, R.body(29, 500), maxw):
            d.text((MARGIN, y), l, font=R.body(29, 500), fill=MUT_D)
            y += 40
        y += 30
    # note
    for l in R.wrap(d, C.PRICE_NOTE, R.body(30, 500), maxw):
        d.text((MARGIN, y), l, font=R.body(30, 500), fill=SOFT)
        y += 42
    _footer(d, dark=True, index=f"{idx:02d} — {total:02d}")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


def frame_cta(story, idx, total, out_path):
    """Closing frame — one clear action."""
    img = Image.new("RGB", (W, H), COAL)
    d = ImageDraw.Draw(img)
    maxw = W - MARGIN * 2
    R._pill(d, MARGIN, TOP_SAFE + 20, "СПРОБУЙ БЕЗКОШТОВНО", R.body(22, 700), ACC_D, COAL, tr=2)
    y = H // 2 - 240
    for l in ("Створи галерею,", "яку клієнт", "захоче показати"):
        d.text((MARGIN, y), l, font=R.disp(78, 600), fill=PAPER)
        y += 96
    y += 30
    d.rectangle([MARGIN, y, MARGIN + 120, y + 9], fill=ACC_D)
    y += 60
    R.tracked(d, MARGIN, y, C.SITE, R.disp(60, 600), PAPER, tr=1)
    y += 84
    R.tracked(d, MARGIN, y, "Посилання в шапці профілю", R.body(32, 500), MUT_D)
    _footer(d, dark=True, index=f"{idx:02d} — {total:02d}")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


def highlight(story, out_dir):
    """Render every frame of one highlight; returns the ordered paths."""
    os.makedirs(out_dir, exist_ok=True)
    frames = story["frames"]
    total = len(frames)
    paths = []
    for i, fr in enumerate(frames):
        p = os.path.join(out_dir, f"{i:02d}_{fr['type']}.png")
        t = fr["type"]
        if t == "cover":
            frame_cover(story, p)
        elif t == "price":
            frame_price(story, i, total, p)
        elif t == "cta":
            frame_cta(story, i, total, p)
        else:
            frame_feature(story, fr, i, total, p)
        paths.append(p)
    return paths


if __name__ == "__main__":
    for st in C.STORIES:
        out = os.path.join("output", "stories", st["id"])
        made = highlight(st, out)
        print(f"{st['id']}: {len(made)} frames -> {out}")
