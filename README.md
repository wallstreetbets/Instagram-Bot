# VocalMetric (MVP)

VocalMetric is a minimal proof-of-concept web app that performs voice-based impairment checks. Users record a short phrase in the browser, the backend extracts lightweight features, runs a placeholder classifier, and returns a sobriety guess.

## Project structure
- `backend/` — FastAPI backend
  - `main.py` — API entrypoint
  - `ml_model.py` — placeholder feature extraction and heuristic classifier
  - `models.py` — SQLAlchemy models
  - `schemas.py` — Pydantic response models
  - `database.py` — SQLite engine/session factory
  - `recordings/` — saved uploads (created automatically)
- `frontend/` — Static SPA (HTML/CSS/JS)
  - `index.html` — main UI
  - `styles.css` — basic styling
  - `app.js` — MediaRecorder logic and API calls
- `requirements.txt` — backend dependencies

## Setup
1. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   ```
2. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the backend
From the repository root:
```bash
uvicorn backend.main:app --reload
```
The API will be available at `http://localhost:8000`.

## Serving the frontend
Use any static file server from the `frontend` directory. For example:
```bash
cd frontend
python -m http.server 5500
```
Then open `http://localhost:5500` in your browser. The frontend expects the API at `http://localhost:8000`.

## API
- `GET /api/health` → `{ "status": "ok" }`
- `POST /api/analyze` → accepts audio upload (`audio/webm`, `audio/wav`, etc.) via `multipart/form-data`. Returns analysis JSON including `state`, `confidence`, `details`, and `timestamp`.

Example health check:
```bash
curl http://localhost:8000/api/health
```

Example analysis request using an audio file:
```bash
curl -X POST \
  -F "file=@path/to/audio.webm" \
  http://localhost:8000/api/analyze
```

## Notes
- The classifier is a simple heuristic based on duration and RMS energy; it should be replaced with a real model in production.
- All uploads are stored under `backend/recordings/` with timestamped filenames.
