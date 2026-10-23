"""应用入口。

当前提供健康检查与注册接口；其余业务接口（登录、号源、预约、核销、结果、导出）
待按 docs/PRD.md 实现。
"""

from fastapi import FastAPI

from app.api.routes import auth as auth_routes

SERVICE_NAME = "tbscr-appt"
VERSION = "0.2.0"

app = FastAPI(
    title="结核病筛查预约管理 API",
    description=(
        "河北农业大学校医院结核病筛查预约管理后端。"
        "当前已实现健康检查与邮箱密码注册，其余业务接口开发中。"
    ),
    version=VERSION,
)

app.include_router(auth_routes.router)


@app.get("/health", tags=["system"], summary="健康检查")
async def health() -> dict[str, str]:
    """返回服务存活状态，供部署探活与联调自检使用。"""
    return {"status": "ok", "service": SERVICE_NAME, "version": VERSION}
