# 接口文档（按已实现接口维护）

- 对应需求：`docs/PRD.md` 3.1-S1（邮箱验证码登录/注册，同一邮箱唯一账号）
- 对应技术方案：`docs/TECH_STACK.md`（FastAPI + Pydantic v2）
- 本文只记录**代码里已实现**的接口；运行时文档见 `http://127.0.0.1:8000/docs`（OpenAPI 自动生成）。

## 0. 通用约定

| 项 | 约定 |
| --- | --- |
| 请求/响应格式 | JSON，`Content-Type: application/json` |
| 时间字段 | ISO 8601，UTC 带时区（如 `2026-10-23T17:14:02.147149Z`），前端本地化展示 |
| 成功响应 | 直接返回业务字段，无统一信封 |
| 业务错误 | `{"detail": {"code": "<机器可读错误码>", "message": "<中文提示>"}}` |
| 参数校验错误 | FastAPI 默认 422 结构 `{"detail": [{"loc": [...], "msg": "...", ...}]}`，`msg` 为英文（Pydantic 默认） |

---

## 1. POST /auth/register

邮箱 + 密码注册学生账号。**当前不返回 token，登录接口另行实现。**

### 1.1 请求体

| 字段 | 类型 | 必填 | 规则 |
| --- | --- | --- | --- |
| `email` | string | 是 | 合法邮箱格式；首尾空白会被去除，统一转小写存储（`A@x.com` 与 `a@x.com` 视为同一账号） |
| `password` | string | 是 | 8–128 位；必须同时包含字母和数字；不强制特殊字符 |

```json
{
  "email": "student001@hebau.edu.cn",
  "password": "tbscr2026"
}
```

### 1.2 成功响应 `201 Created`

```json
{
  "id": "0f38eb10f1c5410e9d38f4045bff25b5",
  "email": "student001@hebau.edu.cn",
  "created_at": "2026-10-23T17:14:02.147149Z"
}
```

- `id`：用户 ID，UUID4 hex（32 位小写十六进制）。
- 响应体**不含** `password`、`password_hash` 等任何密码信息。

### 1.3 邮箱已注册 `409 Conflict`

```json
{
  "detail": {
    "code": "email_already_registered",
    "message": "该邮箱已注册，请直接登录"
  }
}
```

邮箱比较不区分大小写；冲突时不覆盖原账号、不产生第二条记录。

### 1.4 参数不合法 `422 Unprocessable Entity`

覆盖：邮箱格式错误、密码长度不足 8 位或超过 128 位、密码缺字母或缺数字、缺少必填字段、请求体非 JSON。非法请求不会写入任何数据。

---

## 2. 密码存储

- 算法：`hashlib.scrypt`（Python 标准库，未引入 bcrypt / passlib）。
- 参数：`n=2^14, r=8, p=1`，每账号 16 字节随机盐，派生 32 字节。
- 入库格式：`scrypt$<n>$<r>$<p>$<base64(salt)>$<base64(hash)>`，参数随哈希保存，日后调参不影响旧数据校验。
- 校验用 `hmac.compare_digest` 常量时间比较。实现见 `backend/app/core/security.py`。

## 3. 数据存储现状（临时）

用户数据当前存在 `backend/app/repositories/user_repository.py` 的进程内仓储（`InMemoryUserRepository`）：
**重启即丢、多 worker 之间不共享**，仅为骨架阶段与接口测试服务。MySQL 尚未接入（README「已知限制」）。

接入 MySQL 时按下列等价结构建表，并把仓储实现换成 SQLAlchemy async 版本，接口与业务层无需改动：

```sql
CREATE TABLE `user` (
  `id`            CHAR(32)     NOT NULL COMMENT 'UUID4 hex',
  `email`         VARCHAR(254) NOT NULL COMMENT '登录邮箱，小写归一化',
  `password_hash` VARCHAR(255) NOT NULL COMMENT 'scrypt$n$r$p$salt$hash',
  `created_at`    DATETIME(6)  NOT NULL COMMENT 'UTC',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

唯一性由 `uk_user_email` 保证：并发注册同一邮箱时捕获 MySQL 1062 冲突 → 返回 409，与当前进程内实现的语义一致。

## 4. 未实现（本次范围外）

- 登录发码 / 校验验证码 / 签发 JWT（PRD 3.1-S1 后半段）
- 身份绑定学号、姓名、学院（PRD 3.1-S2）
- 注册频控与验证码表 `email_code`（TECH_STACK 4.3）
