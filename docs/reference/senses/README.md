# `senses` package

Source: [`senses/`](../../../senses/)

The `senses` package groups C.H.R.I.S.'s perception modules — one sub-package
per sense. Each sense is self-contained and exposes a small, stable API.

## Modules

| Module | Sense | Contract | Reference |
| --- | --- | --- | --- |
| `senses.sense_ear` | Hearing | `audio -> text` | [sense_ear/](sense_ear/README.md) |

> Future senses (e.g. vision) would live here as additional sub-packages,
> following the same "small public contract, hidden implementation" pattern.

## Importing

```python
from senses.sense_ear import transcribe
```
