# Requirements: Khostumner (Խոստումներ)

**Defined:** 2026-05-20
**Core Value:** Любой человек может проверить, выполнил ли политик свои предвыборные обещания — с доказательствами и источниками.

## v1 Requirements

### Authentication

- [ ] **AUTH-01**: User can register an account with email and password
- [ ] **AUTH-02**: User receives email verification link after registration
- [ ] **AUTH-03**: User can reset password via email link
- [ ] **AUTH-04**: User can log in via Google or GitHub (OAuth)
- [ ] **AUTH-05**: Authenticated user session persists across browser refresh (JWT)

### Promises

- [ ] **PROM-01**: Anyone can view paginated promise list with filtering by status, politician, and election
- [ ] **PROM-02**: Anyone can view a promise detail page (verbatim quote, dates, status badge, source links, shareable slug URL)
- [ ] **PROM-03**: Registered user can submit a new promise (verbatim quote + source URL required + promised date + optional expected fulfillment date)
- [ ] **PROM-04**: Registered user can submit an edit to an existing promise (edit enters admin review queue)
- [ ] **PROM-05**: Admin can view moderation queue and approve or reject submitted and edited promises
- [ ] **PROM-06**: Admin can view full edit history of any promise

### Voting & Status

- [ ] **VOTE-01**: Registered user (account ≥30 days old, email verified) can cast a vote on promise status (Կատարված / Խախտված / Ընթացքի մեջ / Կասեցված / Չգնահատված) and change their vote at any time
- [ ] **VOTE-02**: Resolved status is set automatically: the leading status wins if it holds >50% of votes AND total votes ≥ configurable minimum (default: 25); otherwise status remains Չգնահատված (Not Rated)
- [ ] **VOTE-03**: Promise detail page displays vote count per status, total vote count, and current resolved status — always publicly visible
- [ ] **VOTE-04**: Admin can reset all votes for a promise when coordinated brigading is detected and documented; vote threshold minimum is configurable by admin
- [ ] **VOTE-05**: Every vote action is recorded in a vote history log (user, promise, status voted, timestamp); when a user changes their vote the old entry is preserved with a `changed_at` timestamp — full audit trail retained indefinitely

### Politicians & Parties

- [ ] **POLS-01**: Anyone can view a politician profile page (photo, full name, current role, party affiliation, promise list, fulfillment percentage)
- [ ] **POLS-02**: Anyone can browse the "Persons" section — paginated list of all politicians with filtering
- [ ] **POLS-03**: Anyone can view a party or bloc page showing all linked promises and member politicians
- [ ] **POLS-04**: Admin can create and edit politician and party profiles
- [ ] **POLS-05**: Registered user can submit a new or edited politician/party profile (submission enters admin review queue)

### Elections

- [ ] **ELEC-01**: Anyone can view the elections list page showing all elections with promise counts
- [ ] **ELEC-02**: Anyone can view an election detail page showing all promises linked to that election across all politicians
- [ ] **ELEC-03**: When submitting a promise, user can link it to one or more elections

### Discovery & Navigation

- [ ] **DISC-01**: Homepage displays overall statistics (total promises, fulfillment breakdown by status)
- [ ] **DISC-02**: "Կատարված" (Fulfilled) section shows all promises with fulfilled status, paginated
- [ ] **DISC-03**: "Չկատարված" (Not Fulfilled) section shows promises with broken or stalled status, paginated
- [ ] **DISC-04**: Site-wide search returns matching promises, politicians, and parties
- [ ] **DISC-05**: Promise detail pages include Open Graph meta tags (title, status, politician name) for social sharing

## v2 Requirements

### Notifications

- **NOTF-01**: Registered user can follow a politician and receive email when a new promise is added
- **NOTF-02**: Admin receives email notification for new moderation queue items

### AI Features

- **AI-01**: AI automatically scans Armenian news sources for promise fulfillment evidence and suggests status updates
- **AI-02**: AI-assisted translation of Armenian content to English

### Content

- **CONT-01**: Promise detail page shows a timeline of status changes with dates and evidence
- **CONT-02**: Users can flag a promise as disputed (enters admin review)

### Internationalization

- **I18N-01**: Site available in English (for diaspora and international audience)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Comment threads on promises | High moderation burden; toxicity risk on political content; defer to v2+ |
| Gamification / karma points | Risk of gaming the system; detracts from credibility |
| Mobile app (iOS/Android) | Web-first; mobile browser is sufficient for v1 |
| Real-time push notifications | Complexity vs. value; email is sufficient for v1 |
| AI auto-verification in v1 | Reliability risk; needs human moderation layer first |
| Multi-language UI in v1 | Focus on Armenian audience; English in v2 |
| Artsakh/NKR political figures | Scope boundary decision; can be revisited with content policy |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUTH-01 | Phase 4 | Pending |
| AUTH-02 | Phase 4 | Pending |
| AUTH-03 | Phase 4 | Pending |
| AUTH-04 | Phase 4 | Pending |
| AUTH-05 | Phase 4 | Pending |
| PROM-01 | Phase 3 | Pending |
| PROM-02 | Phase 3 | Pending |
| PROM-03 | Phase 5 | Pending |
| PROM-04 | Phase 5 | Pending |
| PROM-05 | Phase 6 | Pending |
| PROM-06 | Phase 6 | Pending |
| VOTE-01 | Phase 7 | Pending |
| VOTE-02 | Phase 7 | Pending |
| VOTE-03 | Phase 7 | Pending |
| VOTE-04 | Phase 7 | Pending |
| VOTE-05 | Phase 7 | Pending |
| POLS-01 | Phase 2 | Pending |
| POLS-02 | Phase 2 | Pending |
| POLS-03 | Phase 2 | Pending |
| POLS-04 | Phase 6 | Pending |
| POLS-05 | Phase 6 | Pending |
| ELEC-01 | Phase 2 | Pending |
| ELEC-02 | Phase 2 | Pending |
| ELEC-03 | Phase 5 | Pending |
| DISC-01 | Phase 3 | Pending |
| DISC-02 | Phase 3 | Pending |
| DISC-03 | Phase 3 | Pending |
| DISC-04 | Phase 8 | Pending |
| DISC-05 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 29 total
- Mapped to phases: 29
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-20*
*Last updated: 2026-05-20 after roadmap creation*