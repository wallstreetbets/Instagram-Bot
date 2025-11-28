"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class AnalyzeResponse(BaseModel):
    state: str
    confidence: float = Field(ge=0.0, le=1.0)
    details: dict
    timestamp: datetime

    class Config:
        orm_mode = True


class HealthResponse(BaseModel):
    status: str
