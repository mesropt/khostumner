# Domain Pitfalls: Political Promise Tracking (Khostumner)

**Domain:** Political accountability / crowdsourced promise tracking website
**Researched:** 2026-05-20
**Confidence:** HIGH (Armenia-specific legal context), HIGH (crowdsourcing failure modes), MEDIUM (civic tech sustainability)

---

## Critical Pitfalls

Mistakes that cause rewrites, legal exposure, or complete loss of credibility.

---

### Pitfall C1: Undefined Fulfillment Criteria — The "Who Decides?" Trap

**What goes wrong:**
The most fundamental question — "is this promise fulfilled?" — is never formally defined before launch. Different users apply different standards: some accept partial progress, others demand full delivery, others consider changed circumstances. The voting becomes meaningless noise. Community fights break out over every contested promise. Admins are overwhelmed with disputes they have no policy to resolve.

**Why it happens:**
Teams build the voting UI first and assume the methodology will emerge from community consensus. It never does. Promise tracking research (FullFact, PolitiFact, Code for Africa's PromiseTracker) consistently shows that without a written, public standard, every status decision is perceived as partisan.

**Consequences:**
- Votes become popularity contests, not factual assessments
- Credibility evaporates on the first high-profile disputed case (e.g., a ruling-party promise rated "fulfilled" by supporters despite obvious failure)
- Journalists refuse to cite the site
- Disputes consume admin time indefinitely

**Prevention:**
Define and publish a fulfillment rubric before accepting any content. The rubric must specify at minimum:
  - "Fulfilled": Verifiable, concrete outcome delivered (not intent, not effort)
  - "In Progress": Measurable steps taken with public evidence
  - "Not Fulfilled": Term ended or politician left office without delivery
  - "Broken": Active reversal or contradiction of original promise
  - "Ambiguous": Promise wording too vague to assess — requires admin reclassification

Require at least one evidence link for any status change. Show the criteria publicly on every promise page.

**Warning signs:**
- Team debating "fulfilled vs in progress" without a written policy
- Two admins disagreeing on the same promise with no tie-break process
- More than 10% of promises stuck in unresolved voting

**Phase:** Must be addressed in Phase 1 (data model design) before any voting UI is built.

---

### Pitfall C2: Armenian Defamation Exposure — Legal Attack Vector

**What goes wrong:**
A politician (or their legal team) files a civil defamation or insult complaint against the site operators for a promise classified as "broken" or a user comment deemed insulting. Under Armenia's 2021 Civil Code amendments, fines reach 6 million AMD (~$12,600) for defamation of a public figure — roughly 30x the average journalist's monthly salary. Criminal "grave insult" charges carry up to 3 months imprisonment. The site has no legal defense structure.

**Why it happens:**
Armenia has a documented pattern of politicians using defamation law selectively against critical media. In 2023 alone, 48 new court cases were opened against journalists and media, more than half filed by government representatives. The CPJ documented a 2023 case where a deputy mayor sued a journalist for a corruption report and had 18 million AMD in assets frozen before trial. A "Broken" label on a ruling-party promise is legally equivalent risk to that investigative report.

**Consequences:**
- Asset freeze or injunction before trial shuts site down without a verdict
- Financial penalties capable of bankrupting individual operators
- Chilling effect: admins stop marking promises as "broken" out of fear
- Self-censorship destroys the entire value proposition

**Prevention:**
1. **Source everything.** Every promise entry and every status decision must link to primary sources (official statements, news archives, parliamentary records). "We reported facts with sources" is the core legal defense.
2. **No editorial opinion in promise text.** Promises are quoted verbatim from original sources. Status labels are applied per the published rubric, not editorial judgment.
3. **Distinguish promise status from personal character.** "This promise was not fulfilled" is factual. "This politician lied" is defamation territory.
4. **Consult an Armenian media lawyer before launch.** Organizations like the Committee to Protect Freedom of Expression in Armenia (CPFE) provide guidance.
5. **Operator anonymity or legal entity structure.** Consider whether site operators should be a registered NGO (which may have more protection) versus individuals.
6. **User content moderation policy.** Comments and user-added evidence must be moderated — user content is the highest-risk exposure.

**Warning signs:**
- Promise entries contain editorializing beyond factual description
- User comments allowed without moderation
- No evidence links required for status changes
- Site operated by named individuals with no legal entity

**Phase:** Legal review in Phase 1 (before public launch). Moderation policy in Phase 2 (user content). Ongoing for every phase.

---

### Pitfall C3: Coordinated Political Manipulation — Brigading and Astroturfing

**What goes wrong:**
A political party's supporters (or a single person with many accounts) organizes a coordinated push to vote all promises of their preferred politician as "fulfilled" and all opponents as "broken." In Armenia's polarized political environment (ruling Civil Contract party vs. opposition coalitions), this is not hypothetical — it mirrors documented behavior on Facebook groups and Telegram channels. Research on Community Notes (X/Twitter's crowdsourced system) found that a minority of 5-20% of bad-faith raters can strategically suppress targeted content. The site's vote counts become weapons, not measurements.

**Why it happens:**
Open registration + anonymous voting + no rate-limiting = trivial to game. Political operatives routinely run astroturfing campaigns across social media. A niche Armenian political site is a soft target.

**Consequences:**
- All promise statuses reflect political faction strength, not reality
- Site becomes a propaganda tool for whichever faction mobilizes first
- Credibility collapse is instant and irreversible once documented

**Prevention:**
1. **Account age and activity minimums before voting.** Accounts less than 7 days old or with fewer than 3 contributions should not be able to vote.
2. **Rate-limit votes per user per day.** Caps prevent single-session brigading.
3. **IP/device fingerprinting for sockpuppet detection.** Multiple accounts from same IP = automatic flag.
4. **Email verification required.** No anonymous voting.
5. **Admin override beats community vote.** Community vote surfaces consensus, admin decision is final for disputed cases. Never let a raw vote count determine status automatically.
6. **Audit trails.** Every vote is logged with timestamp and user ID (not public, but available to admins). Suspicious voting patterns (20 votes in 10 minutes from new accounts) trigger review.
7. **Transparent vote display.** Show number of votes, not just result percentage — a 51%/49% split on 12 votes means nothing; a 85%/15% split on 340 votes means more.

**Warning signs:**
- Sudden spike in new registrations around a specific politician or election
- Vote distribution shifts dramatically overnight
- Multiple accounts with similar usernames, registration dates, or IPs

**Phase:** Phase 2 (user system design). Rate limiting and anti-abuse in Phase 2. Audit tooling in Phase 3.

---

### Pitfall C4: Source Rot and Orphaned Evidence

**What goes wrong:**
Promises are entered with links to news articles, official statements, or Facebook posts as evidence. Over 2-3 years, those links die: news sites restructure URLs, Facebook posts are deleted, official government pages are redesigned. The evidence base silently disappears. When someone challenges a status, there is no way to verify the original claim. The site looks fabricated even when it was accurate.

**Why it happens:**
Armenian news outlets (Factor, Armenpress, 1in.am, CivilNet) do not have stable URL structures. Politicians routinely delete inconvenient social media posts. This is documented behavior: promise-tracking research finds sources need to be archived at submission time, not linked externally.

**Consequences:**
- Promises appear unsourced and unverifiable years after accurate entry
- Political opponents point to dead links as evidence of fabrication
- Site cannot be cited by journalists or researchers

**Prevention:**
1. **Archive evidence at submission time.** When a user submits a source URL, automatically attempt to archive it via Wayback Machine API (save.org/save API) or store a local snapshot.
2. **Store the original quote or excerpt alongside the URL.** Even if the link dies, the quoted text remains.
3. **Broken link detection.** Periodic health checks on all evidence links. Flag dead links to admins.
4. **Prioritize official sources.** Parliamentary records, official government announcements, CEC (Central Electoral Commission) materials are more stable than news articles.

**Warning signs:**
- Evidence links added without any quotation or excerpt
- No automated link health checks after launch
- Sources predominantly from Facebook/social media (high deletion risk)

**Phase:** Phase 1 (data model must include archived_url and quote_excerpt fields). Phase 3 (automated link health checks).

---

## Moderate Pitfalls

---

### Pitfall M1: Credibility Collapse from Perceived Partisan Bias

**What goes wrong:**
Even if the site is methodologically sound, it is perceived as politically biased because of the distribution of its content — more promises tracked for ruling-party politicians, or a higher "broken" rate for opposition figures (or vice versa). PolitiFact, despite rigorous methodology, faces permanent accusations of partisan bias. For an Armenian site in an intensely polarized political environment, one high-profile disputed ruling is enough to brand the project as belonging to one political camp, making it useless to the other half of the audience.

**Why it happens:**
Early content reflects who submitted it. If early contributors are opposition supporters, more ruling-party promises get tracked and labeled. Coverage asymmetry creates perception of intent even when none exists.

**Prevention:**
1. **Coverage balance dashboard.** Publicly visible count of promises tracked by party/politician. Make imbalance transparent rather than hidden.
2. **Written methodology page.** Explains status categories, evidence requirements, admin process. Cite it as a defense.
3. **Editorial independence signals.** Site is not affiliated with any party or media outlet. State this prominently.
4. **Encourage balanced contributions.** On-boarding prompts could suggest adding promises for politicians across the spectrum.
5. **Admin team diversity.** If one admin makes all final decisions, their political affiliation will define the site. Multi-admin teams with transparent decision logs reduce this risk.

**Warning signs:**
- Coverage ratio exceeds 3:1 between any two major parties without editorial justification
- All admins are from the same political background
- No public methodology page exists

**Phase:** Phase 1 (methodology page as static content). Phase 2 (coverage balance metric in admin dashboard).

---

### Pitfall M2: Content Stagnation and the Cold Start Problem

**What goes wrong:**
The site launches with an empty or near-empty database. Visitors arrive, see few promises, and leave without contributing. The site never reaches the critical mass of content that makes it useful. Promise-tracking research notes that fact-checking sites have an average lifespan under 6 years, and many fail to achieve sustainability. Civic tech projects routinely fail to attract broad user bases even when well-built.

**Why it happens:**
"If you build it they will come" is false for niche civic tech. Armenia has roughly 3 million people; politically engaged users capable of contributing quality content number in the thousands, not millions. There is no organic discovery engine.

**Prevention:**
1. **Pre-populate at launch.** Do not launch with an empty database. Before launch, admins should manually enter 50-100 high-quality promises from major politicians (2018 and 2021 parliamentary elections are logical starting points).
2. **Partner with journalists and NGOs before launch.** A single article in CivilNet, Hetq, or Factor mentioning the site is worth more than any marketing. Outreach to these outlets should begin before public launch.
3. **Make adding promises easy.** The contribution form should take under 2 minutes to complete with minimal required fields.
4. **Gamification signals are dangerous here** (see Pitfall M3), but simple recognition (contributor profile showing number of accepted promises) is safe and motivating.

**Warning signs:**
- Fewer than 30 promises in the database at public launch
- No partnerships with Armenian journalism organizations established
- Contribution form requires more than 5 fields

**Phase:** Phase 1 (seed content strategy). Phase 2 (contribution flow UX). Pre-launch (outreach).

---

### Pitfall M3: Gamification Incentivizing Volume Over Quality

**What goes wrong:**
Adding points, badges, leaderboards, or contribution counts to incentivize participation causes users to add low-quality, duplicate, or unverifiable promises to maximize their score. Wikipedia has this problem at scale; for a small site with limited moderation, it is worse. Admins spend all their time rejecting junk submissions instead of verifying quality ones.

**Why it happens:**
Gamification systems are designed to maximize engagement. They maximize whatever behavior users can perform most easily — which is submitting low-effort content, not researching and sourcing accurate promises.

**Prevention:**
1. **Do not add gamification in v1.** Defer entirely. The audience (journalists, activists, engaged citizens) is intrinsically motivated enough — they don't need points.
2. **If contributor recognition is added later**, base it on admin-approved contributions only, not raw submissions.
3. **Soft rate limits.** A user cannot submit more than 5 promises per day without admin review.

**Warning signs:**
- More than 30% of submissions being rejected
- Same user submitting 10+ promises in a single session
- Promise entries with no evidence links and vague descriptions

**Phase:** Defer gamification to post-v1. If added, Phase 3 with approved-only counting.

---

### Pitfall M4: Admin Bottleneck and Moderation Burnout

**What goes wrong:**
All disputed votes, new promise submissions, new user registrations, and reported content require admin attention. With one or two admins, the backlog grows faster than it is processed. Admin burnout follows. Decisions become inconsistent. Users lose trust in the moderation process. The site becomes a ghost town as contributors stop seeing their submissions reviewed.

**Why it happens:**
Political content moderation is psychologically demanding. Moderators face constant exposure to contested political material, personal attacks, and pressure from politically motivated users. Research on content moderation shows secondary trauma and burnout are documented occupational risks even for professional moderators at large platforms.

**Prevention:**
1. **Design for minimum admin burden.** Most promise statuses should be determinable from evidence alone. Reserve admin decisions for genuinely contested cases.
2. **Clear escalation policy.** Define what does and does not require admin review. Community votes on non-contested promises should be sufficient.
3. **Multiple admins from the start.** Three admins minimum with documented decision authority.
4. **SLA for moderation.** Publicly commit to a review timeline (e.g., new submissions reviewed within 72 hours). This sets expectations and creates accountability.
5. **Batch moderation UI.** Admins should be able to review a queue, not dig through the site manually.

**Warning signs:**
- Submission queue exceeds 20 unreviewed items
- Single admin making all decisions
- Admins publicly contradicting each other on similar cases

**Phase:** Phase 2 (admin dashboard and queue UI). Phase 3 (SLA policy, multi-admin workflow).

---

### Pitfall M5: Data Model Inflexibility for Political Reality

**What goes wrong:**
The data model is built around a clean "one politician, one promise, one election" structure. Reality is messier: politicians switch parties, coalitions dissolve mid-term, a promise made by a party becomes a promise of a different coalition after the election, a politician makes the same promise in 2018 and again in 2021 without fulfilling either. The schema cannot represent this, so data entry either becomes impossible or inconsistent hacks accumulate.

**Why it happens:**
Data model design happens before seeing real content. Armenian political landscape is particularly complex: parties merge, rebrand, and splinter frequently. Civil Contract did not exist before 2019. The Republican Party went from ruling party to near-irrelevance in two election cycles.

**Prevention:**
1. **Model politicians and parties as separate entities with a membership history table**, not a static foreign key.
2. **Allow promises to be associated with multiple elections** (reiterated promise across cycles).
3. **Party affiliation is time-bounded.** A politician's party at time of promise may differ from their party today.
4. **Coalition groupings should be first-class entities**, separate from individual parties.
5. Review real Armenian political data (at least 10-15 actual promises) before finalizing the schema.

**Warning signs:**
- Schema has politician.party_id as a single non-nullable field
- No way to represent "this promise was made on behalf of a coalition, not a single party"
- Schema review has not been done with any actual political data

**Phase:** Phase 1 (schema design). Cannot be fixed cheaply after data entry begins.

---

## Minor Pitfalls

---

### Pitfall N1: Armenian Font and Text Rendering Issues

**What goes wrong:**
Armenian (Հայերեն) uses the Unicode Armenian block (U+0530–U+058F). While it is not RTL (Armenian reads left-to-right), it requires proper UTF-8 encoding throughout the stack and a web font that covers the full character set. The default system font stack on many Windows configurations does not render Armenian characters well. Search and indexing fail if the database is not configured for UTF-8 or if the search engine tokenizer treats Armenian script incorrectly.

**Why it happens:**
Developers test on a system where Armenian fonts are pre-installed. The production server or CI environment does not have them, or the database defaults to latin1 collation.

**Prevention:**
1. **Database character set: utf8mb4** (not utf8, which is MySQL's 3-byte variant). Collation: utf8mb4_unicode_ci.
2. **Load a reliable Armenian web font** (e.g., Google Fonts: Noto Serif Armenian or Mardoto). Do not rely on system fonts.
3. **All API responses: Content-Type: application/json; charset=utf-8.**
4. **Search configuration:** If using full-text search or Elasticsearch, configure the analyzer for Unicode text, not just ASCII tokenization.
5. **Test with Armenian text from day one of development.** Do not leave it as "we'll handle i18n later."

**Warning signs:**
- Test database uses latin1 collation
- Armenian characters display as boxes or question marks in development
- Search returns no results for Armenian-script queries

**Phase:** Phase 1 (database setup). Cannot be retrofitted cheaply after data exists.

---

### Pitfall N2: URL and SEO Structure for Armenian Content

**What goes wrong:**
Politician and promise pages use Armenian-script slugs in URLs. Some social media platforms, older browsers, or link-preview scrapers mangle or percent-encode these URLs, making them unshearable. Alternatively, auto-generated slugs from Armenian text produce ugly percent-encoded strings. SEO for Armenian-language content is impaired by missing hreflang tags or wrong locale settings.

**Prevention:**
1. **Use transliterated ASCII slugs for URLs** (e.g., /politician/nikol-pashinyan rather than /politician/նիկոլ-փաշինյան). Store the Armenian display name separately.
2. **Set html lang="hy"** on all pages.
3. **Canonical URLs and Open Graph tags** must render correctly when pages are shared on Facebook and Telegram (primary sharing channels in Armenia).

**Phase:** Phase 1 (routing and slug design).

---

### Pitfall N3: Content Scope Creep Beyond Armenian Politics

**What goes wrong:**
Users begin adding content about diaspora politicians, international figures who made statements about Armenia, or Armenian-origin politicians in other countries (e.g., Ruben Vardanyan). Each exception creates moderation overhead, sets a precedent, and dilutes the site's identity. The project file explicitly scopes to Armenian politics only; violating this scope is almost inevitable without clear enforcement.

**Prevention:**
1. **Explicit scope rule in the submission form.** "This site tracks promises made by politicians in the Republic of Armenia's national and local governments."
2. **Rejection template for out-of-scope submissions.**
3. **Admin documentation on scope edge cases** (Artsakh/Nagorno-Karabakh political figures post-2023 is an immediate edge case requiring a decision).

**Warning signs:**
- Submissions for diaspora politicians arriving within first month
- Admins approving out-of-scope entries "just this once"

**Phase:** Phase 1 (submission form copy and admin policy doc). Pre-launch.

---

### Pitfall N4: Promise Text as Editorial Opinion Rather Than Verbatim Quote

**What goes wrong:**
Contributors summarize or paraphrase a politician's promise rather than quoting it directly. The paraphrase introduces an editorial spin. Politicians or their supporters contest the characterization. The disputed wording becomes the argument, not the fulfillment status.

**Prevention:**
1. **Require a verbatim quote from the primary source.** The promise text field should contain the politician's actual words (in Armenian), not a contributor's summary.
2. **Separate fields:** original_quote (verbatim, required), source_url (required), source_date (required), short_summary (optional, for display).
3. **Admin review step specifically checks quote accuracy against the source URL.**

**Phase:** Phase 1 (data model). Phase 2 (submission form UX).

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Data model design | Political entities don't fit clean schema (C2, M5) | Review with real Armenian political data before finalizing |
| User registration system | Sockpuppets and fake accounts (C3) | Account age minimums, email verification, IP logging |
| Voting/status system | No defined fulfillment criteria (C1) | Publish written rubric before any voting goes live |
| Evidence submission | Source rot over time (C4) | Archive URLs at submission time, require quote excerpts |
| Public launch | Legal exposure without entity structure (C2) | Legal consultation before launch |
| Admin tooling | Moderation bottleneck (M4) | Queue-based moderation UI, multiple admins |
| Community growth | Cold start / content stagnation (M2) | Seed 50-100 promises before launch, journalist outreach |
| User contributions | Gamification driving junk (M3) | No gamification in v1 |
| Localization | Armenian text rendering (N1, N2) | utf8mb4 from day one, web font, ASCII slugs |
| Coverage balance | Perceived partisan bias (M1) | Balance dashboard, public methodology page |

---

## Sources

- [Understanding election promise tracking as a form of fact-checking — Nature/Humanities and Social Sciences Communications](https://www.nature.com/articles/s41599-026-06603-7)
- [Armenia's New Digital Disinformation Bills Threaten Free Speech and Press Freedom — CIMA/NED](https://www.cima.ned.org/blog/armenias-new-digital-disinformation-bills-threaten-free-speech-and-press-freedom/)
- [As Armenia legislates libel and insult, journalists worry 'selective justice' — CPJ](https://cpj.org/2022/01/as-armenia-legislates-libel-and-insult-journalists-worry-selective-justice-will-be-used-against-the-press/)
- [Armenian court orders freeze on assets of journalist Davit Sargsyan — CPJ](https://cpj.org/2023/05/armenian-court-orders-freeze-on-assets-of-journalist-davit-sargsyan-and-outlet-168-hours/amp/)
- [Armenia: Freedom on the Net 2023 — Freedom House](https://freedomhouse.org/country/armenia/freedom-net/2023)
- [Armenia: Freedom on the Net 2025 — Freedom House](https://freedomhouse.org/country/armenia/freedom-net/2025)
- [Community Notes are Vulnerable to Rater Bias and Manipulation — arXiv](https://arxiv.org/pdf/2511.02615)
- [Community Notes and potential vote brigading — Conspirator0](https://www.conspirator0.com/p/community-notes-and-potential-vote)
- [The trust-consensus paradox: why decentralized fact-checking faces challenges — ISD Global](https://www.isdglobal.org/digital-dispatch/the-trust-consensus-paradox-why-decentralized-fact-checking-faces-challenges-on-polarizing-topics/)
- [Transparency is Insufficient: Lessons From Civic Technology for Anticorruption — Harvard Ash Center](https://ash.harvard.edu/articles/transparency-is-insufficient-lessons-from-civic-technology-for-anticorruption/)
- [Failed yet successful: Learning from discontinued civic tech initiatives — Academia.edu](https://www.academia.edu/101605660/Failed_yet_successful_Learning_from_discontinued_civic_tech_initiatives)
- [Ideological bias on Wikipedia — Wikipedia](https://en.wikipedia.org/wiki/Ideological_bias_on_Wikipedia)
- [PolitiFact methodology — PolitiFact](https://www.politifact.com/article/2018/feb/12/principles-truth-o-meter-politifacts-methodology-i/)
- [Methodology — PromiseTracker, Code for Africa](https://promisetracker.dev.codeforafrica.org/about/methodology)
- [Internationalization beyond code — Phrase.com](https://phrase.com/blog/posts/internationalization-beyond-code-a-developers-guide-to-real-world-language-challenges/)