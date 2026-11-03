import json
from collections.abc import Iterator
from decimal import Decimal
from typing import NamedTuple
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import bindparam, text
from sqlalchemy.engine import Engine

from backend.server.app import app
from backend.server.sheet import get_sheet_service

_MISSING_ID = 9_000_000_000_001
_PASSWORD = "test-password"
_READ_DENIED = "You do not have READ permissions to access this resource"
_FULL_DENIED = "You do not have FULL permissions to access this resource"
_A4 = "\u04104"
_density = 910_000


class _Api(NamedTuple):
    client: TestClient
    engine: Engine
    sheet_ids: list[int]
    order_ids: list[int]
    usernames: list[str]


class _EmptyCatalog:
    def take_all(self) -> list[object]:
        return []


def _next_density() -> int:
    global _density
    _density += 1
    return _density


def _sheet_body(**overrides: object) -> dict[str, object]:
    body: dict[str, object] = {
        "name": "чужое",
        "height": 210,
        "width": 297,
        "density": _next_density(),
        "cost": "10",
    }
    body.update(overrides)
    return body


def _count_sheets(engine: Engine) -> int:
    with engine.connect() as connection:
        count = connection.execute(
            text("SELECT count(*) FROM sheet")
        ).scalar_one()
    return int(count)


def _token(api: _Api, permissions: str) -> dict[str, str]:
    username = uuid4().hex
    api.usernames.append(username)
    registered = api.client.post(
        "/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": _PASSWORD,
        },
    )
    assert registered.status_code == 201
    with api.engine.begin() as connection:
        connection.execute(
            text(
                'UPDATE "user" SET permissions = '
                "CAST(:permissions AS permission) "
                "WHERE username = :username"
            ),
            {"permissions": permissions, "username": username},
        )
    token = api.client.post(
        "/auth/token",
        json={"username": username, "password": _PASSWORD},
    )
    assert token.status_code == 200
    access_token = token.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


def _create_sheet(
    api: _Api, headers: dict[str, str], **overrides: object
) -> tuple[int, dict[str, object]]:
    body = _sheet_body(**overrides)
    created = api.client.post(
        "/api/v2/sheet/", headers=headers, json=body
    )
    assert created.status_code == 200
    payload = created.json()
    assert set(payload) == {"id"}
    sheet_id = payload["id"]
    assert type(sheet_id) is int
    api.sheet_ids.append(sheet_id)
    return sheet_id, body


def _listed(
    api: _Api, headers: dict[str, str], sheet_id: int
) -> dict[str, object]:
    listed = api.client.get("/api/v2/sheet/", headers=headers)
    assert listed.status_code == 200
    matches = [
        item for item in listed.json() if item["id"] == sheet_id
    ]
    assert len(matches) == 1
    return matches[0]


def _assert_a4(row: dict[str, object], body: dict[str, object]) -> None:
    assert set(row) == {
        "id", "name", "height", "width", "density", "cost",
    }
    assert row["name"] == _A4
    assert ord(str(row["name"])[0]) == 0x0410
    assert row["height"] == 210
    assert row["width"] == 297
    assert row["density"] == body["density"]
    assert type(row["cost"]) is str
    assert Decimal(str(row["cost"])) == Decimal(str(body["cost"]))
    assert "version" not in row


def _order_using(sheet_id: int) -> dict[str, object]:
    return {
        "unit_count": 1,
        "tax_rate": "1",
        "markup": "0",
        "operations": [],
        "printings": [{
            "count": 1,
            "chroma": "ZERO_ZERO",
            "lamination": "DONT",
            "die_cutting": False,
            "stack_height": 0,
            "spacing": 0,
            "press_sheet": sheet_id,
            "list": {"width": 10, "height": 10, "bleeds": 0},
            "press_pricing": {
                "cyan": "0",
                "magenta": "0",
                "yellow": "0",
                "black": "0",
                "salary": "0",
            },
            "cut_pricing": {"salary": "0"},
            "lamination_pricing": {
                "startup": "0",
                "film_cost": "0",
                "salary": "0",
            },
            "die_cut_pricing": {"salary": "0"},
            "comment": "",
        }],
    }


