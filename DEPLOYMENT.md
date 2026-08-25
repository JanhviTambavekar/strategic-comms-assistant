# Deploy to Streamlit Community Cloud

This repository is ready to deploy as a public Streamlit application. The
entry point is `app.py`; the `config/`, `prompts/`, `docs/`, `data/`, and `src/`
directories are application assets and must remain in the repository.

## Before deployment

1. Create a GitHub account if needed and install Git for Windows from
   <https://git-scm.com/download/win>. This computer does not currently have
   Git available on its command path.
2. Create an empty **public** GitHub repository, for example
   `strategic-comms-assistant`.
3. From the project root, run the following in PowerShell, replacing the URL
   with your repository URL:

   ```powershell
   git init
   git add .
   git commit -m "Prepare Streamlit deployment"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/strategic-comms-assistant.git
   git push -u origin main
   ```

   Do not use `git add -f .env` and do not commit a populated
   `.streamlit/secrets.toml`. Both are ignored deliberately.

## Deploy

1. Go to <https://share.streamlit.io> and sign in with GitHub.
2. Select **Create app** (or **Deploy an app**).
3. Select your repository and its `main` branch.
4. Set **Main file path** to `app.py`.
5. Open **Advanced settings** and paste one of the secret configurations below.
6. Select **Deploy**. After the build completes, Streamlit supplies a public
   `https://YOUR-APP.streamlit.app` URL. Share that URL; visitors only need a
   normal web browser.

Pushing later commits to `main` triggers a redeploy.

## Secrets

The app runs in mock mode without any secret, which is suitable for an
offline/demo version but returns canned content. For live tailored strategies,
set `LLM_PROVIDER` plus the matching provider key. Root-level Streamlit secrets
are exposed to this app as environment variables, so no code changes are needed.

### Gemini (recommended live configuration)

```toml
LLM_PROVIDER = "gemini"
GOOGLE_API_KEY = "your-real-key"
GOOGLE_MODEL = "gemini-2.0-flash"
```

### Anthropic

```toml
LLM_PROVIDER = "anthropic"
ANTHROPIC_API_KEY = "your-real-key"
ANTHROPIC_MODEL = "claude-sonnet-4-6"
```

### OpenAI

```toml
LLM_PROVIDER = "openai"
OPENAI_API_KEY = "your-real-key"
OPENAI_MODEL = "gpt-4o-mini"
```

For NVIDIA NIM, use `LLM_PROVIDER = "openai"`, set `OPENAI_BASE_URL` to
`https://integrate.api.nvidia.com/v1`, and set `OPENAI_API_KEY` (or the optional
model-specific NVIDIA key variables described in `.env.example`).

## Notes

- There is no database, filesystem write requirement, or localhost service.
  Uploaded briefs are processed in memory for the active session.
- Live LLM calls use the project owner's API account. Public visitors can
  therefore incur API charges or consume rate limits. Apply provider-side spend
  limits and consider authentication/rate limiting before wide public sharing.
- Streamlit Community Cloud is hosted in the United States. Do not invite users
  to upload confidential or sensitive material unless that is appropriate for
  your data-handling obligations.
