"""FastAPI entrypoint for the VocalMetric backend."""
from datetime import datetime
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import VoiceCheck
from .schemas import AnalyzeResponse, HealthResponse
from .ml_model import analyze_audio, SUPPORTED_MIME_TYPES, AudioAnalysisError

# Ensure recordings directory exists
RECORDINGS_DIR = Path(__file__).resolve().parent / "recordings"
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="VocalMetric", description="Voice-based impairment detection")

# Allow local development frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health() -> Dict[str, str]:
    """Simple healthcheck endpoint."""
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Receive an audio recording, run analysis, and persist the result."""
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    if file.content_type not in SUPPORTED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported content type: {file.content_type}")

    timestamp = datetime.utcnow().isoformat()
    safe_filename = f"recording_{timestamp.replace(':', '-')}.{file.filename.split('.')[-1]}"
    save_path = RECORDINGS_DIR / safe_filename

    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty audio file")
        save_path.write_bytes(contents)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save audio: {exc}") from exc

    try:
        state, confidence, duration_seconds, feature_vector = analyze_audio(str(save_path))
    except AudioAnalysisError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - safety net
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc

    # Persist result
    voice_check = VoiceCheck(
        state=state,
        confidence=confidence,
        duration_seconds=duration_seconds,
        file_path=str(save_path.relative_to(Path(__file__).resolve().parent)),
    )
    db.add(voice_check)
    db.flush()  # obtain ID if needed

    response = AnalyzeResponse(
        state=state,
        confidence=confidence,
        details={
            "duration_seconds": duration_seconds,
            "feature_vector": feature_vector,
        },
        timestamp=datetime.utcnow(),
    )
    return JSONResponse(content=response.dict())
