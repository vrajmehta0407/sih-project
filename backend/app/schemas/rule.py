from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict


class RuleBase(BaseModel):
    rule_code: str
    title: str
    statutory_source: str
    statutory_penalty_source: str = "Section 36, Legal Metrology Act, 2009"
    penalty_first_offence: str = "Fine up to ₹25,000"
    penalty_repeat_offence: str = "Fine up to ₹50,000 or imprisonment up to 1 year"
    description: str
    field_to_validate: str
    is_mandatory: bool = True
    validation_type: str = "presence_and_format"
    validation_parameters: Dict[str, Any] = {}
    severity: str = "critical"
    state_override: Optional[str] = None
    is_active: bool = True


class RuleCreate(RuleBase):
    version_id: str


class RuleUpdate(BaseModel):
    title: Optional[str] = None
    statutory_source: Optional[str] = None
    statutory_penalty_source: Optional[str] = None
    penalty_first_offence: Optional[str] = None
    penalty_repeat_offence: Optional[str] = None
    description: Optional[str] = None
    field_to_validate: Optional[str] = None
    is_mandatory: Optional[bool] = None
    validation_type: Optional[str] = None
    validation_parameters: Optional[Dict[str, Any]] = None
    severity: Optional[str] = None
    state_override: Optional[str] = None
    is_active: Optional[bool] = None


class RuleResponse(RuleBase):
    id: str
    version_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RuleVersionBase(BaseModel):
    version_tag: str
    statutory_act: str = "Legal Metrology Act, 2009 & Packaged Commodities Rules, 2011"
    description: Optional[str] = None
    gazette_notification_ref: Optional[str] = None
    is_active: bool = True


class RuleVersionCreate(RuleVersionBase):
    pass


class RuleVersionResponse(RuleVersionBase):
    id: str
    published_at: datetime
    created_by: Optional[str] = None
    rules: List[RuleResponse] = []

    model_config = ConfigDict(from_attributes=True)
