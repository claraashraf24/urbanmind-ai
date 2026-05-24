from pydantic import BaseModel
from typing import Any, Literal


class CityEvent(BaseModel):
    source: str
    category: Literal[
        "weather",
        "transit",
        "traffic",
        "crowd",
        "safety",
        "infrastructure",
        "other"
    ]
    severity: Literal["low", "medium", "high", "critical"]
    title: str
    description: str
    latitude: float
    longitude: float
    confidence: float = 0.7
    raw_payload: dict[str, Any] = {}