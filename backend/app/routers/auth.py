from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user
from app.schemas.auth import RegisterRequest, LoginRequest, UserResponse
from app.services.auth import get_user_by_email, create_user, authenticate_user
from app.security import create_access_token
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    user = await create_user(db, data.email, data.password, data.name, data.department_id)

    token = create_access_token({"sub": str(user.id)})
    response.set_cookie(
        key="access_token", value=token, httponly=True, samesite="lax", max_age=60 * 60 * 24
    )
    return user


@router.post("/login", response_model=UserResponse)
async def login(data: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    token = create_access_token({"sub": str(user.id)})
    response.set_cookie(
        key="access_token", value=token, httponly=True, samesite="lax", max_age=60 * 60 * 24
    )
    return user


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"detail": "ok"}


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
