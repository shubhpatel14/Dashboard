# Trishula Capital Terminal

Institutional macro intelligence platform built around the existing Python scoring engines.

## Architecture

- Backend: FastAPI wrapping the current `engines/`, `data/`, and `models/` logic.
- Frontend: Next.js, React, TypeScript, Tailwind CSS, and ECharts.
- Database: PostgreSQL schema in `database/schema.sql`.
- Cache: Redis when available, in-memory fallback otherwise.

## Run Locally

Start infrastructure:

```powershell
docker compose up -d
```

Start the API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Start the terminal in development mode:

```powershell
cd frontend
npm run dev -- --hostname 127.0.0.1 --port 3000
```

For the most responsive local experience, run the optimized production build:

```powershell
cd frontend
npm run build
npm run start -- --hostname 127.0.0.1 --port 3000
```

Open:

- Frontend: http://127.0.0.1:3000
- API health: http://127.0.0.1:8000/health
- API docs: http://127.0.0.1:8000/docs

## API Surface

- `GET /api/macro/dashboard`
- `GET /api/macro/{category}`
- `GET /api/assets/{asset}`
- `GET /api/institutional/{asset}`

The existing Streamlit app remains in `dashboard.py`.
