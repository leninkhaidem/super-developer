---
name: readme-polish
description: >-
  Author/polish a single repository README and optional GitHub/GHE repo metadata when asked to
  create/update README, improve repo polish, About/description, website, topics, or social preview.
  Near miss: whole-codebase or multi-file docs route to code-doc.
---

# Readme-Polish

Author or improve a repository's front-door `README.md` and optional GitHub/GitHub Enterprise repo
metadata through one explicit approval gate: analyze the repo, name exactly what will be changed in a
structured checklist, and write/apply only after the user approves the contract.

## Arguments

- `$ARGUMENTS` — Optional repo path (defaults to cwd) and/or mode hint: open-ended (default) or
  `menu` / "let me pick" for menu-selection mode.

## Always

- Use exactly one approval gate per attempt: **Repository Polish Contract Approval**.
- Present the proposed Repository Polish Contract — a structured checklist covering README items and
  any repo metadata actions — before any file write or remote metadata change.
- Never write/overwrite `README.md`, write/overwrite a banner/social-preview asset, or change GitHub
  or GitHub Enterprise metadata before the user approves the contract.
- Scope is the single front-door `README.md`, any banner/social-preview asset it references or uses,
  and approved repo metadata: About/description, website URL, topics/tags, and social preview image.
  This is not a whole-codebase documentation generator; defer architecture/developer/multi-file docs
  to `code-doc`.
- Default mode is **analyze → draft plan → present contract → approve/edit → write/apply**; the user
  does not start from a blank menu.
- Menu-selection mode is opt-in only (the user asks to pick sections); it converges on the same
  no-write-or-apply-before-approval discipline and is never the default.
- Treat the approved checklist as the only gate: no diff preview, no `.bak` backup, no draft file.
  Write/edit `README.md` and assets with ordinary tooling; git history and remote audit history
  provide rollback where available.
- Keep enhancement scope two-tier: Tier 1 core (Banner, About/Description, Badges, Repo Metadata) is
  first-class; Tier 2 sections are scouted per-repo. Do not hardcode a fixed catalog of non-core
  sections.
- Make every proposed badge, topic, website URL, or metadata value trace to a detected repo signal or
  explicit user instruction; propose no item when no signal exists and never fabricate facts.
- Offer the banner as ASCII **or** SVG, mutually exclusive — one README gets one or neither, never
  both.
- Generate banner/social-preview artwork with the LLM directly
- Surface every choice with a tradeoff (banner form, palette, scouted sections, badge set, metadata
  values, remote application method) in the contract so the user decides before write/apply.
- Prefer `gh` for GitHub/GHE metadata when authenticated and capable; otherwise stop with exact
  manual steps or ask for the user's preferred method. Never request or expose credentials.

## Do

1. Resolve the target repo (default cwd), mode (open-ended default, or menu-selection if requested),
   and whether repo metadata polish is in scope from the user's request.
2. Analyze the repository to ground every proposal in real facts:
   - existing `README.md` (present/absent, size, template-like vs. substantial, human content to
     preserve);
   - project type, primary language, frameworks, structure, package manifests, and likely audience;
   - Git remote host/owner/repo and whether it is GitHub.com or GitHub Enterprise;
   - existing repo metadata if available without new credentials (`gh repo view --json` or equivalent):
     description/About, homepage/website URL, repository topics, and visibility constraints;
   - badge signals: license file (`LICENSE`, `LICENSE.md`), CI config (`.github/workflows/`,
     `.gitlab-ci.yml`, etc.), package manifest (`package.json`, `pyproject.toml`, `Cargo.toml`,
     `go.mod`, etc.), primary language/tech, coverage config/report;
   - URL signals for website/homepage: package manifest homepage/docs, Docusaurus/Vite/Pages config,
     docs site links, existing README links, or explicit user instruction;
   - topic/tag signals: project name/domain, primary language, frameworks, package ecosystem,
     deployment target, and existing topics;
   - branding signals for palette and social preview (existing logo, brand colors, project identity);
   - existing asset pattern/dir (`.github/assets/`, `docs/assets/`, `assets/`, images referenced by
     an existing README) for SVG/social-preview placement.
