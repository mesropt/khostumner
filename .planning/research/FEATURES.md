 # Feature Landscape

**Domain:** Political promise tracker / political accountability website
**Project:** Khostumner (Խոստումներ) — Armenian politician promise tracker
**Researched:** 2026-05-20
**Sources:** PolitiFact, VowTrack, Full Fact (UK), political-accountability.in (India), Code for Africa PromiseTracker, MIT Promise Tracker, civictech.guide directory

---

## Table Stakes

Features users expect on any political accountability site. Missing any of these and the site feels incomplete or untrustworthy.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Promise list view (browsable, paginated) | Core browsing action; without it the site has nothing to show | Low | Filterable grid or card list |
| Promise status badge / label | Every comparable site uses visible status indicators; users arrive expecting to quickly see "kept / broken" | Low | Color-coded badge on every card |
| Standard status vocabulary (5–6 values) | PolitiFact, Full Fact, VowTrack all use 5–7 categories; users pattern-match to these conventions | Low | See recommended vocabulary below |
| Per-promise detail page | Users need to read the full context, source links, and history of each promise | Medium | Slug-based URL, shareable |
| Source / evidence links on each promise | Distinguishes a fact-based tracker from mere opinion; expected by journalists and activists | Low | External URLs + optional description |
| Politician profile page | Aggregates all promises under one person; necessary for "is Pashinyan keeping promises?" queries | Medium | Photo, role, party, promise list, completion % |
| Promise creation (by registered users) | Wikipedia-model requires community contribution; without this the site can't scale content | Medium | Form with required source URL field |
| User registration / login | Prerequisite for submitting promises and casting status votes | Medium | Email + password minimum; OAuth optional |
| Admin moderation queue | Without moderation, vandalism and propaganda make the site unusable; every civic wiki needs it | Medium | Review, approve, reject, edit pending submissions |
| Election / campaign filter | Promises are made per election cycle; users search "2021 parliamentary election" promises | Medium | Election entity with associated promises |
| Promise status filter | Most-used filter globally — "show me all broken promises" | Low | Multi-select by status value |
| Politician filter | "Show all promises by Pashinyan" from the promise list | Low | Dropdown or search-as-you-type |
| Search (basic text search) | Users arrive with a politician name or keyword; no search = frustrating dead end | Medium | Full-text on promise title and description |
| Completion percentage per politician | Shown on politician profile; PolitiFact, VowTrack, Full Fact all surface this; users expect a score | Low | Derived metric, computed from statuses |
| Mobile-responsive layout | 68%+ of civic site visits come from mobile; non-responsive is effectively broken for most users | Low–Med | CSS only, no separate app needed |
| Armenian-language UI | Target audience is Armenian speakers; English UI alienates the primary audience | Low | All labels, nav, and system text in Armenian |

### Recommended Status Vocabulary

Based on PolitiFact (6-status), Full Fact (7-status), and VowTrack (4-status) analysis, use **5 statuses** to balance nuance and simplicity:

| Status (Armenian label TBD) | Meaning | Visual |
|------------------------------|---------|--------|
| Կատարված (Kept) | Promise fulfilled with verifiable evidence | Green |
| Խախտված (Broken) | Promise explicitly violated or reversed | Red |
| Ընթացքի մեջ (In Progress) | Active work or legislation underway | Blue |
| Կասեցված (Stalled) | No movement; neither kept nor explicitly broken | Yellow/Orange |
| Չգնահատված (Not Yet Rated) | Default for new entries | Grey |

A "Compromise" category (PolitiFact uses this) can be deferred — it adds cognitive load and is hard to judge for Armenian politics context.

---

## Differentiators

Features that set Khostumner apart. Not universally expected, but high value for the Armenian civic audience.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Crowdsourced status voting | Users vote on promise status; admin resolves disputes. VowTrack uses this; most others are editorial-only. Builds community ownership and scales review without full-time staff | High | Core differentiator for this project; requires vote aggregation and admin dispute workflow |
| Election-scoped promise collections | "2021 Parliamentary" or "2018 Velvet Revolution" as named entities linking promises; most trackers don't structure this explicitly | Medium | Election model with start/end date, type (national/local/party), linked politicians |
| Party / bloc promise tracking | Tracks promises made by parties and parliamentary blocs as organizations, not just individuals — relevant for Armenian coalition politics | Medium | Politician entity covers both persons and parties/blocs |
| Local government coverage (mayors, councillors) | Most Armenian civic attention goes to national level; tracking Yerevan mayor and regional officials is a gap no existing site fills | Low (data) / Med (features) | Same schema works; requires content strategy |
| Evidence versioning / edit history | Wikipedia-style revision history on promises and evidence. Critical for trust — anyone can see what changed and when | High | Audit log on all edits, with diff view |
| Contribution audit trail (public) | All votes, edits, and submissions visible by user. Makes bad-faith editing costly | Medium | User contribution page |
| Shareable promise card (OG meta tags) | Each promise URL generates a shareable social card with politician photo, promise text, and status. Viral sharing is how civic sites grow | Low | Open Graph + Twitter Card meta |
| Flag / dispute mechanism | Users flag inaccurate entries; goes to admin queue. Reduces vandalism load on admins | Low–Med | Flag button per promise, flagged reason, admin review |
| Progress notes / timeline on a promise | Ordered log of updates as a promise evolves (e.g., "bill introduced → passed committee → signed"). Full Fact does this for UK pledges | Medium | Append-only event log per promise |
| Category / topic tagging | Tag promises by policy area (economy, security, healthcare, education) for cross-politician comparison | Low | Many-to-many tag model |

