---
name: readme-polish
description: >
  Author or upgrade a single repository's front-door README.md — analyze the repo, propose a
  structured per-section checklist contract, and only after the user approves or edits it,
  write/update README.md. Use when the user wants to create/update a README, polish a README,
  make a repo look professional or complete, or add a banner, badges, About/description, or
  README sections. Front-door README authoring only — for whole-codebase documentation,
  architecture guides, developer guides, or multi-file doc generation, use code-doc instead.
---

# Readme-Polish

Author or improve a repository's single front-door `README.md` through one explicit approval gate:
analyze the repo, name exactly what will be created/changed in a structured checklist, and write only
after the user approves the plan.

## Arguments

- `$ARGUMENTS` — Optional repo path (defaults to cwd) and/or mode hint: open-ended (default) or
  `menu` / "let me pick" for menu-selection mode.

## Always

- Use exactly one approval gate per README attempt: **README Contract Approval**.
- Present the proposed README Contract — a structured per-section checklist — before any file write.
- Never write or overwrite `README.md` or any banner asset before the user approves the contract.
- Scope is the single front-door `README.md` plus any banner asset it references. This is not a
  whole-codebase documentation generator; defer architecture/developer/multi-file docs to `code-doc`.
- Default mode is **analyze → draft plan → present contract → approve/edit → write**; the user does
  not start from a blank menu.
- Menu-selection mode is opt-in only (the user asks to pick sections); it converges on the same
  no-write-before-approval discipline and is never the default.
- Treat the approved checklist as the only gate: no diff preview, no `.bak` backup, no draft file.
  Write/edit `README.md` with ordinary write/edit tooling; git history provides any rollback.
- Keep enhancement scope two-tier: Tier 1 core (Banner, About/Description, Badges) is first-class;
  Tier 2 sections are scouted per-repo. Do not hardcode a fixed catalog of non-core sections.
- Make every proposed badge trace to a detected repo signal; propose no badges when no signal exists
  and never fabricate a badge.
- Offer the banner as ASCII **or** SVG, mutually exclusive — one README gets one or neither, never both.
- Generate both banner forms with the LLM directly; do not assume any external ASCII tooling
  (figlet/toilet/pyfiglet/boxes/lolcat) is installed.
- Surface every choice that has a tradeoff (banner form, palette, scouted sections, badge set) in the
  contract so the user decides before write.

## Do

1. Resolve the target repo (default cwd) and mode (open-ended default, or menu-selection if the user
   asked to pick sections themselves).
2. Analyze the repository to ground every proposal in real facts:
   - existing `README.md` (present/absent, size, template-like vs. substantial, human content to preserve);
   - project type, primary language, frameworks, and structure;
   - badge signals: license file (`LICENSE`, `LICENSE.md`), CI config (`.github/workflows/`,
     `.gitlab-ci.yml`, etc.), package manifest (`package.json`, `pyproject.toml`, `Cargo.toml`,
     `go.mod`, etc.), primary language/tech, coverage config/report;
   - branding signals for palette (existing logo, brand colors, project identity);
   - existing asset pattern/dir (`.github/assets/`, `docs/assets/`, `assets/`, images referenced by
     an existing README) for SVG fallback placement.
3. Build the proposed plan as a **structured per-section checklist**, not a prose blurb and not a
   full pre-rendered README draft. Each item carries a short note on what will be added/changed:
   - **Banner** — chosen form (ASCII xor SVG) + note; for SVG, the resolved asset path and the
     agent-proposed palette/theme;
   - **About / Description** — new or revised;
   - **Badges** — the fact-detected set, each item naming the repo signal it traces to (omit entirely
     if no signal);
   - **Scouted sections** (Tier 2) — repo-appropriate additions (e.g. Installation, Usage, Features,
     Configuration, Contributing, License) proposed only because the repo analysis warrants them.
4. For the banner item, make the ASCII-vs-SVG tradeoff visible: ASCII is portable monochrome plain
   text in a code block (renders everywhere, zero deps); SVG is a committed color/gradient vector
   asset (renders on GitHub/GitLab web, not in plain-text views, requires an asset file + path ref).
5. For an SVG banner, resolve the asset location: default to `.github/assets/banner.svg`; if the repo
   already has an established asset pattern/dir, reuse that instead. Reference the committed SVG from
   the README by **relative path**. Propose a palette derived from branding signals or a sensible
   default, surfaced in the contract for tweaking.
6. Present the README Contract checklist and let the user **approve all, deselect individual items,
   or request edits**. The approved checklist is the contract. Ask once; do not re-prompt for staged
   re-approvals unless observed repo state invalidates the contract.
7. After approval, write only approved items:
   - write/edit `README.md` in place with ordinary tooling (new file or in-place edit);
   - when SVG was approved, write the asset to the resolved path (overwrite in place if one exists,
     per the normal write/edit discipline) and reference it by relative path;
   - do not create diff previews, `.bak` backups, or draft files.
8. Report what was written: README path, banner form/asset path if any, badges added with their
   signals, and scouted sections written.

## Stop if

- The user has not yet approved the README Contract — never write or overwrite `README.md` or any
  banner asset before approval (binds AC-1: README-MODE-001, README-WRITE-006). Present the checklist
  and wait.
- A requested write is not an item in the approved contract.
- A proposed badge or section cannot be traced to a real detected repo signal — drop it rather than
  fabricate; do not invent facts.
- The request is for whole-codebase documentation, architecture/developer guides, or multi-file doc
  generation — that is `code-doc`'s territory, not this skill's.
- The target repo, the README to author, or the SVG asset location is ambiguous and cannot be
  resolved from analysis — clarify before proposing.
- A write would require a destructive action, a new dependency/service, credentials, or any side
  effect outside writing the approved `README.md` and its referenced banner asset.

## Output

Return:

- mode used (default analyze-propose or menu-selection);
- the approved README Contract checklist (items approved / deselected / edited);
- `README.md` written or updated (new vs. in-place);
- banner form chosen (ASCII, SVG, or none) and, for SVG, the asset path and palette;
- badges added, each with the repo signal it traces to;
- scouted (Tier 2) sections written;
- any items the user declined.
