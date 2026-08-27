# Problem Frames

This directory contains active target-repository problem frames, authoring guidance, and reusable templates for validator-ready specs.

## Purpose

Use `.dev/problem-frames/` when a use case needs structured, traceable, machine-readable specification inputs for `spec-compliance-validator`.

## Usage

Start with `.dev/problem-frames/INDEX.md` when you need the file catalog, minimum frame layout, or template list. Use this README only to understand the folder purpose and boundary.

## Boundary

- Requirements remain under `.dev/requirement/`.
- Human-readable functional specs remain under `.dev/specs/`.
- Problem frames hold structured machine-readable validation inputs.
- Product-specific frames listed in `INDEX.md` are active validation inputs for this repository and must remain traceable to requirements, production specs, code, and tests.
- A frame draft does not establish compliance; `spec-compliance-validator` owns the 100% gate and truthful gap report.
