"""注册接口测试（POST /auth/register）。

覆盖三类场景：
1. 成功注册：201、响应字段、邮箱归一化、密码只以哈希形式落库；
2. 邮箱重复：409 且返回明确错误码，且不产生第二个账号；
3. 非法参数：邮箱格式、密码长度与复杂度、缺失字段均返回 422。
"""

from __future__ import annotations

import asyncio
import re

import pytest
from fastapi.testclient import TestClient

from app.core.security import verify_password
from app.main import app
from app.repositories.user_repository import (
    InMemoryUserRepository,
    get_user_repository,
)

REGISTER_URL = "/auth/register"
VALID_EMAIL = "student001@hebau.edu.cn"
VALID_PASSWORD = "tbscr2026"


@pytest.fixture
def repository() -> InMemoryUserRepository:
    """每个用例一个干净仓储，避免用例之间互相污染。"""
    return InMemoryUserRepository()


@pytest.fixture
def client(repository: InMemoryUserRepository) -> TestClient:
    app.dependency_overrides[get_user_repository] = lambda: repository
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _get_user(repository: InMemoryUserRepository, email: str):
    return asyncio.run(repository.get_by_email(email))


# --------------------------------------------------------------------------
# 1. 成功注册
# --------------------------------------------------------------------------
def test_register_success(client: TestClient) -> None:
    response = client.post(
        REGISTER_URL,
        json={"email": VALID_EMAIL, "password": VALID_PASSWORD},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == VALID_EMAIL
    assert re.fullmatch(r"[0-9a-f]{32}", body["id"])
    # 创建时间必须带时区（docs/TECH_STACK.md 5.3：统一存 UTC）
    assert body["created_at"].endswith("Z") or "+00:00" in body["created_at"]
    # 响应体不能泄露密码或哈希
    assert "password" not in body
    assert "password_hash" not in body


def test_register_normalizes_email_case(client: TestClient, repository) -> None:
    response = client.post(
        REGISTER_URL,
        json={"email": "  Student001@HEBAU.Edu.CN  ", "password": VALID_PASSWORD},
    )

    assert response.status_code == 201
    assert response.json()["email"] == VALID_EMAIL
    assert _get_user(repository, VALID_EMAIL) is not None


def test_register_stores_only_hashed_password(client: TestClient, repository) -> None:
    client.post(
        REGISTER_URL,
        json={"email": VALID_EMAIL, "password": VALID_PASSWORD},
    )

    user = _get_user(repository, VALID_EMAIL)
    assert user is not None
    assert user.password_hash != VALID_PASSWORD
    assert VALID_PASSWORD not in user.password_hash
    assert user.password_hash.startswith("scrypt$")
    assert verify_password(VALID_PASSWORD, user.password_hash) is True
    assert verify_password("wrong-password1", user.password_hash) is False


def test_same_password_gets_different_hash(client: TestClient, repository) -> None:
    """每个账号独立随机盐，相同密码不能产生相同哈希。"""
    client.post(
        REGISTER_URL,
        json={"email": "a@hebau.edu.cn", "password": VALID_PASSWORD},
    )
    client.post(
        REGISTER_URL,
        json={"email": "b@hebau.edu.cn", "password": VALID_PASSWORD},
    )

    hash_a = _get_user(repository, "a@hebau.edu.cn").password_hash
    hash_b = _get_user(repository, "b@hebau.edu.cn").password_hash
    assert hash_a != hash_b


# --------------------------------------------------------------------------
# 2. 邮箱重复
# --------------------------------------------------------------------------
def test_register_duplicate_email_returns_409(client: TestClient) -> None:
    payload = {"email": VALID_EMAIL, "password": VALID_PASSWORD}
    assert client.post(REGISTER_URL, json=payload).status_code == 201

    response = client.post(REGISTER_URL, json=payload)

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "email_already_registered"
    assert "已注册" in detail["message"]


def test_register_duplicate_email_ignores_case(client: TestClient) -> None:
    client.post(REGISTER_URL, json={"email": VALID_EMAIL, "password": VALID_PASSWORD})

    response = client.post(
        REGISTER_URL,
        json={"email": VALID_EMAIL.upper(), "password": "another2026"},
    )

    assert response.status_code == 409


def test_register_duplicate_does_not_create_second_account(
    client: TestClient, repository
) -> None:
    client.post(REGISTER_URL, json={"email": VALID_EMAIL, "password": VALID_PASSWORD})
    first = _get_user(repository, VALID_EMAIL)

    client.post(REGISTER_URL, json={"email": VALID_EMAIL, "password": "another2026"})

    second = _get_user(repository, VALID_EMAIL)
    assert second is not None
    # 原账号未被覆盖，密码仍是第一次注册的那一个
    assert second.id == first.id
    assert second.password_hash == first.password_hash
    assert verify_password(VALID_PASSWORD, second.password_hash) is True


# --------------------------------------------------------------------------
# 3. 非法参数
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "email",
    [
        "not-an-email",
        "student001@",
        "@hebau.edu.cn",
        "student 001@hebau.edu.cn",
        "",
    ],
)
def test_register_invalid_email_returns_422(client: TestClient, email: str) -> None:
    response = client.post(
        REGISTER_URL,
        json={"email": email, "password": VALID_PASSWORD},
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("password", "reason"),
    [
        ("tb2026", "少于 8 位"),
        ("tbscr" + "a" * 123 + "1", "超过 128 位"),
        ("tbscrpassword", "缺少数字"),
        ("1234567890", "缺少字母"),
        ("", "空密码"),
    ],
)
def test_register_invalid_password_returns_422(
    client: TestClient, password: str, reason: str
) -> None:
    response = client.post(
        REGISTER_URL,
        json={"email": VALID_EMAIL, "password": password},
    )

    assert response.status_code == 422, reason


@pytest.mark.parametrize(
    "payload",
    [
        {"password": VALID_PASSWORD},
        {"email": VALID_EMAIL},
        {},
        {"email": VALID_EMAIL, "password": VALID_PASSWORD, "extra": "ignored"},
    ],
)
def test_register_missing_fields_returns_422(client: TestClient, payload: dict) -> None:
    response = client.post(REGISTER_URL, json=payload)

    if "email" in payload and "password" in payload:
        # 多余字段被忽略，注册照常成功
        assert response.status_code == 201
    else:
        assert response.status_code == 422


def test_register_rejects_non_json_body(client: TestClient) -> None:
    response = client.post(
        REGISTER_URL,
        data={"email": VALID_EMAIL, "password": VALID_PASSWORD},
    )

    assert response.status_code == 422


def test_invalid_request_does_not_persist_user(client: TestClient, repository) -> None:
    client.post(REGISTER_URL, json={"email": VALID_EMAIL, "password": "short"})

    assert _get_user(repository, VALID_EMAIL) is None
