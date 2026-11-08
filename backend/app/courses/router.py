from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_teacher
from app.auth.models import User
from app.core.database import get_db
from app.courses import service
from app.courses.models import Course
from app.courses.schemas import LEVEL_QUERY_PATTERN, CourseCreate, CourseRead, CourseUpdate

router = APIRouter(prefix="/courses", tags=["courses"])

COURSE_NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
NOT_COURSE_OWNER = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You can only modify your own courses",
)

AUTH_RESPONSES = {
    status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid token"},
}
OWNER_RESPONSES = {
    **AUTH_RESPONSES,
    status.HTTP_403_FORBIDDEN: {"description": "Not a teacher, or not the course owner"},
    status.HTTP_404_NOT_FOUND: {"description": "Course not found"},
}


def owned_course(
    course_id: int,
    teacher: User = Depends(require_teacher),
    db: Session = Depends(get_db),
) -> Course:
    try:
        return service.get_owned_course(db, course_id, teacher)
    except service.CourseNotFoundError:
        raise COURSE_NOT_FOUND
    except service.NotCourseOwnerError:
        raise NOT_COURSE_OWNER


@router.get("", response_model=list[CourseRead], responses=AUTH_RESPONSES)
def list_courses(
    subject: Annotated[str | None, Query(max_length=80)] = None,
    level: Annotated[str | None, Query(pattern=LEVEL_QUERY_PATTERN)] = None,
    teacher_id: Annotated[int | None, Query(gt=0)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CourseRead]:
    courses = service.list_courses(
        db, subject=subject, level=level, teacher_id=teacher_id, limit=limit, offset=offset
    )
    return [CourseRead.from_course(course) for course in courses]


@router.get(
    "/{course_id}",
    response_model=CourseRead,
    responses={**AUTH_RESPONSES, status.HTTP_404_NOT_FOUND: {"description": "Course not found"}},
)
def get_course(
    course_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CourseRead:
    try:
        return CourseRead.from_course(service.get_course(db, course_id))
    except service.CourseNotFoundError:
        raise COURSE_NOT_FOUND


@router.post(
    "",
    response_model=CourseRead,
    status_code=status.HTTP_201_CREATED,
    responses={**AUTH_RESPONSES, status.HTTP_403_FORBIDDEN: {"description": "Not a teacher"}},
)
def create_course(
    data: CourseCreate,
    teacher: User = Depends(require_teacher),
    db: Session = Depends(get_db),
) -> CourseRead:
    return CourseRead.from_course(service.create_course(db, teacher, data))


@router.patch("/{course_id}", response_model=CourseRead, responses=OWNER_RESPONSES)
def update_course(
    data: CourseUpdate,
    course: Course = Depends(owned_course),
    db: Session = Depends(get_db),
) -> CourseRead:
    return CourseRead.from_course(service.update_course(db, course, data))


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT, responses=OWNER_RESPONSES)
def delete_course(
    course: Course = Depends(owned_course),
    db: Session = Depends(get_db),
) -> None:
    service.delete_course(db, course)
