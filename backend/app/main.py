"""应用入口。

当前为最小可运行版本，只提供健康检查接口。
业务接口（登录、号源、预约、核销、结果、导出）待按 docs/PRD.md 实现。
"""

from fastapi import FastAPI

SERVICE_NAME = "tbscr-appt"
VERSION = "0.1.0"

app = FastAPI(
    title="结核病筛查预约管理 API",
    description="河北农业大学校医院结核病筛查预约管理后端。最小可运行版本，仅提供健康检查。",
    version=VERSION,
)


@app.get("/health", tags=["system"], summary="健康检查")
async def health() -> dict[str, str]:
    """返回服务存活状态，供部署探活与联调自检使用。"""
    return {"status": "ok", "service": SERVICE_NAME, "version": VERSION}
