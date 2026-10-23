"""注册业务逻辑。

只做三件事：归一化 → 唯一性校验 → 哈希后落库。
登录、发验证码、身份绑定均不在本次范围内（见 docs/PRD.md 3.1-S1/S2）。
"""

from __future__ import annotations

from app.core.security import hash_password
from app.repositories.user_repository import (
    EmailConflictError,
    User,
    UserRepository,
)


class EmailAlreadyRegisteredError(Exception):
    """邮箱已被注册。"""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"邮箱已注册: {email}")


async def register_user(
    *,
    email: str,
    password: str,
    repository: UserRepository,
) -> User:
    """注册一个学生账号。

    邮箱已在仓储层存在时抛 ``EmailAlreadyRegisteredError``；
    唯一性以仓储的原子写入为准（对应 MySQL 的唯一索引 + 1062 冲突），
    所以这里不需要「先查再插」的两次查询来保证正确性。
    """
    normalized_email = email.strip().lower()

    try:
        return await repository.create(
            email=normalized_email,
            password_hash=hash_password(password),
        )
    except EmailConflictError as exc:
        raise EmailAlreadyRegisteredError(normalized_email) from exc
