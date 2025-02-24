import datetime
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

import src.email.service as email_service
import src.user.service as user_service
from src import security
from src.auth import service
from src.auth.schemas import Token, NewPassword
from src.config import settings
from src.dependencies import SessionDep, get_current_active_superuser
from src.user.schemas import Message, UserRegister, UserCreate, UserPublic


main_router = APIRouter()


@main_router.post("/signup", response_model=Message)
def register_user(session: SessionDep, user_in: UserRegister) -> Message:
    """Create new user without needing to be logged in."""
    existing_user = user_service.get_by_email(session=session, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists in the system",
        )

    now = datetime.datetime.now(datetime.UTC)
    user_create = UserCreate(
        email=user_in.email,
        password=user_in.password,
        is_active=False,
        is_superuser=False,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        created_at=now,
        updated_at=now,
    )
    user = user_service.create(session=session, user_create=user_create)

    confirmation_token = security.generate_confirmation_token(str(user.id))
    email_data = email_service.generate_account_confirmation_email(token=confirmation_token, user=user)
    # email_service.send_email(
    #     email_to=user.email,
    #     subject=email_data.subject,
    #     html_content=email_data.html_content
    # )
    return Message(message="Your user has been created. Please check your email to activate your account.")


@main_router.get("/confirm-signup", response_model=UserPublic)
def confirm_email(session: SessionDep, token: str) -> UserPublic:
    """Activate user account using the confirmation token."""
    user_id = security.verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired confirmation token.",
        )
    user = user_service.activate(session=session, user_id=uuid.UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user


@main_router.post("/login/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """OAuth2 compatible token login, get an access token for future requests"""
    user = service.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    access_token_expires = datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )


@main_router.post("/reset-password/{email}")
def send_password_reset_token(email: str, session: SessionDep) -> Message:
    """Send password reset token via emai."""
    user = user_service.get_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this email does not exist in the system.",
        )
    password_reset_token = security.generate_password_reset_token(email=email)
    email_data = email_service.generate_password_reset_email(token=password_reset_token, user=user)
    # email_service.send_email(
    #     email_to=user.email,
    #     subject=email_data.subject,
    #     html_content=email_data.html_content
    # )
    return Message(message="Password reset email has been sent.")


@main_router.post("/reset-password/")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """Reset password"""
    email = security.verify_token(token=body.token)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    user = user_service.get_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this email does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    user_service.update_password(session=session, user_id=user.id, new_password=body.new_password)
    return Message(message="Password updated successfully")


# ----- Superuser only endpoints ----- #
admin_router = APIRouter()


@admin_router.patch(
    "/activate-account/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
    include_in_schema=False
)
def confirm_email(session: SessionDep, user_id: uuid.UUID) -> UserPublic:
    """Activate user account; used manually by a superuser."""
    user = user_service.activate(session=session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user


@admin_router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
    include_in_schema=False
)
def recover_password_html_content(session: SessionDep, email: str) -> Any:
    """HTML Content for Password Recovery; used manually by a superuser."""
    user = user_service.get_by_email(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = security.generate_password_reset_token(email=email)
    email_data = email_service.generate_password_reset_email(token=password_reset_token)
    return HTMLResponse(content=email_data.html_content, headers={"subject:": email_data.subject})
