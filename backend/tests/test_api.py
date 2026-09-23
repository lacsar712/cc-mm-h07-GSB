import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.main as main


@pytest.fixture()
def client(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    main.Base.metadata.create_all(engine)
    test_session = sessionmaker(bind=engine)
    monkeypatch.setattr(main, "engine", engine)
    monkeypatch.setattr(main, "SessionLocal", test_session)

    app = main.app
    app.dependency_overrides[main.require_writer] = lambda: {"username": "gasman", "role": "writer"}
    app.dependency_overrides[current_user_dep()] = lambda: {"username": "gasman", "role": "writer"}
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def current_user_dep():
    return main.current_user


def test_input_over_line_alarms_and_shows_real_pct(client):
    # 输入 1.2 且测点名合法：判定进入报警分支，上报浓度为真实值，详情显示百分比。
    resp = client.post("/api/readings", json={"site": "回风巷", "ch4_pct": 1.2})
    assert resp.status_code == 201
    created = resp.json()
    assert created["level"] == "报警"
    assert created["note"] == "甲烷达到报警线"
    assert created["ch4_pct"] == pytest.approx(1.2)

    detail = client.get(f"/api/readings/{created['id']}").json()
    assert detail["ch4_pct"] == pytest.approx(1.2)
    assert detail["ch4_display"] == "1.2"
    assert detail["level"] == "报警"

    rows = client.get("/api/readings").json()
    stored = next(r for r in rows if r["id"] == created["id"])
    assert stored["ch4_pct"] == pytest.approx(1.2)
    assert stored["level"] == "报警"


def test_east_wing_035_stays_normal(client):
    # 东翼 0.35 保持正常：启动种子数据判定正常、存真实值、详情显示百分比。
    rows = client.get("/api/readings").json()
    east = next(r for r in rows if r["site"] == "东翼-12")
    assert east["level"] == "正常"
    assert east["note"] == "甲烷低于报警线"
    assert east["ch4_pct"] == pytest.approx(0.35)

    detail = client.get(f"/api/readings/{east['id']}").json()
    assert detail["ch4_pct"] == pytest.approx(0.35)
    assert detail["ch4_display"] == "0.35"
    assert detail["level"] == "正常"
