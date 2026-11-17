"""ChromaCatalog application service."""

from backend.new_core.application_services.chroma.catalog import ChromaCatalog
from backend.new_core.chroma import Chroma, ChromaID
from backend.new_core.values.percent import Percent
from backend.test.new_core.test_print_run import chroma_four_zero


class _FakeChromaRepository:
    def __init__(self, rows: tuple[Chroma, ...]) -> None:
        self._rows = rows

    def take_all(self) -> tuple[Chroma, ...]:
        return self._rows

    def take(self, chroma_id: ChromaID) -> Chroma:
        for row in self._rows:
            if row.id == chroma_id:
                return row
        raise KeyError(chroma_id)

    def add(
        self,
        name: str,
        cyan: int,
        magenta: int,
        yellow: int,
        black: int,
    ) -> ChromaID:
        raise NotImplementedError

    def replace(self, chroma: Chroma) -> None:
        raise NotImplementedError

    def delete(self, chroma_id: ChromaID) -> None:
        raise NotImplementedError

    def find_or_add(
        self,
        name: str,
        cyan: int,
        magenta: int,
        yellow: int,
        black: int,
    ) -> ChromaID:
        raise NotImplementedError


def test_chroma_rows_omits_rows_with_empty_name():
    named = chroma_four_zero()
    unnamed = Chroma(
        id=ChromaID(99),
        name="",
        cyan=Percent(0),
        magenta=Percent(0),
        yellow=Percent(0),
        black=Percent(0),
    )
    catalog = ChromaCatalog(_FakeChromaRepository((unnamed, named)))

    rows = tuple(catalog.chroma_rows())

    assert rows == (named,)