import json
import re
from collections.abc import Iterator
from datetime import date
from decimal import Decimal
from typing import NamedTuple
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import bindparam, text
from sqlalchemy.engine import Engine

from backend.server.app import app
from backend.server.workplace_order import get_workplace_order_service
from backend.workplace.administrator import Administrator
from backend.workplace.cost_order import Order
from backend.workplace.order_repository import (
    OrderNotFound,
    OrderStoreUnavailable,
)
from backend.workplace.order_service import WorkplaceOrderService
from backend.workplace.reports import CostReport
from backend.workplace_order_db import (
    SqlWorkplaceOrderRepository,
    create_sync_engine,
)

_MISSING_ID = 9_000_000_000_001
_PASSWORD = "test-password"
_READ_DENIED = "You do not have READ permissions to access this resource"
_FULL_DENIED = "You do not have FULL permissions to access this resource"

_ORDER_KEYS = {
    "unit_count",
    "tax_rate",
    "markup",
    "operations",
    "printings",
    "id",
    "comment",
    "status",
    "creation_date",
}
_PRINTING_KEYS = {
    "count",
    "chroma",
    "lamination",
    "die_cutting",
    "sheet_by_fitting",
    "stack_height",
    "press_sheet",
    "list",
    "press_pricing",
    "cut_pricing",
    "lamination_pricing",
    "die_cut_pricing",
    "comment",
}
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_ZERO_REPORT = {
    "unit_cost_price": "0.00",
    "unit_cost": "0.00",
    "edition_cost": "0.00",
    "profit_after_tax": "0.00",
    "printing_cost_reports": [],
}
_OPERATION_REPORT = {
    "unit_cost_price": "3.00",
    "unit_cost": "3.00",
    "edition_cost": "6.00",
    "profit_after_tax": "0.00",
    "printing_cost_reports": [],
}
_ZERO_COST = CostReport(
    Decimal("0.00"),
    Decimal("0.00"),
    Decimal("0.00"),
    Decimal("0.00"),
    (),
)
_OPERATION_COST = CostReport(
    Decimal("3.00"),
    Decimal("3.00"),
    Decimal("6.00"),
    Decimal("0.00"),
    (),
)
_PRESS_KEYS = ("cyan", "magenta", "yellow", "black", "paper", "salary")


class _Api(NamedTuple):
    client: TestClient
    engine: Engine
    saved_ids: list[int]
    usernames: list[str]


class _EmptyCatalog:
    def take_all(self) -> list[Order]:
        return []


class _UnavailableTake:
    def take(self, order_id: int) -> Order:
        cause = RuntimeError(
            "postgres://user:secret-token@127.0.0.1/db"
        )
        raise OrderStoreUnavailable("take", 5) from cause


def _empty_order(**overrides: object) -> dict[str, object]:
    body: dict[str, object] = {
        "unit_count": 1,
        "tax_rate": "1",
        "markup": "0",
        "operations": [],
        "printings": [],
    }
    body.update(overrides)
    return body


def _operation_order(**overrides: object) -> dict[str, object]:
    return _empty_order(
        unit_count=2,
        operations=[{
            "name": "рез",
            "cost": "3",
            "description": "кромка",
        }],
        **overrides,
    )


def _zero_rates() -> dict[str, str]:
    return {name: "0" for name in _PRESS_KEYS}


def _printing(
    *,
    chroma: str,
    lamination: str,
    die_cutting: bool,
    press: dict[str, str],
    cut: str,
    film: dict[str, str],
    die_cut: str,
    comment: str = "",
) -> dict[str, object]:
    return {
        "count": 2,
        "chroma": chroma,
        "lamination": lamination,
        "die_cutting": die_cutting,
        "sheet_by_fitting": 3,
        "stack_height": 4,
        "press_sheet": {
            "density": 5,
            "width": 6,
            "height": 7,
            "spacing": 8,
        },
        "list": {"width": 9, "height": 10, "bleeds": 11},
        "press_pricing": press,
        "cut_pricing": {"salary": cut},
        "lamination_pricing": film,
        "die_cut_pricing": {"salary": die_cut},
        "comment": comment,
    }


