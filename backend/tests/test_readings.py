import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.main as main
from app.main import app


@pytest.fixture()
def client():
    # 用共享单连接的内存 SQLite 替换 PostgreSQL，startup 建表并播种东翼-12/回风巷
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    main.engine = test_engine
    main.SessionLocal = sessionmaker(bind=test_engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def writer_token(client):
    resp = client.post(
        "/api/auth/login",
        json={"username": "gasman", "password": "gas123456"},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_report_1_2_with_legal_site_must_alarm_and_show_real_pct(client, writer_token):
    """第一笔：合法测点名上报 1.2%，判定入口、入库浓度、详情展示都必须是真实值并报警。"""
    resp = client.post(
        "/api/readings",
        headers=auth(writer_token),
        json={"site": "回风巷-2", "ch4_pct": 1.2},
    )
    assert resp.status_code == 201, resp.text
    created = resp.json()
    reading_id = created["id"]

    # 判定入口吃真实数值：1.2 >= 1.0 必须报警，不能被旁路压成正常
    assert created["level"] == "报警"
    assert created["note"] == "甲烷达到报警线"
    # 上报带上来的浓度原样入库/回传，不能被压低到 0.95
    assert created["ch4_pct"] == pytest.approx(1.2)
    assert created["site"] == "回风巷-2"

    detail = client.get(f"/api/readings/{reading_id}", headers=auth(writer_token)).json()
    assert detail["level"] == "报警"
    assert detail["ch4_pct"] == pytest.approx(1.2)
    # 详情页必须显示真实百分比，不能再给“—/浓度待复核”
    assert detail["ch4_display"] == "1.2%"

    listed = [r for r in client.get("/api/readings", headers=auth(writer_token)).json() if r["id"] == reading_id]
    assert listed and listed[0]["ch4_pct"] == pytest.approx(1.2)
    assert listed[0]["level"] == "报警"


def test_east_wing_0_35_stays_normal(client, writer_token):
    """第二笔：播种数据东翼-12 浓度 0.35%，保持正常且详情显示真实百分比。"""
    rows = client.get("/api/readings", headers=auth(writer_token)).json()
    east = [r for r in rows if r["site"] == "东翼-12"]
    assert len(east) == 1
    assert east[0]["ch4_pct"] == pytest.approx(0.35)
    assert east[0]["level"] == "正常"
    assert east[0]["note"] == "甲烷低于报警线"

    detail = client.get(f"/api/readings/{east[0]['id']}", headers=auth(writer_token)).json()
    assert detail["level"] == "正常"
    assert detail["ch4_pct"] == pytest.approx(0.35)
    assert detail["ch4_display"] == "0.35%"
