import pandas as pd
import pytest

from create_report import add_excel_table, dataframe_to_table_data

class DummyWorksheet:
    def __init__(self):
        self.add_table_calls = []

    def add_table(self, first_row, first_col, last_row, last_col, options):
        self.add_table_calls.append(
            (first_row, first_col, last_row, last_col, options)
        )


def test_add_excel_table_basic(monkeypatch):
    ws = DummyWorksheet()
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    table_style = "Table Style Light 1"

    last_row, last_col = add_excel_table(ws, df, start_row=0, start_col=0, table_style=table_style)

    assert (last_row, last_col) == (2, 1)

    assert len(ws.add_table_calls) == 1
    first_row, first_col, lr, lc, options = ws.add_table_calls[0]

    assert first_row == 0
    assert first_col == 0
    assert lr == 2
    assert lc == 1

    assert options["style"] == table_style
    assert options["banded_rows"] is True
    assert options["columns"] == [{"header": "A"}, {"header": "B"}]

    assert options["data"] == dataframe_to_table_data(df)


def test_add_excel_table_with_offset():
    ws = DummyWorksheet()
    df = pd.DataFrame({"X": [10], "Y": [20], "Z": [30]})

    last_row, last_col = add_excel_table(ws, df, start_row=5, start_col=3, table_style="MyStyle")

    assert (last_row, last_col) == (6, 5)

    (fr, fc, lr, lc, options), = ws.add_table_calls
    assert fr == 5
    assert fc == 3
    assert lr == 6
    assert lc == 5


def test_add_excel_table_headers_converted_to_strings():
    ws = DummyWorksheet()
    df = pd.DataFrame(
        {
            123: [1, 2],
            ("a", "b"): [3, 4]
        }
    )

    add_excel_table(ws, df, start_row=0, start_col=0, table_style="Style")

    (_, _, _, _, options), = ws.add_table_calls

    assert options["columns"] == [
        {"header": "123"},
        {"header": "('a', 'b')"},
    ]


def test_add_excel_table_return_matches_add_table_coords():
    ws = DummyWorksheet()
    df = pd.DataFrame({"A": [1, 2, 3]})

    last_row, last_col = add_excel_table(ws, df, start_row=2, start_col=4, table_style="Style")

    (fr, fc, lr, lc, _), = ws.add_table_calls

    assert (last_row, last_col) == (lr, lc)
    assert fr == 2
    assert fc == 4


def test_add_excel_table_empty_dataframe():
    ws = DummyWorksheet()
    df = pd.DataFrame(columns=["A", "B"])

    last_row, last_col = add_excel_table(ws, df, start_row=0, start_col=0, table_style="Style")

    assert (last_row, last_col) == (0, 1)

    (fr, fc, lr, lc, options), = ws.add_table_calls

    assert fr == 0
    assert lr == 0
    assert options["columns"] == [{"header": "A"}, {"header": "B"}]

    assert options["data"] == dataframe_to_table_data(df)

    
