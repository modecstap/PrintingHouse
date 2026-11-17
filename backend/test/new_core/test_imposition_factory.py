"""ImpositionFactory assembles impositions from fields or printer spacing."""

from backend.new_core import Imposition
from backend.new_core.edges import Edges, EdgesID
from backend.test.new_core.test_print_run import build_worked_run


__all__ = [
    "test_create_keeps_passed_spacing_and_press_sheet",
]

def test_create_keeps_passed_spacing_and_press_sheet():
    """Direct Imposition build keeps spacing and press_sheet."""
    run, _, _, _, _ = build_worked_run()
    imp = run.block.imposition

    built = Imposition(
        target=imp.target,
        press_sheet=imp.press_sheet,
        edges=Edges(id=EdgesID(0), name="", bleeds=imp.bleeds, spacing=17),
    )

    assert built.spacing == 17
    assert built.press_sheet is imp.press_sheet
    assert built.count() == Imposition(
        target=imp.target,
        press_sheet=imp.press_sheet,
        edges=Edges(id=EdgesID(0), name="", bleeds=imp.bleeds, spacing=17),
    ).count()
