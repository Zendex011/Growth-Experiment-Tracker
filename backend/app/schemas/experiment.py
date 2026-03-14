from pydantic import BaseModel, field_validator, Field
from typing import Optional


class CreateExperimentSchema(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    hypothesis: str = Field(..., min_length=10)
    metric_name: str = Field(..., min_length=2, max_length=100)
    metric_baseline: float = Field(..., ge=0)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be blank")
        return v.strip()

    @field_validator("hypothesis")
    @classmethod
    def hypothesis_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("hypothesis must not be blank")
        return v.strip()


class UpdateVerdictSchema(BaseModel):
    verdict: str = Field(..., pattern="^(ship|rollback|iterate)$")
    verdict_reason: Optional[str] = Field(None, max_length=1000)

    @field_validator("verdict_reason")
    @classmethod
    def reason_strip(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v else v
