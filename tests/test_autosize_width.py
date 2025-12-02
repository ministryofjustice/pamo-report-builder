import pandas as pd
import numpy as np

from create_report import autosize_width


def test_autosize_width_uses_longest_value():
    """Test autosize_width deduces longest value"""
    s = pd.Series(["short", "much_longer_value"], name="col")
    # longest value = len("much_longer_value") = 17
    # +2 padding = 19, within default [10, 40]
    width = autosize_width(s)

    assert width == 19


def test_autosize_width_header_longer_than_values():
    """Test autosize_width takes longest value between header and value"""
    s = pd.Series(["a", "bb"], name="very_long_column_name")
    # header len: len("very_long_column_name") = 21
    # values max: len("bb") = 2
    # max_len = 21, +2 = 23
    width = autosize_width(s)

    assert width == 23

    
def test_autosize_width_none_header_treated_as_empty_string():
    """Test autosize_width takes no header as empty string and sets default min"""
    s = pd.Series(["abc", "defgh"], name=None)
    
    width = autosize_width(s)

    assert width == 10

    
def test_autosize_width_respects_min_width():
    """Test autosize_width takes min width input"""
    s = pd.Series(["x"], name="y")
    width = autosize_width(s, min_w=12)

    assert width == 12

    
def test_autosize_width_respects_max_width():
    """Test autosize_width takes max width input"""
    s = pd.Series(["x" * 100], name="wide")

    width = autosize_width(s, max_w=40)

    assert width == 40


def test_autosize_width_ignores_nan_values():
    """Test autosize_width skips nan values"""
    s = pd.Series([np.nan, None, "abc", "defghij"], name="col")

    width = autosize_width(s)

    assert width == 10
    

def test_autosize_width_only_samples_first_200():
    """Test autosize_width ignores data >200 rows"""
    # first 200 values are short
    data = ["short"] * 200
    data.append("x" * 100)

    s = pd.Series(data, name="col")

    width = autosize_width(s)

    assert width == 10


def test_autosize_width_empty_series():
    """Test autosize_width takes empty series"""
    s = pd.Series([], dtype=object, name="empty_col")

    width = autosize_width(s)

    assert width == 11
