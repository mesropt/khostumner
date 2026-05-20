# Khostumner (Խոստումներ)

## What This Is

Վիքիպեդիայի նման կայք հայ քաղաքականների ընտրախոստումների հավաքագրման և կատարման հետևելու համար։ Registered users and administrators collect politicians' promises with sources and dates; the community tracks fulfillment through crowdsourced voting with admin moderation. Охватывает национальный, местный уровень и партии Армении.

## Core Value

Любой человек может проверить, выполнил ли политик свои предвыборные обещания — с доказательствами и источниками.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Пользователи могут просматривать обещания политиков со статусом и доказательствами
- [ ] Зарегистрированные пользователи могут добавлять новые обещания с источниками
- [ ] Сообщество голосует за статус обещания, администраторы разрешают спорные случаи
- [ ] Страница политика: фото, должность, список обещаний, процент выполнения
- [ ] Раздел «Выборы» — обещания, привязанные к конкретным предвыборным кампаниям
- [ ] Навигация: «Выполнено», «Не выполнено», «Персоны», «Выборы», «Создать обещание»

### Out of Scope

- Многоязычность (русский, английский) — только армянский для v1. Русского не будет. В будущем планируем добавить ИИ-перевод с армянского на английский.
- ИИ-поиск и автообновление новостей — будущая версия
- Мобильное приложение — только веб в v1

## Context

- Аналогичные сайты существуют (PolitiFact, Obietnice.pl и др.), но нет армянского контента
- Целевая аудитория: армянские граждане, журналисты, политические активисты
- Контент охватывает: национальный уровень (президент, премьер, парламентарии), местный уровень (мэры, городские советники), партии и блоки партий (фракции) как организации
- Название «Khostumner» (Խոստումներ) означает «Обещания» по-армянски

## Constraints

- **Язык**: Армянский — единственный и основной язык интерфейса и контента в v1. В будущем добавим английский.
- **Контент**: Только армянская политика
- **Верификация**: Краудсорсинг с модерацией администраторов (не AI в v1)
- **Платформа**: Веб-сайт, не мобильное приложение
- **Стек**: FastAPI (Python) + React/Vite + PostgreSQL
- **Масштаб**: Ожидаются десятки тысяч пользователей

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Только армянский язык в v1 | Фокус на целевой аудитории, снижение сложности | — Pending |
| Краудсорсинг + модерация администраторами | Масштабируемость при сохранении качества данных | — Pending |
| Веб-сайт (не приложение) | Снижение сложности v1, охват любого устройства | — Pending |
| FastAPI (Python) как backend | Разработчик изучает FastAPI; async-native, auto OpenAPI docs, Pydantic validation | — Pending |
| React + Vite как frontend | SPA, вызывающий FastAPI API; чистое разделение ответственности | — Pending |
| PostgreSQL как база данных | Реляционная модель для иерархии политик→обещание→выборы; tsvector для поиска | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-20 after initialization*