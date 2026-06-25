---
name: readme-polish
description: >-
  Author/polish a single repository README and optional GitHub/GHE repo metadata when asked to
  create/update README, improve repo polish, About/description, website, topics, or social preview.
  Near miss: whole-codebase or multi-file docs route to code-doc.
---

# Readme-Polish

Improve one repository's front-door `README.md` and optional GitHub/GitHub Enterprise metadata
through one explicit approval gate: analyze real repo signals, propose a structured Repository Polish
Contract, then write/apply only after the user approves that contract.

## Arguments

- `$ARGUMENTS` — Optional repo path (defaults to cwd) and/or mode hint: open-ended default, or
  `menu` / "let me pick" for menu-selection mode.

## Always

- Use exactly one approval gate per attempt: **Repository Polish Contract Approval**.
- Before approval, do not write/overwrite `README.md`, banner/social-preview assets, or GitHub/GHE
  metadata. A README-polish request is not write approval.
- Scope is the single front-door README, assets it references/uses, and approved repo metadata:
  About/description, website URL, topics/tags, and social preview image. Whole-codebase docs,
  architecture guides, and multi-file documentation belong to `code-doc`.
- Default mode is analyze → draft contract → approve/edit → write/apply. Menu-selection mode is
  opt-in only and still uses the same no-write-before-approval gate.
- Treat the approved checklist as the only gate: no diff-preview gate, `.bak` backup, or draft file.
  Use ordinary file edits; git/remote history provide rollback where available.
- Keep scope two-tier: Tier 1 core is Banner, About/Description, Badges, and Repo Metadata; Tier 2
  sections are scouted per repo, not hardcoded from a fixed catalog.
- Every proposed badge, topic, website URL, metadata value, or section must trace to a detected repo
  signal or explicit user instruction. Drop unsupported items; never fabricate facts.
- Offer one banner form per README: ASCII **or** SVG **or** none. For requested banner work,
  optimize for a readable wordmark first: block letters or large text, short tagline, high contrast,
  and no tiny glyph art that collapses in README rendering.
- Generate banner/social-preview artwork with the LLM directly; do not rely on external image
  generators, remote asset services, external fonts, scripts, or network-loaded image content.
- Surface tradeoffs in the contract: banner form, palette, example family, badges, scouted sections,
  metadata values, asset paths, and remote application method.
- Prefer `gh` for GitHub/GHE metadata when authenticated and capable; otherwise stop with concise
  manual steps or ask for method preference. Never request or expose credentials.

## Do

1. Resolve target repo, mode, and whether repo metadata polish is in scope.
2. Analyze before proposing. Ground the contract in:
   - existing README state and human content to preserve;
   - project type, language/frameworks, manifests, structure, audience, and likely usage path;
   - git remote host/owner/repo plus GitHub.com vs. GHE status;
   - existing repo metadata available without new credentials (`gh repo view --json` or equivalent);
   - badge signals: license, CI, package manifests, primary language/tech, coverage config/report;
   - URL/topic signals: package homepage/docs, Pages/docs config, existing links, project domain,
     primary ecosystem, deployment target, existing topics, or explicit user instruction;
   - branding/asset signals: existing logo, palette, social preview, and asset directory pattern
     (`.github/assets/`, `docs/assets/`, `assets/`, or currently referenced image paths).
3. Draft the **Repository Polish Contract** as a structured checklist, not a prose blurb or full
   rendered README. Include only supported items:
   - **Banner** — ASCII xor SVG, readable example family, tagline note; for SVG/social preview, asset
     path, dimensions, and palette/theme;
   - **About / Description** — new or revised summary and evidence source;
   - **Badges** — each badge plus the repo signal that justifies it; omit when no signal exists;
   - **Repo Metadata** — if requested or clearly in scope: current value, proposed value, evidence,
     and apply method (`gh`, API, or manual) for description/About, website URL, topics/tags, and
     social preview;
   - **Scouted sections** — repo-appropriate Tier 2 sections such as Installation, Usage, Features,
     Configuration, Contributing, or License, only when analysis warrants them.
4. For any banner item, load `references/banner-examples.md`. If the user supplied a style example,
   adapt its readable structure, spacing, contrast, and tagline pattern without copying unrelated
   branding. Make the ASCII-vs-SVG tradeoff explicit: ASCII is portable monochrome text in a code
   block; SVG is a committed color/gradient asset that renders on web views but needs an asset path.
5. Resolve SVG/social-preview asset location before approval. Default to `.github/assets/`; reuse an
   established repo asset directory when one exists. README asset references must be relative paths.
6. Separate remote-only metadata from file-backed work. `gh repo edit` may apply description, website,
   and topics when supported and authenticated. If social preview has no supported local API/tool,
   create the approved asset if requested and return manual upload steps instead of pretending it was
   applied remotely.
7. Present the contract and ask once. The user may approve all, deselect items, or request edits.
   Re-prompt only if observed repo/remote state invalidates the contract.
8. After approval, write/apply only approved items: edit `README.md` in place, write approved assets,
   reference them where applicable, and apply approved metadata only through the approved method to
   the resolved repo.
9. Report the approved/deselected items, paths changed, badge signals, metadata applied or left as
   manual steps, banner form/palette/assets, and scouted sections written.

## Load if needed

- Banner, wordmark, ASCII art, SVG hero, social-preview art, or user-supplied banner style example is
  requested/proposed → `references/banner-examples.md`

## Stop if

- The Repository Polish Contract has not been approved.
- A requested write, asset, or metadata change is not in the approved contract.
- A proposed badge, topic, website URL, metadata value, or section lacks a detected repo signal or
  explicit user instruction.
- Target repo, README, remote identity, metadata target, or asset location is ambiguous after
  analysis.
- A GitHub/GHE operation requires credentials, auth-state changes, elevated permissions,
  visibility/default-branch changes, transfer/deletion, or settings outside approved polish metadata.
- Social preview update has no supported local API/tool path; provide the approved asset and manual
  upload steps instead of automating browser-only flows.

## Output

Return mode used, approved/deselected contract items, README write status, banner form and asset path
if any, badges with signals, metadata applied/proposed/manual, social-preview status, scouted sections
written, checks run, and unresolved blockers or declined items.