def _first_printing() -> dict[str, object]:
    press = _zero_rates()
    press["cyan"] = "1.5"
    press["magenta"] = "2"
    return _printing(
        chroma="FOUR_ZERO",
        lamination="ONE_ONE",
        die_cutting=True,
        press=press,
        cut="3",
        film={"startup": "4", "film_cost": "5", "salary": "6"},
        die_cut="7",
        comment="кромка",
    )


def _second_printing() -> dict[str, object]:
    return _printing(
        chroma="ZERO_ZERO",
        lamination="DONT",
        die_cutting=False,
        press=_zero_rates(),
        cut="0",
        film={"startup": "0", "film_cost": "0", "salary": "0"},
        die_cut="0",
    )


def _count_rows(engine: Engine, table: str) -> int:
    with engine.connect() as connection:
        count = connection.execute(
            text(f"SELECT count(*) FROM {table}")
        ).scalar_one()
    return int(count)


def _counts(api: _Api) -> tuple[int, int]:
    return (
        _count_rows(api.engine, "workplace_order"),
        _count_rows(api.engine, "workplace_cost_report"),
    )


def _reference_document(engine: Engine) -> object:
    with engine.connect() as connection:
        return connection.execute(
            text(
                "SELECT document FROM workplace_reference WHERE id = 1"
            )
        ).scalar_one_or_none()


def _restore_reference(engine: Engine, document: object) -> None:
    with engine.begin() as connection:
        if document is None:
            connection.execute(
                text("DELETE FROM workplace_reference WHERE id = 1")
            )
            return
        connection.execute(
            text(
                "INSERT INTO workplace_reference (id, document) "
                "VALUES (1, CAST(:document AS jsonb)) "
                "ON CONFLICT (id) DO UPDATE "
                "SET document = EXCLUDED.document"
            ),
            {"document": json.dumps(document)},
        )


def _zero_printing() -> dict[str, object]:
    return {
        "count": 0,
        "chroma": "ZERO_ZERO",
        "lamination": "DONT",
        "die_cutting": False,
        "sheet_by_fitting": 0,
        "stack_height": 0,
        "press_sheet": {
            "density": 0,
            "width": 0,
            "height": 0,
            "spacing": 0,
        },
        "list": {"width": 0, "height": 0, "bleeds": 0},
        "press_pricing": _zero_rates(),
        "cut_pricing": {"salary": "0"},
        "lamination_pricing": {
            "startup": "0",
            "film_cost": "0",
            "salary": "0",
        },
        "die_cut_pricing": {"salary": "0"},
        "comment": "",
    }


def _reference_body(cyan: str, comment: str) -> dict[str, object]:
    printing = _zero_printing()
    press = _zero_rates()
    press["cyan"] = cyan
    printing["press_pricing"] = press
    return {
        "unit_count": 1,
        "tax_rate": "0",
        "markup": "0",
        "operations": [],
        "printings": [printing],
        "id": _MISSING_ID,
        "comment": comment,
        "status": "Отложен",
    }


def _reports(api: _Api, order_id: int) -> list[CostReport]:
    return SqlWorkplaceOrderRepository(api.engine).reports(order_id)


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


def _remember(api: _Api, response: Response) -> int:
    body = response.json()
    assert set(body) == {"id"}
    order_id = body["id"]
    assert type(order_id) is int
    api.saved_ids.append(order_id)
    return order_id


def _internal_error(response: Response) -> str:
    content_type = response.headers.get("content-type", "")
    if content_type.startswith("application/json"):
        detail = response.json()["detail"]
        assert type(detail) is str
        return detail
    return response.text


def _assert_money(actual: object, expected: str) -> None:
    assert type(actual) is str
    assert Decimal(actual) == Decimal(expected)


