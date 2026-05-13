# Schema

Authoritative implementation: pydantic models in `src/cvclaw/schema.py`
(strict — unknown fields fail validation). Validate any file with
`cv-claw validate <file.json>`.

## Models

```python
class Link(BaseModel):
    label: str
    href: str

class Contact(BaseModel):
    location: str | None = None
    email: str | None = None
    phone: str | None = None
    note: str | None = None         # free-form, e.g. visa status

class Header(BaseModel):
    name: str
    contact: Contact | None = None
    links: list[Link] = []

class TimelineItem(BaseModel):
    title: str
    org: str | None = None
    location: str | None = None
    dates: str | None = None        # free-form: "Jan 2023 – Present", "2019"
    href: str | None = None
    bullets: list[str] = []         # empty → item renders compactly

class Resume(BaseModel):
    template: str                   # template key, e.g. "classic"
    header: Header
    sections: list[Section]         # rendered top-to-bottom
```

`Section` is a discriminated union on `kind`. Every section has a `name`
(the heading) and a `data` payload whose shape depends on `kind`:

| `kind`     | `data` shape                                            | Use for                                       |
|------------|---------------------------------------------------------|-----------------------------------------------|
| `prose`    | `{ body: str }`                                         | Summary, objective, short bio                 |
| `keyvalue` | `{ items: [{ label: str, value: str }] }`               | Skills by category, certifications, languages |
| `list`     | `{ items: [{ text: str, href: str \| None }] }`         | Publications, interests, references           |
| `timeline` | `{ items: [TimelineItem] }`                             | Experience, education, projects               |

## Field discipline

- Dates are free-form strings — preserve the source's format.
- String fields render as plain text; only `href` becomes a link.
  Don't put markdown like `**bold**` in bullets.
- `sections[]` and each section's `items[]` render top-to-bottom.
- Omit optional fields entirely rather than including them as `""` or
  `[]`. Omit `bullets` rather than `"bullets": []`.

## Jinja access (templates only)

In a template, the validated `Resume` is bound to `resume`. Access
fields by attribute (`resume.header.name`, `section.data.items`). All
optional fields can be missing, so guard with `{% if ... %}`.

## Short example

```json
{
  "template": "classic",
  "header": {
    "name": "Ada Lovelace",
    "contact": { "location": "London, UK", "email": "ada@example.com" },
    "links": [{ "label": "github.com/ada", "href": "https://github.com/ada" }]
  },
  "sections": [
    {
      "kind": "prose",
      "name": "Summary",
      "data": { "body": "Mathematician and analyst." }
    },
    {
      "kind": "timeline",
      "name": "Experience",
      "data": {
        "items": [
          {
            "title": "Analyst",
            "org": "Analytical Engine Project",
            "dates": "1843",
            "bullets": ["Published the first algorithm intended for a machine."]
          }
        ]
      }
    }
  ]
}
```
