from collections.abc import Callable
from typing import TypeVar

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response

from backend.core.sheet.repository import (
    SheetInUse,
    SheetNotFound,
    SheetSizeRejected,
    SheetStoreUnavailable,
    SheetVersionConflict,
)
from backend.core.sheet.service import SheetService
from backend.server.dependencies import (
    get_current_user_with_full_permission,
    get_current_user_with_read_permission,
)
from backend.server.models.sheet_body import (
    SheetBody,
    SheetSavedBody,
    body_from_sheet,
    command_from_body,
)

_T = TypeVar("_T")

router = APIRouter(prefix="/api/v2/sheet", tags=["core-sheet"])
_service: SheetService | None = None


def bind_sheet_service(service: SheetService) -> None:
    """Remembers the sheet service for the routes.

    :param service:
    """
    global _service
    _service = service


def get_sheet_service() -> SheetService:
    """Returns the service that application startup remembered.

    :raises RuntimeError:
    "сервис листа не собран" if bind has not been called yet.

    :return: the SheetService of this process.
    """
    if _service is None:
        raise RuntimeError("сервис листа не собран")
    return _service


def _call(action: Callable[[], _T]) -> _T:
    try:
        return action()
    except SheetNotFound as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except SheetStoreUnavailable as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except (SheetVersionConflict, SheetInUse) as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except SheetSizeRejected as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get(
    "/",
    dependencies=[Depends(get_current_user_with_read_permission)],
)
def list_sheets(
    service: SheetService = Depends(get_sheet_service),
) -> list[SheetBody]:
    """Returns every sheet through take_all.

    :param service:

    :raises HTTPException: status 503 if there is no connection to the database.

    :return: HTTP 200 and a JSON array of sheets. An empty catalog gives [].
    version is not in the JSON.
    """
    return _call(
        lambda: [body_from_sheet(sheet) for sheet in service.take_all()]
    )


@router.post(
    "/",
    dependencies=[Depends(get_current_user_with_full_permission)],
)
def save_sheet(
    body: SheetBody,
    service: SheetService = Depends(get_sheet_service),
) -> SheetSavedBody:
    """Saves a sheet through save.

    :param body: name is read and discarded.
    :param service:

    :raises HTTPException: status 404 if the given id does not exist.
    :raises HTTPException: status 409 if the stored version differs.
    The row is left unchanged.
    :raises HTTPException: status 422 if the body is not accepted
    or the height and width are not a factory format.
    :raises HTTPException: status 500 if the paper rate is negative.
    :raises HTTPException: status 503 if there is no connection to the database.

    :return: HTTP 200 and JSON with a single key id.
    """
    saved_id = _call(lambda: service.save(command_from_body(body)))
    return SheetSavedBody(id=saved_id)


@router.delete(
    "/{id}",
    response_model=None,
    dependencies=[Depends(get_current_user_with_full_permission)],
)
def delete_sheet(
    id: int,
    service: SheetService = Depends(get_sheet_service),
) -> Response:
    """Deletes the sheet through delete.

    :param id:
    :param service:

    :raises HTTPException: status 404 if the sheet does not exist.
    :raises HTTPException: status 409 if an order or the reference
    still points at this sheet. The row and those references stay.
    :raises HTTPException: status 422 if the path id is not an integer.
    :raises HTTPException: status 503 if there is no connection to the database.

    :return: HTTP 200 with no body.
    """
    _call(lambda: service.delete(id))
    return Response(status_code=200)
