# Target Repository Checks

This directory retains only target-owned checks called by current project policy:

- `validate-assessment-artifacts.py`: assessment artifact contract.
- `validate-workflow-artifacts.py`: workflow locator and artifact contract.
- `validate-workflow-handoff.py`: repository handoff checkpoint contract.
- `validate-dependency-versions.py`: offline dependency and managed-tool version consistency.

`python_prerequisites.py` and `python-entrypoints.json` provide their shared
Python 3.11/PyYAML prerequisite check. A missing prerequisite remains blocked;
this target has no source-framework requirements mirror or package release runner.

Framework admission is selected by
`.dev/project-config.yaml#validation.current_framework.local`. It is currently
`unconfigured`, so normal admission and handoff remain blocked. Issue #22's
owner-deferred gate is limited to this RC2 adoption; these other checks do not
stand in for the framework gate.
