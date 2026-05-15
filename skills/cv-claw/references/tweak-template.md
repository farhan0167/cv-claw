# tweak-template

Edit the active template in response to a small visual change request.

## When to use

The user is looking at a rendered resume and asks for a change to how
it looks: "make the name bigger," "move the location onto the role
line," "tighten the section spacing," "change the heading color." The
content is fine; the *display* needs adjustment.

If the request is for a fundamentally different look ("two-column",
"more modern", "serif version") rather than a tweak, route to
[create-template.md](create-template.md) instead.

## What to produce

A minimal edit to the active template's `.html.j2` and/or `.css`,
followed by a re-render. No new template, no new files (unless
ejection happens — see below).

## Procedure

1. **Identify the active template from the rendered HTML.** Read the
   first ~15 lines of the rendered file the user is looking at. The
   `<!-- cv-claw render -->` header lists `template`, `template-source`,
   and `template-path`. Use those — do not ask the user which template
   they're using.

   Example header:

   ```
   <!--
     cv-claw render
     template: classic
     template-source: bundled
     template-path: src/cvclaw/templates/classic
     resume: resumes/example.json
     cv-claw-version: 0.1.0
     rendered-at: 2026-05-14T10:23:00Z
   -->
   ```

2. **Decide: edit in place, or new template?**

   - **Small tweak** (move/resize/recolor an element, tighten margins,
     swap a font, reorder header fields) → edit in place. Continue to
     step 3.
   - **Big swing or ambiguous** (different layout, different visual
     character, "make it more modern", anything where the prior look
     might be worth keeping) → ask the user: *"edit `<name>` in place,
     or save this as a new template?"* If they want a new template,
     route to [create-template.md](create-template.md).

   When in genuine doubt about which bucket a request falls into, ask.
   When it's clearly a small tweak, don't ask — just edit.

3. **Make sure the template is editable.**

   - If `template-source: workspace` — the template already lives at
     `template-path`. Edit it directly. Skip ahead to step 4.
   - If `template-source: bundled` — run `cv-claw eject <name>`
     silently. This copies the template into `./.cvclaw/templates/<name>/`
     so edits persist. Then re-derive the template path from the
     ejection output (or by reading
     `./.cvclaw/templates/<name>/<name>.html.j2`); **do not trust the
     pre-eject lineage header** — it still says `bundled`.
   - If `template-source: override` — the user invoked
     `--templates-dir`. Edit the file at `template-path` directly; do
     not eject.

4. **Locate the element the user pointed at.** Read the template's
   `.html.j2` and `.css`. Map "the name in the header" or "the
   Self-employed line" to the specific Jinja variable and CSS
   selector. The `.html.j2` shows the structure; the `.css` shows
   how each piece is styled. Per-template CSS rules are scoped under
   `.<name>` (see [template-anatomy.md](template-anatomy.md)).

5. **Make the edit.** Smallest change that achieves what the user
   asked for. Don't refactor surrounding code; don't rename
   classes; don't rewrite the section. If the change requires both
   markup and CSS, edit both — but keep each diff minimal.

6. **Re-render.** Run `cv-claw render <path-to-resume>.json` (the
   `resume:` field in the lineage header tells you which file). The
   user can refresh the HTML in their browser.

7. **Tell the user what changed, in one or two sentences.** If
   ejection happened in step 3, add one line: *"Template `<name>` is
   now at `./.cvclaw/templates/<name>/` so future edits stick."*
   Otherwise, say nothing about template plumbing.

## What not to do

- **Don't ask the user which template they're using.** The lineage
  header answers that. Asking is the friction the lineage header
  exists to remove.
- **Don't ask before every small tweak whether to make a new
  template.** Default to edit-in-place for clear small tweaks; only
  ask on big swings or genuine ambiguity. Asking too often is its
  own kind of friction.
- **Don't edit the rendered HTML directly.** The next `cv-claw render`
  will blow it away, and the change won't apply to any future
  job-tailored variant. Always edit the template.
- **Don't edit a bundled template in place** (the path inside the
  installed package, typically under `site-packages/cvclaw/templates/`).
  Eject first; the workspace copy is what should be edited.
- **Don't add a `.prev.html` safety net by hand.** That's `--keep-prev`'s
  job (a separate flag the user opts into).
- **Don't accumulate `<name>-v2`, `<name>-v3` from a string of small
  tweaks.** Each tweak edits the template in place. New templates are
  for fundamentally different looks, decided up front by asking.