def _reference_document(engine: Engine) -> object:
    with engine.connect() as connection:
        return connection.execute(
            text("SELECT document FROM reference WHERE id = 1")
        ).scalar_one_or_none()


def _restore_reference(engine: Engine, document: object) -> None:
    with engine.begin() as connection:
        if document is None:
            connection.execute(text("DELETE FROM reference WHERE id = 1"))
            return
        connection.execute(
            text(
                "INSERT INTO reference (id, document) "
                "VALUES (1, CAST(:document AS jsonb)) "
                "ON CONFLICT (id) DO UPDATE "
                "SET document = EXCLUDED.document"
            ),
            {"document": json.dumps(document)},
        )


@pytest.fixture
def api(engine: Engine, client: TestClient) -> Iterator[_Api]:
    sheet_ids: list[int] = []
    order_ids: list[int] = []
    usernames: list[str] = []
    bundle = _Api(client, engine, sheet_ids, order_ids, usernames)
    try:
        yield bundle
    finally:
        app.dependency_overrides.pop(get_sheet_service, None)
        if order_ids:
            statement = text(
                'DELETE FROM "order" WHERE id IN :ids'
            ).bindparams(bindparam("ids", expanding=True))
            with engine.begin() as connection:
                connection.execute(statement, {"ids": order_ids})
        if sheet_ids:
            statement = text(
                "DELETE FROM sheet WHERE id IN :ids"
            ).bindparams(bindparam("ids", expanding=True))
            with engine.begin() as connection:
                connection.execute(statement, {"ids": sheet_ids})
        for username in usernames:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        'DELETE FROM "user" WHERE username = :username'
                    ),
                    {"username": username},
                )


def test_should_return_an_empty_list_when_the_catalog_is_empty(
    api: _Api,
) -> None:
    headers = _token(api, "READ")
    app.dependency_overrides[get_sheet_service] = lambda: _EmptyCatalog()
    listed = api.client.get("/api/v2/sheet/", headers=headers)
    assert listed.status_code == 200
    assert listed.json() == []


def test_should_store_an_a4_sheet_under_the_factory_name(
    api: _Api,
) -> None:
    headers = _token(api, "FULL")
    before = _count_sheets(api.engine)
    sheet_id, body = _create_sheet(api, headers)
    assert _count_sheets(api.engine) == before + 1
    _assert_a4(_listed(api, headers, sheet_id), body)


def test_should_return_the_same_id_when_the_same_tuple_is_posted_again(
    api: _Api,
) -> None:
    headers = _token(api, "FULL")
    sheet_id, body = _create_sheet(api, headers)
    before = _count_sheets(api.engine)
    again = api.client.post(
        "/api/v2/sheet/",
        headers=headers,
        json={**body, "name": "другое"},
    )
    assert again.status_code == 200
    assert again.json()["id"] == sheet_id
    assert _count_sheets(api.engine) == before
    _assert_a4(_listed(api, headers, sheet_id), body)


def test_should_reject_a_sheet_whose_sides_are_not_a_factory_format(
    api: _Api,
) -> None:
    headers = _token(api, "FULL")
    before = _count_sheets(api.engine)
    response = api.client.post(
        "/api/v2/sheet/",
        headers=headers,
        json=_sheet_body(height=450, width=320),
    )
    assert response.status_code == 422
    assert response.json()["detail"] == (
        "save: высота и ширина не из фабрики"
    )
    assert _count_sheets(api.engine) == before


