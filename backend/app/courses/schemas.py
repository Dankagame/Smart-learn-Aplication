import re
from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

from app.courses.models import Course

LEVEL_PATTERN = re.compile(r"^S[1-6]$")
LEVEL_QUERY_PATTERN = r"^[sS][1-6]$"


def collapse_whitespace(value: str) -> str:
    return " ".join(value.split())


def text_with_min_length(min_length: int):
    def validate(value: str) -> str:
        value = collapse_whitespace(value)
        if len(value) < min_length:
            raise ValueError(f"Must have at least {min_length} characters")
        return value

    return AfterValidator(validate)


def normalize_level(value: str) -> str:
    value = value.strip().upper()
    if not LEVEL_PATTERN.match(value):
        raise ValueError("Level must be one of S1, S2, S3, S4, S5, S6")
    return value


def normalize_description(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


Title = Annotated[str, Field(max_length=150), text_with_min_length(3)]
Subject = Annotated[str, Field(max_length=80), text_with_min_length(2)]
Level = Annotated[str, Field(max_length=2), AfterValidator(normalize_level)]
Description = Annotated[str | None, Field(max_length=2000), AfterValidator(normalize_description)]


class CourseCreate(BaseModel):
    title: Title
    subject: Subject
    level: Level
    description: Description = None


class CourseUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Title | None = None
    subject: Subject | None = None
    level: Level | None = None
    description: Description = None

    @model_validator(mode="after")
    def validate_fields(self) -> "CourseUpdate":
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update")
        for required_field in ("title", "subject", "level"):
            if required_field in self.model_fields_set and getattr(self, required_field) is None:
                raise ValueError(f"{required_field} cannot be null")
        return self


class CourseRead(BaseModel):
    id: int
    title: str
    subject: str
    level: str
    description: str | None
    teacher_id: int
    teacher_name: str
    created_at: datetime

    @classmethod
    def from_course(cls, course: Course) -> "CourseRead":
        return cls(
            id=course.id,
            title=course.title,
            subject=course.subject,
            level=course.level,
            description=course.description,
            teacher_id=course.teacher_id,
            teacher_name=course.teacher.full_name,
            created_at=course.created_at,
        )
