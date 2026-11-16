"""ImpositionFactory assembles impositions from fields or printer spacing."""

from dataclasses import replace

from backend.new_core import Imposition
from backend.new_core.equipment.printer import PrinterID
from backend.new_core.print_run.imposition_factory import (
    CatalogImposition,
    ImpositionFactory,
)
from backend.test.new_core.in_memory_repositories import (
    InMemoryPrinterRepository,
    InMemorySheetRepository,
)
from backend.test.new_core.test_print_run import build_worked_run


def test_create_keeps_passed_spacing_and_press_sheet():
    """Direct Imposition build keeps spacing and press_sheet."""
    run, _, _, _, ctx = build_worked_run()
    imp = run.block.imposition

    built = Imposition(
        target=imp.target,
        press_sheet=imp.press_sheet,
        bleeds=imp.bleeds,
        spacing=17,
    )

    assert built.spacing == 17
    assert built.press_sheet is imp.press_sheet
    assert built.count() == Imposition(
        target=imp.target,
        press_sheet=imp.press_sheet,
        bleeds=imp.bleeds,
        spacing=17,
    ).count()


def test_create_for_printer_takes_spacing_from_catalog():
    """create_for_printer hydrates the sheet and uses printer spacing."""
    run, printing, _, _, ctx = build_worked_run()
    printer_id = printing.printer_id
    printer = ctx.printers[printer_id]
    ctx.printers[printer_id] = replace(printer, spacing=9)
    imp = run.block.imposition
    factory = ImpositionFactory(
        InMemorySheetRepository(items=dict(ctx.sheets)),
        InMemoryPrinterRepository(items=dict(ctx.printers)),
    )

    built = factory.create_for_printer(
        CatalogImposition(
            target=imp.target,
            sheet_id=imp.press_sheet.id,
            bleeds=imp.bleeds,
            printer_id=PrinterID(printer_id.value),
        ),
    )

    assert built.spacing == 9
    assert built.press_sheet == ctx.sheets[imp.press_sheet.id]
    assert built.press_sheet.id == imp.press_sheet.id