3. Build the proposed plan as a **structured per-section checklist**, not a prose blurb and not a
   full pre-rendered README draft. Each item carries a short note on what will be added/changed:
   - **Banner** — chosen form (ASCII xor SVG) + note; for SVG, resolved asset path and palette/theme;
   - **About / Description** — new or revised README summary;
   - **Badges** — fact-detected set, each item naming the repo signal it traces to (omit entirely if
     no signal);
   - **Repo Metadata** — only if requested or clearly part of repo polish: About/description, website
     URL, topics/tags, and social preview image, each showing current value, proposed value, evidence,
     and apply method (`gh`, API, or manual);
   - **Scouted sections** (Tier 2) — repo-appropriate additions (e.g. Installation, Usage, Features,
     Configuration, Contributing, License) proposed only because repo analysis warrants them.
4. For the banner item, make the ASCII-vs-SVG tradeoff visible: ASCII is portable monochrome plain
   text in a code block (renders everywhere, zero deps); SVG is a committed color/gradient vector
   asset (renders on GitHub/GitLab web, not in plain-text views, requires an asset file + path ref).
5. For SVG/banner/social-preview assets, resolve the asset location: default to `.github/assets/`;
   if the repo already has an established asset pattern/dir, reuse that instead. Reference README
   assets by **relative path**. Surface palette/theme and dimensions in the contract for tweaking.
6. For repo metadata, separate file-backed values from remote-only values:
   - description/About, website URL, and topics/tags may be applied with `gh repo edit` when supported
     by the target host and authenticated account;
   - social preview image is commonly remote UI-only or host/version-dependent; if no supported local
     API/tool is available, create/commit the approved image asset if requested and return concise
     manual upload steps instead of pretending it was applied.
7. Present the Repository Polish Contract checklist and let the user **approve all, deselect
   individual items, or request edits**. The approved checklist is the contract. Ask once; do not
   re-prompt for staged re-approvals unless observed repo or remote state invalidates the contract.
8. After approval, write/apply only approved items:
   - write/edit `README.md` in place with ordinary tooling (new file or in-place edit);
   - when an SVG banner or social-preview asset was approved, write the asset to the resolved path
     and reference it where applicable;
   - apply approved GitHub/GHE metadata only through the approved method and only to the resolved
     repository;
   - do not create diff previews, `.bak` backups, or draft files.
9. Report what changed: README path, banner/social-preview asset paths, badges and their signals,
   metadata values applied or left as manual steps, and scouted sections written.

## Stop if

- The user has not yet approved the Repository Polish Contract — never write/overwrite `README.md`,
  write/overwrite assets, or change remote metadata before approval.
- A requested write or metadata change is not an item in the approved contract.
- A proposed badge, topic, website URL, metadata value, or section cannot be traced to a real detected
  repo signal or explicit user instruction — drop it rather than fabricate.
- The request is for whole-codebase documentation, architecture/developer guides, or multi-file doc
  generation — that is `code-doc`'s territory, not this skill's.
- The target repo, README, remote repository identity, metadata target, or asset location is ambiguous
  and cannot be resolved from analysis — clarify before proposing.
- The GitHub/GHE operation would require credentials, changing auth state, elevated permissions,
  visibility/default-branch changes, repository transfer/deletion, or settings outside approved
  polish metadata — stop and ask or provide manual instructions.
- A social preview update has no supported local API/tool path — do not automate browser-only flows;
  provide the approved asset and manual upload steps.

## Output

Return:

- mode used (default analyze-propose or menu-selection);
- the approved Repository Polish Contract checklist (items approved / deselected / edited);
- `README.md` written or updated (new vs. in-place);
- banner form chosen (ASCII, SVG, or none) and, for SVG, the asset path and palette;
- badges added, each with the repo signal it traces to;
- repo metadata applied or proposed: About/description, website URL, topics/tags, social preview;
- social-preview asset path and whether it was applied remotely or requires manual upload;
- scouted (Tier 2) sections written;
- any items the user declined.
