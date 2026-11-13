# Build checkpoints

## Phase 1 — Inspection and backup: repository complete; live-site portion blocked

- [x] Inspected the actual `/workspace/planner` checkout: empty, unborn Git branch; no source, framework, database, deployment files, or existing user data.
- [x] Verified GitHub read access; remote had no branches or commits.
- [x] Read and retained the complete specification; extracted all 29 recipes verbatim.
- [x] Created and reopened `/workspace/backups/planner/before-build.tar.gz`, verified its Git metadata; made private pre-edit copies of subsequently changed files.
- [x] Chose a standalone Python/SQLite implementation based on available tools, leaving the existing website untouched.
- [ ] Inspect real hosting source, database schema, authentication, existing planner behavior, unrelated features, and deployment method. No authorized hosting connection is available; public HTTPS request received proxy 403.
- [ ] Back up and verify the live site's files and database before any live changes.

## Phase 2 — Data and recipes: implemented and tested locally

- [x] Persistent SQLite storage, transactional repeatable versioned seed migration, no duplicate imports.
- [x] All 29 titles and exact ingredient lines verified against the supplied specification; instructions remain blank.
- [x] Structured amounts, units, notes, alternatives and conditional ingredients; unknown amounts retained.
- [x] Recipe create/edit/archive, optional instructions, eligibility flags, editable cost defaults, timestamps.
- [x] Saved edits persist; historical snapshots survive edits and archiving.

## Phase 3 — Planning and history: implemented and tested locally

- [x] Any starting date, exactly 14 consecutive dates, date-only DST-safe arithmetic, Detroit initial date.
- [x] Taco Tuesday, crockpot Thursday, anchored alternating Friday, Saturday defaults/overrides, weekend-only restrictions, crockpot on other days.
- [x] Ranked variety, recent 60-day/future history, consecutive/repeated dinner penalties, higher-cost clustering penalty.
- [x] Bounded deterministic strategy with controllable random seed; useful errors and rollback when eligibility is insufficient.
- [x] Safe save/reopen/regenerate, one assignment per date across overlaps, intentional replacement, previous versions and snapshots.
- [x] Single-dinner edits preserve other dates; retained 112 days of history in tests; no history expiry.

## Phase 4 — Groceries: implemented and tested locally

- [x] Recipe-derived aggregation, exact reliable conversions, incompatible units preserved, unknown quantities and alternatives retained.
- [x] Winter/Summer eggs and Halloween-only Chili sour cream.
- [x] Categories, manual additions, exclusions, quantity overrides, bought checkboxes, stable identifiers and persistence.
- [x] Recalculation on dinner/recipe/season changes; unrelated manual edits remain on dinner changes.
- [x] Plain-text clipboard output with categories and quantities; print layout; honest $300 target.

## Phase 5 — Interface: implemented and tested locally

- [x] Responsive clean vertical layout, starting date/generate, 14 readable dated dinners, groceries below.
- [x] Inline dinner/quantity editing, recipes, history/date lookup/snapshots, season selection, minimal controls.
- [x] Loading/errors, confirmation for archive/regeneration, login, keyboard controls, refresh persistence.
- [x] Desktop 1280px and mobile 375px real Chromium validation without horizontal overflow.

## Phase 6 — Validation: local suite passed

- [x] Mandatory A–M covered by 17 executed tests, including actual Chromium interactions.
- [x] Repeatable migration, exact recipe import, calendar rules across 100 starting dates, DST/year/leap-date cases.
- [x] Quantity/conversion safety, alternatives, conditional/seasonal groceries, edits, archive, regeneration, overlap, retention.
- [x] Unauthenticated writes rejected, login password/rate limit, CSRF and origin checks, static file boundary, logout.
- [x] Browser clipboard, quantity editing, exclusions, recipe CRUD/archive, history, reload, mobile, keyboard, print.
- [x] JavaScript syntax and Python compilation; verified SQLite backup.
- [ ] Verify the unchanged live website and unrelated functionality through hosting access.

## Phase 7 — Deployment: pending hosting access

- [x] Local startup/usage/backup/rollback documented in README.
- [ ] Inspect actual hosting compatibility and access; verify live pre-deployment backups.
- [ ] Deploy using the existing appropriate workflow and configure persistent disk, HTTPS, private authentication, process manager.
- [ ] Verify live assets, migrations, saved recipes/plans, smoke tests and unaffected unrelated pages.

Local screenshots: `/workspace/artifacts/planner/desktop.png` and `/workspace/artifacts/planner/mobile.png`. Browser tests use temporary records, not the personal planner database. Nothing has been committed, pushed, or deployed.
