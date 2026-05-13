# create-template

Scaffold a new cv-claw template from a design reference.

## When to use

The user wants a new visual layout for their resume. They might:
- Show you a PDF resume whose design they want to match.
- Describe a look ("minimalist, single-column, sans-serif, lots of whitespace").
- Ask for a variant of an existing template ("like classic but with a left sidebar").
- Provide a reference screenshot or Figma export.

## What to produce

**A new folder** at `templates/<name>/` containing:
- `<name>.html.j2` — the Jinja2 entry-point template.
- `<name>.css` — scoped styles, every rule prefixed by the root class.
- `_macros.html.j2` (optional) — section renderers, factored into macros.

`<name>` is lowercase-with-hyphens (`minimalist`, `two-column`,
`academic`).

You do **not** need to register the template anywhere — cv-claw
auto-discovers any `templates/<name>/<name>.html.j2`. Just drop the folder.
Directories starting with `_` are reserved for shared partials and are
skipped by discovery.

## Before you start

Read these in order:
1. [schema.md](schema.md) — the JSON shape your template consumes.
2. [template-anatomy.md](template-anatomy.md) — CSS scoping rules, page sizing, print conventions.
3. [kind-renderers.md](kind-renderers.md) — how each section kind should be rendered.
4. The starter at [../assets/starter/](../assets/starter/) — boilerplate to copy and modify.

Also look at the existing `templates/classic/` in the workspace as a
working reference.

## Procedure

1. **Pick a `<name>`.** Lowercase-with-hyphens. Confirm with the user if
   unsure, or pick something descriptive from the design ("minimalist",
   "two-column", "academic", "creative").

2. **Copy the starter** from `assets/starter/` (relative to this skill)
   into the workspace's `templates/<name>/`. Rename
   `starter.html.j2` → `<name>.html.j2`, `starter.css` → `<name>.css`,
   and replace every occurrence of `starter` (the root CSS class) with
   `<name>`.

3. **Study the design reference.** Identify:
   - Page proportions (most templates target US Letter, 8.5×11in).
   - Header layout (centered name? top-bar? sidebar with photo?).
   - Section heading style (color, weight, divider, all-caps).
   - Per-kind treatments — see [kind-renderers.md](kind-renderers.md).
   - Typography (serif/sans/monospace, sizes, line-height).
   - Color palette (accent, text, muted, rule).

4. **Edit the CSS.** Every rule must be prefixed with `.<name>` to
   prevent cross-template leakage when CSS is inlined into the rendered
   HTML. Use CSS custom properties for the color palette so they're easy
   to tweak.

5. **Edit the template.** Keep the structure from the starter — a header
   block, then `{% for section in resume.sections %}` dispatching over
   `section.kind`. Adjust the per-kind macros to match the design.

6. **Test by running the renderer.** Set `"template": "<name>"` in any
   resume JSON (e.g. `resumes/example.json`) and run:

   ```bash
   cv-claw render resumes/example.json
   ```

   This writes `resumes/example.html` next to the JSON. Open it in a
   browser to inspect. For an iterative loop with auto-reload, run
   `cv-claw serve` (requires the optional `[serve]` extra installed).

7. **Iterate visually.** The user will likely want CSS tweaks after
   seeing it rendered. Treat that as a normal back-and-forth.

## Key conventions (must follow)

- **CSS scoping.** Every rule starts with `.<name>` — no global selectors,
  no leakage. cv-claw inlines the CSS into a single `<style>` block at
  render time, so unscoped rules would clash with other templates if the
  same HTML is ever combined.
- **Page sizing.** A `.page` div inside the root, sized `8.5in × 11in`
  (or whatever the design calls for) with shadowed border in screen mode
  and `@media print { ... box-shadow: none; ... }` for clean printing.
- **Render the header first.** Then dispatch over `sections`.
- **Handle all four kinds** (`prose`, `keyvalue`, `list`, `timeline`)
  even if the current resume doesn't use them all. The user may add
  sections later.
- **Honor `href`** on timeline items and list items where the design
  permits links.
- **Don't break on missing optional fields.** Header `contact` and
  `links` are optional. Timeline `org`, `location`, `dates`, `href`,
  `bullets` are all optional — guard with `{% if ... %}` in Jinja.
- **Autoescape is on.** Jinja2 escapes `{{ var }}` by default, so user
  content is safe. Don't reach for `| safe` unless you have a clear
  reason and the source is trusted.

## What not to do

- **Don't edit the renderer or loader.** Auto-discovery handles
  registration; you only add files under `templates/<name>/`.
- **Don't import from other templates' folders.** Each template is
  self-contained. If you're tempted to share code, put it under
  `templates/_partials/` and `{% include %}` from there — but only when
  three+ templates would actually use it.
- **Don't add new section kinds.** If the design calls for something
  that doesn't fit the existing four, render it under an existing kind
  (usually `timeline` with custom CSS, or `keyvalue`). Adding kinds is a
  schema change, out of scope.
- **Don't use `| safe` on user-provided strings.** Anything from the
  resume JSON should remain autoescaped.

## After producing the template

Tell the user:
- The template name and folder path.
- That cv-claw auto-discovered it — no registration needed.
- How to use it: set `"template": "<name>"` in any resume JSON, then run
  `cv-claw render resumes/<file>.json`.
- Anything you had to make a judgment call on (color choices, fallbacks
  for kinds the design didn't show).
