from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_teacher
from app.auth.models import User
from app.core.database import get_db
from app.courses.service import CourseNotFoundError, NotCourseOwnerError
from app.quizzes import service
from app.quizzes.models import Quiz
from app.quizzes.schemas import QuizCreate, QuizPublic, QuizSummary, QuizWithAnswers

router = APIRouter(tags=["quizzes"])

COURSE_NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
QUIZ_NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
NOT_COURSE_OWNER = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You can only add quizzes to your own courses",
)
NOT_QUIZ_OWNER = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You can only manage quizzes in your own courses",
)

UNAUTHORIZED_RESPONSE = {status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid token"}}
OWNER_RESPONSES = {
    **UNAUTHORIZED_RESPONSE,
    status.HTTP_403_FORBIDDEN: {"description": "Not a teacher, or not the course owner"},
    status.HTTP_404_NOT_FOUND: {"description": "Course or quiz not found"},
}


def owned_quiz(
    quiz_id: int,
    teacher: User = Depends(require_teacher),
    db: Session = Depends(get_db),
) -> Quiz:
    try:
        return service.get_owned_quiz(db, quiz_id, teacher)
    except service.QuizNotFoundError:
        raise QUIZ_NOT_FOUND
    except service.NotQuizOwnerError:
        raise NOT_QUIZ_OWNER


@router.post(
    "/courses/{course_id}/quizzes",
    response_model=QuizWithAnswers,
    status_code=status.HTTP_201_CREATED,
    responses=OWNER_RESPONSES,
)
def create_quiz(
    course_id: int,
    data: QuizCreate,
    teacher: User = Depends(require_teacher),
    db: Session = Depends(get_db),
) -> QuizWithAnswers:
    try:
        quiz = service.create_quiz(db, course_id, teacher, data)
    except CourseNotFoundError:
        raise COURSE_NOT_FOUND
    except NotCourseOwnerError:
        raise NOT_COURSE_OWNER
    return QuizWithAnswers.from_quiz(quiz)


@router.get(
    "/courses/{course_id}/quizzes",
    response_model=list[QuizSummary],
    responses={**UNAUTHORIZED_RESPONSE, status.HTTP_404_NOT_FOUND: {"description": "Course not found"}},
)
def list_course_quizzes(
    course_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[QuizSummary]:
    try:
        quizzes = service.list_course_quizzes(db, course_id)
    except CourseNotFoundError:
        raise COURSE_NOT_FOUND
    return [QuizSummary.from_quiz(quiz) for quiz in quizzes]


@router.get(
    "/quizzes/{quiz_id}",
    response_model=QuizPublic,
    responses={**UNAUTHORIZED_RESPONSE, status.HTTP_404_NOT_FOUND: {"description": "Quiz not found"}},
)
def get_quiz(
    quiz_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QuizPublic:
    try:
        return QuizPublic.from_quiz(service.get_quiz(db, quiz_id))
    except service.QuizNotFoundError:
        raise QUIZ_NOT_FOUND


@router.get("/quizzes/{quiz_id}/answer-key", response_model=QuizWithAnswers, responses=OWNER_RESPONSES)
def get_quiz_answer_key(quiz: Quiz = Depends(owned_quiz)) -> QuizWithAnswers:
    return QuizWithAnswers.from_quiz(quiz)


@router.delete("/quizzes/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT, responses=OWNER_RESPONSES)
def delete_quiz(quiz: Quiz = Depends(owned_quiz), db: Session = Depends(get_db)) -> None:
    service.delete_quiz(db, quiz)
