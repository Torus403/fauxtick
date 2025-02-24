import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from src import security
from src.dependencies import SessionDep, CurrentUser, get_current_active_superuser
from src.email import service as email_service
from src.user import service
from src.user.schemas import UserPublic, UserCreate, UserUpdateMe, Message, UpdatePassword, UsersPublic, UserUpdate


main_router = APIRouter()


@main_router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """Get current user."""
    return current_user


@main_router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, current_user: CurrentUser, user_in: UserUpdateMe,
) -> Any:
    """Update own user."""
    if user_in.email:
        existing_user = service.get_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists"
            )

    updated_user = service.update_me(session=session, user=current_user, user_update=user_in)
    return updated_user


@main_router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """Update own password."""
    if not security.verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="New password cannot be the same as the current one"
        )

    service.update_password(session=session, user_id=current_user.id, new_password=body.new_password)
    return Message(message="Password updated successfully.")


@main_router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    service.delete(session=session, user=current_user)
    return Message(message="User deleted successfully")


# ----- Superuser only endpoints ----- #
admin_router = APIRouter()


@admin_router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
    include_in_schema=False
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> UsersPublic:
    """Retrieve users."""
    return service.get_users(session=session, skip=skip, limit=limit)


@admin_router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
    include_in_schema=False
)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """Create new user; used manually by a superuser."""
    user = service.get_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    user = service.create(session=session, user_create=user_in)
    confirmation_token = security.generate_confirmation_token(str(user.id))
    email_data = email_service.generate_account_confirmation_email(token=confirmation_token)
    # email_service.send_email(
    #     email_to=user.email,
    #     subject=email_data.subject,
    #     html_content=email_data.html_content
    # )
    return user


@admin_router.get(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
    include_in_schema=False
)
def read_user_by_id(session: SessionDep, user_id: uuid.UUID) -> UserPublic:
    """Get a specific user by id."""
    user = service.get_by_id(session=session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user


@admin_router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
    include_in_schema=False
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> UserPublic:
    """Update a user."""
    user = service.get_by_id(session=session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )
    if user_in.email:
        existing_user = service.get_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists."
            )

    updated_user = service.update(session=session, user=user, user_update=user_in)
    return updated_user


@admin_router.delete(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    include_in_schema=False
)
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """Delete a user."""
    user = service.get_by_id(session=session, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if user == current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Superusers cannot delete themselves."
        )
    service.delete(session=session, user=user)
    return Message(message="User deleted successfully.")