def _assert_printing(
    actual: dict[str, object], expected: dict[str, object]
) -> None:
    assert set(actual) == _PRINTING_KEYS
    assert actual["chroma"] == expected["chroma"]
    assert type(actual["chroma"]) is str
    assert actual["lamination"] == expected["lamination"]
    assert type(actual["lamination"]) is str
    assert type(actual["die_cutting"]) is bool
    assert actual["die_cutting"] is expected["die_cutting"]
    for key in ("count", "sheet_by_fitting", "stack_height"):
        assert type(actual[key]) is int
        assert actual[key] == expected[key]
    for key in ("density", "width", "height", "spacing"):
        assert type(actual["press_sheet"][key]) is int
        assert actual["press_sheet"][key] == expected["press_sheet"][key]
    for key in ("width", "height", "bleeds"):
        assert type(actual["list"][key]) is int
        assert actual["list"][key] == expected["list"][key]
    for name in _PRESS_KEYS:
        _assert_money(
            actual["press_pricing"][name],
            expected["press_pricing"][name],
        )
    _assert_money(
        actual["cut_pricing"]["salary"],
        expected["cut_pricing"]["salary"],
    )
    for name in ("startup", "film_cost", "salary"):
        _assert_money(
            actual["lamination_pricing"][name],
            expected["lamination_pricing"][name],
        )
    _assert_money(
        actual["die_cut_pricing"]["salary"],
        expected["die_cut_pricing"]["salary"],
    )
    assert type(actual["comment"]) is str
    assert actual["comment"] == expected["comment"]


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    sync_engine = create_sync_engine()
    try:
        yield sync_engine
    finally:
        sync_engine.dispose()


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    # Один цикл на модуль: async-движок приложения не переживает
    # закрытие портала TestClient между тестами.
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture
def api(engine: Engine, client: TestClient) -> Iterator[_Api]:
    saved_ids: list[int] = []
    usernames: list[str] = []
    bundle = _Api(client, engine, saved_ids, usernames)
    try:
        yield bundle
    finally:
        app.dependency_overrides.pop(get_workplace_order_service, None)
        if saved_ids:
            statement = text(
                "DELETE FROM workplace_order WHERE id IN :ids"
            ).bindparams(bindparam("ids", expanding=True))
            with engine.begin() as connection:
                connection.execute(statement, {"ids": saved_ids})
        for username in usernames:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        'DELETE FROM "user" WHERE username = :username'
                    ),
                    {"username": username},
                )


def test_should_create_an_order_and_return_only_its_id(api: _Api) -> None:
    full = _token(api, "FULL")
    read = _token(api, "READ")
    created = api.client.post(
        "/api/v2/order/",
        headers=full,
        json=_empty_order(creation_date="2020-01-01", economy=1),
    )
    assert created.status_code == 200
    order_id = _remember(api, created)
    loaded = api.client.get(
        f"/api/v2/order/{order_id}", headers=read
    )
    assert loaded.status_code == 200
    body = loaded.json()
    assert set(body) == _ORDER_KEYS
    assert body["id"] == order_id
    assert body["comment"] == ""
    assert body["status"] == "Отложен"
    assert type(body["unit_count"]) is int
    assert body["unit_count"] == 1
    assert type(body["tax_rate"]) is str
    assert type(body["markup"]) is str
    assert Decimal(body["tax_rate"]) == Decimal("1")
    assert Decimal(body["markup"]) == Decimal("0")
    assert body["operations"] == []
    assert body["creation_date"] == date.today().isoformat()
    assert body["printings"] == []
    assert _reports(api, order_id) == []


def test_should_update_the_same_order_without_a_report(api: _Api) -> None:
    headers = _token(api, "FULL")
    created = api.client.post(
        "/api/v2/order/", headers=headers, json=_empty_order()
    )
    order_id = _remember(api, created)
    created_on = api.client.get(
        f"/api/v2/order/{order_id}", headers=headers
    ).json()["creation_date"]
    reports_before = _count_rows(api.engine, "workplace_cost_report")
    updated = api.client.post(
        "/api/v2/order/",
        headers=headers,
        json=_empty_order(
            id=order_id, comment="стало", status="Завершён"
        ),
    )
    assert updated.status_code == 200
    assert updated.json()["id"] == order_id
    loaded = api.client.get(
        f"/api/v2/order/{order_id}", headers=headers
    )
    assert loaded.json()["comment"] == "стало"
    assert loaded.json()["status"] == "Завершён"
    assert loaded.json()["creation_date"] == created_on
    assert _reports(api, order_id) == []
    assert (
        _count_rows(api.engine, "workplace_cost_report") == reports_before
    )


