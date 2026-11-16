"""Shared insert and update helpers for operator SQL rows."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

IdT = TypeVar("IdT")


def save_operator_row(
    session: Session,
    row: object,
    operator_id: IdT,
    occupied: Callable[[str, IdT], BaseException],
) -> None:
    """Inserts an operator row or maps id conflicts to occupied errors.

    :param session:
    :param row: mapped row to insert.
    :param operator_id: id passed to ``occupied`` on conflict.
    :param occupied: builds the domain occupied error.

    :return: nothing.
    """
    try:
        session.add(row)
        session.flush()
    except IntegrityError as exc:
        raise occupied("save", operator_id) from exc


def replace_operator_row(
    session: Session,
    row: object | None,
    operator: object,
) -> None:
    """Updates name and salary on an existing operator row.

    :param session:
    :param row: mapped row or ``None`` when missing.
    :param operator: domain operator with ``id``, ``name``, and
        ``salary_by_operation``.

    :raises KeyError: when ``row`` is ``None``.

    :return: nothing.
    """
    if row is None:
        raise KeyError(operator.id)
    row.name = operator.name
    row.salary_by_operation = operator.salary_by_operation.amount
    session.flush()
