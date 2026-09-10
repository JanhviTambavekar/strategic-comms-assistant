# Deployment

The entry point is `app.py`. Runtime assets are `src/`, `config/` and `prompts/`, with dependencies in `requirements.txt`. No client dataset, generated report or dissertation file is required.

## Render

The repository includes a [Render blueprint](render.yaml) for `main`:

```text
Build: pip install -r requirements.txt
Start: streamlit run app.py --server.address 0.0.0.0 --server.port $PORT --server.headless true
Health endpoint: /_stcore/health
```

Connect the repository through Render and use the blueprint. Supply credentials in the hosting dashboard, not in Git. Entries marked `sync: false` require values outside the repository. The blueprint configures the free-model panel; its model identifiers must be available to the provider account.

For an offline demonstration, set `LLM_PROVIDER=mock`. For live generation, use `LLM_PROVIDER=free` with provider credentials, or a direct provider from `.env.example`.

The blueprint enables deployment on commits. Inspect the hosting build and service logs after a push; a successful Git push alone does not confirm a successful deployment.

## Streamlit Community Cloud alternative

Connect this repository, choose a branch and select `app.py` as the entry point. Add root-level configuration through the hosting secrets settings, using `.streamlit/secrets.toml.example` as a starting point. Keep the populated file out of Git.

## Configuration and operational checks

- Use the configuration names in `.env.example` and supply only credentials needed for the selected provider.
- Keep local `.env` off the server when host environment values should be authoritative: the app loads `.env` with override enabled.
- Verify persona selection, questionnaire entry, generation, evaluation and downloads after deployment.
- Check fallback labels and actual provider/model metadata during evaluation.
- Provider calls consume account quota and may incur charges. Control public access and provider budgets as appropriate.
- The prototype has no persistent client-record store or production authentication. Assess data handling before accepting confidential uploads.

See the [README](README.md) for local setup and tests.
