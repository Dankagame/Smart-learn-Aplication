from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.auth.models import User
from app.courses.models import Course
from app.courses.schemas import CourseCreate, CourseUpdate


class CourseNotFoundError(Exception):
    pass


class NotCourseOwnerError(Exception):
    pass


def list_courses(
    db: Session,
    *,
    subject: str | None = None,
    level: str | None = None,
    teacher_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Course]:
    query = select(Course).options(joinedload(Course.teacher))
    if subject:
        query = query.where(func.lower(Course.subject) == " ".join(subject.split()).lower())
    if level:
        query = query.where(Course.level == level.strip().upper())
    if teacher_id is not None:
        query = query.where(Course.teacher_id == teacher_id)
    query = query.order_by(Course.created_at.desc(), Course.id.desc()).limit(limit).offset(offset)
    return list(db.scalars(query))


def get_course(db: Session, course_id: int) -> Course:
    course = db.scalar(
        select(Course).options(joinedload(Course.teacher)).where(Course.id == course_id)
    )
    if course is None:
        raise CourseNotFoundError
    return course


def get_owned_course(db: Session, course_id: int, teacher: User) -> Course:
    course = get_course(db, course_id)
    if course.teacher_id != teacher.id:
        raise NotCourseOwnerError
    return course


def create_course(db: Session, teacher: User, data: CourseCreate) -> Course:
    course = Course(**data.model_dump(), teacher=teacher)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def update_course(db: Session, course: Course, data: CourseUpdate) -> Course:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(course, field, value)
    db.commit()
    db.refresh(course)
    return course


def delete_course(db: Session, course: Course) -> None:
    db.delete(course)
    db.commit()
