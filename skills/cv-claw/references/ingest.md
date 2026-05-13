# ingest

Convert a resume from any source format (PDF, image, pasted text) into
a cv-claw JSON file.

## What to produce

**One file**: `resumes/<name>.json`, where `<name>` is a short
lowercase-with-hyphens identifier (e.g. `default`, `ada-lovelace`).
If unsure, use `default`.

The file must conform to the schema —
[schema.md](schema.md).

## Procedure

1. **Read the source.** If it's a PDF or image, extract all text. If it's
   pasted text, work with it directly. Don't paraphrase — preserve the
   user's wording, especially in bullets.

2. **Identify the header.** Find the person's name, location, email,
   phone, and any links (LinkedIn, GitHub, portfolio). These go into
   `header`, not into a section.

3. **Identify section boundaries.** Most resumes have visual or
   typographic section breaks (a heading like "EXPERIENCE", then content,
   then another heading like "EDUCATION"). Each becomes one section.

4. **Pick a `kind` for each section** (see the kinds table in
   [schema.md](schema.md)):
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
   - `bullets` is the list of bullet points. For education entries
     without bullets, omit the field entirely.

   For `keyvalue` items:
   - `label` is the category name. Include the trailing `:` if the
     original had one.
   - `value` is the comma-separated content.

6. **Preserve section order** from the original. cv-claw renders
   `sections[]` top-to-bottom in array order.

7. **Write the file** to `resumes/<name>.json`. Pretty-print with
   2-space indentation.

8. **Tell the user where you put it** and what `template` key it uses
   (default to `"classic"` unless asked otherwise).

## Edge cases

- **No clear sections.** Put the whole thing in a single `prose` section
  named "Summary". The user can split it later.
- **Mixed kinds in one section.** Prefer `timeline` and put flat items
  as items without bullets — the renderer handles compact rendering.
- **Skills as one big paragraph.** Split into `keyvalue` rows by
  category if sensible ("Languages:", "Cloud:", etc.). Otherwise keep
  as a single `keyvalue` item with label "Skills:".
- **Header info inside a section.** If "Contact" is a section heading
  in the source, still lift its content into `header`.
- **Markdown formatting in the source.** Strip it. cv-claw renders all
  string fields as plain text.
- **Unknown template.** Default to `"classic"`. If the user asked for a
  template that doesn't exist, use the requested name and tell them
  they'll also need to create it
  (see [create-template.md](create-template.md)).

## What not to do

- **Don't rewrite content.** This is a faithful conversion, not
  tailoring. If the user wants to tailor for a job, that's
  [tailor.md](tailor.md).
- **Don't invent fields.** If the resume has no phone number, omit
  `phone`. Don't insert "N/A" or empty strings.
- **Don't add a `summary` if there isn't one.** Only include sections
  that exist in the source.

## After producing the file

Briefly tell the user:
- Where you wrote the file.
- Which sections you created and what kind each one is.
- The render command: `cv-claw render resumes/<name>.json` (writes
  `resumes/<name>.html` next to the JSON).
- Any judgment calls you made.
