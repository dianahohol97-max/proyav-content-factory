import render as R, config as C
from PIL import Image, ImageDraw
W, H = R.W, R.H
MARGIN = R.MARGIN

img = R._scrim(R._photo("input/photos/gallery-hero.jpg", W, H, 0, False),
               base=120, floor=0.0, peak=230, gamma=1.0)
d = ImageDraw.Draw(img)

# corner chrome (wordmark + rubric line)
R._meta(d, "brand", "", "", dark=True)

# eyebrow pill, centered
pill = "СКОРО ЗАПУСК"
pf = R.body(20, 700)
pw = R._tw(d, pill, pf, 2) + 44
R._pill(d, (W - pw) // 2, 300, pill, pf, R.ACC, R.WHITE)

# hero word — fit to width
maxw = W - MARGIN * 2
size = 160
while size > 60:
    f = R.disp(size, 700)
    if R._tw(d, "НЕЗАБАРОМ", f, 0) <= maxw:
        break
    size -= 4
R.tracked(d, W/2, 470, "НЕЗАБАРОМ", f, R.WHITE, tr=0, anchor="ma")

# subtitle
sub = ["Українська галерея, де твої зйомки", "виглядають як бренд, а не як папка файлів"]
sf = R.body(34, 500)
y = 700
for l in sub:
    R.tracked(d, W/2, y, l, sf, R.SOFT, anchor="ma"); y += 48

# big site line centered near bottom
site = getattr(C, "SITE", "проЯв.space")
sfont = R.disp(58, 600)
R.tracked(d, W/2, H - 360, site, sfont, R.WHITE, tr=1, anchor="ma")
sw = R._tw(d, site, sfont, 1)
d.rectangle([W/2 - sw/2, H - 360 + 74, W/2 + sw/2, H - 360 + 81], fill=R.ACC)
R.tracked(d, W/2, H - 250, C.HANDLE, R.body(26, 700), R.MUT_D, tr=2, anchor="ma")

img.save("output/coming_soon.png", "PNG")
print("saved output/coming_soon.png")
