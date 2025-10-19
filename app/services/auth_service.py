from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_password, get_password_hash, create_access_token
from app.db.models.user import User, UserRole
from app.schemas.user import UserCreate


class AuthService:

    async def create_user(
        self,
        db: AsyncSession,
        user_data: UserCreate,
        role: UserRole = UserRole.USER,
    ) -> User:
        stmt = select(User).where(User.email == user_data.email)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise ValueError("User with this email already exists")

        user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            preferred_language=user_data.preferred_language,
            role=role,
            is_active=True,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    async def authenticate_user(
        self,
        db: AsyncSession,
        email: str,
        password: str,
    ) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        return user

    def create_user_token(self, user: User) -> str:
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
        }
        return create_access_token(token_data)

    async def get_user_by_email(
        self,
        db: AsyncSession,
        email: str,
    ) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_id(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_user(
        self,
        db: AsyncSession,
        user: User,
        **kwargs,
    ) -> User:
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)

        await db.commit()
        await db.refresh(user)
        return user
