# Initial Retrieval Evaluation

This is a routing smoke test, not a visual-quality evaluation of generated code. Seven of eight representative briefs have a relevant self-authored pattern in the top result. Mobile onboarding remains a documented coverage gap.

| Brief | Stack | Expected route | Top observed result |
|---|---|---|---|
| SaaS dashboard 后台 | React | self pattern | `dashboard-app-shell` |
| tactile physical lighting controls | Vanilla CSS | self pattern | `ambient-light-system` |
| brand design system tokens | Vue | self pattern | `design-contract` |
| React accessible loading button | React | self pattern | `accessible-action-button` |
| ecommerce product variant cart | Next.js | self pattern | `commerce-variant-selector` |
| semantic data flow diagram | agnostic | self pattern | `semantic-diagram-layout` |
| polish existing interface on mobile | React | self pattern | `bounded-interface-review` |
| mobile onboarding paywall | React | reference or user-direct provider | no self pattern yet; paid provider options require consent |

Next quality gate: use real user briefs to compare implementation quality from `get_pattern` against the older raw-file workflow. Review semantics, responsiveness, accessibility, provenance disclosure and whether the model copied source code unintentionally.
