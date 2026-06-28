# C.H.R.I.S. — Documentation

Welcome to the project documentation. This folder is the single source of truth
for how C.H.R.I.S. is built and used.

## How this documentation is organized

We follow the [Diátaxis](https://diataxis.fr/) framework, which splits docs by
**purpose** instead of dumping everything into one file. Each page knows whether
it is teaching, instructing, describing, or explaining:

| Type | Question it answers | Where |
| --- | --- | --- |
| **Tutorial / Getting started** | "How do I get this running for the first time?" | [getting-started.md](getting-started.md) |
| **Explanation** | "How is it built and *why* those choices?" | [architecture.md](architecture.md) |
| **Reference** | "What exactly does this function/module do and return?" | [reference/](reference/) |

> **How-to guides** (task recipes like "transcribe a file from a script") are
> kept short and live next to the relevant reference page.

> **Writing docs yourself?** See [writing-documentation.md](writing-documentation.md)
> for the conventions every page here follows.

## The reference mirrors the code

The [`reference/`](reference/) tree is a 1:1 mirror of the project's source
layout — one documentation page per code unit. If you can find a file in the
repo, you can find its page in the same place under `reference/`:

```
project                         docs/reference
├── app.py            ───────►  ├── app.md
├── effectors/        ───────►  ├── effectors/
│   └── effector_voice/ ─────►  │   └── effector_voice/
│       ├── __init__.py ─────►  │       ├── README.md   (public API)
│       ├── synthesizer.py ──►  │       ├── synthesizer.md
│       └── _models.py  ─────►  │       └── models.md
├── mind/             ───────►  ├── mind/
│   ├── __init__.py ─────────►  │   ├── README.md   (public API)
│   └── agent.py    ─────────►  │   └── agent.md
└── senses/           ───────►  └── senses/
    └── sense_ear/    ───────►      └── sense_ear/
        ├── __init__.py ─────►          ├── README.md   (public API)
        ├── transcriber.py ──►          ├── transcriber.md
        └── _cuda.py    ─────►          └── cuda.md
```

## Start here

- **New to the project?** Read [getting-started.md](getting-started.md).
- **Want to understand the design?** Read [architecture.md](architecture.md).
- **Just need to call the speech module?** Jump to
  [reference/senses/sense_ear/](reference/senses/sense_ear/README.md) — it covers
  how to call it and what it returns.
- **Just need the thinking module?** Jump to
  [reference/mind/](reference/mind/README.md) — send it text, get a reply.
- **Just need the voice module?** Jump to
  [reference/effectors/effector_voice/](reference/effectors/effector_voice/README.md)
  — send it text, get a spoken audio file.

## Documentation conventions

- Everything is written in **English** (UI and code comments too).
- Code blocks are runnable as-is unless marked otherwise.
- Each reference page documents the **public** surface (what callers may rely
  on); names prefixed with `_` are internal and may change without notice.
- When code changes, update the matching page in `reference/` in the same commit.
