"""The chroma and the press-sheet paper of one print."""

from dataclasses import dataclass

from backend.core.accountant.money import Money
from backend.core.workplaces.printing.models import Chroma
from backend.new_core.sheet import Sheet


@dataclass(frozen=True, slots=True)
class PrintSpecification:
    """
    Value Object. The chroma and the press-sheet paper of one print.
    """

    chroma: Chroma
    paper: Sheet

    def paper_price(self) -> Money:
        """Returns the price of the press sheet paper.

        :return: the price of one sheet of this paper.
        """
        return self.paper.price()
