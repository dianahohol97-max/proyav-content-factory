"""Design tokens + content library for the проЯв content factory.

Everything the generators need lives here. To add a carousel, append to
CAROUSELS — render.py and build.py pick it up automatically. Text is drawn by
code (zero typos, exact brand colours, brand font), same approach as the
VistelaCo / bloom focus factories.
"""

REPO = "dianahohol97-max/proyav-content-factory"
RAW  = f"https://raw.githubusercontent.com/{REPO}/main"   # CDN for generated media

# --- brand / design tokens (проЯв brand book) ------------------------------
BG          = "#F4F4F1"   # off-white paper
INK         = "#0D0C0A"   # near-black text
MUTED       = "#6F6D66"   # muted labels / body
HAIR        = "#E5E3DC"   # hairline rules
ACCENT      = "#2F55FF"   # cobalt — the one bold colour
ACCENT_DEEP = "#1F3FE0"
ACCENT_SOFT = "#8FA2FF"
COAL        = "#12110E"

WORDMARK = "fonts/Unbounded.ttf"     # brand wordmark only (проЯв anchor)
SERIF    = "fonts/Playfair.ttf"       # elegant editorial headlines
SERIF_IT = "fonts/PlayfairItalic.ttf" # italic accent words
BODY     = "fonts/Manrope.ttf"        # body + tracked small-caps labels
DISPLAY  = "fonts/Unbounded.ttf"      # (kept for back-compat)

BRAND    = "проЯв"
HANDLE   = "@proyav"
SITE     = "проЯв.space"
TAGLINE  = "УКРАЇНСЬКА ГАЛЕРЕЯ ДЛЯ ФОТОГРАФІВ"

CAROUSEL_SIZE = (1080, 1350)  # 4:5 -> Instagram carousel
SWIPE_CUE     = "ГОРТАЙ  →"

# Photos are colour by default; flip to True for a black-&-white feed, or set
# "mono": True on a single carousel below for a per-carousel mix.
MONO_PHOTOS   = False

# Rubric labels (rendered as tracked eyebrow — no emoji, Pillow-safe).
RUBRIC = {
    "edu":     "ОСВІТА",
    "product": "ПРОДУКТ",
    "brand":   "БРЕНД",
}

