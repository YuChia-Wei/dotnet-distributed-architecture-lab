# Sub-Agent Role Prompts

本目錄放置 delegated sub-agent 的 canonical 定義。

## 角色

- 表達 worker-role prompt / delegation template / sub-agent role prompt
- 不是 top-level skill
- 給 main agent 在委派 bounded task 時作為 canonical source

常見類型：

- implementation sub-agents
- test-generation sub-agents
- delegated review sub-agents
- infrastructure / integration sub-agents

## 建議結構

```text
.ai/assets/sub-agent-role-prompts/<sub-agent-id>/
  sub-agent.yaml
  references/
```

## 與其他目錄的分工

- `.ai/assets/skills/`
  - top-level skills
- `.ai/assets/sub-agent-role-prompts/`
  - delegated sub-agent role prompts
- `.ai/assets/shared/`
  - shared prompt packages / common rules / templates

## 例子

- `command-sub-agent`
- `query-sub-agent`
- `reactor-sub-agent`
- `usecase-test-sub-agent`
- `aggregate-test-sub-agent`
- `controller-test-sub-agent`
- `code-review-sub-agent`
- `aggregate-code-review-sub-agent`
- `controller-code-review-sub-agent`
- `reactor-code-review-sub-agent`

