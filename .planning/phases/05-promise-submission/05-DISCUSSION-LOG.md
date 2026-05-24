# Phase 5: Promise Submission - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-24
**Phase:** 5-Promise-Submission
**Areas discussed:** Submission guard, Edit model, Form design, Politician & election pickers

---

## Submission Guard

### Q1: Who is allowed to submit a new promise?

| Option | Description | Selected |
|--------|-------------|----------|
| Logged in only | Any authenticated user; unverified accounts fine since submissions go to moderation | |
| Logged in + email verified | Extra check: is_verified == True | |
| Logged in + verified + account ≥ N days | Same as voting guard but applied to submission | ✓ |

**User's choice:** Logged in + verified + account ≥ N days

---

### Q2: Minimum account age for submitting?

| Option | Description | Selected |
|--------|-------------|----------|
| 7 days | Low barrier, matches CLAUDE.md brigading reference | ✓ |
| 30 days | Same as voting; consistent but strict | |

**User's choice:** 7 days

---

### Q3: What does the user see if not yet eligible?

| Option | Description | Selected |
|--------|-------------|----------|
| Inline message on the form | Show form but replace submit button with explanation | ✓ |
| Redirect to gate page | /submit-locked page with explanation | |
| Hide nav button entirely | Submit entry point hidden until eligible | |

**User's choice:** Inline message on the form

---

## Edit Model

### Q1: How should promise edits be stored?

| Option | Description | Selected |
|--------|-------------|----------|
| Separate promise_edits table | Full snapshot, live promise untouched until approved | ✓ |
| Set promise back to pending on edit | Hides live promise site-wide during review | |

**User's choice:** Separate promise_edits table

---

### Q2: What fields can users edit?

| Option | Description | Selected |
|--------|-------------|----------|
| All content fields | title_hy, quote_hy, description_hy, source_url, dates, elections | ✓ |
| Quote + source URL only | Restrict to most critical factual fields | |
| Source URL only | Only fix dead links | |

**User's choice:** All content fields — with history preserved (user's free-text note: "save history")

---

### Q3: How is edit history preserved after approval?

| Option | Description | Selected |
|--------|-------------|----------|
| Keep promise_edits rows forever | Append-only; approved marks the row, updates live promise | ✓ |
| Snapshot into promise_history at approval | Two tables instead of one | |
| You decide | Claude picks | |

**User's choice:** Keep promise_edits rows forever (append-only audit trail)

---

## Form Design

### Q1: How should the submission form be structured?

| Option | Description | Selected |
|--------|-------------|----------|
| Single long page at /promises/new | All fields on one page; consistent with RegisterPage | |
| Multi-step wizard | Stepper with Back/Next navigation | |
| Two visual sections on one scrollable page | Logical groups without stepper navigation | ✓ |

**Notes:** User initially selected "multi-step wizard" then clarified "all on one page" in Armenian ("И всё это на одной странице"). Confirmed as two visual sections on one scrollable page.

---

### Q2: Where does the submit entry point live?

| Option | Description | Selected |
|--------|-------------|----------|
| Nav link — always visible | "Ներկայացնել խոստում" in header; ineligible users see inline message | ✓ |
| Nav link — only when logged in | Appears after login only | |
| Button on promise list page only | No nav link; just a CTA on /promises | |

**User's choice:** Nav link always visible

---

## Politician & Election Pickers

### Q1: How does the user select the politician?

| Option | Description | Selected |
|--------|-------------|----------|
| Searchable autocomplete | shadcn Combobox; live search via GET /api/politicians | ✓ |
| Simple <select> dropdown | Load all politicians on mount; works for v1 seed data | |
| Separate 'pick politician' step | Pre-select from politician profile page; no picker in form | |

**User's choice:** Searchable autocomplete (Combobox)

---

### Q2: How does the user select elections?

| Option | Description | Selected |
|--------|-------------|----------|
| Checkboxes from full list | Simple; multi-select natural for short list | |
| Multi-select searchable combobox | Consistent with politician picker; overkill for short list | |
| Optional — shown only if user checks toggle | Reduces noise; most promises may not be election-linked | ✓ |

**User's choice:** Optional behind toggle

---

### Q3: When toggle is checked, what picker appears?

**User's free-text response:** "Сначала предлагается выбрать уровень выборов (парламентские, президента, общин и так далее). После выбора уже предлагается выбрать конкретные выборы."
(First select the election level — parliamentary, presidential, municipal, etc. Then select the specific elections.)

**Decision:** Cascading picker — level selection first, then filtered elections.

---

### Q4: Level + election picker components?

| Option | Description | Selected |
|--------|-------------|----------|
| Level = radio buttons, elections = checkboxes | Row of radio buttons for level; checkboxes for filtered elections | ✓ |
| Level = dropdown, elections = checkboxes | <select> for level; same checkbox list | |
| You decide | Claude picks | |

**User's choice:** Radio buttons for level, checkboxes for elections

---

## Claude's Discretion

- Slug generation: backend auto-generates from `title_hy` using Armenian-to-ASCII transliteration
- Form validation: client-side (required fields highlighted) + server-side 422 errors inline
- Post-submission redirect: `/promises` list with success toast (Armenian text)
- `promise_edits` table requires a new Alembic migration

## Deferred Ideas

None — discussion stayed within phase scope.
