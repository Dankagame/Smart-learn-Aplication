"""Courses (e.g. Mathematics - S6) and their learning materials."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    subject: Mapped[str] = mapped_column(String(80), index=True)  # e.g. "Mathematics"
    level: Mapped[str] = mapped_column(String(20), index=True)  # e.g. "S6"
    description: Mapped[str | None] = mapped_column(Text)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    teacher: Mapped["User"] = relationship(back_populates="courses")
    materials: Mapped[list["Material"]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )
    quizzes: Mapped[list["Quiz"]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Course id={self.id} {self.subject} {self.level}>"


class Material(Base):
    """A note or a link that a teacher posts to a course."""

    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(150))
    content: Mapped[str | None] = mapped_column(Text)  # written notes
    link_url: Mapped[str | None] = mapped_column(String(500))  # external resource
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    course: Mapped["Course"] = relationship(back_populates="materials")

    def __repr__(self) -> str:
        return f"<Material id={self.id} title={self.title!r}>"
