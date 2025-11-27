import pytest

from create_report import build_format


class DummyWorkbook:
    def __init__(self):
        self.last_fmt_args = None
        self.return_value = object() 

    def add_format(self, fmt_args):
        self.last_fmt_args = fmt_args
        return self.return_value

def test_build_format_with_num_format():
    wb = DummyWorkbook()
    spec = {"num_format": "£#,##0"}

    result = build_format(wb, spec)

    assert wb.last_fmt_args == {"num_format": "£#,##0"}
    assert result is wb.return_value

    
def test_build_format_without_format():
    wb = DummyWorkbook()
    spec = {}

    result = build_format(wb, spec)

    assert wb.last_fmt_args is None


def test_build_format_num_format_none_treated_as_absent():
    wb = DummyWorkbook()
    spec = {"num_format": None}

    result = build_format(wb, spec)

    assert wb.last_fmt_args == None


def test_build_format_ignores_unknown_keys():
    wb = DummyWorkbook()
    spec = {
        "num_format": "0.00",
        "bold": True,
        "align": "center", 
    }

    result = build_format(wb, spec)

    assert wb.last_fmt_args == {"num_format": "0.00"}
    assert result is wb.return_value

    