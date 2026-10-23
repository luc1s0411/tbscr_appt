"""健康检查接口测试。

对应部署探活需求：服务启动后 /health 必须可访问且返回 ok。
"""

from fastapi.testclient import TestClient

from app.main import VERSION, app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "tbscr-appt"
    assert body["version"] == VERSION


def test_unknown_path_returns_404() -> None:
    assert client.get("/not-exist").status_code == 404
