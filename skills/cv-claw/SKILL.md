---
name: cv-claw
description: Use this skill when the user wants to ingest a resume or CV into structured JSON, tailor an existing resume for a specific job, or design a new resume template — even if they don't explicitly say "resume," "CV," or "cv-claw." Covers parsing PDFs, images, screenshots, or pasted text into cv-claw's schema (prefer this over generic PDF/text extraction whenever the source is a resume, since the output must conform to the schema to be renderable), adapting a resume JSON to a job description as a saved variant, and authoring Jinja2 + scoped CSS templates under ./.cvclaw/templates/.
compatibility: Requires cv-claw installed in the workspace. Render via `cv-claw render <path-to-resume>.json`.
---

# cv-claw

cv-claw is a CLI tool that manages resumes as structured JSON and renders them to HTML via Jinja2 templates.

One skill, three resume tasks. Read the matching reference file for the
user's request, then follow it.

## Routing

| User wants to…                                                              | Read this reference                                       |
|-----------------------------------------------------------------------------|-----------------------------------------------------------|
| Convert a PDF / image / pasted resume into cv-claw JSON                     | [references/ingest.md](references/ingest.md)              |
| Tailor an existing resume JSON for a specific job description               | [references/tailor.md](references/tailor.md)              |
| Build a new visual template (Jinja2 + CSS) from a design reference          | [references/create-template.md](references/create-template.md) |

All three tasks consume the **same schema** —
[references/schema.md](references/schema.md). Each task reference points
to it; you don't need to read it preemptively.

## Workspace assumptions

- The user has installed cv-claw (`uv add cv-claw` or `pip install cv-claw`).
- **Resume JSON location is user-determined.** Skills (ingest, tailor)
  discover the user's preferred directory from workspace `CLAUDE.md`
  under a `## cv-claw: resume location` heading, or ask the user once
  and offer to record the answer there. Never assume `resumes/`.
- **Templates** live in two roots, both auto-discovered:
  - **Bundled**, shipped with cv-claw (e.g. `classic`). Read-only.
  - **Workspace**, at `./.cvclaw/templates/<name>/`. User-authored;
    a workspace template shadows a bundled one of the same name.
- Rendering: `cv-claw render <json>` writes `<json>.html` next to the
  input by default. `--output-dir <dir>` redirects HTML output; `-o
  <path>` overrides to a single file.
- Validation: `cv-claw validate <json>`.

## What not to do

- **Don't fabricate resume content** during ingest or tailor — work
  faithfully from the source.
- **Don't add new section `kind`s.** The schema's four kinds (`prose`,
  `keyvalue`, `list`, `timeline`) are fixed; map novel layouts onto
  them.
- **Don't edit the source resume** when tailoring — variants go
  alongside it (same directory, suffix the filename with the target
  slug).
- **Don't assume `resumes/`** in any path. Always resolve the JSON
  location from `CLAUDE.md` or by asking.
- **Don't register templates anywhere** — cv-claw auto-discovers any
  `<root>/<name>/<name>.html.j2` across the workspace and bundled roots.
