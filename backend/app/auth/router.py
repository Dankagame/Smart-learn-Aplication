from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, unauthorized
from app.auth.models import User
from app.auth.schemas import TokenResponse, UserLogin, UserRead, UserRegister
from app.auth.service import EmailAlreadyRegisteredError, authenticate_user, register_user
from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_409_CONFLICT: {"description": "Email already registered"}},
)
def register(data: UserRegister, db: Session = Depends(get_db)) -> UserRead:
    try:
        user = register_user(db, data)
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )
    return UserRead.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Invalid email or password"}},
)
def login(data: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, data.email, data.password)
    if user is None:
        raise unauthorized("Invalid email or password")

    settings = get_settings()
    access_token = create_access_token(
        subject=str(user.id),
        extra_claims={"role": user.role.value},
    )
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserRead.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserRead,
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid token"}},
)
def read_current_user(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)
