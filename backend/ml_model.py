"""Placeholder ML logic for voice impairment detection.

This module is intentionally simple so it can be swapped with a real
model later. For now, it extracts a few basic audio features and applies
heuristic rules to generate a state and confidence score.
"""
from typing import List, Tuple

import numpy as np
from pydub import AudioSegment


class AudioAnalysisError(Exception):
    """Raised when audio analysis fails."""


# Supported MIME types for convenience
SUPPORTED_MIME_TYPES = {"audio/wav", "audio/x-wav", "audio/webm", "audio/ogg", "audio/mpeg"}


def extract_features(file_path: str) -> Tuple[float, float, float, List[float]]:
    """Extract lightweight features from an audio file.

    Returns duration (seconds), RMS energy, zero crossing rate, and the
    feature vector list. Uses pydub for decoding to support common web
    recording formats.
    """
    try:
        audio = AudioSegment.from_file(file_path)
    except Exception as exc:  # pragma: no cover - safety net for unsupported media
        raise AudioAnalysisError(f"Could not read audio file: {exc}") from exc

    duration_seconds = len(audio) / 1000.0

    # Convert samples to numpy array for simple stats
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    if audio.channels > 1:
        samples = samples.reshape((-1, audio.channels)).mean(axis=1)

    # Normalize to [-1, 1]
    max_val = np.iinfo(samples.dtype).max if np.issubdtype(samples.dtype, np.integer) else 1.0
    norm_samples = samples / float(max_val)

    rms_energy = float(np.sqrt(np.mean(norm_samples**2))) if norm_samples.size else 0.0

    # Simple zero crossing rate
    zero_crossings = np.nonzero(np.diff(np.sign(norm_samples)))[0]
    zcr = float(len(zero_crossings)) / duration_seconds if duration_seconds > 0 else 0.0

    feature_vector = [duration_seconds, rms_energy, zcr]
    return duration_seconds, rms_energy, zcr, feature_vector


def analyze_audio(file_path: str) -> Tuple[str, float, float, List[float]]:
    """Analyze an audio file and return a (state, confidence, duration, feature_vector).

    Heuristic placeholder:
    - If duration < 2.5 seconds -> intoxicated with moderate confidence.
    - Else if RMS energy is extremely low (quiet) -> intoxicated lower confidence.
    - Else -> sober with higher confidence.
    """
    duration_seconds, rms_energy, zcr, feature_vector = extract_features(file_path)

    if duration_seconds < 2.5:
        state = "intoxicated"
        confidence = 0.7
    elif rms_energy < 0.02:
        state = "intoxicated"
        confidence = 0.55
    else:
        state = "sober"
        confidence = 0.82

    return state, confidence, duration_seconds, feature_vector
