import os
from pathlib import Path

import pandas as pd
import pytest

from create_report import load_dataframe


def test_load_dataframe_csv():
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    filename = "test.csv"
    data_sources = {}
    data_sources[filename] = df
    source = {"type": "csv", "data_source": str(filename)}
    
    result = load_dataframe(data_sources,source)
    pd.testing.assert_frame_equal(df, result)


def test_load_dataframe_excel():
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    filename = "temp_test.xlsx"
    data_sources = {}
    data_sources[filename] = df
    source = {"type": "excel", "data_source": str(filename)}
    
    result = load_dataframe(data_sources,source)
    pd.testing.assert_frame_equal(df, result)


def test_load_dataframe_function_registry_returns_df():
    """Load df from function in func_registry"""
    def dummy_df(data_sources, x):
        return pd.DataFrame({"x": [x]})
    data_sources = {}
    source = {
        "type": "function",
        "registry": "make_df",
        "data_source": "file_path_data",
        "kwargs": {"x": 5},
    }
    registry = {"make_df": dummy_df}

    result = load_dataframe(data_sources, source, func_registry=registry)

    expected = pd.DataFrame({"x": [5]})
    pd.testing.assert_frame_equal(result, expected)

    
def test_load_dataframe_function_registry_missing_key():
    """Errors when function registry key is missing"""
    data_sources = {}
    source = {
        "type": "function",
        "registry": "missing",
        "kwargs": {},
    }
    registry = {}
    data_sources = {}
    
    with pytest.raises(ValueError) as excinfo:
        load_dataframe(data_sources, source, func_registry=registry)

    assert "Function source requi" in str(excinfo.value)
    

def test_load_dataframe_function_returns_dict_with_key():
    """Load df via key in dict in function"""
    def make_dict(data_sources):
        return {
            "train": pd.DataFrame({"id": [1, 2]}),
            "test": pd.DataFrame({"id": [3]}),
        }

    data_sources = {}
    source = {
        "type": "function",
        "registry": "make_dict",
        "key": "test",
    }
    registry = {"make_dict": make_dict}

    result = load_dataframe(data_sources, source, func_registry=registry)

    expected = pd.DataFrame({"id": [3]})
    pd.testing.assert_frame_equal(result, expected)

    
def test_load_dataframe_function_dict_value_not_df():
    """Errors when loading non-df from function dict key"""
    def make_dict(data_sources):
        return {"wrong": [1, 2, 3]}

    data_sources = {}
    source = {
        "type": "function",
        "registry": "make_dict",
        "key": "wrong",
    }
    registry = {"make_dict": make_dict}

    with pytest.raises(TypeError) as excinfo:
        load_dataframe(data_sources, source, func_registry=registry)

    assert "is not a DataFrame" in str(excinfo.value)
    
    
def test_load_dataframe_function_returns_invalid_type():
    """Errors when non-df returned"""
    def bad_func(data_sources):
        return [1, 2, 3]

    data_sources = {}
    source = {
        "type": "function",
        "registry": "bad",
    }
    registry = {"bad": bad_func}

    with pytest.raises(TypeError) as excinfo:
        load_dataframe(data_sources, source, func_registry=registry)

    assert "did not return a pandas DataFrame" in str(excinfo.value)


def test_load_dataframe_unsupported_type():
    """Errors when unsupported type passed"""
    data_sources = {}
    source = {
        "type": "json",
        "path": "data.json",
    }

    with pytest.raises(ValueError) as excinfo:
        load_dataframe(data_sources, source)

    assert "Unsupported source.type='json'" in str(excinfo.value)
