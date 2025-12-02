import numpy as np
import pandas as pd
import pytest

from create_report import dataframe_to_table_data


def test_dataframe_to_table_data_replaces_nan_with_empty_string():
    """Test function takes nan and returns empty string"""
    df = pd.DataFrame({"a": [1, np.nan], "b": ["x", "y"]})

    result = dataframe_to_table_data(df)

    assert result == [
        [1, "x"],
        ["", "y"],
    ]


def test_dataframe_to_table_data_preserves_values():
    """Test function returns values as expected"""
    df = pd.DataFrame({"a": [1, 2], "b": ["u", "v"]})

    result = dataframe_to_table_data(df)

    assert result == [
        [1, "u"],
        [2, "v"],
    ]


def test_dataframe_to_table_data_converts_numpy_types():
    """Test function converts numpy types to appropriate types"""
    df = pd.DataFrame({
        "a": [np.int64(5)],
        "b": [np.float64(2.5)],
    })

    result = dataframe_to_table_data(df)

    assert isinstance(result[0][0], (int, float))
    assert isinstance(result[0][1], float)
    assert result == [[result[0][0], 2.5]]



def test_dataframe_to_table_data_handles_none():
    """Test function takes None and returns empty string"""
    df = pd.DataFrame({"a": [None], "b": ["ok"]})

    result = dataframe_to_table_data(df)

    assert result == [["", "ok"]]

    
def test_dataframe_to_table_data_mixed_types():
    """Test function returns values as expected with mixed dtypes"""
    df = pd.DataFrame({
        "a": [1, None],
        "b": ["x", "y"],
        "c": [3.14, np.nan],
    })

    result = dataframe_to_table_data(df)

    assert result == [
        [1, "x", 3.14],
        ["", "y", ""],
    ]

    
def test_dataframe_to_table_data_empty_dataframe():
    """Test function runs with empty df"""
    df = pd.DataFrame()

    result = dataframe_to_table_data(df)

    assert result == []

    
def test_dataframe_to_table_data_no_rows_some_columns():
    """Test function returns empty from no rows"""
    df = pd.DataFrame({"a": [], "b": []})

    result = dataframe_to_table_data(df)

    assert result == []
    
    
def test_dataframe_to_table_data_all_nan():
    """Test function returns empty strings when data all nan"""
    df = pd.DataFrame({"a": [np.nan, np.nan]})

    result = dataframe_to_table_data(df)

    assert result == [[""], [""]]

    
def test_dataframe_to_table_data_does_not_modify_original():
    """Test function preserves input"""
    df = pd.DataFrame({"a": [1, np.nan]})
    df_copy = df.copy()

    _ = dataframe_to_table_data(df)

    pd.testing.assert_frame_equal(df, df_copy)
