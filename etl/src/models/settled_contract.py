from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SettledContractDto(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    contract_ref: str | None = None
    contract_number: str | None = None
    conclusion_date: str | None = None
    title: str | None = None
    contract_url: str | None = None
    tender_refs: list[str] = Field(default_factory=list)
    extra_fields: dict[str, Any] = Field(default_factory=dict)
