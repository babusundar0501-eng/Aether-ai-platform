# AETHER — Unified AI Platform

AETHER is an early-stage AI workspace with a single interface for chat, research, agents, code assistance, document drafting, voice, memory, model configuration, and AETHER Forge custom assistants.

## What is in this repository

- **Chat** — unified conversation workspace.
- **Research** — structured research brief generation.
- **Agents** — task-focused agent templates.
- **Code** — code explanation and review (no arbitrary execution).
- **Studio / Create** — turn notes into drafts and creative briefs.
- **Voice** — browser speech recognition and speech synthesis support where available.
- **Memory** — local browser notes.
- **Models** — backend health and provider configuration guidance.
- **Forge** — create, configure, test, and share assistant previews.
- **FastAPI backend** — Gemini or OpenAI-compatible chat, password-hashed accounts, signed sessions, SQLite assistant storage, private/public assistant endpoints.

## Run locally on Windows

1. Install Python 3.11 or newer.
2. Open PowerShell in this repository.
3. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Copy `.env.example` to `.env`. Set a long random `AETHER_SECRET_KEY` and optionally `GEMINI_API_KEY` or `OPENAI_API_KEY`. The backend loads `.env` automatically. Never put provider keys in `app.js` or `index.html`.
6. Start the server:

   ```powershell
   python -m uvicorn server:app --host 127.0.0.1 --port 8000
   ```

8. Open http://127.0.0.1:8000

## API

- `GET /health` — service/provider status
- `POST /api/auth/register` — create account
- `POST /api/auth/login` — sign in
- `GET /api/auth/me` — current account (Bearer token)
- `POST /api/chat` — authenticated model chat
- `GET/POST /api/bots` — list/create assistants
- `PUT/DELETE /api/bots/{id}` — update/delete an owned assistant
- `POST /api/bots/{id}/publish` — publish an assistant and receive its public slug
- `GET /api/public/{slug}` — public assistant metadata
- `POST /api/public/{slug}/chat` — public assistant chat

Interactive API docs are available at http://127.0.0.1:8000/docs

## Deploying

Deploy the FastAPI application to a Python host (Render, Railway, Fly.io, or your own server). Configure environment variables in the host dashboard, use persistent storage for `AETHER_DB_PATH`, and set `AETHER_ALLOWED_ORIGINS` to your actual frontend origin. Because the backend serves the frontend, one deployment can host both together.

For production, use HTTPS, a strong persistent secret, managed PostgreSQL, backups, rate limiting, email verification, password reset, abuse monitoring, and a security review. The included SQLite database is suitable for local development and small prototypes, not multi-instance production.

## Honest feature status

This is a functional starter platform, not a finished competitor to mature AI platforms. The frontend includes sign-in and account creation screens. When signed in, Forge can save assistants to the API, sync cloud assistants, and publish a hosted public assistant page. Unsigned-in drafts and Memory notes remain in browser localStorage. A production embed widget and account recovery/email verification are not included yet. Research uses the connected model to draft a brief; it does not crawl the web or guarantee citations. Code is reviewed as text and is never executed. File uploads/RAG, image generation, real-time voice conversations, team workspaces, billing, analytics, and model streaming are not implemented.

## Security notes

- API keys belong only in server environment variables.
- Passwords are stored as PBKDF2-HMAC-SHA256 hashes; plaintext passwords are never stored.
- Sessions are signed and expire after 14 days.
- Configure a stable random `AETHER_SECRET_KEY` before deploying.
- Set allowed CORS origins explicitly for your deployment.
- Do not expose the SQLite database file publicly.
