# Diesel Designs — Dinner & Grocery Planner

A private, mobile-friendly dinner planner: 29 editable family recipes, 14 calendar days, permanent meal rules, saved history, and a combined grocery list. Built with Python 3.12+, SQLite, and plain HTML/CSS/JavaScript. No third-party runtime dependencies or external recipe services.

## Start in this cloud environment

```bash
cd /workspace/planner
./bin/start
```

The server defaults to port 8000 on loopback. The first run creates a random private password in `/workspace/private/planner/password` (mode 600); it never prints it or includes it in Git. To retrieve it yourself in your terminal:

```bash
cat /workspace/private/planner/password
```

You can instead supply your own `PLANNER_PASSWORD` (12+ characters) through secure environment settings, or point `PLANNER_PASSWORD_FILE` to a private file. Do not put passwords into source or chat. Database records default to `/workspace/private/planner/planner.sqlite3`. Set `PLANNER_DB` to a persistent private path on the real host. Live processes must restart in future tasks; files and database must be retained. Each cloud task is isolated; use the existing checkout, without creating a worktree unless requested.

Open the planner through your development environment's supported browser connection. Unlock, select any starting date, and choose **Generate 2 Weeks**. Select **Change** on a date to replace that dinner; the grocery list recalculates. Use **Have it** for pantry items, **Edit** for quantities, or add extras below the list. These changes persist. **Manage Recipes** supports adding, editing and archiving. **History** reopens saved menus and shows immutable earlier versions with their recipe ingredients. The season selector controls egg shopping only.

## Safety and data behavior

- Initial seed is imported once in an atomic migration, preserving every supplied ingredient line and blank instructions. Cost categories are editable defaults.
- Tuesdays require taco eligibility; Thursdays require crockpot eligibility. Eat-out Fridays use the October 16, 2026 anchor. Saturdays default to Fend for Yourself and allow manual dinners. Weekend-only recipes are rejected on weekdays.
- Calendar arithmetic uses date objects, independent of daylight saving; the initial date uses America/Detroit.
- One current dinner per date. Overlapping menus share those dates; ordinary generation preserves saved dinners. Regeneration requires explicit confirmation, snapshots affected menus, replaces shared dates and resets the selected menu's grocery edits. Other menus keep their own shopping edits.
- Dinner snapshots and previous versions remain indefinitely. Recipe edits affect current grocery calculations, while historical snapshots retain the recipe originally selected. Archiving never destroys history.
- Quantities combine using exact volume/weight conversions only. Counts, weight, large cans, regular cans, flavor variants, unspecified amounts, and alternatives stay distinguishable. An alternative remains a single choice on the list. Sour cream on Chili is included only on October 31. Eggs are omitted only when Summer is selected.
- Enchiladas & Rice is flagged for review: rice was not supplied as an ingredient and is not invented.
- $300 is a target, with no fabricated estimate. Ranking penalizes higher-cost clusters and recent repeats after enforcing hard restrictions.
- All APIs require a password session. Writes additionally require a CSRF token; cookies are HttpOnly and SameSite=Strict. Input is parameterized and displayed using text nodes. Login attempts are rate limited. Only three explicitly named static assets and the index are served. Database, backups and secrets are outside static assets.
- A server restart ends login sessions, but preserves recipes, dinners, shopping edits, settings and history.

## Validate

```bash
cd /workspace/planner
python -m unittest discover -s tests -v
node --check static/app.js
python -m compileall -q planner tests
```

The full suite includes actual Chromium interactions, desktop and 375px mobile checks, clipboard, printing, keyboard navigation, persistence, security, and all mandatory cases A–M. Browser tests use an isolated temporary database and `/usr/bin/chromium`. This cloud already provides Playwright and Chromium. On another machine, install `requirements-dev.txt` into a virtual environment and provide Chromium at that path. Without Playwright the browser test is explicitly skipped; that does **not** meet full acceptance.

## Backups and rollback

Before editing existing source files, make and verify a backup outside the served directory. The verified initial checkout archive is `/workspace/backups/planner/before-build.tar.gz`; development revision copies are in that same private directory. A verified initial seeded database backup is `/workspace/backups/planner/initial-seeded.sqlite3`.

For a live database use SQLite's backup API, not a bare copy of a database with active WAL files:

```bash
cd /workspace/planner
python -m planner.server --backup /workspace/backups/planner/pre-change-UNIQUE.sqlite3
```

An existing backup target is refused. The backup is checked with `PRAGMA integrity_check`. For rollback: stop only this planner service, preserve another backup of its current database, restore a chosen verified backup to `PLANNER_DB`, remove stale WAL/SHM companions only while the service is stopped and backed up, and restart. Restore source from a verified source archive if needed. Never restore over a running database or expose backups from a web directory.

## Live deployment is pending

The connected repository was empty. No live server files, database, authentication configuration, or deployment credentials were attached. The public site request was blocked by the cloud network policy. This implementation has **not** replaced or modified the live website. Existing hosting compatibility and unrelated live pages cannot yet be verified.

Before deployment, inspect the actual hosting and current planner, back up source and database there, and choose a compatible service/reverse-proxy configuration. This application requires a persistent Python process and SQLite-capable persistent disk. It must not be uploaded as static files or assumed to work on PHP-only hosting. A hosting-specific adaptation may be necessary.

For HTTPS deployment at `/planner/`, proxy that prefix to this service with the prefix stripped, preserving the public Host header; redirect `/planner` to `/planner/`. The frontend uses prefix-relative assets/APIs. Keep other site routes untouched. Set `PLANNER_SECURE_COOKIE=1` when HTTPS terminates at the reverse proxy. Restrict backend access to the proxy. Set a private persistent `PLANNER_DB`, configure a password securely, and register the process with the host's existing service manager. Do not serve the project root. Verify live authentication, 14-day generation, saved edits, backup/restore, and surrounding site pages before declaring deployment complete.
