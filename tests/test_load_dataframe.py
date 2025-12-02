import os
from pathlib import Path

import pandas as pd
import pytest

from create_report import load_dataframe


def test_load_dataframe_csv_relative_path(tmp_path, monkeypatch):
    """Load df from csv via relative path"""
    base_dir = tmp_path
    csv_path = base_dir / "data" / "test.csv"
    csv_path.parent.mkdir()
    df_in = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    df_in.to_csv(csv_path, index=False)

    source = {
        "type": "csv",
        "path": "data/test.csv",
    }

    result = load_dataframe(source, base_dir=base_dir)

    assert isinstance(result, pd.DataFrame)
    pd.testing.assert_frame_equal(result, df_in)
    

def test_load_dataframe_csv_absolute_path(tmp_path):
    """Load df from csv via absolute path"""
    csv_path = tmp_path / "abs.csv"
    df_in = pd.DataFrame({"x": [10]})
    df_in.to_csv(csv_path, index=False)

    source = {
        "type": "csv",
        "path": str(csv_path),
    }

    result = load_dataframe(source, base_dir=Path("/some/other/path"))
    pd.testing.assert_frame_equal(result, df_in)

def test_load_dataframe_excel_with_sheet(tmp_path):
    """Load df from sheet in .xlsx"""
    xlsx_path = tmp_path / "book.xlsx"
    df_sheet1 = pd.DataFrame({"a": [1]})
    df_sheet2 = pd.DataFrame({"b": [2]})

    with pd.ExcelWriter(xlsx_path) as writer:
        df_sheet1.to_excel(writer, sheet_name="Sheet1", index=False)
        df_sheet2.to_excel(writer, sheet_name="Data", index=False)

    source = {
        "type": "excel",
        "path": str(xlsx_path),
        "sheet": "Data",
    }

    result = load_dataframe(source)
    pd.testing.assert_frame_equal(result, df_sheet2)
    

def test_load_dataframe_function_registry_returns_df():
    """Load df from function in func_registry"""
    def dummy_df(x):
        return pd.DataFrame({"x": [x]})

    source = {
        "type": "function",
        "registry": "make_df",
        "kwargs": {"x": 5},
    }
    registry = {"make_df": dummy_df}

    result = load_dataframe(source, func_registry=registry)

    expected = pd.DataFrame({"x": [5]})
    pd.testing.assert_frame_equal(result, expected)

    
def test_load_dataframe_function_registry_missing_key():
    """Errors when function registry key is missing"""
    source = {
        "type": "function",
        "registry": "missing",
        "kwargs": {},
    }
    registry = {}

    with pytest.raises(ValueError) as excinfo:
        load_dataframe(source, func_registry=registry)

    assert "Function source requi" in str(excinfo.value)
    

def test_load_dataframe_function_returns_dict_with_key():
    """Load df via key in dict in function"""
    def make_dict():
        return {
            "train": pd.DataFrame({"id": [1, 2]}),
            "test": pd.DataFrame({"id": [3]}),
        }

    source = {
        "type": "function",
        "registry": "make_dict",
        "key": "test",
    }
    registry = {"make_dict": make_dict}

    result = load_dataframe(source, func_registry=registry)

    expected = pd.DataFrame({"id": [3]})
    pd.testing.assert_frame_equal(result, expected)

    
def test_load_dataframe_function_dict_value_not_df():
    """Errors when loading non-df from function dict key"""
    def make_dict():
        return {"wrong": [1, 2, 3]}

    source = {
        "type": "function",
        "registry": "make_dict",
        "key": "wrong",
    }
    registry = {"make_dict": make_dict}

    with pytest.raises(TypeError) as excinfo:
        load_dataframe(source, func_registry=registry)

    assert "is not a DataFrame" in str(excinfo.value)
    
    
def test_load_dataframe_function_returns_invalid_type():
    """Errors when non-df returned"""
    def bad_func():
        return [1, 2, 3]

    source = {
        "type": "function",
        "registry": "bad",
    }
    registry = {"bad": bad_func}

    with pytest.raises(TypeError) as excinfo:
        load_dataframe(source, func_registry=registry)

    assert "did not return a pandas DataFrame" in str(excinfo.value)


def test_load_dataframe_unsupported_type():
    """Errors when unsupported type passed"""
    source = {
        "type": "json",
        "path": "data.json",
    }

    with pytest.raises(ValueError) as excinfo:
        load_dataframe(source)

    assert "Unsupported source.type='json'" in str(excinfo.value)
