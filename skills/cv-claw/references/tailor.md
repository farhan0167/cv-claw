# tailor

Produce a job-specific variant of an existing resume.

## When to use

The user has:
1. A resume already ingested as a cv-claw JSON file (or one they're
   about to ingest — see [ingest.md](ingest.md)), AND
2. A specific job description they want to apply for.

## What to produce

**A new file** at `<dir>/<base>-<slug>.json`, where:
- `<dir>` is the directory that holds the source resume — variants
  live next to their source, never in a different directory. If the
  user passed an absolute path, write the variant next to it.
- `<base>` is the source resume's filename (without `.json`).
- `<slug>` is a short identifier for the target job — usually the
  company name lowercased and hyphenated, e.g. `default-stripe.json`,
  `ada-acme-corp.json`.

**Never overwrite the source.** The user keeps the original as their
canonical resume; tailored variants live alongside it.

The output must conform to the schema — [schema.md](schema.md). Same
shape as the input, just edited content.

## Procedure

1. **Read the source resume** at the path the user passed. If the
   user named the resume by short identifier rather than full path,
   resolve `<dir>` via the same discovery sequence as
   [ingest.md](ingest.md) step 7 (workspace `CLAUDE.md` → ask →
   optionally persist), then read `<dir>/<base>.json`.

2. **Read the job description.** Identify:
   - Required skills and technologies (especially anything in
     "Requirements" or "Must have").
   - Nice-to-haves.
   - Role responsibilities — these tell you what bullets to emphasize.
   - Seniority signal — "Senior", "Staff", "Lead", or "Entry-level".
   - Industry/domain — fintech, healthcare, devtools, etc.

3. **Copy the source JSON.** Use it as the starting point. Preserve
   `template` and `header` exactly. The user's name and contact info
   never change across variants.

4. **Read [tailoring-guide.md](tailoring-guide.md)** for the judgment
   calls on what to cut, rewrite, and reorder.

5. **Tailor the content.** In rough order of impact:
   - **Reorder skills** so the most relevant ones (matching the JD's
     required tech) appear first within each `keyvalue` row.
   - **Reorder timeline items** rarely — usually keep
     reverse-chronological. But if the user has two roles at the same
     time, surface the more relevant one.
   - **Rewrite bullets** to mirror the JD's vocabulary where honest.
     Don't fabricate. See the tailoring guide.
   - **Trim bullets** that don't pull weight for this role. A bullet
     about React when applying to a backend role is dead weight —
     either rewrite to focus on the backend aspect, or drop it.
   - **Drop sections** the JD makes irrelevant. If a backend role has
     no design component, the "Design" section can go.

6. **Pick the output slug.** Use the company name from the JD,
   lowercased and hyphenated. If no clear company name, use a short
   role descriptor (e.g. `default-senior-backend`).

7. **Write the file** to `<dir>/<base>-<slug>.json`, where `<dir>` is
   the directory containing the source resume. Pretty-print with
   2-space indentation. The parent directory is guaranteed to exist
   already (the source resume is in it).

8. **Tell the user what you changed.**

## Edge cases

- **JD mentions skills the user doesn't have.** Don't add them.
  Tailoring is rewriting honestly, not inventing. If the gap is large,
  flag it: "This role wants X and Y, which aren't in your resume — you
  may want to consider whether it's a fit."

- **Very different role from the user's background.** If a backend
  engineer applies to a PM role, this skill can only do so much. Do
  what's possible (emphasize cross-functional work, leadership) and tell
  the user the resume's structural fit is limited.

- **JD is a URL, not text.** Ask the user to paste the text, or fetch
  the page if you have web access. Don't guess at JD content.

- **No source resume yet.** Run [ingest.md](ingest.md) first, then
  this. Don't try to tailor from raw PDF in one pass — the
  schema-conformance step deserves its own pass.

- **Multiple tailoring rounds for the same JD.** If the user wants to
  iterate, edit the existing variant file rather than creating a third
  copy. Confirm with the user first.

## What not to do

- **Don't fabricate experience.** No inventing skills, employers, dates,
  or accomplishments. Rewriting truthful content is the whole job.
- **Don't change `header`.** Name, contact, links stay identical across
  variants.
- **Don't change `template`.** The user picks their visual style; this
  task only changes content.
- **Don't delete the source file.** The variant goes alongside it.
- **Don't over-tailor.** If 80% of the bullets get rewritten, the
  resume starts feeling AI-shaped. Aim for surgical edits.

## Where should rendered HTML go?

Before telling the user the render command, decide where HTML output
should land. Three options:

1. **Next to the JSON** — simplest, default behavior, HTML lives
   alongside the input file.
2. **A build directory** like `build/` or `dist/` — clean separation;
   the user can gitignore it. Use `--output-dir <dir>`.
3. **A specific file path** — use `-o <path>`. Mainly for one-offs.

Ask the user only if you can't tell. Skip the question if:
- The user already stated a preference earlier in the session (e.g.
  during ingest of the source resume).
- A `build/` or `dist/` directory already exists in the workspace.
- The user's `.gitignore` mentions a build dir.

Default if no signal: option (1), HTML next to JSON.

## After producing the file

Tell the user:
- The output path.
- The render command, picking the form that matches the HTML-output
  choice above. Substitute `<json>` with the actual variant path:
  - `cv-claw render <json>` (HTML next to JSON)
  - `cv-claw render <json> --output-dir build/` (HTML in a build dir)
  - `cv-claw render <json> -o /path/to/out.html` (single explicit path)
- A short summary of what you changed: "Reordered Skills to put
  PostgreSQL/Go first; rewrote 3 bullets in the Stripe role to emphasize
  payment systems; dropped the React-focused bullet from the EFL role."
- Any honest gaps you noticed between the JD and the resume.
