from pydantic import BaseModel, Field, field_validator


class CreateResultSchema(BaseModel):
    control_value: float = Field(..., ge=0)
    variant_value: float = Field(..., ge=0)
    sample_size_control: int = Field(..., gt=0)
    sample_size_variant: int = Field(..., gt=0)
    duration_days: int = Field(..., gt=0)

    @field_validator("control_value", "variant_value")
    @classmethod
    def value_is_finite(cls, v: float) -> float:
        import math
        if math.isnan(v) or math.isinf(v):
            raise ValueError("value must be a finite number")
        return v
