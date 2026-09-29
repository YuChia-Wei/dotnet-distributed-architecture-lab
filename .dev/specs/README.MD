# Specs

This directory contains the distributed-commerce lab's production specifications, test designs, reconstruction contracts and authoring guidance. Products, Orders, Inventory and Procurement are active bounded contexts with source under `src/`.

## Purpose and navigation

Start with [INDEX.MD](INDEX.MD) for the catalog. Production behavior belongs under `domains/`; verification scenarios belong under `tests/`. The [Procurement specifications](domains/procurement/README.md) cover purchases, supplier HTTP integration and receipt publication; their [test entry](tests/procurement/README.md) maps scenarios to existing test sources and remaining verification targets.

## Authority and limits

- Specs retain their requirement/source bindings and describe the scope they actually cover. A source-reconciled specification distinguishes observed behavior from accepted intent and records conflicts rather than silently changing either.
- Test design and test source presence do not establish execution or full compliance. Keep runtime evidence, skipped tests and remaining targets explicit.
- The [reconstruction contracts](reconstruction/README.MD) describe a dated three-context baseline. [Current extensions](current-system-extension.md) identify later additions; a new domain specification does not update every reconstruction contract automatically.
- [SPEC-GUIDE.MD](SPEC-GUIDE.MD) and [SPEC-ORGANIZATION-GUIDE.MD](SPEC-ORGANIZATION-GUIDE.MD) define authoring and placement. Framework examples are guidance; target requirements and verified product source supply product facts.
