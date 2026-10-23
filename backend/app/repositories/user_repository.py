"""用户数据访问层。

当前仓库还没有接入 MySQL（见 docs/TECH_STACK.md 与 README「已知限制」），
所以这里先定义抽象的 ``UserRepository`` 协议 + 进程内实现，业务层只依赖协议。
接入数据库时新增一个 SQLAlchemy 实现替换依赖注入即可，接口与业务代码不用动。

需要注意：进程内实现只在单进程内有效，重启即丢失，仅用于骨架阶段与测试。
对应的 MySQL 建表语句见 docs/API.md。
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol, runtime_checkable


class EmailConflictError(Exception):
    """邮箱已存在。由唯一约束（或等价的唯一性校验）抛出。"""


@dataclass(frozen=True, slots=True)
class User:
    """用户实体。只保存密码哈希，不保存明文密码。"""

    id: str
    email: str
    password_hash: str
    created_at: datetime


@runtime_checkable
class UserRepository(Protocol):
    """用户仓储协议。方法全部异步，方便日后替换为 SQLAlchemy async 实现。"""

    async def get_by_email(self, email: str) -> User | None: ...

    async def create(self, *, email: str, password_hash: str) -> User:
        """创建用户；邮箱已存在时抛 ``EmailConflictError``。"""
        ...


class InMemoryUserRepository:
    """进程内用户仓储，用锁保证「邮箱唯一」在校验+写入之间不被并发穿透。"""

    def __init__(self) -> None:
        self._users: dict[str, User] = {}
        self._lock = asyncio.Lock()

    async def get_by_email(self, email: str) -> User | None:
        return self._users.get(email)

    async def create(self, *, email: str, password_hash: str) -> User:
        async with self._lock:
            if email in self._users:
                raise EmailConflictError(email)

            user = User(
                id=uuid.uuid4().hex,
                email=email,
                password_hash=password_hash,
                created_at=datetime.now(timezone.utc),
            )
            self._users[email] = user
            return user


_repository = InMemoryUserRepository()


def get_user_repository() -> UserRepository:
    """FastAPI 依赖：返回用户仓储实例。测试中可整体覆盖。"""
    return _repository