def test_should_reprice_a_sheet_and_keep_its_name_and_sides(
    api: _Api,
) -> None:
    headers = _token(api, "FULL")
    sheet_id, body = _create_sheet(api, headers)
    before = _count_sheets(api.engine)
    density = int(body["density"]) + 1
    updated = api.client.post(
        "/api/v2/sheet/",
        headers=headers,
        json={
            "id": sheet_id,
            "name": "чужое",
            "height": 450,
            "width": 320,
            "density": density,
            "cost": "20",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["id"] == sheet_id
    assert _count_sheets(api.engine) == before
    row = _listed(api, headers, sheet_id)
    assert row["name"] == _A4
    assert row["height"] == 210
    assert row["width"] == 297
    assert row["density"] == density
    assert Decimal(str(row["cost"])) == Decimal("20")


def test_should_answer_500_and_write_nothing_when_the_paper_rate_is_negative(
    api: _Api,
) -> None:
    headers = _token(api, "FULL")
    before = _count_sheets(api.engine)
    response = api.client.post(
        "/api/v2/sheet/",
        headers=headers,
        json=_sheet_body(cost="-1"),
    )
    assert response.status_code == 500
    assert response.status_code not in (422, 404)
    assert _count_sheets(api.engine) == before


def test_should_delete_a_free_sheet(api: _Api) -> None:
    headers = _token(api, "FULL")
    sheet_id, _body = _create_sheet(api, headers)
    deleted = api.client.delete(
        f"/api/v2/sheet/{sheet_id}", headers=headers
    )
    assert deleted.status_code == 200
    assert deleted.content == b""
    listed = api.client.get("/api/v2/sheet/", headers=headers)
    assert all(item["id"] != sheet_id for item in listed.json())
    api.sheet_ids.remove(sheet_id)


def test_should_refuse_to_delete_a_sheet_that_an_order_uses(
    api: _Api,
) -> None:
    headers = _token(api, "FULL")
    sheet_id, body = _create_sheet(api, headers)
    created = api.client.post(
        "/api/v2/order/",
        headers=headers,
        json=_order_using(sheet_id),
    )
    assert created.status_code == 200
    order_id = created.json()["id"]
    api.order_ids.append(order_id)
    deleted = api.client.delete(
        f"/api/v2/sheet/{sheet_id}", headers=headers
    )
    assert deleted.status_code == 409
    assert deleted.json()["detail"] == (
        f"delete: лист занят, id={sheet_id}"
    )
    _assert_a4(_listed(api, headers, sheet_id), body)
    loaded = api.client.get(
        f"/api/v2/order/{order_id}", headers=headers
    )
    assert loaded.status_code == 200
    assert loaded.json()["printings"][0]["press_sheet"] == sheet_id


def test_should_refuse_to_delete_a_sheet_that_the_reference_uses(
    api: _Api,
) -> None:
    full = _token(api, "FULL")
    read = _token(api, "READ")
    sheet_id, body = _create_sheet(api, full)
    previous = _reference_document(api.engine)
    try:
        saved = api.client.post(
            "/api/v2/reference/",
            headers=full,
            json=_order_using(sheet_id),
        )
        assert saved.status_code == 200
        deleted = api.client.delete(
            f"/api/v2/sheet/{sheet_id}", headers=full
        )
        assert deleted.status_code == 409
        assert deleted.json()["detail"] == (
            f"delete: лист занят, id={sheet_id}"
        )
        _assert_a4(_listed(api, full, sheet_id), body)
        loaded = api.client.get("/api/v2/reference/", headers=read)
        assert loaded.status_code == 200
        printing = loaded.json()["printings"][0]
        assert printing["press_sheet"] == sheet_id
    finally:
        _restore_reference(api.engine, previous)


def test_should_refuse_to_delete_an_unknown_sheet(api: _Api) -> None:
    headers = _token(api, "FULL")
    before = _count_sheets(api.engine)
    deleted = api.client.delete(
        f"/api/v2/sheet/{_MISSING_ID}", headers=headers
    )
    assert deleted.status_code == 404
    assert deleted.json()["detail"] == (
        f"delete: листа нет, id={_MISSING_ID}"
    )
    assert _count_sheets(api.engine) == before


def test_should_refuse_a_list_without_read_permission(api: _Api) -> None:
    headers = _token(api, "NONE")
    listed = api.client.get("/api/v2/sheet/", headers=headers)
    assert listed.status_code == 403
    assert listed.json()["detail"] == _READ_DENIED


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("post", "/api/v2/sheet/"),
        ("delete", f"/api/v2/sheet/{_MISSING_ID}"),
    ],
)
def test_should_refuse_a_write_without_full_permission(
    api: _Api, method: str, path: str
) -> None:
    headers = _token(api, "READ")
    before = _count_sheets(api.engine)
    payload = _sheet_body() if method == "post" else None
    response = api.client.request(
        method, path, headers=headers, json=payload
    )
    assert response.status_code == 403
    assert response.json()["detail"] == _FULL_DENIED
    assert _count_sheets(api.engine) == before
