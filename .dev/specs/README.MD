# Specs

This directory contains active target-repository production, test, and system-reconstruction specifications together with their authoring guidance.

## Purpose

Use `.dev/specs/reconstruction/README.MD` as the source-independent reconstruction entrypoint. Domain behavior lives under `domains/`, test oracles under `tests/`, and authoring guidance remains at this directory root.

## Usage

Start with `.dev/specs/INDEX.MD` when you need the file and directory catalog. Use this README only to understand the folder purpose and boundary.

## Boundary

- Requirements remain under `.dev/requirement/`; specifications must trace to them rather than replace them.
- Product/domain specs under `domains/` and structured problem frames under `.dev/problem-frames/` describe this repository's active system truth.
- Reusable examples under `.ai/` are guidance and cannot override target-repository requirements, specifications, or directly verified project facts.
- Every observed gap and future improvement must remain labeled; a desired quality uplift is not evidence that current source already implements it.
