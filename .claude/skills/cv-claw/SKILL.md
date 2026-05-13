---
name: cv-claw
description: Work with resumes through the cv-claw CLI — ingest a PDF/image/text resume into the JSON schema, tailor an existing resume JSON for a job description, or create a new visual template (Jinja2 + CSS). Use when the user mentions resumes, CVs, cv-claw, or asks to ingest/import/convert a resume, tailor/adjust a resume for a role, or build/design a resume template. Routes to the right task by reading one reference file on demand.
compatibility: Requires cv-claw installed in the workspace. Render via `cv-claw render resumes/<file>.json`.
---

# cv-claw

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
- Resume JSON files live in `resumes/<name>.json`. Templates live in
  `templates/<name>/`.
- Rendering: `cv-claw render resumes/<name>.json` writes
  `resumes/<name>.html` next to the JSON.
- Validation: `cv-claw validate resumes/<name>.json`.

## What not to do

- **Don't fabricate resume content** during ingest or tailor — work
  faithfully from the source.
- **Don't add new section `kind`s.** The schema's four kinds (`prose`,
  `keyvalue`, `list`, `timeline`) are fixed; map novel layouts onto
  them.
- **Don't edit the source resume** when tailoring — variants go
  alongside it at `resumes/<base>-<slug>.json`.
- **Don't register templates anywhere** — cv-claw auto-discovers
  `templates/<name>/<name>.html.j2`.
