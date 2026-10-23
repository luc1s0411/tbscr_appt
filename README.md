# 结核病筛查预约管理 App

河北农业大学校医院使用的结核病筛查预约管理系统。学生用邮箱验证码登录后预约筛查时段，校医院管理员配置号源、现场扫码核销、录入结果并导出名单。

> **当前状态：骨架 + 注册接口。** 后端提供 `GET /health` 与 `POST /auth/register`，前端仅有一个静态首页，其余业务功能尚未开发。

## 当前进度

| 部分 | 状态 |
| --- | --- |
| 后端 | ✅ FastAPI 骨架，`GET /health` 可用，25 条接口测试通过 |
| 注册 | ✅ `POST /auth/register` 邮箱 + 密码注册，密码 scrypt 哈希，邮箱重复返回 409（数据暂存进程内，见「已知限制」） |
| 前端 | ✅ uni-app 骨架，H5 首页可打开，`build:h5` 构建通过 |
| 登录 / 数据库 / 预约 / 核销 / 导出 | ⬜ 未开发（见 `docs/PRD.md`） |

## 技术栈

| 层 | 选型 | 当前版本 |
| --- | --- | --- |
| 前端 | uni-app（Vue 3 + Vite） | uni-app 3.0.0-5030320261023001 / Vue 3.4.21 / Vite 5.2.8 |
| 后端 | Python + FastAPI + uvicorn | FastAPI 0.161.1 / uvicorn 0.54.0 |
| 数据库 | MySQL 8.0 | 未接入 |
| 部署 | Caddy + Docker Compose | 未配置 |

未引入 Redis、消息队列、微服务。理由见 `docs/TECH_STACK.md`。

## 目录结构

```
tbscr_appt/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    FastAPI 入口，装配 /health 与 /auth
│   │   ├── api/routes/auth.py         POST /auth/register
│   │   ├── services/auth_service.py   注册业务逻辑（归一化 + 唯一性 + 哈希）
│   │   ├── repositories/user_repository.py  用户仓储（当前为进程内实现）
│   │   ├── schemas/auth.py            注册请求/响应模型
│   │   ├── schemas/errors.py          统一错误响应模型
│   │   └── core/security.py           密码哈希与校验（scrypt）
│   ├── .venv/                 本地虚拟环境（不入库）
│   ├── requirements.txt
│   └── requirements-dev.txt   含 pytest、httpx
├── frontend/
│   ├── src/
│   │   ├── pages/index/index.vue   首页
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── pages.json
│   │   └── manifest.json
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── tests/
│   ├── test_health.py         对应 GET /health
│   └── test_auth_register.py  对应 POST /auth/register
├── docs/
│   ├── PRD.md                 需求
│   ├── TECH_STACK.md          技术方案与实现红线
│   └── API.md                 已实现接口契约（注册）
├── pytest.ini
├── AGENTS.md                  协作约定（动手前先读）
├── .env.example
└── README.md
```

## 环境要求

- Python 3.11+（本机以 3.13 验证）
- Node.js 18+（本机以 22.22 验证）

## 安装与启动

### 1. 后端

```bash
cd backend
python -m venv .venv
```

激活虚拟环境：

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Windows CMD
.venv\Scripts\activate.bat
# macOS / Linux
source .venv/bin/activate
```

安装依赖并启动：

```bash
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

- 健康检查：<http://127.0.0.1:8000/health> → `{"status":"ok","service":"tbscr-appt","version":"0.1.0"}`
- 接口文档：<http://127.0.0.1:8000/docs>

> pip 下载慢时加国内镜像：`pip install -r requirements-dev.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

### 2. 前端

```bash
cd frontend
npm install
npm run dev:h5
```

打开 <http://127.0.0.1:5173> 即为首页。

构建 H5（产物在 `frontend/dist/build/h5`）：

```bash
npm run build:h5
```

> APK 打包需先到 `frontend/src/manifest.json` 填写 `appid`，再用 HBuilderX 云打包。当前 `appid` 为空，仅影响 APK 与统计功能，H5 不受影响。

### 3. 测试

在仓库根目录执行（`pytest.ini` 已配置 `pythonpath = backend`）：

```bash
pytest tests -v
```

预期输出：`25 passed`。

### 4. 环境变量

```bash
cp .env.example .env
```

**当前最小版本尚未读取任何环境变量**，`.env.example` 是为后续接入数据库、邮件、JWT 预留的模板。`.env` 已在 `.gitignore` 中排除。

## 已验证结果

| 检查项 | 命令 | 结果 |
| --- | --- | --- |
| 后端测试 | `pytest tests -v` | 25 passed |
| 后端启动 | `uvicorn app.main:app` | `/health` 返回 200 |
| 注册接口冒烟 | `curl -X POST /auth/register` | 首次 201；同邮箱（改大小写）再注册 409；非法邮箱 422 |
| 前端构建 | `npm run build:h5` | Build complete |
| 前端启动 | `npm run dev:h5` | 首页返回 200，页面标题与组件编译正常 |

## 已知限制

- `frontend/src/manifest.json` 的 `appid` 为空，APK 打包前需补；打包时控制台会提示「未配置 Appid，统计不可用」，属预期。
- `npm install` 报告 33 个依赖漏洞，均来自 uni-app 工具链的传递依赖，暂不处理。
- 首页为静态页面，**不请求后端接口**，前后端尚未联调（按「暂不开发业务功能」要求）。
- **用户数据暂存进程内**（`backend/app/repositories/user_repository.py`）：后端重启后注册数据丢失，多 worker 之间不共享。MySQL 尚未接入，建表语句与替换步骤见 `docs/API.md` 第 3 节。
- 已实现接口只有 `GET /health` 与 `POST /auth/register`；登录（发验证码 / 换 JWT）、身份绑定、业务接口均未创建。

## 文档

| 文档 | 内容 |
| --- | --- |
| [docs/PRD.md](docs/PRD.md) | 项目目标、用户流程、功能清单、暂不开发项、验收标准 |
| [docs/TECH_STACK.md](docs/TECH_STACK.md) | 技术选型、实现要点、已知坑、部署方案 |
| [docs/API.md](docs/API.md) | 已实现接口契约：`POST /auth/register`、密码存储、数据存储现状 |
| [AGENTS.md](AGENTS.md) | 协作约定与开发规则 |

## 使用单位

河北农业大学校医院