def test_should_refuse_to_save_an_unknown_id(api: _Api) -> None:
    headers = _token(api, "FULL")
    before = _count_rows(api.engine, "workplace_order")
    response = api.client.post(
        "/api/v2/order/",
        headers=headers,
        json=_empty_order(id=_MISSING_ID),
    )
    assert response.status_code == 404
    assert response.json()["detail"] == (
        f"save: заказа нет, id={_MISSING_ID}"
    )
    assert "secret" not in response.json()["detail"]
    assert "localhost" not in response.json()["detail"]
    assert "postgresql" not in response.json()["detail"]
    assert _count_rows(api.engine, "workplace_order") == before


def test_should_round_trip_printings_in_request_order(api: _Api) -> None:
    headers = _token(api, "FULL")
    first = _first_printing()
    second = _second_printing()
    created = api.client.post(
        "/api/v2/order/",
        headers=headers,
        json=_empty_order(printings=[first, second]),
    )
    order_id = _remember(api, created)
    loaded = api.client.get(
        f"/api/v2/order/{order_id}", headers=headers
    )
    printings = loaded.json()["printings"]
    assert len(printings) == 2
    _assert_printing(printings[0], first)
    _assert_printing(printings[1], second)


def test_should_list_created_orders_by_descending_id(api: _Api) -> None:
    full = _token(api, "FULL")
    read = _token(api, "READ")
    first = _remember(
        api,
        api.client.post(
            "/api/v2/order/", headers=full, json=_empty_order()
        ),
    )
    second = _remember(
        api,
        api.client.post(
            "/api/v2/order/", headers=full, json=_empty_order()
        ),
    )
    listed = api.client.get("/api/v2/order/", headers=read)
    assert listed.status_code == 200
    body = listed.json()
    assert type(body) is list
    ids = [item["id"] for item in body]
    assert ids.count(first) == 1
    assert ids.count(second) == 1
    assert ids.index(max(first, second)) < ids.index(min(first, second))
    for item in body:
        assert "cost_report" not in item
        assert _DATE.fullmatch(item["creation_date"])


def test_should_return_an_empty_list_when_the_service_has_no_orders(
    api: _Api,
) -> None:
    headers = _token(api, "READ")
    service = WorkplaceOrderService(_EmptyCatalog(), Administrator())
    app.dependency_overrides[get_workplace_order_service] = lambda: service
    listed = api.client.get("/api/v2/order/", headers=headers)
    assert listed.status_code == 200
    assert listed.json() == []


def test_should_delete_an_order_with_an_empty_body(api: _Api) -> None:
    headers = _token(api, "FULL")
    order_id = _remember(
        api,
        api.client.post(
            "/api/v2/order/", headers=headers, json=_empty_order()
        ),
    )
    deleted = api.client.delete(
        f"/api/v2/order/{order_id}", headers=headers
    )
    assert deleted.status_code == 200
    assert deleted.content == b""
    loaded = api.client.get(
        f"/api/v2/order/{order_id}", headers=headers
    )
    assert loaded.status_code == 404
    assert loaded.json()["detail"] == (
        f"take: заказа нет, id={order_id}"
    )
    with pytest.raises(OrderNotFound):
        _reports(api, order_id)
    api.saved_ids.remove(order_id)


def test_should_refuse_to_delete_an_unknown_id(api: _Api) -> None:
    headers = _token(api, "FULL")
    before = _count_rows(api.engine, "workplace_order")
    deleted = api.client.delete(
        f"/api/v2/order/{_MISSING_ID}", headers=headers
    )
    assert deleted.status_code == 404
    assert deleted.json()["detail"] == (
        f"delete: заказа нет, id={_MISSING_ID}"
    )
    assert _count_rows(api.engine, "workplace_order") == before


