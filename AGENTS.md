# AGENTS.md

## 项目说明

- 项目目标：河北农业大学校医院的结核病筛查预约管理 App。学生用邮箱验证码登录，预约筛查日期与时段、查看预约凭证、开检前 24 小时可取消或改约；校医院管理员配置号源、按学院批次排期、现场扫码核销、录入 4 项筛查结果并导出名单。
- 技术栈：前端 uni-app（Vue 3 + Vite），产出 Android APK；后端 Python 3.12 + FastAPI + SQLAlchemy 2.0（async）+ Alembic；数据库 MySQL 8.0；认证 JWT；验证码邮件走 aiosmtplib；导出用 openpyxl；部署为 Caddy + Docker Compose。未使用 Redis、消息队列、微服务。
- 前端目录：`frontend/`（uni-app 客户端，尚未初始化）
- 后端目录：`backend/`（FastAPI 后端，尚未初始化）

需求见 `docs/PRD.md`，技术方案与已知坑见 `docs/TECH_STACK.md`，验收测试放 `tests/`。

## 开发规则

1. 一次只实现当前任务，不修改无关文件。
2. 不做未经要求的大范围重构。
3. 密钥和密码只能通过环境变量提供，不提交 .env。
4. 接口或数据库有变化时同步更新对应文档。
5. 完成任务前运行相关测试、构建或静态检查。
6. 删除文件、执行数据库迁移、修改生产配置前必须确认。

> 技术红线见 `docs/TECH_STACK.md` 第 5 节（名额扣减、核销幂等、时区、验证码存储）。

## 常用命令

- 启动后端：`cd backend && uvicorn app.main:app --reload`（需先激活 `.venv`；接口文档 `http://127.0.0.1:8000/docs`）
- 启动前端：`cd frontend && npm run dev:h5`（`http://127.0.0.1:5173`）
- 后端测试：`pytest tests -v`（在仓库根目录执行）
- 前端检查：`cd frontend && npm run build:h5`（当前未配置 ESLint，以构建代替静态检查）

> 前后端骨架已可运行（后端 `GET /health`、前端静态首页），业务功能未开发。
