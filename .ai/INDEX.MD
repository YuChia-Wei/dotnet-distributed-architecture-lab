# .ai index

`.ai/` contains the selected RC2 managed skill and knowledge packages, the explicit target configuration under `custom/`, and the installer-owned lock. Use the [current target framework contract](../.dev/ai-context/CURRENT-FRAMEWORK.md), [skill registry](../.dev/ai-context/skills.md), and [target engineering rules](../.dev/ai-context/TARGET-ENGINEERING-RULES.md) for actual authority. The final managed inventory is determined by the installed lock; old `.ai/assets` and source-side distribution documents are not active runtime fallbacks.

Codex entries live under `.agents/skills/<skill-id>/`; Claude entries live under `.claude/skills/<skill-id>/`. Selected knowledge lives under `.ai/core/knowledge/<knowledge-id>/` and selected skills under `.ai/core/skills/<skill-id>/`. Project product and workflow truth lives in `.dev/`, source, tests and Compose.
