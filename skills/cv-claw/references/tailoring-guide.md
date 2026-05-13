# Tailoring guide

The judgment calls behind a good tailoring pass. The SKILL.md handles
mechanics; this file handles taste.

## The cardinal rule

**Rewrite truthfully or don't rewrite.** The resume belongs to a real
person who has to back up every line in an interview. Aggressive
rewording that drifts from the source is worse than no tailoring at all
— it wastes the user's time and sets up uncomfortable interview moments.

If you can't honestly say a bullet is true after your rewrite, revert it.

## What to actually change

### Skills (`keyvalue` section)

**Reorder items within each row.** If the JD requires Go and PostgreSQL,
move those to the front of their respective rows:

```diff
- "Languages: Python, TypeScript, Go"
+ "Languages: Go, Python, TypeScript"
```

**Don't add skills the user doesn't have.** If the JD wants Rust and
the user doesn't list Rust, leave it out. The recruiter can ask.

**Trim rarely.** Removing a skill the user listed because the JD doesn't
mention it is usually a bad trade — it can read as a gap. Keep the row,
just reorder.

### Bullets (`timeline` items)

**Lead with the work most relevant to the JD.** For a given item, reorder
bullets so the most relevant ones appear first. Recruiters skim — the
first bullet under each role does the most work.

**Mirror the JD's vocabulary, honestly.** If the JD says "distributed
systems" and the user's bullet says "microservices that scale across
multiple nodes", change "microservices" to "distributed systems" — it's
the same thing, said in the recruiter's words. But if the JD says
"machine learning" and the user actually built a heuristic, don't call
it ML.

**Quantify when truthful.** "Improved performance" is weaker than
"reduced p99 latency by 40%." If the original bullet has the number,
keep it. If it doesn't, don't invent one.

**Cut hedge words.** "Helped with", "contributed to", "was involved in"
all dilute. Prefer "built", "shipped", "led", "owned" — but only when
the user actually did it. If they did help rather than lead, leave the
hedge in.

**Drop bullets that don't pull weight.** A React-styling bullet on a
backend application is noise. Two options:
1. Drop it.
2. Rewrite to focus on the relevant aspect: "Built React frontend with
   a Python+FastAPI backend exposing 12 endpoints" → "Built FastAPI
   backend with 12 endpoints serving a React frontend."

### Timeline items themselves

**Don't drop entire jobs lightly.** A gap in employment looks worse than
a less-relevant job. But if a 4-month freelance gig is squeezing out the
detail on the user's main 3-year role, dropping the freelance gig is
fair.

**Don't reorder timeline items chronologically.** Reverse-chronological
is the convention; recruiters expect it. The one exception: if the user
has two concurrent roles at the same time, surface the more relevant one
first.

### Whole sections

**Drop sections the JD makes irrelevant.** Examples:
- A "Hobbies" or "Interests" section can usually go for a senior role.
- A "Publications" section can go for an industry engineering role
  (unless the JD specifically values academic output).
- A "Volunteer" section can go if space is tight and the JD is
  hard-skills-focused.

**Keep sections the JD doesn't mention but most reviewers expect.**
Education is rarely irrelevant. Experience never is.

## What not to change

- **Header**: name, contact, links never change. The person is the same.
- **Template**: visual style is the user's choice, not the JD's.
- **Dates**: never. Inflating tenure or shifting dates is fraud.
- **Job titles**: only fix obvious typos or expand abbreviations. Don't
  promote yourself from "Engineer" to "Senior Engineer" because the JD
  is for a Senior role.
- **Company names**: never.

## Calibration

A good tailoring pass touches **maybe 30-50%** of the bullets in the
most relevant 1-2 timeline items, plus reorders skills. If you're
rewriting 80% of the resume, you're probably either drifting from the
source or applying to a role the resume doesn't fit.

Resist the temptation to "improve" bullets that don't need improvement.
A bullet that's already good in the source is good in the variant.

## Honest gaps

When the JD wants something the resume genuinely lacks, **flag it to
the user** rather than papering over it. Examples:

> "This JD emphasizes Kubernetes operator development. Your resume
> mentions Kubernetes deployments but not operator/CRD work — you may
> want to add detail if you have any, or note this as a gap."

> "The role is described as 'Staff' level. Your most recent title is
> 'Senior Software Engineer' — the recruiter will likely ask about
> scope. Worth thinking about what scope examples to lead with in the
> cover letter."

This is more useful than burying the gap and letting the user discover
it in the interview.

## Naming the output file

The slug should be recognizable a month from now. Good:
- `default-stripe.json` — clear which company.
- `ada-anthropic-research.json` — base + company + team.
- `default-senior-backend.json` — for a generic role without a company.

Bad:
- `default-tailored.json` — which job?
- `default-2.json` — for what?
- `ada-jd-1.json` — opaque.
