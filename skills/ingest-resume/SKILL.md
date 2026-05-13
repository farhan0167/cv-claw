---
name: ingest-resume
description: Convert a resume (PDF, image, or pasted text) into a cv-claw JSON file. Use when the user provides an existing resume and wants it rendered through cv-claw, or asks to "ingest", "import", "convert my resume", or similar. Output is a single resumes/<name>.json file conforming to the cv-claw schema.
compatibility: Produces a JSON file. Render via `cv-claw render resumes/<name>.json`.
---

# ingest-resume

Convert a resume from any source format into a cv-claw JSON file.

## When to use

The user has an existing resume — usually a PDF, sometimes a Word doc,
LinkedIn export, or pasted plain text — and wants it represented in
cv-claw's editable JSON format. They'll usually say "ingest", "import",
"convert this", or just drop the file and ask you to "put it in cv-claw".

## What to produce

**One file**: `resumes/<name>.json`, where `<name>` is a short
lowercase-with-hyphens identifier (e.g. `default`, `ada-lovelace`,
`generic`). If you're not sure, use `default`.

The file must conform to the [cv-claw schema](../../SCHEMA.md). Read that
file before producing output — it defines `Resume`, `HeaderData`, the four
section kinds, and the `TimelineItem` shape.

## Procedure

1. **Read the source.** If it's a PDF or image, extract all text. If it's
   pasted text, work with it directly. Don't paraphrase — preserve the
   user's wording, especially in bullets.

2. **Identify the header.** Find the person's name, location, email,
   phone, and any links (LinkedIn, GitHub, portfolio). These go into
   `header`, not into a section.

3. **Identify section boundaries.** Most resumes have visual or
   typographic section breaks (a heading like "EXPERIENCE", then content,
   then another heading like "EDUCATION"). Each becomes one section in
   the output.

4. **Pick a `kind` for each section.** Use the [taxonomy in
   SCHEMA.md](../../SCHEMA.md#the-five-kinds-taxonomy):

   - Paragraph of text → `prose`
   - Label-then-content rows like "Languages: Python, Go" → `keyvalue`
   - Flat list of items (publications, interests) → `list`
   - Items with dates and detail (experience, education, projects) → `timeline`

   When in doubt, prefer `timeline` — it degrades fine when fields are missing.

5. **Map content into each kind's shape.**

   For `timeline` items:
   - `title` is the role/degree/project name.
   - `org` is the company, school, or affiliation.
   - `location` is city/state if present.
   - `dates` is the date range as a string — preserve the original format.
   - `href` is the project/company URL if there's one to link to.
   - `bullets` is the list of bullet points under the item. For education
     entries without bullets, omit the field entirely.

   For `keyvalue` items:
   - `label` is the category name. Include the trailing `:` if the
     original had one.
   - `value` is the comma-separated content.

6. **Preserve section order** from the original resume. cv-claw renders
   `sections[]` top-to-bottom in array order.

7. **Write the file** to `resumes/<name>.json`. Pretty-print with
   2-space indentation.

8. **Tell the user where you put it** and what `template` key it uses
   (default to `"classic"` unless they've asked for something else).

## Edge cases

- **No clear sections.** If the resume is unstructured prose, put the
  whole thing in a single `prose` section named "Summary" or similar.
  The user can split it later.

- **Mixed kinds in one section.** Sometimes "Projects" has both bulleted
  detail items and a flat list. Prefer `timeline` and put the flat items
  as items without bullets — the renderer handles compact-mode rendering.

- **Skills as one big paragraph.** Some resumes have "Skills: Python,
  Go, PostgreSQL, AWS, Docker, ..." as one line. Split sensibly into
  `keyvalue` rows by category if you can ("Languages:", "Cloud:", etc.).
  If splitting feels forced, keep it as a single `keyvalue` item with
  label "Skills:" and the full string as the value.

- **Header info inside a section.** If the original has "Contact" as a
  section heading, still lift its content into `header`. The schema
  treats header as a fixed top-level field, not a section.

- **Markdown formatting in the source.** Strip it. cv-claw renders all
  string fields as plain text — `**bold**` and `_italic_` won't be
  interpreted.

- **Unknown template.** If the user hasn't said which template, use
  `"classic"`. If they've requested a template that doesn't exist yet,
  use the requested name anyway and tell them they'll also need to run
  the `create-template` skill.

## What not to do

- **Don't rewrite content.** This skill is a faithful conversion, not a
  tailoring pass. Bullets keep their original wording. If the user wants
  to tailor for a job, that's the `tailor-resume` skill.
- **Don't invent fields.** If the resume has no phone number, omit
  `phone`. Don't insert "N/A" or empty strings.
- **Don't add a `summary` if there isn't one.** Only include sections
  that exist in the source.

## After producing the file

Briefly tell the user:
- Where you wrote the file (path).
- Which sections you created and what kind each one is.
- The render command: `cv-claw render resumes/<name>.json` (writes
  `resumes/<name>.html` next to the JSON; open in a browser to view or
  print to PDF).
- Anything you had to make a judgment call on (e.g. "I split your skills
  paragraph into four keyvalue rows by category — adjust if you'd rather
  group them differently").
