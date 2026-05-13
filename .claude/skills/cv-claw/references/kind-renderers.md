# Kind renderers

How to render each of the four section kinds in Jinja2. Every template
should handle all four, even if the current resume doesn't use them all.

## Dispatcher

```jinja
{% for section in resume.sections %}
  {% if section.kind == "prose" %}
    {# ...prose body... #}
  {% elif section.kind == "keyvalue" %}
    {# ...keyvalue body... #}
  {% elif section.kind == "list" %}
    {# ...list body... #}
  {% elif section.kind == "timeline" %}
    {# ...timeline body... #}
  {% endif %}
{% endfor %}
```

For larger templates, factor each branch into a macro in
`_macros.html.j2` and call `{{ m.prose(section) }}` etc.

## Section heading

A shared macro, since every kind uses the same heading style:

```jinja
{% macro section_heading(name) %}
<h2 class="section">{{ name }}</h2>
<hr class="rule">
{% endmacro %}
```

The CSS controls the look — colored text, underline rule, all-caps, etc.

## `prose`

A paragraph.

```jinja
<section class="prose">
  {{ section_heading(section.name) }}
  <p>{{ section.data.body }}</p>
</section>
```

CSS just needs `.foo .prose p { margin: ... }`. Keep the paragraph tight
— it's almost always a summary that should fit in 2–4 lines.

## `keyvalue`

Label/value rows, typically rendered as a bulleted list with the label
inline.

```jinja
<section class="keyvalue">
  {{ section_heading(section.name) }}
  <ul>
    {% for it in section.data.items %}
      <li><span class="label">{{ it.label }}</span> {{ it.value }}</li>
    {% endfor %}
  </ul>
</section>
```

CSS gives `.label` a fixed `min-width` so values align in a column. Some
templates make labels bold; others rely on the colon. Match the reference.

## `list`

Flat bulleted items, optionally linked.

```jinja
<section class="list">
  {{ section_heading(section.name) }}
  <ul>
    {% for it in section.data.items %}
      <li>
        {% if it.href %}<a href="{{ it.href }}">{{ it.text }}</a>{% else %}{{ it.text }}{% endif %}
      </li>
    {% endfor %}
  </ul>
</section>
```

CSS styles the bullets and the link color (usually the accent).

## `timeline`

The most complex kind. Two rendering modes:

- **Full mode**: when any item has bullets. Each item gets a multi-line
  block with title/dates on the first row, org and location below, then
  bullets.
- **Compact mode**: when no item has bullets (typical for Education).
  Each item is a single row with title+org on the left and dates on the
  right.

```jinja
{% set items = section.data.items %}
{% set any_bullets = items | selectattr("bullets") | list | length > 0 %}

{% if not any_bullets %}
  <section class="timeline compact">
    {{ section_heading(section.name) }}
    <ul>
      {% for it in items %}
        <li>
          <span><strong>{{ it.title }}</strong> {{ it.org or "" }}</span>
          {% if it.dates %}<span class="dates">{{ it.dates }}</span>{% endif %}
        </li>
      {% endfor %}
    </ul>
  </section>
{% else %}
  <section class="timeline">
    {{ section_heading(section.name) }}
    {% for it in items %}
      <div class="item">
        <div class="item-header">
          <div class="item-title">
            {% if it.href %}<a href="{{ it.href }}">{{ it.title }}</a>{% else %}{{ it.title }}{% endif %}
          </div>
          {% if it.dates %}<div class="item-dates">{{ it.dates }}</div>{% endif %}
        </div>
        {% if it.org %}<div class="item-sub">{{ it.org }}</div>{% endif %}
        {% if it.location %}<div class="item-location">{{ it.location }}</div>{% endif %}
        {% if it.bullets %}
          <ul>
            {% for b in it.bullets %}<li>{{ b }}</li>{% endfor %}
          </ul>
        {% endif %}
      </div>
    {% endfor %}
  </section>
{% endif %}
```

`selectattr("bullets")` filters items where `bullets` is truthy (i.e. a
non-empty list). Empty lists are falsy in Jinja, so this correctly
detects "no item in the section has bullets".

CSS for full mode typically uses a grid for the title/dates row:

```css
.foo .timeline .item-header {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: baseline;
  margin-top: 8px;
}
.foo .timeline .item-title { font-weight: 700; }
.foo .timeline .item-dates { font-weight: 700; }
.foo .timeline .item-sub { font-weight: 700; }
.foo .timeline .item-location { color: var(--muted); font-size: 10pt; }
.foo .timeline .item ul { margin: 4px 0 0 22px; padding: 0; }
.foo .timeline .item li { margin: 3px 0; }
```

CSS for compact mode aligns dates flush right:

```css
.foo .timeline.compact ul { list-style: disc; margin: 4px 0 0 24px; padding: 0; }
.foo .timeline.compact li {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: baseline;
  margin: 3px 0;
}
.foo .timeline.compact .dates { font-weight: 700; }
```

## Special rendering by section name

A template can branch on `section.name` when a particular section
deserves bespoke treatment. Example: Skills as a two-column grid even
though it's a generic `keyvalue`.

```jinja
{% set is_skills = section.name | lower == "skills" %}
<section class="keyvalue {% if is_skills %}skills-grid{% endif %}">
  ...
</section>
```

Use this sparingly. The point of the kinds taxonomy is that templates
mostly **don't** need to special-case section names. If you find yourself
branching on `name` more than once or twice per template, the kind
abstraction is probably wrong for this design.
