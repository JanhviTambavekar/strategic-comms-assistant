# Documentation guide

Start with the [project README](../README.md) for the user workflow, setup, architecture and limitations.

## Design and evaluation

| Guide | Purpose |
|---|---|
| [Prompt template](AISCE_prompt_template.md) | Strategy structure and requirements |
| [Evaluation rubric](evaluation_rubric.md) | Criteria and quality gates |
| [Human evaluation method](human_evaluation_method.md) | Qualitative review and its development |
| [Model comparison](model_comparison.md) | Controlled comparisons and measurements |
| [Prompt/evaluation alignment](prompt_evaluation_alignment.md) | Relationship between requirements and review |
| [Likert scale](likert_scale.md) | Interpretation of human ratings |
| [Cost model](cost_model.md) | Token accounting and configured estimates |

The code is authoritative for implemented behaviour. Provider names and prices in method documents describe configuration or historical snapshots, not guaranteed availability or quotations. Input datasets and recorded evaluation outputs are kept outside the current public tree.

## Running and maintaining the app

- [Deployment](../DEPLOYMENT.md): runtime assets, hosting configuration and checks.
- [Contribution guidance](../CONTRIBUTING.md): testing and repository data boundaries.
- [Example environment](../.env.example): configuration names and empty credentials.

## Historical development notes

[Project updates](../PROJECT_UPDATES.md), [strategy/change log](project_strategy_and_change_log.md), [evaluation changes](evaluation_changes_summary.md), [LLM research](../LLM_RESEARCH.md), [specialist LLMs](specialist_llms.md), [NVIDIA panel](nvidia_free_model_panel.md) and [earlier API setup](live_api_setup.md) preserve development context. They can describe earlier choices or planned work. Use the README, deployment guide and current source for setup; these notes are not current service-status pages or published evaluation datasets.
