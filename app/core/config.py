from pydantic_settings import BaseSettings
from typing import List, Optional
from pydantic import Field, field_validator

class Settings(BaseSettings):
    API_ID: str = Field(..., alias="telegram_api_id")
    API_HASH: str = Field(..., alias="telegram_api_hash")
    PHONE_NUMBER: str = Field(..., alias="telegram_phone_number")
    CHANNEL_IDS: Optional[List[str]] = Field(default=None, alias="TELEGRAM_CHANNEL_ID")
    CHANNEL_USERNAME: Optional[List[str]] = Field(default=None, alias="TELEGRAM_CHANNEL_USERNAME")
    DATABASE_URL: str

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
        "populate_by_name": True,
    }

    @field_validator("CHANNEL_IDS", "CHANNEL_USERNAME", mode="before")
    @classmethod
    def split_str_to_list(cls, v):
        if isinstance(v, str):
            # Split by comma, strip whitespace and quotes
            return [item.strip().strip("'").strip('"') for item in v.split(',')]
        return v

settings = Settings()