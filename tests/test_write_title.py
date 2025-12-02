import pytest

from create_report import write_title

class DummyWorksheet:
    def __init__(self):
        self.calls = []

    def write(self, row, col, text, fmt):
        self.calls.append((row, col, text, fmt))


def test_write_title_calls_worksheet_write_with_correct_arguments():
    """Test function writes title as expected and offsets new_row + 2"""
    ws = DummyWorksheet()
    row, col = 3, 1
    text = "Report Title"
    fmt = "title_format"

    new_row = write_title(ws, row, col, text, fmt)

    assert ws.calls == [(3, 1, "Report Title", "title_format")]
    assert new_row == row + 2


def test_write_title_allows_empty_text():
    """Test function takes empty string as title"""
    ws = DummyWorksheet()

    new_row = write_title(ws, 2, 0, "", "fmt")

    assert ws.calls == [(2, 0, "", "fmt")]
    assert new_row == 4




