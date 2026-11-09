"""``new_core`` must not import ``backend.storage``."""

from pathlib import Path


def test_new_core_modules_do_not_import_storage():
    """Domain package stays free of persistence imports."""
    root = Path(__file__).resolve().parents[2] / "new_core"
    offenders: list[str] = []
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "backend.storage" in text or "from storage" in text:
            offenders.append(str(path.relative_to(root.parent)))
    assert offenders == []
