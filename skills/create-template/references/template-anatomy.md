# Template anatomy

The conventions every cv-claw template follows.

## Folder layout

```
templates/<name>/
├── <name>.html.j2     # Jinja2 entry point
├── <name>.css         # scoped styles, inlined by the renderer
└── _macros.html.j2    # (optional) section renderers as Jinja macros
```

The folder name is the template key. It's what users put in their JSON's
`"template": "<name>"` field. cv-claw auto-discovers any folder containing
a `<name>.html.j2` file — no registration needed. Folders whose names
begin with `_` are reserved for shared partials and are skipped by
discovery.

## Render contract

The renderer:

1. Validates the resume JSON against the schema.
2. Resolves `template` → loads `templates/<name>/<name>.html.j2`.
3. Renders with `resume` (a validated `Resume` model) in context.
4. Reads `templates/<name>/<name>.css`, inlines it into a `<style>`
   block, and wraps everything in a complete HTML document.
5. Writes a single self-contained HTML file.

Your template is responsible for the **body** markup only — the
`<!doctype>`, `<head>`, `<style>`, `<body>` shell is added by the
renderer.

## Template structure

```jinja
{# templates/foo/foo.html.j2 #}
<div class="foo">
  <div class="page">

    {# header #}
    <header class="top">
      <div class="name">{{ resume.header.name }}</div>
      {# ...contact + links... #}
    </header>

    {# sections #}
    {% for section in resume.sections %}
      {% if section.kind == "prose" %}        {# ...prose body...    #}
      {% elif section.kind == "keyvalue" %}   {# ...keyvalue body... #}
      {% elif section.kind == "list" %}       {# ...list body...     #}
      {% elif section.kind == "timeline" %}   {# ...timeline body... #}
      {% endif %}
    {% endfor %}

  </div>
</div>
```

Two nested divs:

- **Root** (`.foo`) — the template scope. Every CSS rule for this
  template starts with `.foo`.
- **`.page`** — the printable page. Sized to physical paper dimensions
  with a shadow in screen mode and clean in print mode.

For larger templates, factor the per-kind rendering into a
`_macros.html.j2` file and import it:

```jinja
{% import "foo/_macros.html.j2" as m %}
...
{{ m.timeline(section) }}
```

## Jinja conventions

- **Autoescape is on.** `{{ var }}` is HTML-escaped by default. Do not
  use `| safe` on resume content.
- **Guard optional fields** with `{% if ... %}`. Header `contact` and
  `links` are optional, and timeline items have several optional fields
  (`org`, `location`, `dates`, `href`, `bullets`).
- **Use `loop.last`** when you need to know you're on the final
  iteration (e.g. for `<br>` separators between links).
- **The renderer uses `StrictUndefined`** — referencing a name that
  isn't defined raises an error rather than silently rendering empty.
  This catches typos like `resume.headers.name`.

## CSS scoping

**Every selector must start with the template's root class.** No global
selectors. No bare element selectors. CSS from your template is inlined
into the rendered HTML — without scoping, rules would clash if templates
are ever combined.

```css
/* Good */
.foo h2.section { color: #333; }
.foo .timeline .item-title { font-weight: 700; }

/* Bad — would leak if combined with another template */
h2.section { color: #333; }
.timeline .item-title { font-weight: 700; }
```

Use CSS custom properties on the root for the palette:

```css
.foo {
  --accent: #2f5496;
  --text: #1a1a1a;
  --muted: #666;
  --rule: #ccc;
  font-family: "Inter", sans-serif;
  color: var(--text);
  font-size: 11pt;
  line-height: 1.4;
}
```

## Page sizing

Most templates target US Letter:

```css
.foo .page {
  width: 8.5in;
  min-height: 11in;
  margin: 0 auto;
  background: #fff;
  padding: 0.5in 0.6in;
  box-shadow: 0 2px 10px rgba(0,0,0,0.15);
  box-sizing: border-box;
}
```

A4 alternative: `width: 210mm; min-height: 297mm;` with metric padding.
Pick one — don't try to support both in one template.

## Print rules

Wrap a `@media print` block to clean up for PDF export:

```css
@media print {
  .foo .page {
    margin: 0;
    box-shadow: none;
    width: auto;
    min-height: auto;
    padding: 0.5in 0.6in;
  }
}
```

A global `@page { size: letter; margin: 0 }` rule in the document keeps
the printed page edge-to-edge so your `.page` padding controls the real
margins.

## Typography

- **Font size**: 10–11pt for body, 22–28pt for the name, 12–14pt for
  section headings. Use `pt` units — they print at predictable physical
  sizes.
- **Line height**: 1.3–1.45 for body. Tighter feels cramped, looser
  wastes space.
- **Font family**: pick fonts that exist on most systems
  (Calibri/Carlito, Helvetica/Arial, Georgia, Garamond, Inter) or import
  from a CDN. Always provide fallbacks.

## Color discipline

A typical resume needs only 3–4 colors:

- Accent (section headings, links): a single brand color.
- Text (body): near-black, often `#1a1a1a` instead of pure black.
- Muted (locations, dates): a darker gray.
- Rule (dividers): a light gray or tinted version of the accent.

Don't introduce more colors than the design needs.

## Header conventions

Three common header layouts:

1. **Three-column grid**: contact | name | links. Used by classic.
2. **Stacked centered**: large name, contact line under, links line under.
   Used by the starter.
3. **Sidebar**: name + photo + contact in a left column, sections in the
   right. Heavier design lift; only do if the reference calls for it.

In all cases, render from `resume.header.name`, `resume.header.contact`,
and `resume.header.links`. Guard every optional field with `{% if %}` —
all contact subfields and the `contact`/`links` containers themselves
are optional.