---

## Anti-Features

Features to deliberately NOT build in v1, with rationale.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| AI-powered auto-verification / news scraping | High engineering cost, high error rate on Armenian-language sources, produces false confidence in statuses | Manual community + admin review; flag AI as future roadmap |
| Comment / discussion threads per promise | Becomes a political debate forum, attracts toxicity, requires intensive moderation, dilutes the factual focus | Use structured voting + evidence links instead of freeform text |
| User reputation / karma gamification (points, badges, leaderboards) | Incentivizes gaming the system (fake votes for/against politicians); political-accountability.in includes this and it creates adversarial dynamics | Rely on admin moderation quality gates instead |
| Multi-language UI in v1 (Russian, English) | Triples UI translation work, splits audience focus, adds complexity before core feature set is stable | Armenian-only for v1; add AI translation to English in v2 |
| Mobile application (iOS/Android) | Doubles development surface, adds app store review cycles, not justified for v1 audience size | Responsive web covers all devices |
| Email notifications / subscriptions | Infrastructure cost (email deliverability), low value until the site has significant traffic | Add only after there are enough users to justify it |
| Donations / crowdfunding integration | Changes the site's perceived neutrality; political audiences are suspicious of monetized accountability sites | Keep ad-free and donation-free for v1 to protect credibility |
| Endorsements or "upvotes" on politicians themselves | Crosses from accountability into partisan campaigning; destroys editorial trust | Track promises only, not politicians' general popularity |
| Real-time live tracking during parliamentary sessions | Requires dedicated staff and live data feeds; out of scope for crowdsourced model | Manual promise entry post-event is sufficient |
| Formal fact-checking scores / "Truth-O-Meter" style ratings | PolitiFact's model requires full-time fact-checking journalists; crowdsourced sites cannot reliably replicate this without becoming politically captured | Status reflects community consensus + admin adjudication, not editorial rating |

---

## Feature Dependencies

```
User Registration
  └─> Promise Creation (requires auth)
  └─> Status Voting (requires auth)
  └─> Flagging / Dispute (requires auth)

Admin Role (elevated user)
  └─> Moderation Queue (approve/reject submissions)
  └─> Dispute Resolution (override community votes)
  └─> Admin Edit (correct facts, update status)

Politician Profile
  └─> Promise List (politician as FK on promise)
  └─> Completion % (derived from statuses on politician's promises)
  └─> Election Association (politician participates in election)

Election Entity
  └─> Promise Collection (promises scoped to election)
  └─> Politician Participation (which politicians ran)

Promise Entry
  └─> Evidence Links (one-to-many URLs per promise)
  └─> Status (one of 5 values; set by votes or admin)
  └─> Tags / Categories (many-to-many)
  └─> Progress Notes Timeline (append-only log)
  └─> Crowdsourced Votes (many users → one status tally)
  └─> Flag / Dispute (user-initiated, admin-resolved)

Crowdsourced Status Voting
  └─> Vote Aggregation (majority or threshold rule)
  └─> Dispute Escalation to Admin (if votes are close or flagged)
```

---

## MVP Recommendation

### Must ship for Day 1

These six features constitute the minimum usable product — without them the site provides no unique value:

1. **Politician profiles** — photo, role, party, promise list, completion %
2. **Promise entry** — title, full text, original source URL, politician FK, election FK, status
3. **Status display with 5-value vocabulary** — color-coded on list and detail views
4. **Election entity + filter** — scoped browsing of a specific campaign
5. **User registration + promise submission** — crowd can add content
6. **Admin moderation queue** — approve/reject submissions, override disputed statuses

### Ship in first iteration after MVP

These features add trust and engagement without being blocking:

- Evidence versioning / edit history (builds credibility with journalists)
- Crowdsourced status voting with admin dispute resolution (core differentiator; can start with admin-only status setting in week 1)
- Category / topic tags (enables cross-politician analysis)
- Shareable OG meta tags (cheap, high distribution value)
- Flag / dispute mechanism (reduces admin load from scanning every entry)

### Defer explicitly

- Progress notes / timeline — valuable but requires more data to be useful; add after 100+ promises
- Search — add after basic browsing is stable and there's enough content to justify it (50+ promises)
- Party/bloc as politician entity type — same schema works once individual politician model is solid

---

## Sources

- PolitiFact Trump-O-Meter: https://www.politifact.com/truth-o-meter/promises/trumpometer/
- PolitiFact Methodology (Press Club Institute): https://www.pressclubinstitute.org/2025/02/06/how-politifact-uses-the-maga-meter-to-monitor-presidential-campaign-promises/
- Full Fact Government Tracker (UK): https://fullfact.org/government-tracker/
- VowTrack: https://www.vowtrack.app/
- political-accountability.in (India): https://www.political-accountability.in/
- Code for Africa PromiseTracker: https://github.com/CodeForAfrica/PromiseTracker
- MIT Promise Tracker overview: https://www.media.mit.edu/projects/promise-tracker/overview/
- CivicTech Guide Promise Trackers directory: https://civictech.guide/promisetrackers/
- OpenNews "Tracking the Trump Trackers" (multi-tracker comparison): https://source.opennews.org/articles/tracking-trump-trackers/
- Wikipedia content moderation model: https://design.wikimedia.org/blog/2020/07/30/content-moderation-anti-vandalism-wikipedia.html