"""密码哈希与校验。

设计要点：
- 仅用标准库 ``hashlib.scrypt``，不引入 bcrypt / passlib，少一个依赖。
  scrypt 是内存硬算法，抗 GPU 爆破，参数见 ``_SCRYPT_*``。
- 每个密码单独生成随机盐，哈希结果自带参数与盐，便于日后调参后仍能校验旧密码。
- 明文密码不出本模块，数据库中只存 ``scrypt$n$r$p$salt$hash`` 形式的字符串。
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

# scrypt 参数：n=2^14 时约 16 MiB 内存 / 每次，单次耗时在 50ms 量级，适合登录注册接口。
_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1
_SALT_BYTES = 16
_KEY_LEN = 32
_ALGORITHM = "scrypt"


def hash_password(password: str) -> str:
    """把明文密码转成可入库的哈希字符串（含盐与参数）。"""
    if not password:
        raise ValueError("密码不能为空")

    salt = secrets.token_bytes(_SALT_BYTES)
    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=_KEY_LEN,
    )
    return "$".join(
        (
            _ALGORITHM,
            str(_SCRYPT_N),
            str(_SCRYPT_R),
            str(_SCRYPT_P),
            base64.b64encode(salt).decode("ascii"),
            base64.b64encode(derived).decode("ascii"),
        )
    )


def verify_password(password: str, password_hash: str) -> bool:
    """校验明文密码与哈希是否匹配。哈希格式非法时返回 False，不抛异常。"""
    if not password or not password_hash:
        return False

    parts = password_hash.split("$")
    if len(parts) != 6 or parts[0] != _ALGORITHM:
        return False

    try:
        n, r, p = int(parts[1]), int(parts[2]), int(parts[3])
        salt = base64.b64decode(parts[4], validate=True)
        expected = base64.b64decode(parts[5], validate=True)
    except (ValueError, TypeError):
        return False

    try:
        derived = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=n,
            r=r,
            p=p,
            dklen=len(expected),
        )
    except ValueError:
        # 参数超出 OpenSSL 限制（如 maxmem 不足）时按校验失败处理。
        return False

    return hmac.compare_digest(derived, expected)
