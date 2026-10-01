# Reproduce the installed candidate

The tracked evidence binds to immutable source commit
`16f3f0c072bd22c3945fce8aca8295bf2b88f330`; no new release/tag is asserted.
The independent engine pin is retained in `engine-pin.json`, assembled catalog
identity in `build.json`, and final selection and inventory in this branch's
`.ai/custom/installation.json` and installer-owned `.ai/framework.lock`.

Use the supported source entry points from that commit:

1. `python -I -B tools/build-catalog.py --repository <source> --commit 16f3f0c072bd22c3945fce8aca8295bf2b88f330 --release-version 0.19.0-rc.3 --engine-pin <engine-pin.json> --output-root <catalog-output> --scratch-root <build-scratch> --engine-output-root <engine-output>`.
2. Run the emitted engine's `tools/derive-subset.py` with the returned catalog
   root/identity, this target's exact saved selection, independent engine pin,
   and distinct subset output/scratch roots. Artifact directory names are
   allocation details; catalog/subset identities bind content.
3. Run the emitted engine's `src/tools/maintain_framework.py` without CLI
   arguments, passing supported API2 JSON on stdin. Supply exact project/engine/
   candidate identities, current lock hash, isolated scratch/staging/recovery
   roots, `windows-inventory-only`, explicitly declared process-termination
   durability, and protected project-input preimages. Any project edit uses
   `before_sha256`, `after_sha256` and an exact staged `after_content_ref`.
4. Observe the real plan. For apply, bind `expected_plan_sha256` and declare
   actual quiescence over its exact `maintenance_scope`. Do not use this
   historical declaration as proof of current stopped sessions or writers.
5. Inspect and compare installed package hashes, selection and all prior
   tracked-file preimages. Reconcile drift rather than treating a prior success
   as a current pass. An equal already-installed candidate may yield no-op.

The receipt files are tracked. Plan and inspect summaries explicitly project
the real engine responses and retain their response hashes; omitted unchanged
inventories remain authoritative in the installed lock. They are local
installation evidence, not platform certification, agent behavior, independent
review, product acceptance or hosted admission.
