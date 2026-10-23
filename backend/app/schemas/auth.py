"""认证相关的请求/响应模型。

校验策略：
- 邮箱用 Pydantic 的 ``EmailStr``（依赖 email-validator），格式不合法直接 422。
- 密码 8–128 位，且必须同时包含字母和数字；不做「特殊字符」强制，避免影响学生输入习惯。
- 响应体只回 id / email / created_at，任何情况下都不回传密码或哈希。
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128


class RegisterRequest(BaseModel):
    """注册请求体。"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "student001@hebau.edu.cn",
                "password": "tbscr2026",
            }
        }
    )

    email: EmailStr = Field(description="登录邮箱，全局唯一，大小写不敏感")
    password: str = Field(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        description=f"密码，{PASSWORD_MIN_LENGTH}–{PASSWORD_MAX_LENGTH} 位，需同时包含字母和数字",
    )

    @field_validator("password")
    @classmethod
    def _check_password_strength(cls, value: str) -> str:
        if not any(ch.isalpha() for ch in value):
            raise ValueError("密码必须包含至少一个字母")
        if not any(ch.isdigit() for ch in value):
            raise ValueError("密码必须包含至少一个数字")
        return value

    @field_validator("email", mode="before")
    @classmethod
    def _normalize_email(cls, value: object) -> object:
        """先去掉首尾空白并转小写，再做格式校验。

        保证 ``A@x.com`` 与 ``a@x.com`` 被判定为同一账号。
        """
        if isinstance(value, str):
            return value.strip().lower()
        return value


class RegisterResponse(BaseModel):
    """注册成功响应体。"""

    id: str = Field(description="用户 ID（UUID4 hex）")
    email: EmailStr = Field(description="已归一化为小写的登录邮箱")
    created_at: datetime = Field(description="创建时间，UTC 带时区")
