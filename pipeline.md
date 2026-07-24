# проЯв — контент-конвеєр (адмінка → авто-постинг)

Дані живуть у Supabase проЯв (`proiav.space`), поруч із блогом.

## Таблиці
- **social_topics** — беклог ідей (як `blog_topics`): `slug, title, rubric, kind
  (carousel|reel|story|single), status (todo|done), position`.
- **social_posts** — готовий контент зі статусами:
  `kind, rubric, hook, body(jsonb), caption, hashtags, media(jsonb),
   video_prompt, status, scheduled_at, posted_at, external_id, source, position`.
  - `status`: `draft → needs_video → ready → approved → scheduled → posted`.
  - Для каруселей `external_id` = id у фабриці; повні слайди/підпис бере Make з
    `queue/carousel_queue.json` (у Supabase — лише обкладинка для прев'ю).

## Потік
1. **Я генерую** → рядок у `social_posts` (`draft`; рілс — `needs_video` +
   `video_prompt` під Gemini omni, 9:16).
2. **Рілс**: ти робиш відео за промтом → вантажиш → `ready`.
3. **Ти в адмінці** тиснеш «Затвердити» → `approved` (+ `scheduled_at`).
4. **Make** (той самий, що постить каруселі) опитує `approved`, постить у IG,
   ставить `posted` + `posted_at`.

## Статус
- [x] Таблиці + RLS + сід (20 тем, 3 каруселі `draft`).
- [ ] Вкладка «Контент» в адмінці проЯв — чекає репо застосунку.
- [ ] Make: додати гілку «читати social_posts зі статусом approved».
- [ ] Рілс-генерація (сценарій + промт Gemini omni).
