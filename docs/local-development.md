# Local Development — Running Backend + Frontend

How to spin up both halves on your own machine for development. Two processes,
two terminals. No Docker needed for this (Docker comes later, for deployment).

## Prerequisites

- **uv** (Python package manager) — backend. Install: https://docs.astral.sh/uv/
- **Node.js** (with npm) — frontend.

## 1. Backend (FastAPI + uvicorn) — port 8000

```bash
cd backend
uv sync                                              # install deps (first time / after changes)
uv run uvicorn app.main:app --reload --port 8000
```

- `app.main:app` = the FastAPI instance in `backend/app/main.py`. Note it's
  `app.main`, **not** `main` (that errors with `Could not import module "main"`).
- `--reload` auto-restarts on code changes.
- Verify it's up: open http://localhost:8000/ping → should return
  `{"ping":"pong","environment":"dev","testing":false}`.

The game WebSocket lives at `ws://localhost:8000/ws/{gameid}`. It runs the
authoritative Pong sim and pushes one state snapshot per tick. Wire format:
see `docs/websocket-protocol.md`.

## 2. Frontend (Next.js) — port 3000

In a **second** terminal:

```bash
cd frontend
npm install                                          # first time / after dep changes
npm run dev
```

- Open http://localhost:3000.
- Click **PLAY** → the page opens a WebSocket to the backend on port 8000.
- Open the browser console (F12) to watch incoming `state` messages.

## Ports at a glance

| Service  | URL                       | Notes                                  |
|----------|---------------------------|----------------------------------------|
| Backend  | http://localhost:8000     | uvicorn; `/ping` health, `/ws/{id}` game |
| Frontend | http://localhost:3000     | Next.js dev server                     |

The frontend currently hardcodes `ws://localhost:8000` (in `src/app/page.tsx`).
Keep the backend on 8000 in dev or the socket won't connect. (`docker-compose.yml`
also maps the backend to host port 8000, so the containerized path matches.)

## Quick checks if something breaks

- **`Could not import module "main"`** → you ran `uvicorn main:app`; use
  `app.main:app` from inside `backend/`.
- **Browser: "can't establish a connection to ws://localhost:8000/..."** →
  backend not running, wrong port, or the WS library is missing
  (`uv add websockets` then restart uvicorn).
- **Frontend page crashes on PLAY** → the render reads game state that isn't
  there yet; make sure placeholder state is set (see `startGame`).

## Typical workflow

1. Terminal 1: start backend (`uv run uvicorn app.main:app --reload --port 8000`).
2. Terminal 2: start frontend (`npm run dev`).
3. Edit code — both auto-reload.
4. Browser console (F12) for the live WebSocket stream.
</content>
