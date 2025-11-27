import pandas as pd
import pytest

import create_report
from create_report import build_from_toml


def test_build_from_toml_no_sheets(monkeypatch, tmp_path):
    """Calls correct toml and returns correct output path"""

    cfg = {
        "workbook": {"output": str(tmp_path / "out.xlsx")},
        "defaults": {},
        "formats": {},
        "sheets": [],
    }

    load_toml_calls = []
    monkeypatch.setattr(
        create_report,
        "load_toml",
        lambda path: load_toml_calls.append(path) or cfg,
    )

    writer_calls = []

    class DummyWriter:
        def __init__(self, path, engine=None):
            writer_calls.append((path, engine))

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        @property
        def book(self):
            class DummyBook:
                def add_format(self, spec):
                    return spec

                def add_worksheet(self, name):
                    class DummySheet:
                        pass
                    return DummySheet()
            return DummyBook()

        @property
        def sheets(self):
            return {}

    monkeypatch.setattr(pd, "ExcelWriter", DummyWriter)

    monkeypatch.setattr(
        create_report,
        "load_dataframe",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("load_dataframe should not be called")),
    )
    monkeypatch.setattr(
        create_report,
        "load_image",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("load_image should not be called")),
    )

    build_from_toml("report_config.toml")

    assert load_toml_calls == ["report_config.toml"]
    assert writer_calls == [(str(tmp_path / "out.xlsx"), "xlsxwriter")]


def test_build_from_toml_single_chart(monkeypatch, tmp_path):
    """Single chart calls load_image with correct dotted and insert_image called"""
    
    cfg = {
        "workbook": {"output": str(tmp_path / "out.xlsx")},
        "defaults": {"spacing_rows": 1},
        "formats": {},
        "sheets": [
            {
                "name": "Summary",
                "charts": [
                    {
                        "title": "Chart 1",
                        "start_cell": "K5",
                        "source": [
                            {"type": "function", "dotted": "builders.make_chart"}
                        ],
                        "chart_notes_start_cell": "K25",
                        "chart_notes": ["Notes:", "Line 1"],
                    }
                ],
            }
        ],
    }

    monkeypatch.setattr(create_report, "load_toml", lambda path: cfg)

    class DummyWorksheet:
        def __init__(self, name):
            self.name = name
            self.insert_images = []
            self.writes = []

        def set_header(self, *a, **k): pass
        def set_footer(self, *a, **k): pass
        def write(self, row, col, value, fmt=None):
            self.writes.append((row, col, value, fmt))
        def write_blank(self, *a, **k): pass
        def set_row(self, *a, **k): pass
        def set_column(self, *a, **k): pass

        def insert_image(self, cell, filename, options):
            self.insert_images.append((cell, filename, options))

    class DummyWorkbook:
        def __init__(self):
            self.worksheets = []

        def add_format(self, spec):
            return spec

        def add_worksheet(self, name):
            ws = DummyWorksheet(name)
            self.worksheets.append(ws)
            return ws

    class DummyWriter:
        def __init__(self, path, engine=None):
            self.path = path
            self.engine = engine
            self.book = DummyWorkbook()
            self._sheets = {}

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        @property
        def sheets(self):
            return self._sheets

    monkeypatch.setattr(pd, "ExcelWriter", DummyWriter)

    img_calls = []

    def fake_load_image(source, base_dir, func_registry):
        img_calls.append(source["dotted"])
        return b"fake-img"

    monkeypatch.setattr(create_report, "load_image", fake_load_image)

    monkeypatch.setattr(create_report, "load_dataframe", lambda *a, **k: pd.DataFrame())
    monkeypatch.setattr(create_report, "add_excel_table", lambda *a, **k: (0, 0))
    monkeypatch.setattr(create_report, "set_column_formats_and_widths", lambda *a, **k: None)

    monkeypatch.setattr(create_report, "xl_cell_to_rowcol",
                        lambda cell: (4, 10) if cell == "K5" else (24, 10))
    monkeypatch.setattr(create_report, "xl_rowcol_to_cell",
                        lambda r, c: f"R{r}C{c}")

    build_from_toml("report_config.toml")

    assert img_calls == ["builders.make_chart"]
