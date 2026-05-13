# cv-claw resume schema

The canonical shape for a `resumes/*.json` file. All cv-claw skills produce
JSON conforming to this schema; all cv-claw templates render JSON conforming
to this schema.

The schema is **template-agnostic**. The same JSON renders through any
template that supports the section kinds used. Templates decide *how* each
kind looks; the JSON decides *which* sections exist and *in what order*.

---

## Top-level shape

```ts
type Resume = {
  template: string;       // key of a registered template, e.g. "classic"
  header: HeaderData;
  sections: Section[];    // rendered top-to-bottom in array order
};
```

- **`template`** — the template key (folder name under `src/templates/`).
  Required. If unknown, the renderer shows a fallback message instead of
  rendering.
- **`header`** — top-level identity block. Always rendered first by every
  template. See [Header](#header).
- **`sections`** — ordered list of content sections. See [Sections](#sections).

---

## Header

```ts
type HeaderData = {
  name: string;                       // required — the person's name
  contact?: {
    location?: string;
    email?: string;
    phone?: string;
    note?: string;                    // free-form, e.g. visa status
  };
  links?: { label: string; href: string }[];
};
```

Example:

```json
"header": {
  "name": "Ada Lovelace",
  "contact": {
    "location": "London, UK",
    "email": "ada@example.com",
    "phone": "+44 20 7946 0958"
  },
  "links": [
    { "label": "github.com/ada", "href": "https://github.com/ada" }
  ]
}
```

Header is **not** a section. It's a fixed top-level field. Most templates
render it as a three-column block (contact | name | links) or a centered
heading.

---

## Sections

A section is one of four discriminated shapes, each tagged by `kind`. Every
section has a `name` (the human-readable heading, e.g. "Experience") and a
`data` payload whose shape depends on `kind`.

```ts
type Section =
  | { name: string; kind: "prose";    data: { body: string } }
  | { name: string; kind: "keyvalue"; data: { items: { label: string; value: string }[] } }
  | { name: string; kind: "list";     data: { items: { text: string; href?: string }[] } }
  | { name: string; kind: "timeline"; data: { items: TimelineItem[] } };
```

### The five-kinds taxonomy

There are four section `kind`s plus the top-level header. Pick the right
one using these rules of thumb:

| If the content is… | Use |
|---|---|
| A paragraph of free text | `prose` |
| Label/value rows (e.g. "Languages: Python, Go") | `keyvalue` |
| A flat bulleted list of single items, optionally linked | `list` |
| Items with title + dates + (usually) bullets | `timeline` |

When in doubt, prefer `timeline` — it's the most expressive and degrades
fine to "title only" rendering when bullets/org/location are missing.

### `prose`

A paragraph. Use for summaries, objectives, short bios.

```json
{
  "name": "Summary",
  "kind": "prose",
  "data": {
    "body": "Backend engineer with 8 years of experience building distributed systems."
  }
}
```

### `keyvalue`

Label/value rows. Use for **skills grouped by category**, certifications,
awards-with-year, languages spoken.

```json
{
  "name": "Skills",
  "kind": "keyvalue",
  "data": {
    "items": [
      { "label": "Languages:", "value": "Python, TypeScript, Go" },
      { "label": "Backend:",   "value": "FastAPI, PostgreSQL, Redis" }
    ]
  }
}
```

Labels often end with `:` by convention — include the colon in the label
string if you want it shown.

### `list`

Flat bulleted items, each optionally linked. Use for **selected
publications** when full timeline structure is overkill, lists of interests,
references-on-request, or any "just a bunch of strings" section.

```json
{
  "name": "Publications",
  "kind": "list",
  "data": {
    "items": [
      { "text": "Lovelace, A. (1843). Notes on the Analytical Engine.", "href": "https://example.com/notes" },
      { "text": "Lovelace, A. (1842). Translation of Menabrea's Memoir." }
    ]
  }
}
```

### `timeline`

The workhorse kind. Use for **experience, education, projects,
publications-with-detail, volunteer work** — anything where items have a
title, possibly an organization, dates, and bullets describing the work.

```ts
type TimelineItem = {
  title: string;        // "Senior Engineer" | "B.Sc. Computer Science" | "cv-claw"
  org?: string;         // "Stripe" | "MIT" | "Personal Project"
  location?: string;
  dates?: string;       // free-form: "Jan 2023 – Present", "2019", "Q4 2024"
  href?: string;        // project URL, company site, school link
  bullets?: string[];   // omit or leave empty for compact (no-bullets) rendering
};
```

Example with bullets (experience-style):

```json
{
  "name": "Experience",
  "kind": "timeline",
  "data": {
    "items": [
      {
        "title": "Senior Software Engineer",
        "org": "Stripe",
        "location": "San Francisco, CA",
        "dates": "Jan 2023 – Present",
        "bullets": [
          "Shipped X, scaling Y by 3x.",
          "Led a team of 4 to deliver Z."
        ]
      }
    ]
  }
}
```

Example without bullets (education-style):

```json
{
  "name": "Education",
  "kind": "timeline",
  "data": {
    "items": [
      {
        "title": "M.Sc. Computer Science",
        "org": "Stanford University",
        "dates": "2017 – 2019"
      }
    ]
  }
}
```

Templates typically auto-detect "no bullets in any item" → render a compact
inline form (title + org on one line, dates on the right) rather than the
full per-item block.

---

## Field discipline

- **Dates are strings.** No specific format required ("Jan 2023 – Present",
  "2019", "Q4 2024" all valid). Use whatever the original resume used.
- **Markdown is not interpreted.** All string fields render as plain text
  (with the exception of `href` which becomes an actual link). Don't put
  `**bold**` in bullets expecting it to render.
- **Order matters.** `sections[]` renders top-to-bottom. `items[]` within
  a section renders top-to-bottom. Put the most important thing first.
- **Optional fields can be omitted entirely** — don't include them with
  empty strings or empty arrays. Omit `bullets` rather than `"bullets": []`.

---

## A complete minimal example

```json
{
  "template": "classic",
  "header": {
    "name": "Ada Lovelace",
    "contact": { "email": "ada@example.com" }
  },
  "sections": [
    {
      "name": "Summary",
      "kind": "prose",
      "data": { "body": "Mathematician and writer." }
    },
    {
      "name": "Skills",
      "kind": "keyvalue",
      "data": { "items": [{ "label": "Math:", "value": "Analytical engines" }] }
    },
    {
      "name": "Experience",
      "kind": "timeline",
      "data": {
        "items": [
          {
            "title": "Translator and Annotator",
            "org": "Self-employed",
            "dates": "1842 – 1843",
            "bullets": ["Wrote what is considered the first computer algorithm."]
          }
        ]
      }
    }
  ]
}
```
