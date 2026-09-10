# Contributing

Keep changes focused and explain the behaviour they affect. Start with the [README](README.md) for setup and the [documentation index](docs/README.md) for design context.

## Before committing

1. Run `python -m unittest discover -s tests -q` for code changes. Check interface changes in a browser at normal and narrow sidebar widths.
2. Update the README or relevant guide when behaviour or configuration changes. Label historical notes clearly.
3. Use fictional, minimal in-code fixtures for tests. Do not commit completed questionnaires, uploaded documents, generated strategies, survey responses, experiment datasets or dissertation evidence.
4. Keep credentials in local `.env` or hosting secrets settings. Only empty configuration examples belong in Git.
5. Inspect `git status --short` and `git diff`. Stage named files, then inspect `git diff --cached --stat` and `git diff --cached` before committing.

Ignore rules do not remove already tracked files. Use `git rm --cached` when intentionally removing a local-only file from the current repository while retaining its local copy. Earlier versions remain in Git history.

## Reporting issues

Describe the steps, expected result, actual result and relevant configuration names. Remove credentials and client information from logs and screenshots. Identify mock/fallback output separately from a live model response.

## Change summaries

Explain the problem, resulting behaviour and verification. Keep claims about model quality separate from implementation checks. Configured models are not guaranteed available or independently benchmarked.
