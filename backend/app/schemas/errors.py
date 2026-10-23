"""统一错误响应模型，供 OpenAPI 文档声明非 2xx 响应。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(description="稳定的机器可读错误码，前端据此提示")
    message: str = Field(description="面向用户的中文错误信息")


class ErrorResponse(BaseModel):
    detail: ErrorDetail
