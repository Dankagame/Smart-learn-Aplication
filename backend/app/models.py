"""Import every model here so SQLAlchemy knows about all tables
before it creates them or links relationships between modules."""

from app.auth.models import User, UserRole
from app.courses.models import Course, Material
from app.quizzes.models import AttemptAnswer, Choice, Question, Quiz, QuizAttempt

__all__ = [
    "User",
    "UserRole",
    "Course",
    "Material",
    "Quiz",
    "Question",
    "Choice",
    "QuizAttempt",
    "AttemptAnswer",
]
