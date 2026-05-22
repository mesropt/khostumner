# Phase 3: Promise Browsing & Homepage - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-22
**Phase:** 3-Promise-Browsing-Homepage
**Areas discussed:** Homepage, Fulfilled/Unfulfilled sections, Promise detail page, Open Graph tags

---

## Homepage

| Option | Description | Selected |
|--------|-------------|----------|
| Статистика + последние обещания | Блок цифр (все статусы) + последние N обещаний | ✓ |
| Только статистика | Цифры по статусам, без листинга | |
| Hero + последние обещания + CTA-ссылки | Landing page с hero-блоком и секциями | |

**Что главное:** Статистика + последние обещания разных деятелей

| Статистика | Описание | Selected |
|------------|----------|----------|
| Цифры по каждому статусу | Карточки: Всего / Катарвад / Хахтвац / Ынтацки мей / Касецлах / Чгнахатвах | ✓ |
| Только Катарвад vs Хахтвац | Две большие цифры | |
| Всего + % выполнения | Одна цифра + kept/(kept+broken) | |

**Последние обещания:** 5–10 последних по дате (created_at desc)

**API для статистики:** GET /api/stats — отдельный endpoint

---

## Fulfilled/Unfulfilled Sections

| Option | Description | Selected |
|--------|-------------|----------|
| Отдельные маршруты + страницы | /fulfilled (kept), /unfulfilled (broken+stalled) — самостоятельные страницы | ✓ |
| /promises + pre-applied фильтр | Редирект на /promises?status=kept и т.д. | |

**Структура:** 3 страницы — /promises (все + фильтры), /fulfilled, /unfulfilled

**Фильтры на /promises:** status + politician + election + дата-рейнджер made_date + дата-рейнджер expected_date

**Дата-фильтр:** from/to date range (два date input), не по году

**Notes:** Пользователь уточнил что обещания могут быть без дат (условные — "если А сделает Б"). Такие обещания не исключаются при отсутствии фильтра по дате.

---

## Promise Detail Page

| Option | Description | Selected |
|--------|-------------|----------|
| Цитата (quote_hy) — главный элемент | Verbatim цитата крупным шрифтом + статус + источник + даты | ✓ |
| Заголовок (title_hy) — главный, цитата ниже | Заголовок крупно, цитата курсивом | |

**Источник:** Кнопка «Աղбюр» — внешняя ссылка, target=_blank. Если есть archived_url — вторая ссылка "Wayback Machine".

**Даты:** made_date + expected_date. Если поле null — строка не отображается.

**Notes:** Пользователь также упомянул желание добавить теги и хронику — зафиксированы как deferred.

---

## Open Graph Tags

| Option | Description | Selected |
|--------|-------------|----------|
| FastAPI OG-ендпоинт по bot user-agent | /api/og/promises/{slug} → HTML с <meta og:*>, маршрутизация на уровне прокси | ✓ |
| Vite SSR / Prerender.io | Большой рефакторинг или внешний сервис | |
| react-helmet + FastAPI OG | Двойной путь | |

**Важность:** "Очень важно — требуются реальные OG-превью" (Telegram, Facebook)

**Содержимое OG:** Фрагмент цитаты (первые 150 символов quote_hy) + имя политика + фото политика (og:image)

---

## Claude's Discretion

- Promise list layout на /promises — компактный список (не card grid), consistent с election list
- Status badge colors — following Phase 2 colors
- Date input component — shadcn `<Input type="date">` без отдельной библиотеки date picker
- Mobile hamburger nav — может быть реализован в Phase 3 если появится возможность

## Deferred Ideas

- **Теги/метки** (транспорт, сельское хозяйство, ...) — Phase 5 (Promise Submission)
- **Хроника по теме** (группировка обещаний по кампании) — Phase 6+
- **«Верю/Не верю» credibility poll** — Phase 7 (вместе с voting system)
- **Перенос даты / обновление условий политиком** — Phase 5/6
