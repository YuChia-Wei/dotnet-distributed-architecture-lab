# Session token usage and cost estimate addendum

- Workflow: `2026-10-04-framework-019-init`
- Related work item: [Issue #31](https://github.com/YuChia-Wei/dotnet-distributed-architecture-lab/issues/31)
- Record created: `2026-10-04T21:49:42+08:00`
- Record updated: `2026-10-04T22:02:35+08:00`
- Usage snapshot: `2026-10-04T21:44:40.345+08:00`
- Parent session: `01a10714-8220-7143-94f9-efca3f19f204`
- Authority: The owner requested recording the reported usage estimate in this workflow and committing the record on 2026-10-04, then explicitly authorized all current framework and workflow changes together in the same amended local commit.

## Scope and measurement

This snapshot covers the parent conversation and its four child agents. It
excludes the side conversation that calculated and recorded these estimates,
and all execution after the snapshot. It is a local usage observation, not an
account-wide usage total or a provider billing receipt.

The calculation uses 141 response usage records deduplicated by response ID
from local Codex session logs under
`C:/Users/h4227/.codex/sessions/2026/10/04`. Session context and usage records
identify `gpt-6-astra` with reasoning effort `ultra`. Cached input is included
in total input; reasoning tokens are included in output and are not added twice.
Observed cache-write tokens are zero. The largest individual input is 187,468
tokens, below the model's 272,000-token long-context pricing threshold.

| Conversation / agent | Non-cached input | Cached input | Output | Total tokens | API equivalent USD | Enterprise credits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Parent | 190,430 | 8,588,032 | 35,757 | 8,814,219 | 12.280182 | 307.00455 |
| classify | 93,467 | 952,448 | 4,925 | 1,050,840 | 2.133368 | 53.33420 |
| release | 64,893 | 1,456,512 | 6,241 | 1,527,646 | 2.417492 | 60.43730 |
| initialize | 85,254 | 2,081,536 | 14,380 | 2,181,170 | 3.653076 | 91.32690 |
| repeat | 81,455 | 967,168 | 5,957 | 1,054,580 | 2.079568 | 51.98920 |
| **Total** | **515,499** | **14,045,696** | **67,260** | **14,628,455** | **22.563686** | **564.09215** |

Total input is 14,561,195 tokens. Output includes 15,233 reasoning tokens.
Rounded for reporting, the estimate is **US$22.56 and 564.09 enterprise credits**.

## Pricing basis and calculation

Rates were checked against official documentation on 2026-10-04:

| Category | USD per million tokens | Enterprise credits per million tokens |
| --- | ---: | ---: |
| Non-cached input | 10 | 250 |
| Cached input | 1 | 25 |
| Output, including reasoning | 50 | 1,250 |

Sources: [GPT-6 Astra API model pricing](https://developers.openai.com/api/docs/models/gpt-6-astra)
and [enterprise credit pricing](https://learn.chatgpt.com/docs/pricing).

```text
API equivalent USD = (515499 * 10 + 14045696 * 1 + 67260 * 50) / 1000000
                   = 22.563686
Enterprise credits = (515499 * 250 + 14045696 * 25 + 67260 * 1250) / 1000000
                   = 564.09215
```

The estimates assume Standard processing/speed because the observed records
do not expose a service tier or speed selection. Reasoning effort `ultra` does
not establish Ultrafast speed. Different processing/speed terms or enterprise
contract rates may change the estimate. API equivalent USD is a list-rate
comparison; it is not an invoice or a dollar conversion of actual purchased
credits. Actual enterprise credit debit and actual financial charges were not
available and remain unverified.

## Verification and relationship to the original trial

The per-agent token counts sum to the aggregate. The dollar and credit estimates
are calculated independently using the category-specific rates above, before
rounding. No runtime/product acceptance or account debit is inferred from this
record. The original trial reports retain their historical execution status;
this later addendum records only usage accounting and the owner's local commit
authorization. Framework integration, push, PR, merge and Issue state changes
remain separate operations.
