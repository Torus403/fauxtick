import uuid
import datetime

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.security import get_password_hash
from src.user.models import User
from src.user.schemas import UserCreate, UserUpdate, UserUpdateMe, UsersPublic, UserPublic


def create(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User(
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password),
        is_active=user_create.is_active,
        is_superuser=user_create.is_superuser,
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        created_at=user_create.created_at,
        updated_at=user_create.updated_at,
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_by_id(*, session: Session, user_id: uuid.UUID) -> User | None:
    return session.get(User, user_id)


def get_by_email(*, session: Session, email: str) -> User | None:
    return session.execute(
        select(User).filter(User.email == email)
    ).scalar_one_or_none()


def get_users(*, session: Session, skip: int = 0, limit: int = 100) -> UsersPublic:
    count_statement = select(func.count()).select_from(User)
    count = session.execute(count_statement).scalar_one()
    statement = select(User).offset(skip).limit(limit)
    users = session.execute(statement).scalars().all()
    public_users = [UserPublic.model_validate(user) for user in users]
    return UsersPublic(data=public_users, count=count)


def activate(*, session: Session, user_id: uuid.UUID) -> User | None:
    user = session.get(User, user_id)
    if not user:
        return None
    user.is_active = True
    session.commit()
    session.refresh(user)
    return user


def update_me(*, session: Session, user: User, user_update: UserUpdateMe) -> User:
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    session.commit()
    session.refresh(user)
    return user


def update(*, session: Session, user: User, user_update: UserUpdate) -> User:
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data.pop("password"))
        update_data["hashed_password"] = hashed_password
    for field, value in update_data.items():
        setattr(user, field, value)
    session.commit()
    session.refresh(user)
    return user


def update_password(*, session: Session, user_id: uuid.UUID, new_password: str) -> User | None:
    user = session.get(User, user_id)
    if not user:
        return None
    user.hashed_password = get_password_hash(new_password)
    session.commit()
    session.refresh(user)
    return user


def delete(*, session: Session, user: User) -> None:
    # TODO: must delete all records belonging to that user in other tables.
    session.delete(user)
    session.commit()
