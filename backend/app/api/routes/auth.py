"""认证接口。

当前只实现注册（POST /auth/register）。
登录、邮箱验证码、身份绑定按 PRD 3.1-S1/S2 在后续任务中实现。
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.repositories.user_repository import UserRepository, get_user_repository
from app.schemas.auth import RegisterRequest, RegisterResponse
from app.schemas.errors import ErrorResponse
from app.services.auth_service import EmailAlreadyRegisteredError, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponse,
    summary="邮箱 + 密码注册",
    description=(
        "使用邮箱和密码注册学生账号。邮箱大小写不敏感，统一以小写存储；"
        "密码经 scrypt 加盐哈希后保存，明文不落库、不回传。"
    ),
    responses={
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "邮箱已注册",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "参数不合法（邮箱格式错误、密码长度或复杂度不满足）",
        },
    },
)
async def register(
    payload: RegisterRequest,
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> RegisterResponse:
    """创建账号，成功返回 201 与账号基本信息。"""
    try:
        user = await register_user(
            email=payload.email,
            password=payload.password,
            repository=repository,
        )
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "email_already_registered",
                "message": "该邮箱已注册，请直接登录",
            },
        ) from None

    return RegisterResponse(
        id=user.id,
        email=user.email,
        created_at=user.created_at,
    )
