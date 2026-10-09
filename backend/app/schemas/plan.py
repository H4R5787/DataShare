"""Plan catalog Pydantic schemas."""

from typing import Optional
from pydantic import BaseModel, ConfigDict


class PlanDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    operator_id: str
    circle_id: Optional[str] = None
    plan_code: str
    data_amount: str
    data_amount_mb: int
    validity_desc: str
    price_in_paise: int
    price_formatted: str
    category: str
    description: str
    is_active: bool