def test_should_return_a_cost_report_and_write_nothing(api: _Api) -> None:
    headers = _token(api, "FULL")
    before = _counts(api)
    for payload, report in (
        (_empty_order(), _ZERO_REPORT),
        (_operation_order(), _OPERATION_REPORT),
    ):
        response = api.client.post(
            "/api/v2/order/cost_report", headers=headers, json=payload
        )
        assert response.status_code == 200
        assert response.headers["content-type"].startswith(
            "application/json"
        )
        assert not response.content.startswith(b"%PDF")
        assert response.json() == report
    assert _counts(api) == before


def test_should_answer_500_and_write_nothing_when_calculation_fails(
    api: _Api,
) -> None:
    headers = _token(api, "FULL")
    before = _counts(api)
    response = api.client.post(
        "/api/v2/order/cost_report",
        headers=headers,
        json=_empty_order(unit_count=0),
    )
    assert response.status_code == 500
    assert _internal_error(response) == "Internal Server Error"
    assert _counts(api) == before


@pytest.mark.parametrize(
    ("path", "status_text"),
    [
        ("/api/v2/order/accept", "В работе"),
        ("/api/v2/order/delay", "Отложен"),
    ],
)
def test_should_accept_or_delay_and_append_the_report(
    api: _Api, path: str, status_text: str
) -> None:
    headers = _token(api, "FULL")
    first = api.client.post(
        path,
        headers=headers,
        json=_empty_order(status="Завершён"),
    )
    assert first.status_code == 200
    body = first.json()
    assert set(body) == {"id", "cost_report"}
    assert body["cost_report"] == _ZERO_REPORT
    assert first.headers["content-type"].startswith("application/json")
    assert not first.content.startswith(b"%PDF")
    order_id = body["id"]
    assert type(order_id) is int
    api.saved_ids.append(order_id)
    rows_after_first = _count_rows(api.engine, "workplace_order")
    created_on = api.client.get(
        f"/api/v2/order/{order_id}", headers=headers
    ).json()["creation_date"]
    second = api.client.post(
        path,
        headers=headers,
        json=_operation_order(id=order_id, status="Завершён"),
    )
    assert second.status_code == 200
    assert second.json()["id"] == order_id
    assert second.json()["cost_report"] == _OPERATION_REPORT
    assert _count_rows(api.engine, "workplace_order") == rows_after_first
    loaded = api.client.get(
        f"/api/v2/order/{order_id}", headers=headers
    ).json()
    assert loaded["status"] == status_text
    assert loaded["unit_count"] == 2
    assert loaded["creation_date"] == created_on
    assert len(loaded["operations"]) == 1
    operation = loaded["operations"][0]
    assert operation["name"] == "рез"
    assert type(operation["cost"]) is str
    assert Decimal(operation["cost"]) == Decimal("3")
    assert operation["description"] == "кромка"
    assert _reports(api, order_id) == [_ZERO_COST, _OPERATION_COST]


@pytest.mark.parametrize(
    "path",
    ["/api/v2/order/accept", "/api/v2/order/delay"],
)
def test_should_answer_500_and_write_nothing_when_accept_or_delay_cannot_calculate(
    api: _Api, path: str
) -> None:
    headers = _token(api, "FULL")
    before = _counts(api)
    response = api.client.post(
        path, headers=headers, json=_empty_order(unit_count=0)
    )
    assert response.status_code == 500
    assert _internal_error(response) == "Internal Server Error"
    assert _counts(api) == before


@pytest.mark.parametrize(
    "path",
    ["/api/v2/order/accept", "/api/v2/order/delay"],
)
def test_should_refuse_to_accept_or_delay_an_unknown_id(
    api: _Api, path: str
) -> None:
    headers = _token(api, "FULL")
    before = _counts(api)
    response = api.client.post(
        path, headers=headers, json=_empty_order(id=_MISSING_ID)
    )
    assert response.status_code == 404
    assert response.json()["detail"] == (
        f"save: заказа нет, id={_MISSING_ID}"
    )
    assert _counts(api) == before


