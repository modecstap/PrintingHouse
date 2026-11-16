"""Materials catalog routes with fake film and sheet catalogs."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from fastapi.testclient import TestClient

from backend.auth.config import AuthConfig
from backend.auth.passwords import hash_password
from backend.auth.tokens import create_access_token
from backend.new_core.materials.film import Film, FilmID
from backend.new_core.materials.film_density import FilmDensity
from backend.new_core.materials.sheet import SheetID
from backend.new_core.values.money import Money
from backend.server import dependencies
from backend.server.app import create_app
from backend.test.server.conftest import InMemoryUserStore, _DummyDatabase


__all__ = [
    "test_materials_films_require_token",
    "test_create_film_200_returns_assigned_id",
    "test_replace_film_204",
    "test_get_film_404_when_service_raises_key_error",
    "test_delete_film_204",
    "test_paper_types_require_token",
    "test_paper_types_200_returns_list_from_service",
    "test_paper_types_empty_catalog_returns_empty_list",
    "test_paper_densities_require_token",
    "test_paper_densities_200_returns_list_from_service",
    "test_paper_densities_empty_catalog_returns_empty_list",
    "test_film_densities_require_token",
    "test_film_densities_200_returns_list_from_service",
    "test_film_densities_empty_catalog_returns_empty_list",
]

@dataclass
class _FakeFilmCatalog:
    films_rows: tuple[Film, ...] = ()
    film_densities_rows: tuple[int, ...] = ()
    calls: list[str] = field(default_factory=list)
    missing_film_ids: set[int] = field(default_factory=set)
    created_film_id: int = 7
    last_create_film: tuple[str, Money, int] | None = None
    last_replace_film: Film | None = None

    def films(self) -> tuple[Film, ...]:
        self.calls.append("list_films")
        return self.films_rows

    def film(self, film_id: FilmID) -> Film:
        self.calls.append(f"get_film:{film_id.value}")
        if film_id.value in self.missing_film_ids:
            raise KeyError(film_id)
        return self.films_rows[0]

    def create_film(self, name: str, price: Money, density: int) -> FilmID:
        self.calls.append("create_film")
        self.last_create_film = (name, price, density)
        return FilmID(self.created_film_id)

    def replace_film(self, film: Film) -> None:
        self.calls.append(f"replace:{film.id.value}")
        self.last_replace_film = film

    def delete_film(self, film_id: FilmID) -> None:
        if film_id.value in self.missing_film_ids:
            raise KeyError(film_id)
        self.calls.append(f"delete:{film_id.value}")

    def film_densities(self) -> tuple[int, ...]:
        self.calls.append("list_film_densities")
        return self.film_densities_rows


@dataclass
class _FakeSheetCatalog:
    paper_types_rows: tuple[str, ...] = ()
    paper_densities_rows: tuple[int, ...] = ()
    calls: list[str] = field(default_factory=list)

    def sheets(self) -> tuple:
        return ()

    def sheet(self, sheet_id):
        raise KeyError(sheet_id)

    def create_sheet(self, paper, sheet_format):
        return SheetID(1)

    def replace_sheet(self, sheet) -> None:
        pass

    def delete_sheet(self, sheet_id) -> None:
        pass

    def paper_types(self) -> tuple[str, ...]:
        self.calls.append("list_paper_types")
        return self.paper_types_rows

    def paper_densities(self) -> tuple[int, ...]:
        self.calls.append("list_paper_densities")
        return self.paper_densities_rows


_AUTH = AuthConfig("unit-test-secret", "HS256", 60)


def _client_with_fakes(
    film_fake: _FakeFilmCatalog | None = None,
    sheet_fake: _FakeSheetCatalog | None = None,
) -> tuple[TestClient, dict[str, str]]:
    store = InMemoryUserStore({"tester": hash_password("pass")})
    app = create_app(_AUTH, _DummyDatabase())
    app.dependency_overrides[dependencies.get_film_catalog] = lambda: (
        film_fake if film_fake is not None else _FakeFilmCatalog()
    )
    app.dependency_overrides[dependencies.get_sheet_catalog] = lambda: (
        sheet_fake if sheet_fake is not None else _FakeSheetCatalog()
    )
    app.dependency_overrides[dependencies.get_user_store] = lambda: store
    app.dependency_overrides[dependencies.get_auth_config] = lambda: _AUTH
    token = create_access_token("tester", _AUTH)
    headers = {"Authorization": f"Bearer {token}"}
    return TestClient(app), headers


def test_materials_films_require_token():
    client, _ = _client_with_fakes()
    assert client.get("/api/materials/films").status_code == 401


def test_create_film_200_returns_assigned_id():
    fake = _FakeFilmCatalog(created_film_id=11)
    client, headers = _client_with_fakes(film_fake=fake)
    body = {"name": "matte", "price": "3.50", "density": 80}
    response = client.post("/api/materials/films", headers=headers, json=body)
    assert response.status_code == 200
    assert response.json() == {"id": 11}
    assert fake.calls == ["create_film"]
    assert fake.last_create_film == ("matte", Money(Decimal("3.50")), 80)
    assert "id" not in body


def test_replace_film_204():
    fake = _FakeFilmCatalog()
    client, headers = _client_with_fakes(film_fake=fake)
    response = client.put(
        "/api/materials/films/5",
        headers=headers,
        json={"name": "gloss", "price": "1", "density": 90},
    )
    assert response.status_code == 204
    assert fake.calls == ["replace:5"]
    assert fake.last_replace_film == Film(
        id=FilmID(5),
        name="gloss",
        price=Money(Decimal("1")),
        density=FilmDensity(90),
    )


def test_get_film_404_when_service_raises_key_error():
    fake = _FakeFilmCatalog(
        films_rows=(
            Film(
                id=FilmID(1),
                name="x",
                price=Money(Decimal("1")),
                density=FilmDensity(1),
            ),
        ),
        missing_film_ids={9},
    )
    client, headers = _client_with_fakes(film_fake=fake)
    assert client.get(
        "/api/materials/films/9",
        headers=headers).status_code == 404


def test_delete_film_204():
    fake = _FakeFilmCatalog()
    client, headers = _client_with_fakes(film_fake=fake)
    response = client.delete("/api/materials/films/3", headers=headers)
    assert response.status_code == 204
    assert fake.calls == ["delete:3"]


def test_paper_types_require_token():
    client, _ = _client_with_fakes()
    assert client.get("/api/materials/paper-types").status_code == 401


def test_paper_types_200_returns_list_from_service():
    fake = _FakeSheetCatalog(paper_types_rows=("a", "b"))
    client, headers = _client_with_fakes(sheet_fake=fake)
    response = client.get("/api/materials/paper-types", headers=headers)
    assert response.status_code == 200
    assert response.json() == ["a", "b"]
    assert fake.calls == ["list_paper_types"]


def test_paper_types_empty_catalog_returns_empty_list():
    fake = _FakeSheetCatalog(paper_types_rows=())
    client, headers = _client_with_fakes(sheet_fake=fake)
    response = client.get("/api/materials/paper-types", headers=headers)
    assert response.status_code == 200
    assert response.json() == []
    assert fake.calls == ["list_paper_types"]


def test_paper_densities_require_token():
    client, _ = _client_with_fakes()
    assert client.get("/api/materials/paper-densities").status_code == 401


def test_paper_densities_200_returns_list_from_service():
    fake = _FakeSheetCatalog(paper_densities_rows=(80, 100))
    client, headers = _client_with_fakes(sheet_fake=fake)
    response = client.get("/api/materials/paper-densities", headers=headers)
    assert response.status_code == 200
    assert response.json() == [80, 100]
    assert fake.calls == ["list_paper_densities"]


def test_paper_densities_empty_catalog_returns_empty_list():
    fake = _FakeSheetCatalog(paper_densities_rows=())
    client, headers = _client_with_fakes(sheet_fake=fake)
    response = client.get("/api/materials/paper-densities", headers=headers)
    assert response.status_code == 200
    assert response.json() == []
    assert fake.calls == ["list_paper_densities"]


def test_film_densities_require_token():
    client, _ = _client_with_fakes()
    assert client.get("/api/materials/film-densities").status_code == 401


def test_film_densities_200_returns_list_from_service():
    fake = _FakeFilmCatalog(film_densities_rows=(50, 120))
    client, headers = _client_with_fakes(film_fake=fake)
    response = client.get("/api/materials/film-densities", headers=headers)
    assert response.status_code == 200
    assert response.json() == [50, 120]
    assert fake.calls == ["list_film_densities"]


def test_film_densities_empty_catalog_returns_empty_list():
    fake = _FakeFilmCatalog(film_densities_rows=())
    client, headers = _client_with_fakes(film_fake=fake)
    response = client.get("/api/materials/film-densities", headers=headers)
    assert response.status_code == 200
    assert response.json() == []
    assert fake.calls == ["list_film_densities"]