# --- Carousel library ------------------------------------------------------
# Each carousel: cover hook + content slides (head + body) + CTA + IG caption.
# Slide text is intentionally short — the carousel carries the point, the
# caption expands it. Order = cover, slides…, CTA.
CAROUSELS = [
    {
        "id": "CAR_5_POMYLOK",
        "rubric": "edu",
        "kick": "ПОМИЛКА",
        "cover": "5 *помилок* у передачі зйомки клієнту",
        "cover_sub": "І остання коштує тобі рекомендацій",
        # cover/cta images (drop these files in input/photos/)
        "cover_photo": "gallery-hero.jpg",
        "cta_photo": "site-proyav.jpg",
        # each slide: head + body + image-that-matches-the-text + template.
        # tpl picks a layout from render.TEMPLATES so slides differ visually.
        "slides": [
            {"head": "Архів .zip на 4 ГБ", "tpl": "photo",
             "photo": "screenshot-zip-download.jpg",
             "body": "Клієнт качає його пів години, а половина не відкриває zip з телефона. Перше враження — зіпсоване."},
            {"head": "Посилання, що згасає", "tpl": "uicard",
             "photo": "screenshot-wetransfer.jpg",
             "body": "WeTransfer живе 7 днів. Через місяць клієнт просить фото ще раз — а їх уже нема."},
            {"head": "Купа файлів без ладу", "tpl": "photo",
             "photo": "screenshot-messy-files.jpg",
             "body": "IMG_0421.jpg нічого не каже. Клієнт губиться і не розуміє, що з цим робити далі."},
            {"head": "Жодного «вау»", "tpl": "paper",
             "photo": "screenshot-drive-folder.jpg",
             "body": "Папка з файлами не викликає емоцій. А саме емоція змушує клієнта показати зйомку друзям."},
            {"head": "Немає шляху до наступного замовлення", "tpl": "quote",
             "photo": "photo-photographer.jpg",
             "body": "Після передачі зв'язок обривається. Гарна галерея — місце, де живе твій бренд і наступний продаж."},
        ],
        "cta": "Віддай зйомку так,\nщоб клієнт сказав вау",
        "cta_sub": "Українська галерея для фотографів — спробуй безкоштовно",
        "caption": (
            "Передача зйомки — це останнє враження від роботи з тобою. І саме тут "
            "фотографи втрачають рекомендації.\n\n"
            "Найбільша помилка — не технічна. Це відсутність емоції: папка файлів не змушує "
            "клієнта показати зйомку друзям, а гарна галерея — змушує.\n\n"
            "\U0001F4CC Збережи, щоб не втратити."
        ),
        "hashtags": "#весільнийфотограф #сімейнийфотограф #фотографукраїна #галереядляфото #портфоліофотографа",
    },
    {
        "id": "CAR_GALEREYA_VS_DRIVE",
        "rubric": "product",
        "mono": True,   # this one runs black-&-white for contrast in the feed
        "cover": "Галерея *проти* папки в Google Drive",
        "cover_sub": "Те саме фото — інша реакція клієнта",
        "slides": [
            ("Перше враження",
             "Drive: список файлів і спінер. Галерея: обкладинка на весь екран, як обкладинка альбому."),
            ("Як клієнт дивиться",
             "Drive: тапає кожен файл окремо. Галерея: гортає, як стрічку, у лайтбоксі на повний екран."),
            ("Завантаження",
             "Drive: «завантажити все» одним архівом. Галерея: обирає улюблені, качає в потрібному розмірі."),
            ("Твій бренд",
             "Drive: логотип Google. Галерея: твоє ім'я, твої кольори, твій сайт-портфоліо поруч."),
            ("Наступний крок",
             "Drive: тиша. Галерея: кнопка «замовити ще зйомку» просто під фотографіями."),
        ],
        "cta": "Хай кожна зйомка\nпрацює на твій бренд",
        "cta_sub": "Створи галерею безкоштовно — лінк у шапці",
        "caption": (
            "Одні й ті самі фото у Drive і в галереї викликають різну реакцію. Бо клієнт "
            "реагує не лише на кадр — а на те, як він його отримує.\n\n"
            "Галерея — це не «файли красивіше». Це місце, де твоя робота виглядає завершеною, "
            "а бренд — професійним.\n\n"
            "\U0001F517 Спробуй безкоштовно — лінк у шапці."
        ),
        "hashtags": "#фотографукраїна #весільнийфотограф #галереядляфото #фотопередача #портфоліофотографа",
    },
    {
        "id": "CAR_PODATY_V_INSTAGRAM",
        "rubric": "edu",
        "cover": "Як гарно *подати* зйомку в Instagram",
        "cover_sub": "Щоб пост зберігали, а тебе рекомендували",
        "slides": [
            ("Обери одну історію",
             "Не 40 схожих кадрів. 6–8 фото, що ведуть глядача від емоції до емоції."),
            ("Почни з найсильнішого",
             "Перше фото вирішує, чи гортатимуть далі. Клади кадр, від якого перехоплює подих."),
            ("Тримай ритм",
             "Загальний → деталь → емоція. Чергуй плани, щоб око не втомлювалось."),
            ("Єдиний колорит",
             "Одна обробка на всю добірку. Це те, що робить стрічку впізнаваною з першого погляду."),
            ("Дай клієнту готове",
             "Галерея з відбором — клієнт сам обирає найкращі кадри для свого профілю. Ти економиш години."),
        ],
        "cta": "Подавай зйомки так,\nщоб їх зберігали",
        "cta_sub": "Українська галерея для фотографів — @proyav",
        "caption": (
            "Гарна зйомка і гарно поданa зйомка — це дві різні речі. Алгоритм тягне те, що "
            "зберігають і пересилають, а не те, що просто красиве.\n\n"
            "Секрет не в кількості кадрів, а в історії та ритмі. І в тому, щоб клієнту було "
            "легко обрати найкраще.\n\n"
            "\U0001F4CC Збережи цю добірку собі."
        ),
        "hashtags": "#фотографпочатківець #весільнийфотограф #сімейнийфотограф #фотографукраїна #портфоліофотографа",
    },
]

# IG caption footer appended to every carousel caption (kept separate so it's
# easy to tweak brand-wide).
CAPTION_FOOTER = "\n\n—\n{brand} · українська галерея для фотографів"


# --- Instagram Stories highlights (stories.py) -----------------------------
# Vertical 9:16 frames meant to be saved as a profile "highlight" (закріплені
# сторіс). Same brand as the carousels. Each highlight: cover + feature frames
# + price + CTA. Headlines accent a *word* in cobalt, just like carousels.
STORY_SIZE = (1080, 1920)

