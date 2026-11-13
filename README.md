# AETHER — AI Platform / Forge

AETHER is an early-stage AI platform project. This first repository milestone is **AETHER Forge**, a browser-based assistant builder prototype.

## Current prototype

- Create, edit, and delete assistant profiles.
- Configure name, description, model placeholder, visibility, welcome message, knowledge notes, and system instructions.
- Test a local demo responder in the preview panel.
- Save assistant configurations in the current browser using localStorage.
- Generate a shareable preview URL containing the assistant configuration.

## Run

Open `index.html` in a modern browser, or enable GitHub Pages for this repository and open the published site.

## Important limitations

This is a front-end prototype, not a production AI service:

- The demo responder is local rule-based behavior. It does **not** call GPT, Gemini, or another model.
- Model options are placeholders until a secure backend is implemented.
- Assistant data is stored in the browser that created it. There is no account system or cloud database.
- A shared preview link carries configuration in its URL; it is not a hosted, persistent chatbot service.
- Do not put API keys or secrets in this front-end repository.

## Roadmap

1. Secure FastAPI backend and provider adapters (Gemini / OpenAI-compatible).
2. Authentication, ownership, cloud persistence, and access controls.
3. Real model-backed test chat with streaming.
4. Knowledge-file ingestion and retrieval.
5. Hosted public bot runtime, embed widget, analytics, and version history.
6. Add the wider AETHER platform modules: Chat, Research, Agents, Code, Studio, Voice, Memory, and Business.

## Project status

Early prototype · version 0.1.0
