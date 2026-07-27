import re
import pandas as pd
import pytest

import create_report
from create_report import set_column_formats_and_widths

class DummyWorksheet:
    def __init__(self):
        self.set_column_calls = []
        self.write_calls = []

    def set_column(self, first_col, last_col, width):
        self.set_column_calls.append((first_col, last_col, width))

    def write(self, row, col, value, fmt):
        self.write_calls.append((row, col, value, fmt))

class DummyWorkbook:
    pass


def test_set_column_formats_uses_matchers_and_caches_formats(monkeypatch):
    """Test function returns expected formats from dummy config and df"""
    ws = DummyWorksheet()
    wb = DummyWorkbook()
    df = pd.DataFrame({
        "amount": [10, 20],
        "date":   ["2024-01-01", "2024-01-02"],
    })

    cfg_formats = {
        "default": {"num_format": "", "width": 14},
        "named": {
            "money": {"num_format": "£#,##0"},
            "date": {"num_format": "yyyy-mm-dd"},
        },
        "matchers": {
            r"amount": "money",
            r"date": "date",
        },
    }
    table_cfg = {}

    # Fake format objects to track
    money_fmt = object()
    date_fmt = object()
    default_fmt = object()

    # Track calls to build_format
    build_calls = []

    def fake_build_format(workbook, spec):
        build_calls.append(spec)
        if spec == cfg_formats["named"]["money"]:
            return money_fmt
        if spec == cfg_formats["named"]["date"]:
            return date_fmt
        return default_fmt

    monkeypatch.setattr(create_report, "build_format", fake_build_format)

    set_column_formats_and_widths(ws, df, start_row=0, start_col=0,
                                  workbook=wb, cfg_formats=cfg_formats, table_cfg=table_cfg)

    print("\nBUILD CALLS:")
    print(build_calls)
    print("\nWRITE CALLS:")
    print(ws.write_calls)
    print("\nOBJECTS:")
    print("money_fmt =", money_fmt)
    print("date_fmt =", date_fmt)
    print("default_fmt =", default_fmt)

    assert cfg_formats["named"]["money"] in build_calls
    assert cfg_formats["named"]["date"] in build_calls
    assert build_calls.count(cfg_formats["named"]["money"]) == 1
    assert build_calls.count(cfg_formats["named"]["date"]) == 1

    assert (1, 0, 10, money_fmt) in ws.write_calls
    assert (2, 0, 20, money_fmt) in ws.write_calls
    assert (1, 1, "2024-01-01", date_fmt) in ws.write_calls
    assert (2, 1, "2024-01-02", date_fmt) in ws.write_calls

    
def test_set_column_formats_width_precedence(monkeypatch):
    """Test function honours set widths in cfgs"""
    ws = DummyWorksheet()
    wb = DummyWorkbook()
    df = pd.DataFrame({
        "amount": [10, 20],
        "notes":  ["a", "b"],
    })

    cfg_formats = {
        "default": {"num_format": "", "width": 14},
        "named": {
            "money": {"num_format": "#,##0", "width": 20},
            "text":  {"num_format": "@"},
        },
        "matchers": {
            r"amount": "money",
            r"notes": "text",
        },
    }

    table_cfg = {
        "column_widths": {
            "notes": 30,
        }
    }


    monkeypatch.setattr(create_report, "build_format", lambda workbook, spec: object())

    set_column_formats_and_widths(ws, df, start_row=0, start_col=0,
                                  workbook=wb, cfg_formats=cfg_formats, table_cfg=table_cfg)

    # Column 0: 'amount' -> fmt_name 'money' -> named['money']['width'] = 20
    # Column 1: 'notes' -> override width 30
    assert ws.set_column_calls == [
        (0, 0, 20),  # amount
        (1, 1, 30),  # notes
    ]
    
    
def test_set_column_formats_uses_default_width_when_named_has_no_width(monkeypatch):
    """Test function sets default width when no width key given"""
    ws = DummyWorksheet()
    wb = DummyWorkbook()
    df = pd.DataFrame({"col": [1, 2, 3]})

    cfg_formats = {
        "default": {"num_format": "", "width": 15},
        "named": {
            "myfmt": {"num_format": "#,##0"},
        },
        "matchers": {
            r"col": "myfmt",
        },
    }
    table_cfg = {}

    monkeypatch.setattr(create_report, "build_format", lambda workbook, spec: object())

    set_column_formats_and_widths(ws, df, start_row=0, start_col=0,
                                  workbook=wb, cfg_formats=cfg_formats, table_cfg=table_cfg)

    # Named fmt has no width key -> default_spec["width"] = 15
    assert ws.set_column_calls == [(0, 0, 15)]


def test_set_column_formats_uses_default_format_when_no_match(monkeypatch):
    """Test function sets default format if no match in df to cfg"""
    ws = DummyWorksheet()
    wb = DummyWorkbook()
    df = pd.DataFrame({"other": [1, 2]})

    cfg_formats = {
        "default": {"num_format": "0", "width": 12},
        "named": {},
        "matchers": {},
    }
    table_cfg = {}

    default_fmt = object()
    build_calls = []

    def fake_build_format(workbook, spec):
        build_calls.append(spec)
        return default_fmt

    monkeypatch.setattr(create_report, "build_format", fake_build_format)

    set_column_formats_and_widths(ws, df, start_row=0, start_col=0,
                                  workbook=wb, cfg_formats=cfg_formats, table_cfg=table_cfg)

    assert build_calls == [cfg_formats["default"]]

    # Should all use default_fmt
    assert all(call[3] is default_fmt for call in ws.write_calls)


def test_set_column_formats_writes_all_cells_with_correct_offsets(monkeypatch):
    """Test function honours start_row and start_col inputs"""
    ws = DummyWorksheet()
    wb = DummyWorkbook()
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})

    cfg_formats = {
        "default": {"num_format": "", "width": 10},
        "named": {},
        "matchers": {},
    }
    table_cfg = {}

    default_fmt = object()
    monkeypatch.setattr(create_report, "build_format", lambda wb, spec: default_fmt)

    set_column_formats_and_widths(ws, df, start_row=5, start_col=2,
                                  workbook=wb, cfg_formats=cfg_formats, table_cfg=table_cfg)

    expected_calls = [
        (6, 2, 1, default_fmt),
        (6, 3, 3, default_fmt),
        (7, 2, 2, default_fmt),
        (7, 3, 4, default_fmt),
    ]
    assert ws.write_calls == expected_calls