# This highlight is ONLY about the client photo gallery — no booking, no
# payments, no referral. One product story, told frame by frame.
STORIES = [
    {
        "id": "HL_GALEREYA",
        "title": "проЯв — фотогалерея",      # highlight name (шапка)
        "frames": [
            {"type": "cover"},
            # ціна спершу — одразу після обкладинки
            {"type": "price"},
            {"type": "feature", "kick": "ЩО ЦЕ",
             "head": "Галерея *замість* архіву в Drive",
             "body": "Клієнт відкриває красиву сторінку зі зйомкою за посиланням — а не список файлів у папці.",
             "photo": "gallery-hero.jpg"},
            {"type": "feature", "kick": "ГАЛЕРЕЯ",
             "head": "Клієнт *обирає* улюблені",
             "body": "Відбір у сердечко ♥ в один тап. Клієнт позначає найкраще для друку й Instagram — ти економиш години.",
             "photo": "gallery-beautiful.jpg"},
            {"type": "feature", "kick": "ГАЛЕРЕЯ",
             "head": "*Пароль* і термін дії",
             "body": "Галерея відкривається лише тому, кому ти дозволиш. Постав пароль і дату, до якої вона активна.",
             "photo": "screenshot-password.jpg"},
            {"type": "feature", "kick": "ГАЛЕРЕЯ",
             "head": "*Завантаження* без втрат",
             "body": "Zip-архів одним кліком, оригінали зберігаються байт у байт — без стискання і згаслих посилань."},
            {"type": "feature", "kick": "ГАЛЕРЕЯ",
             "head": "*Відео* та слайдшоу",
             "body": "Додавай відео просто в галерею, показуй зйомку на весь екран у режимі слайдшоу.",
             "photo": "screenshot-video.jpg"},
            {"type": "feature", "kick": "АНАЛІТИКА",
             "head": "*Статистика* переглядів",
             "body": "Бачиш, коли клієнт відкрив галерею, які фото дивився й що завантажив. Жодних здогадок.",
             "photo": "screenshot-stats.jpg"},
            {"type": "feature", "kick": "ДИЗАЙН",
             "head": "*Дизайн-студія*",
             "body": "Обери тему, шрифт, обкладинку й розкладку фото. Галерея виглядає у твоєму стилі, а не шаблонно.",
             "photo": "site-proyav.jpg"},
            {"type": "feature", "kick": "МОВИ",
             "head": "*9 мов* для клієнтів",
             "body": "Українська, англійська, польська, німецька та ще 5 мов. Іноземний клієнт бачить галерею своєю мовою.",
             "photo": "screenshot-langs.jpg"},
            {"type": "feature", "kick": "БРЕНД",
             "head": "Твій *бренд*, не Google",
             "body": "Твоє ім'я, логотип і кольори. На платних тарифах проЯв у галереї ніде не згадується.",
             "photo": "photo-photographer.jpg"},
            {"type": "cta"},
        ],
    },
]

# Highlight price frame — real проЯв tiers (single source of truth).
PRICE_EYEBROW = "ЦІНА · ГРИВНІ"
PRICE_FREE_BIG = "3 ГБ"
PRICE_FREE_SUB = "безкоштовно назавжди · необмежені галереї"
PRICE_TIERS = [
    ("Базовий", "79 грн", "100 ГБ · свій бренд"),
    ("Плюс", "319 грн", "500 ГБ · відео, статистика"),
    ("Максимальний", "559 грн", "1 ТБ · пріоритетна підтримка"),
]
PRICE_NOTE = "Без картки при реєстрації. Оплата в гривні."


# --- Gemini photo prompts (generate_photos.py) -----------------------------
# Only the *photographic* slides — UI screens are made with headless Chromium.
# Filename must match the *_photo fields / slide "photo" used above.
PHOTO_PROMPTS = {
    "gallery-hero.jpg":
        "A photographer's elegant online gallery open on a laptop on a linen "
        "surface beside a coffee, soft morning light, tasteful and premium.",
    "gallery-beautiful.jpg":
        "A happy bride scrolling a beautiful full-screen online photo gallery on "
        "her phone, cozy interior, warm emotion, lifestyle candid.",
    "photo-photographer.jpg":
        "A Ukrainian wedding photographer in a calm studio reviewing photos on a "
        "laptop, confident and warm, editorial portrait, natural light.",
}