def test_should_change_only_the_status(api: _Api) -> None:
    headers = _token(api, "FULL")
    accepted = api.client.post(
        "/api/v2/order/accept",
        headers=headers,
        json=_operation_order(comment="заметка"),
    )
    order_id = accepted.json()["id"]
    api.saved_ids.append(order_id)
    created_on = api.client.get(
        f"/api/v2/order/{order_id}", headers=headers
    ).json()["creation_date"]
    changed = api.client.post(
        "/api/v2/order/status",
        headers=headers,
        json={"order_id": order_id, "new_status": "Завершён"},
    )
    assert changed.status_code == 200
    assert changed.content == b""
    loaded = api.client.get(
        f"/api/v2/order/{order_id}", headers=headers
    ).json()
    assert loaded["status"] == "Завершён"
    assert loaded["comment"] == "заметка"
    assert loaded["unit_count"] == 2
    assert loaded["creation_date"] == created_on
    assert _reports(api, order_id) == [_OPERATION_COST]


def test_should_refuse_an_unknown_status(api: _Api) -> None:
    headers = _token(api, "FULL")
    order_id = _remember(
        api,
        api.client.post(
            "/api/v2/order/", headers=headers, json=_empty_order()
        ),
    )
    before = _count_rows(api.engine, "workplace_order")
    response = api.client.post(
        "/api/v2/order/status",
        headers=headers,
        json={"order_id": order_id, "new_status": "SAVED"},
    )
    assert response.status_code == 422
    loaded = api.client.get(
        f"/api/v2/order/{order_id}", headers=headers
    )
    assert loaded.json()["status"] == "Отложен"
    assert _count_rows(api.engine, "workplace_order") == before
    assert _reports(api, order_id) == []


