from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Paper(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    keywords: List[str] = Field(default_factory=list)
    abstract: str = ""
    notes: str = ""
    pdf_path: Optional[str] = None
    citation: Optional[str] = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title must not be blank")
        return value

    @field_validator("authors", "keywords", mode="before")
    @classmethod
    def split_csv_strings(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("pdf_path")
    @classmethod
    def normalize_pdf_path(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return str(Path(value))
