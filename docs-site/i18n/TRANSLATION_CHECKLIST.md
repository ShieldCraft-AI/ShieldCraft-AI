# ShieldCraft AI i18n Implementation Checklist

Purpose
-------
This checklist is an ordered, incremental plan to implement i18n for ShieldCraft AI docs-site. It focuses on automation-first but supports human review. We start with a small pilot (the homepage) to validate the pipeline, then scale.

How to use
---------
- Work top-to-bottom. Each item is actionable and small.
- Mark items as "[x]" when complete and update notes if needed.
- Keep this file in the repo as a single source of truth for progress.

Owner: @<team-member> (replace with actual names)
Contact: translation@shieldcraft-ai.example (placeholder)

Priority & Estimates
-------------------
- Pilot (homepage): 1 day
- Automate extraction + CI: 2–4 days
- TMS integration and rollout: 3–10 days depending on scope


PHASE 0  -  PREPARATION
---------------------
- [ ] 0.1 Confirm i18n is enabled in `docusaurus.config.*` (locales + defaultLocale). (Done)
- [ ] 0.2 Decide initial locales for pilot and rollout (e.g., `es`, `fr`). (Owner)
- [ ] 0.3 Create this checklist file and add to repo. (Done)


PHASE 1  -  PILOT (Homepage)
--------------------------
Goal: Validate extraction → translation → build → smoke-test using the homepage.

- [ ] 1.1 Identify the homepage source file.
      - Path examples: `docs-site/src/pages/index.tsx` or `docs-site/docs/site/intro.md`  -  locate the actual file.
      - Owner: Dev

- [ ] 1.2 Make UI strings translatable in the homepage component.
      - Replace hard-coded text with Docusaurus Translate helpers or `translate()`:
        - JSX: `<Translate id="home.hero.title">Your hero title</Translate>`
        - Hook: `const {translate} = useDocusaurusContext()` or `useTranslation()` where relevant.
      - Owner: Dev

- [ ] 1.3 Extract translation messages for `en` (source).
      - Command (from `docs-site` root):
        ```bash
        npx docusaurus write-translations
        ```
      - This creates message files under `docs-site/i18n/<locale>/...` and a `messages.json` for `en`.
      - Owner: Dev

- [ ] 1.4 Produce initial machine translations for pilot locales (MT draft).
      - Option A: Use TMS (Crowdin/Lokalise) to auto-translate.
      - Option B: Use local MT (DeepL or Google) scripts to fill `i18n/<locale>/*.json`.
      - Owner: Dev / Localization team

- [ ] 1.5 Import/pull translations into repo under `docs-site/i18n/<locale>/`.
      - If using TMS, pull via CLI or web UI.
      - Otherwise commit the generated JSONs.
      - Owner: Dev

- [ ] 1.6 Build the localized site and run a smoke test for the homepage.
      - Commands:
        ```bash
        npm run build
        # or
        npx docusaurus build
        ```
      - Verify homepage at `/?locale=es` and `/?locale=fr` or `/es/`.
      - Owner: Dev / QA

- [ ] 1.7 Have a native reviewer quickly review the homepage translations.
      - Mark corrections in TMS or update files directly.
      - Owner: Native reviewer / PM

- [ ] 1.8 Accept pilot results and decide automated cadence and TMS choices.
      - Owner: Product / Localization lead


PHASE 2  -  COMPONENT STRINGS & SITE UI
------------------------------------
- [ ] 2.1 Identify other React components with hard-coded text (header, footer, buttons).
- [ ] 2.2 Replace text with `<Translate>` or `useTranslation()`.
- [ ] 2.3 Re-run `write-translations` and confirm message extraction.


PHASE 3  -  DOCS TRANSLATION SCAFFOLD
----------------------------------
- [ ] 3.1 Choose translation strategy for docs:
    - Manual parallel MD files under `i18n/<locale>/docusaurus-plugin-content-docs/<version>/...` (full control), or
    - Extract translatable strings and translate JSONs (good for TMS workflows).
- [ ] 3.2 For pages that need exact localized content, create localized Markdown files in the i18n tree.
- [ ] 3.3 For high-volume docs, integrate TMS and rely on translators to edit via the TMS UI.


PHASE 4  -  AUTOMATION & CI
-------------------------
- [ ] 4.1 Add scripts to repo for extraction and sync:
    - `scripts/extract-i18n.sh`  -  runs `docusaurus write-translations`
    - `scripts/push-to-tms.sh`  -  optional
    - `scripts/pull-from-tms.sh`  -  optional
- [ ] 4.2 Add GitHub Action to:
    - Run extraction/write-translations on schedule or on changes to `main`.
    - Pull translations from TMS (or from repo)
    - Build site for all locales
    - Run smoke tests (Playwright) asserting localized strings exist
    - Post artifact / deploy to staging


PHASE 5  -  TMS & TRANSLATION MANAGEMENT
-------------------------------------
- [ ] 5.1 Select a TMS (Crowdin, Lokalise, Phrase, etc.) and create a project.
- [ ] 5.2 Configure automatic MT in TMS for draft translation.
- [ ] 5.3 Configure reviewer workflow and QA checks (glossary, spellcheck).
- [ ] 5.4 Set up syncing hooks or CI scripts to automate push/pull.


PHASE 6  -  QA, VISUAL & MONITORING
--------------------------------
- [ ] 6.1 Add pseudo-localization job to CI to detect layout issues.
- [ ] 6.2 Add visual regression tests for a sample set of localized pages.
- [ ] 6.3 Add link/SEO checks for localized sitemaps and meta tags.


PHASE 7  -  ROLLOUT
-----------------
- [ ] 7.1 Define rollout order (e.g., es → fr → other locales) and schedule.
- [ ] 7.2 Monitor translation coverage and user feedback.
- [ ] 7.3 Iterate on TMS rules and automation cadence.


Detailed pilot checklist  -  homepage (to run now)
------------------------------------------------
- [ ] A. Locate the homepage file and identify all visible strings.
- [ ] B. Replace strings with `<Translate id="home.<key>">Default text</Translate>`.
- [ ] C. Run `npx docusaurus write-translations`.
- [ ] D. Generate/pull MT for `es` and `fr` for the produced message files.
- [ ] E. Add the resulting `i18n/es` and `i18n/fr` message bundles to the repo (or import to TMS and then pull).
- [ ] F. Build the site and verify the homepage under `/es/` / `/?locale=es`.
- [ ] G. Collect reviewer feedback and iterate.


Verification & acceptance criteria for pilot
-------------------------------------------
- A localized homepage is served at `/es/` and `/fr/`.
- Navbar and locale dropdown show the proper language names.
- No 404s for localized assets referenced on the homepage.
- A native reviewer accepts the language for the homepage.


Notes & tips
-----------
- Use stable translation IDs. If you rename keys frequently, translators and TMS will have more churn.
- For variable strings (e.g., `Hello {name}`) use value interpolation supported by `<Translate>`.
- Keep images without embedded text where possible; otherwise create localized image variants.


Next action (recommended immediate step)
--------------------------------------
If you want me to implement the pilot I will:
1. Locate the homepage source file here and convert hard-coded strings to `<Translate>`.
2. Run `npx docusaurus write-translations` and commit the generated `i18n` message bundles (MT drafts) for `es` and `fr`.
3. Build and run a local smoke test for `/es/` and `/fr/` and report results.

Pick one: "I want you to run the pilot" or "I'll do the homepage edits myself".

---
Last updated: 2025-10-09
