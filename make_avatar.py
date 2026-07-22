import render as R, config as C
from PIL import Image, ImageDraw

S = 1080
def wm_font(sz): return R._f(C.WORDMARK, sz, 700)

def fit_wordmark(d, target_w):
    sz = 300
    while sz > 40:
        f = wm_font(sz)
        w = sum(d.textlength(c, font=f) for c in "проЯв")
        if w <= target_w: return f, w
        sz -= 4
    return wm_font(40), 0

def wordmark(bg, ink, ya):
    img = Image.new("RGB", (S, S), bg); d = ImageDraw.Draw(img)
    f, w = fit_wordmark(d, 620)
    x = (S - w) / 2; y = S/2 - f.size*0.62
    for c in "проЯв":
        col = ya if c == "Я" else ink
        d.text((x, y), c, font=f, fill=col); x += d.textlength(c, font=f)
    return img

def monogram(bg, letter_col, sub_col):
    img = Image.new("RGB", (S, S), bg); d = ImageDraw.Draw(img)
    f = wm_font(560)
    w = d.textlength("Я", font=f)
    d.text(((S-w)/2, S/2 - f.size*0.62 - 20), "Я", font=f, fill=letter_col)
    sf = R.body(40, 700)
    R.tracked(d, S/2, S*0.72, "П Р О Я В", sf, sub_col, tr=6, anchor="ma")
    return img

variants = {
    "avatar_cream": wordmark(R.PAPER, R.INK, R.ACC),
    "avatar_coal":  wordmark(R.COAL, R.WHITE, R.ACC),
    "avatar_cobalt":wordmark(R.ACC, R.WHITE, R.WHITE),
    "avatar_mono":  monogram(R.PAPER, R.ACC, R.MUT_L),
}
import os; os.makedirs("output/avatar", exist_ok=True)
for n, im in variants.items(): im.save(f"output/avatar/{n}.png")

# preview: circle-cropped row (how IG shows it)
names = list(variants)
cell = 300; pad = 24
sheet = Image.new("RGB", (len(names)*cell + pad*(len(names)+1), cell + pad*2), "#d7d5cf")
for i, n in enumerate(names):
    av = variants[n].resize((cell, cell))
    mask = Image.new("L", (cell, cell), 0); ImageDraw.Draw(mask).ellipse([0,0,cell,cell], fill=255)
    ring = Image.new("RGB", (cell, cell), "#d7d5cf")
    ring.paste(av, (0,0), mask)
    sheet.paste(ring, (pad + i*(cell+pad), pad))
sheet.save("_avatars.png")
print("ok", names)
