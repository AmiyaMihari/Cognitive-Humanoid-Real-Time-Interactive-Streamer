# Reference

Precise, code-level documentation. This tree **mirrors the project's source
layout** — every page corresponds to a file or package in the repo.

```
reference/
├── app.md                       ← app.py
├── effectors/
│   ├── README.md                ← effectors/ package
│   └── effector_voice/
│       ├── README.md            ← effectors/effector_voice/__init__.py  (PUBLIC API)
│       ├── synthesizer.md       ← effectors/effector_voice/synthesizer.py
│       └── models.md            ← effectors/effector_voice/_models.py
├── mind/
│   ├── README.md                ← mind/__init__.py  (PUBLIC API)
│   └── agent.md                 ← mind/agent.py
└── senses/
    ├── README.md                ← senses/ package
    └── sense_ear/
        ├── README.md            ← senses/sense_ear/__init__.py  (PUBLIC API)
        ├── transcriber.md       ← senses/sense_ear/transcriber.py
        └── cuda.md              ← senses/sense_ear/_cuda.py
```

## Pages

- [app.md](app.md) — the Streamlit demo application.
- [effectors/](effectors/README.md) — the action package.
  - [effectors/effector_voice/](effectors/effector_voice/README.md) — **the
    text-to-speech module**: send it text, get back a spoken audio file.
  - [effectors/effector_voice/synthesizer.md](effectors/effector_voice/synthesizer.md)
    — the `Voice` class in detail.
  - [effectors/effector_voice/models.md](effectors/effector_voice/models.md) —
    internal Kokoro model-file caching.
- [mind/](mind/README.md) — **the thinking module**: send it text, get a reply.
  - [mind/agent.md](mind/agent.md) — the `Mind` class and its LangGraph graph.
- [senses/](senses/README.md) — the perception package.
  - [senses/sense_ear/](senses/sense_ear/README.md) — **the speech-to-text
    module**: how to call it and what it returns. Start here if you just want to
    use it.
  - [senses/sense_ear/transcriber.md](senses/sense_ear/transcriber.md) — the
    `Transcriber` class in detail.
  - [senses/sense_ear/cuda.md](senses/sense_ear/cuda.md) — internal CUDA library
    preloading.

## Reading a reference page

Each page documents the **public** surface — the names callers may rely on.
Anything prefixed with `_` (e.g. `_cuda`, `_load_model`) is internal: documented
for maintainers, but subject to change without notice.
