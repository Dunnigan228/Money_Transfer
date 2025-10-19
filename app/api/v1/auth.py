from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.schemas.common import ResponseModel
from app.services.auth_service import AuthService
from app.services.audit_service import AuditService
from app.core.dependencies import get_current_active_user
from app.db.models.user import User
from app.utils.localization import localization

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=ResponseModel[UserResponse], status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService()
    audit_service = AuditService()

    try:
        user = await auth_service.create_user(db, user_data)

        await audit_service.log_action(
            db=db,
            action="user_registered",
            entity_type="user",
            entity_id=user.id,
            user=user,
            new_values={"email": user.email, "role": user.role.value},
        )

        await db.commit()

        return ResponseModel(
            status="success",
            message=localization.translate("user_registered", user.preferred_language),
            data=UserResponse.model_validate(user),
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=ResponseModel[TokenResponse])
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService()
    audit_service = AuditService()

    user = await auth_service.authenticate_user(db, credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=localization.translate("invalid_credentials"),
        )

    token = auth_service.create_user_token(user)

    await audit_service.log_action(
        db=db,
        action="user_login",
        entity_type="user",
        entity_id=user.id,
        user=user,
    )

    await db.commit()

    return ResponseModel(
        status="success",
        message="Login successful",
        data=TokenResponse(access_token=token),
    )


@router.get("/me", response_model=ResponseModel[UserResponse])
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    return ResponseModel(
        status="success",
        message="User information retrieved",
        data=UserResponse.model_validate(current_user),
    )
