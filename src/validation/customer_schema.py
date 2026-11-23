from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator


class CustomerSchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    customer_id: str
    full_name: str
    email: str
    customer_status: Literal[
        "Active",
        "Dormant",
        "Closed"
    ]

    @field_validator("customer_id", "full_name")
    @classmethod
    def validate_required_fields(cls, value: str) -> str:
        if not value:
            raise ValueError("Field cannot be empty")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not value:
            raise ValueError("Email cannot be empty")

        if value.count("@") != 1:
            raise ValueError("Invalid email address")

        local, domain = value.split("@")

        if not local or "." not in domain:
            raise ValueError("Invalid email address")

        return value