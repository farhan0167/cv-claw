---
name: tailor-resume
description: Tailor an existing cv-claw resume JSON for a specific job description. Use when the user provides a job description (or URL) and wants their resume optimized for that role — bullets rewritten, skills reordered, irrelevant experience trimmed. Produces a new variant resumes/<base>-<slug>.json, never overwriting the source.
compatibility: Reads and writes resumes/*.json files. Render via `cv-claw render resumes/<base>-<slug>.json`.
---

# tailor-resume

Produce a job-specific variant of an existing resume.

## When to use

The user has:
1. A resume already ingested as a cv-claw JSON file (or one they're
   about to ingest), AND
2. A specific job description they want to apply for.

They'll say "tailor my resume for this role", "make a version for X",
"adjust this for the JD", etc.

## What to produce

**A new file** at `resumes/<base>-<slug>.json`, where:
- `<base>` is the source resume's filename (without `.json`).
- `<slug>` is a short identifier for the target job — usually the
  company name lowercased and hyphenated, e.g. `default-stripe.json`,
  `ada-acme-corp.json`.

**Never overwrite the source.** The user keeps the original as their
canonical resume; tailored variants are alongside it.

The output must conform to the [cv-claw schema](../../SCHEMA.md). Same
shape as the input, just edited content.

## Procedure

1. **Read the source resume** at `resumes/<base>.json`. Read the schema
   doc if you haven't already.

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

4. **Read [references/tailoring-guide.md](references/tailoring-guide.md)**
   for the judgment calls on what to cut, rewrite, and reorder.

5. **Tailor the content.** In rough order of impact:
   - **Reorder skills** so the most relevant ones (matching the JD's
     required tech) appear first within each `keyvalue` row.
   - **Reorder timeline items** rarely — usually keep reverse-chronological
     within each section. But if the user has, say, two roles at the
     same time, surface the more relevant one.
   - **Rewrite bullets** to mirror the JD's vocabulary where honest.
     Don't fabricate. See the tailoring guide for rules.
   - **Trim bullets** that don't pull weight for this role. A bullet
     about React when applying to a backend role is dead weight —
     either rewrite it to focus on the backend aspect, or drop it.
   - **Drop sections** the JD makes irrelevant. If a backend role has
     no design component, the "Design" section can go.

6. **Pick the output slug.** Use the company name from the JD,
   lowercased and hyphenated. If no clear company name, use a short
   role descriptor (e.g. `default-senior-backend`).

7. **Write the file** to `resumes/<base>-<slug>.json`. Pretty-print
   with 2-space indentation.

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

- **No source resume yet.** If the user hasn't ingested one, run the
  `ingest-resume` skill first, then this one. Don't try to tailor from
  raw PDF in one pass — the schema-conformance step deserves its own
  pass.

- **Multiple tailoring rounds for the same JD.** If the user wants to
  iterate, edit the existing variant file rather than creating a third
  copy. Confirm with the user first.

## What not to do

- **Don't fabricate experience.** No inventing skills, employers, dates,
  or accomplishments. Rewriting truthful content is the whole job.
- **Don't change `header`.** Name, contact, links stay identical across
  variants.
- **Don't change `template`.** The user picks their visual style; this
  skill only changes content.
- **Don't delete the source file.** The variant goes alongside it.
- **Don't over-tailor.** If 80% of the bullets get rewritten, the
  resume starts feeling AI-shaped. Aim for surgical edits — the user's
  voice should still come through.

## After producing the file

Tell the user:
- The output path.
- The render command: `cv-claw render resumes/<base>-<slug>.json`.
- A short summary of what you changed: "Reordered Skills to put
  PostgreSQL/Go first; rewrote 3 bullets in the Stripe role to emphasize
  payment systems; dropped the React-focused bullet from the EFL role."
- Any honest gaps you noticed between the JD and the resume.
