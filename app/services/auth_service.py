from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate , UserUpdate ,ChangePassword
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.repositories.user_repository import (
    get_user_by_email,
    create_user,
    update_user,
    deactivate_user,
)


def register_user(db: Session, user: UserCreate):

    existing_user = get_user_by_email(db, user.email)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        is_active=True,
    )

    return create_user(db, new_user)


def login_user(db: Session, email: str, password: str):

    db_user = get_user_by_email(db, email)

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    if not db_user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Account has been deactivated"
        )
    if not verify_password(password, db_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={"sub": db_user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

def update_profile(
    db: Session,
    current_user: User,
    user_data: UserUpdate,
):

    # Update username if provided
    if user_data.username is not None:
        current_user.username = user_data.username

    # Update email if provided
    if user_data.email is not None:

        existing_user = get_user_by_email(
            db,
            user_data.email,
        )

        if (
            existing_user
            and existing_user.id != current_user.id
        ):
            raise HTTPException(
                status_code=400,
                detail="Email already exists",
            )

        current_user.email = user_data.email

    return update_user(
        db,
        current_user,
    )

def change_password(
    db: Session,
    current_user: User,
    password_data: ChangePassword,
):
    # Verify current password
    if not verify_password(
        password_data.current_password,
        current_user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Current password is incorrect",
        )

    # Prevent using the same password again
    if password_data.current_password == password_data.new_password:
        raise HTTPException(
            status_code=400,
            detail="New password must be different from the current password",
        )

    # Hash the new password
    current_user.hashed_password = hash_password(
        password_data.new_password
    )

    # Save changes
    update_user(db, current_user)

    return {
        "message": "Password changed successfully"
    }

def delete_account(
    db: Session,
    current_user: User,
):
    deactivate_user(
        db,
        current_user,
    )

    return {
        "message": "Account deleted successfully"
    }