from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.models import User, UserRole
from app.auth.service import get_user_by_id
from app.core.database import get_db
from app.core.security import InvalidTokenError, decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise unauthorized("Not authenticated")

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (InvalidTokenError, ValueError):
        raise unauthorized("Invalid or expired token")

    user = get_user_by_id(db, user_id)
    if user is None:
        raise unauthorized("Invalid or expired token")
    return user


def require_role(*allowed_roles: UserRole) -> Callable[..., User]:
    def ensure_role(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return ensure_role


require_teacher = require_role(UserRole.TEACHER)
require_student = require_role(UserRole.STUDENT)