def test_should_refuse_to_change_status_of_an_unknown_id(api: _Api) -> None:
    headers = _token(api, "FULL")
    before = _count_rows(api.engine, "workplace_order")
    response = api.client.post(
        "/api/v2/order/status",
        headers=headers,
        json={"order_id": _MISSING_ID, "new_status": "Завершён"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == (
        f"take: заказа нет, id={_MISSING_ID}"
    )
    assert _count_rows(api.engine, "workplace_order") == before


def test_should_reject_a_negative_operation_cost(api: _Api) -> None:
    headers = _token(api, "FULL")
    before = _count_rows(api.engine, "workplace_order")
    response = api.client.post(
        "/api/v2/order/",
        headers=headers,
        json=_empty_order(operations=[{
            "name": "",
            "cost": "-1.25",
            "description": "",
        }]),
    )
    assert response.status_code == 500
    assert _internal_error(response) == "Internal Server Error"
    assert _count_rows(api.engine, "workplace_order") == before


def test_should_save_a_zero_operation_cost(api: _Api) -> None:
    headers = _token(api, "FULL")
    order_id = _remember(
        api,
        api.client.post(
            "/api/v2/order/",
            headers=headers,
            json=_empty_order(operations=[{
                "name": "",
                "cost": "0",
                "description": "",
            }]),
        ),
    )
    loaded = api.client.get(
        f"/api/v2/order/{order_id}", headers=headers
    ).json()
    assert len(loaded["operations"]) == 1
    cost = loaded["operations"][0]["cost"]
    assert type(cost) is str
    assert Decimal(cost) == Decimal("0")


def test_should_refuse_a_negative_money_rate(api: _Api) -> None:
    headers = _token(api, "FULL")
    printing = _first_printing()
    printing["press_pricing"] = {
        **printing["press_pricing"],
        "cyan": "-1",
    }
    before = _count_rows(api.engine, "workplace_order")
    response = api.client.post(
        "/api/v2/order/",
        headers=headers,
        json=_empty_order(printings=[printing]),
    )
    assert response.status_code == 500
    assert response.status_code not in (422, 404)
    assert _internal_error(response) == "Internal Server Error"
    assert _count_rows(api.engine, "workplace_order") == before


def test_should_reject_a_status_name(api: _Api) -> None:
    headers = _token(api, "FULL")
    before = _count_rows(api.engine, "workplace_order")
    response = api.client.post(
        "/api/v2/order/",
        headers=headers,
        json=_empty_order(status="SAVED"),
    )
    assert response.status_code == 422
    assert _count_rows(api.engine, "workplace_order") == before


def test_should_reject_a_chroma_number(api: _Api) -> None:
    headers = _token(api, "FULL")
    printing = _first_printing()
    printing["chroma"] = 0
    before = _count_rows(api.engine, "workplace_order")
    response = api.client.post(
        "/api/v2/order/",
        headers=headers,
        json=_empty_order(printings=[printing]),
    )
    assert response.status_code == 422
    assert _count_rows(api.engine, "workplace_order") == before


def test_should_reject_a_decimal_sent_as_a_number(api: _Api) -> None:
    headers = _token(api, "FULL")
    before = _count_rows(api.engine, "workplace_order")
    response = api.client.post(
        "/api/v2/order/",
        headers=headers,
        json=_empty_order(tax_rate=1),
    )
    assert response.status_code == 422
    assert _count_rows(api.engine, "workplace_order") == before


def test_should_reject_an_operation_cost_sent_as_a_number(
    api: _Api,
) -> None:
    headers = _token(api, "FULL")
    before = _count_rows(api.engine, "workplace_order")
    response = api.client.post(
        "/api/v2/order/",
        headers=headers,
        json=_empty_order(operations=[{
            "name": "",
            "cost": 3,
            "description": "",
        }]),
    )
    assert response.status_code == 422
    assert _count_rows(api.engine, "workplace_order") == before


def test_should_match_the_old_list_when_the_token_is_missing(
    api: _Api,
) -> None:
    new = api.client.get("/api/v2/order/")
    old = api.client.get("/api/order/")
    assert new.status_code == old.status_code
    assert new.json()["detail"] == old.json()["detail"]


def test_should_allow_a_read_token_to_list_orders(api: _Api) -> None:
    headers = _token(api, "READ")
    listed = api.client.get("/api/v2/order/", headers=headers)
    assert listed.status_code == 200
    assert type(listed.json()) is list


def test_should_refuse_a_list_without_read_permission(api: _Api) -> None:
    headers = _token(api, "NONE")
    listed = api.client.get("/api/v2/order/", headers=headers)
    assert listed.status_code == 403
    assert listed.json()["detail"] == _READ_DENIED
    reference = api.client.get("/api/v2/reference/", headers=headers)
    assert reference.status_code == 403
    assert reference.json()["detail"] == _READ_DENIED


@pytest.mark.parametrize(
    ("method", "path", "kind"),
    [
        ("post", "/api/v2/order/", "empty"),
        ("delete", f"/api/v2/order/{_MISSING_ID}", "none"),
        ("post", "/api/v2/order/cost_report", "empty"),
        ("post", "/api/v2/order/delay", "empty"),
        ("post", "/api/v2/order/accept", "empty"),
        ("post", "/api/v2/order/status", "status"),
        ("post", "/api/v2/reference/", "empty"),
    ],
)
def test_should_refuse_a_write_without_full_permission(
    api: _Api, method: str, path: str, kind: str
) -> None:
    headers = _token(api, "READ")
    payload: dict[str, object] | None
    if kind == "empty":
        payload = _empty_order()
    elif kind == "status":
        payload = {
            "order_id": _MISSING_ID,
            "new_status": "Отложен",
        }
    else:
        payload = None
    previous = (
        _reference_document(api.engine)
        if path == "/api/v2/reference/"
        else None
    )
    before = _counts(api)
    try:
        response = api.client.request(
            method, path, headers=headers, json=payload
        )
        assert response.status_code == 403
        assert response.json()["detail"] == _FULL_DENIED
        assert _counts(api) == before
    finally:
        if path == "/api/v2/reference/":
            _restore_reference(api.engine, previous)


def test_should_not_save_on_routes_outside_the_contract(api: _Api) -> None:
    headers = _token(api, "FULL")
    before = _count_rows(api.engine, "workplace_order")
    calls = (
        api.client.put("/api/v2/order/1", headers=headers),
        api.client.post(
            "/api/v2/order/1", headers=headers, json=_empty_order()
        ),
        api.client.post(
            "/api/v2/order/bulk",
            headers=headers,
            json=[_empty_order()],
        ),
    )
    for response in calls:
        assert response.status_code not in (200, 201)
    assert _count_rows(api.engine, "workplace_order") == before


def test_should_report_store_unavailable_without_secrets(api: _Api) -> None:
    headers = _token(api, "READ")
    app.dependency_overrides[get_workplace_order_service] = (
        lambda: _UnavailableTake()
    )
    response = api.client.get("/api/v2/order/5", headers=headers)
    assert response.status_code == 503
    assert response.json()["detail"] == (
        "take: нет соединения с базой, id=5"
    )
    assert "secret-token" not in response.text
    assert "127.0.0.1" not in response.text
    assert "postgresql" not in response.text


class _EmptyReference:
    def reference(self) -> None:
        return None


def test_should_return_a_zero_order_when_the_reference_is_missing(
    api: _Api,
) -> None:
    headers = _token(api, "READ")
    service = WorkplaceOrderService(_EmptyReference(), Administrator())
    app.dependency_overrides[get_workplace_order_service] = lambda: service
    response = api.client.get("/api/v2/reference/", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert "creation_date" not in body
    assert set(body) == _ORDER_KEYS - {"creation_date"}
    assert body["id"] is None
    assert body["status"] == "Отложен"
    assert body["operations"] == []
    assert body["comment"] == ""
    assert type(body["unit_count"]) is int
    assert body["unit_count"] == 1
    _assert_money(body["tax_rate"], "0")
    _assert_money(body["markup"], "0")
    printings = body["printings"]
    assert type(printings) is list
    assert len(printings) == 1
    _assert_printing(printings[0], _zero_printing())


def test_should_replace_the_reference_without_adding_an_order(
    api: _Api,
) -> None:
    full = _token(api, "FULL")
    read = _token(api, "READ")
    comment = f"reference-{uuid4().hex}"
    previous = _reference_document(api.engine)
    before = _count_rows(api.engine, "workplace_order")
    try:
        saved = api.client.post(
            "/api/v2/reference/",
            headers=full,
            json=_reference_body("1.5", comment),
        )
        assert saved.status_code == 200
        assert saved.content == b""
        loaded = api.client.get("/api/v2/reference/", headers=read)
        assert loaded.status_code == 200
        body = loaded.json()
        assert body["id"] is None
        assert "creation_date" not in body
        assert body["printings"][0]["press_pricing"]["cyan"] == "1.5"
        assert _count_rows(api.engine, "workplace_order") == before
        missing = api.client.get(
            f"/api/v2/order/{_MISSING_ID}", headers=read
        )
        assert missing.status_code == 404
        replaced = api.client.post(
            "/api/v2/reference/",
            headers=full,
            json=_reference_body("2.5", comment),
        )
        assert replaced.status_code == 200
        assert replaced.content == b""
        again = api.client.get("/api/v2/reference/", headers=read)
        assert again.status_code == 200
        stored = again.json()
        assert stored["id"] is None
        assert "creation_date" not in stored
        assert stored["printings"][0]["press_pricing"]["cyan"] == "2.5"
        listed = api.client.get("/api/v2/order/", headers=read)
        assert listed.status_code == 200
        assert all(
            item["comment"] != comment for item in listed.json()
        )
        assert _count_rows(api.engine, "workplace_order") == before
    finally:
        _restore_reference(api.engine, previous)


@pytest.mark.parametrize(
    "payload",
    [
        _empty_order(operations=[{
            "name": "",
            "cost": "-1",
            "description": "",
        }]),
        _empty_order(printings=[{
            **_second_printing(),
            "press_pricing": {**_zero_rates(), "cyan": "-1"},
        }]),
    ],
)
def test_should_keep_the_reference_when_a_rate_is_negative(
    api: _Api, payload: dict[str, object]
) -> None:
    headers = _token(api, "FULL")
    previous = _reference_document(api.engine)
    try:
        response = api.client.post(
            "/api/v2/reference/",
            headers=headers,
            json=payload,
        )
        assert response.status_code == 500
        assert _reference_document(api.engine) == previous
    finally:
        _restore_reference(api.engine, previous)
