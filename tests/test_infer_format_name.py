import re
import pytest
from create_report import infer_format_name 


def test_infer_format_name_matches_pattern():
    """Test function returns expected value from pattern"""
    matchers = [
        (re.compile(r"date"), "date_fmt"),
        (re.compile(r"amount"), "amount_fmt"),
    ]

    result = infer_format_name("start_date", matchers, default_name=None)

    assert result == "date_fmt"

    
def test_infer_format_name_first_match_wins():
    """Test function returns first match only"""
    matchers = [
        (re.compile(r".*"), "catch_all"),
        (re.compile(r"date"), "date_fmt"),
    ]

    result = infer_format_name("start_date", matchers, default_name=None)

    assert result == "catch_all"

    
def test_infer_format_name_no_match_returns_default():
    """Test function returns given default if no match"""
    matchers = [
        (re.compile(r"date"), "date_fmt"),
        (re.compile(r"amount"), "amount_fmt"),
    ]

    result = infer_format_name("username", matchers, default_name="text_fmt")

    assert result == "text_fmt"

    
def test_infer_format_name_no_match_and_default_none():
    """Test function returns None when no match and no default"""
    matchers = [
        (re.compile(r"date"), "date_fmt"),
    ]

    result = infer_format_name("count", matchers, default_name=None)

    assert result is None

    
