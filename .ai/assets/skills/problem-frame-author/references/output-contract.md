# Output Contract

Return the result in this order:

1. Source inputs used
2. Use case selection and `CBF` / `SWF` decision
3. Extraction sheet
4. Draft file set:
   - `frame.yaml`
   - `machine/machine.yaml`
   - `machine/use-case.yaml`
   - `controlled-domain/aggregate.yaml` or `workpiece/aggregate.yaml`
   - `acceptance.yaml` or `requirements/*.yaml`
5. Inferred items
6. Open questions
7. Source bindings (reference/revision or section, source ID and approval/observation status)
8. Recommended next skill only for a distinct needed output or decision; otherwise none

Keep the selected frame schemas and file set intact. Shared handoff notes do not
add arbitrary schema fields or create an automatic requirement/spec pipeline.

## Quality Bar

- Inputs and outcomes are explicit
- External constraints are not omitted
- Scenarios are traceable
- `tests_anchor` is present
- Missing truth is surfaced instead of silently guessed
