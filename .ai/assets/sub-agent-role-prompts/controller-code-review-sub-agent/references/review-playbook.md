# Controller Code Review Sub-Agent Playbook

Use this role for a bounded ASP.NET Core controller, endpoint, DTO boundary, or
HTTP-semantics review.

1. Select the `controller` route from `review-routing.yaml`.
2. Load only the controller standard; add the `test` route only when controller
   tests or test-quality findings are in scope.
3. Review transport boundary, delegation, DTO separation, validation, error
   handling, and HTTP semantics against the selected standard.
4. Report evidence-backed findings without inventing target framework choices.

The role prompt does not own controller doctrine.
