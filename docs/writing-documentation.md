# Writing documentation

How to add or change documentation in this project. Read this before writing a
new page so the docs stay consistent. It describes the conventions already used
across [`docs/`](README.md) — it does not invent new ones.

> This is a **meta page**: documentation about writing documentation. Like every
> page here, it is written in **English**.

## The framework: Diátaxis

We follow [Diátaxis](https://diataxis.fr/), which sorts every page by its
**purpose**. Before writing, decide which of the four kinds you are creating —
mixing them in one page is the most common mistake.

| Kind | Answers | Voice | Lives in |
| --- | --- | --- | --- |
| **Tutorial** | "How do I get this running the first time?" | Teaching, step-by-step | [getting-started.md](getting-started.md) |
| **How-to guide** | "How do I accomplish task X?" | Task recipe, goal-oriented | next to the relevant reference page |
| **Reference** | "What exactly does this do and return?" | Dry, precise, complete | [reference/](reference/README.md) |
| **Explanation** | "How is it built and *why*?" | Discursive, background | [architecture.md](architecture.md) (and this page) |

Rule of thumb: if you are explaining *why*, it belongs in an explanation; if you
are listing *what*, it belongs in reference. Keep them apart.

## The golden rules

1. **English only** — prose, code comments, and identifiers in examples.
2. **The `reference/` tree mirrors the source tree 1:1.** One page per code unit.
   If a reader can find a file in the repo, they can find its page in the same
   relative place under `reference/`.
3. **Document the public surface.** Names prefixed with `_` (e.g. `_cuda`,
   `_load_model`) are internal: mention them only in a clearly marked
   "internal / maintainers only" section, if at all.
4. **Update docs in the same commit as the code.** A reference page that drifts
   from the code is worse than no page.
5. **Code blocks are runnable as-is** unless explicitly marked otherwise.

## How the `reference/` mirror works

Every source file maps to one page in the same relative location:

```
project                      docs/reference
├── app.py          ──────►  ├── app.md
├── mind/           ──────►  ├── mind/
│   ├── __init__.py ──────►  │   ├── README.md   (public API)
│   └── agent.py    ──────►  │   └── agent.md
└── senses/         ──────►  └── senses/
    └── sense_ear/  ──────►      └── sense_ear/
        ├── __init__.py ──►          ├── README.md   (public API)
        ├── transcriber.py►          ├── transcriber.md
        └── _cuda.py    ──►          └── cuda.md
```

Conventions for the mirror:

- A **package** (`__init__.py`) is documented in that folder's `README.md`, and
  that page documents the package's **public API** (the names in `__all__`).
- A **module** (`foo.py`) is documented in `foo.md` (drop the extension). Drop a
  leading underscore in the filename (`_cuda.py` → `cuda.md`) but say in the page
  that the module is internal.

## Anatomy of a reference page

Every reference page follows the same skeleton. Copy this template:

```markdown
# `dotted.module.path` — one-line summary

Source: [`path/to/file.py`](relative/link/to/file.py)

One or two sentences stating the module's **contract** in the form
"X in → Y out", plus what it hides.

---

## Quick start
Smallest runnable example, then a numbered list of what it does.

## Public API
A table of the exported names (Name | Kind | Summary), then one `###` subsection
per name with its parameters, return type, and a code example.

## What it returns
The return type and its guarantees (e.g. "always `str`; `""` when empty").

## Behaviour notes
Bullet points on lifecycle, defaults, edge cases.

## Secrets handling   (only if the module reads .env / tokens)

## Related pages
Links to sibling pages, the architecture page, and modules it connects to.
```

Not every section is mandatory — small modules may only need *Quick start*,
*Public API*, and *Related pages*. Use [`mind/README.md`](reference/mind/README.md)
and [`sense_ear/README.md`](reference/senses/sense_ear/README.md) as worked
examples.

## Style conventions

- **Start with the contract.** Lead with the "X in → Y out" idea before details;
  it is the single most useful thing a reader needs.
- **Tables for structured facts** — parameters, return values, exported names,
  configuration. Prose for narrative.
- **Blockquotes (`>`) for callouts** — a `> Note:` for asides, a `> ⚠️` for
  warnings or gotchas.
- **Relative links** between pages so the tree is browsable on disk and on
  GitHub. Always link a page's `Source:` to the actual file.
- **Show, then tell.** A two-line runnable snippet beats a paragraph.
- **Cross-link generously.** Each page should point to its siblings, its
  explanation in `architecture.md`, and the modules it connects to.

## When you add a new module

Do all of these in the same change:

1. Create its reference page(s) under `reference/`, mirroring the source path.
2. Add it to the tree and "Pages" list in [reference/README.md](reference/README.md).
3. Add it to the mirror diagram in [README.md](README.md).
4. If it changes the system's shape, update the diagram, project layout, and
   dependency table in [architecture.md](architecture.md).
5. If it changes setup (a new dependency or secret), update
   [getting-started.md](getting-started.md).

## Checklist before you commit

- [ ] Page is in the correct Diátaxis category (one purpose, not mixed).
- [ ] It lives at the mirrored path under `reference/` (for reference pages).
- [ ] `Source:` link points at the real file and works.
- [ ] Only the public surface is documented as public; `_` names are marked
      internal.
- [ ] All code blocks run as written.
- [ ] Cross-links to siblings / architecture / connected modules are present.
- [ ] Everything is in English.
- [ ] The matching code change is in the same commit.
