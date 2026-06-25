# Banner Examples

Load only when `readme-polish` is proposing or creating an ASCII/SVG banner, social-preview asset,
or adapting a user-supplied banner style example. These examples are patterns, not mandatory copy.

## Contract

- Legibility beats decoration: users should read the project name at a glance in GitHub's README
  column, mobile views, and plain text fallbacks.
- Preserve the user's desired qualities: centered wordmark, heavy readable letterforms, high contrast,
  short tagline, and restrained ornamentation.
- Do not copy unrelated project branding, names, taglines, logos, or trademarked identity from a
  supplied example. Adapt the structure and readability instead.
- One README gets one banner form: ASCII xor SVG. Use a social-preview image only when separately
  approved by the Repository Polish Contract.
- SVG assets must be self-contained: no remote fonts, scripts, embedded external images, analytics,
  or network calls. Include `<title>`/`<desc>` and a useful README `alt` value.

## ASCII Wordmark Pattern

Use this when the user wants maximum portability or likes the terminal-style block-letter look.
Replace the words and tagline with repo-specific text discovered during analysis.

```html
<div align="center"><pre>
██████╗ ███████╗ █████╗ ██████╗ ███╗   ███╗███████╗
██╔══██╗██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
██████╔╝█████╗  ███████║██║  ██║██╔████╔██║█████╗
██╔══██╗██╔══╝  ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝
██║  ██║███████╗██║  ██║██████╔╝██║ ╚═╝ ██║███████╗
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝

██████╗  ██████╗ ██╗     ██╗███████╗██╗  ██╗
██╔══██╗██╔═══██╗██║     ██║██╔════╝██║  ██║
██████╔╝██║   ██║██║     ██║███████╗███████║
██╔═══╝ ██║   ██║██║     ██║╚════██║██╔══██║
██║     ╚██████╔╝███████╗██║███████║██║  ██║
╚═╝      ╚═════╝ ╚══════╝╚═╝╚══════╝╚═╝  ╚═╝
        Readable README front doors for polished repositories
</pre></div>
```

ASCII guardrails:

- Keep lines under roughly 100 characters when possible.
- Prefer two short word rows over one ultra-wide row.
- Use plain `<pre>` or fenced code; avoid color escape sequences because GitHub strips or displays
  them inconsistently.

## SVG Hero Pattern

Use this when the user wants color, gradients, and a committed visual asset. Place it in the resolved
asset directory, usually `.github/assets/<repo-slug>-banner.svg`, and reference it relatively.

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="360" viewBox="0 0 1280 360" role="img" aria-labelledby="title desc">
  <title id="title">README Polish</title>
  <desc id="desc">Readable gradient banner with a large README POLISH wordmark and short tagline.</desc>
  <defs>
    <linearGradient id="wordmark" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#67e8f9"/>
      <stop offset="50%" stop-color="#a78bfa"/>
      <stop offset="100%" stop-color="#f472b6"/>
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="20%" r="75%">
      <stop offset="0%" stop-color="#334155" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#020617" stop-opacity="1"/>
    </radialGradient>
  </defs>
  <rect width="1280" height="360" rx="36" fill="url(#glow)"/>
  <text x="640" y="145" text-anchor="middle"
        font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
        font-size="92" font-weight="900" letter-spacing="4" fill="url(#wordmark)">README</text>
  <text x="640" y="240" text-anchor="middle"
        font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
        font-size="92" font-weight="900" letter-spacing="4" fill="url(#wordmark)">POLISH</text>
  <text x="640" y="296" text-anchor="middle"
        font-family="Inter, ui-sans-serif, system-ui, sans-serif" font-size="28" fill="#cbd5e1">
    Readable front doors for polished repositories
  </text>
</svg>
```

README reference:

```md
<p align="center">
  <img src=".github/assets/<repo-slug>-banner.svg" alt="<Project> — <short tagline>" width="100%">
</p>
```

SVG guardrails:

- Use real text for the project name unless a block-character wordmark is explicitly preferred.
- Keep contrast high against both GitHub light and dark surrounding pages.
- Avoid tiny subtitles, dense background grids, low-contrast neon, and decorative strokes that make
  letters harder to read.
