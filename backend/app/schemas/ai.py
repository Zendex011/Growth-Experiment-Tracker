from pydantic import BaseModel, Field
from typing import Optional


# ── Request Schemas ────────────────────────────────────────────────────────────

class HypothesisRequestSchema(BaseModel):
    rough_idea: str = Field(..., min_length=5, max_length=500)


class VerdictRequestSchema(BaseModel):
    metric_name: str
    control_value: float
    variant_value: float
    sample_size_control: int
    sample_size_variant: int
    duration_days: int


# ── Response Schemas (internal, for parsing AI output) ────────────────────────

class HypothesisSuggestion(BaseModel):
    hypothesis: Optional[str] = None
    confidence: Optional[str] = None   # low | medium | high
    degraded: bool = False
    reason: Optional[str] = None       # populated when degraded=True


class VerdictSuggestion(BaseModel):
    verdict: Optional[str] = None      # ship | rollback | iterate
    interpretation: Optional[str] = None
    suggested_reason: Optional[str] = None
    degraded: bool = False
    reason: Optional[str] = None


class SummarySuggestion(BaseModel):
    summary: Optional[str] = None
    degraded: bool = False
    reason: Optional[str] = None
