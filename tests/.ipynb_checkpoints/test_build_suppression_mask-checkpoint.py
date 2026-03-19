import pandas as pd
import pytest

from create_report import build_suppression_mask

def test_returns_same_shape_and_boolean_mask():
    df = pd.DataFrame({
        "A": [1, 10],
        "B": [5, 6],
        "A %": [10.0, 20.0],
    })

    mask = build_suppression_mask(df, primary_threshold=3)

    assert list(mask.columns) == list(df.columns)
    assert list(mask.index) == list(df.index)
    assert mask.dtypes.eq(bool).all()


def test_no_base_columns_returns_all_false():
    df = pd.DataFrame({
        "A %": [1, 2],
        "B £": [3, 4],
    })

    mask = build_suppression_mask(df)

    expected = pd.DataFrame(False, index=df.index, columns=df.columns)
    pd.testing.assert_frame_equal(mask, expected)


def test_primary_suppression_applies_only_to_base_columns():
    df = pd.DataFrame({
        "Count": [2, 5, 1],
        "Rate %": [2, 1, 0],
        "Cost £": [1, 2, 3],
    })

    mask = build_suppression_mask(
        df,
        primary_threshold=3,
        k_per_row=0,
        k_per_col=0,
    )

    expected = pd.DataFrame({
        "Count": [True, False, True],
        "Rate %": [False, False, False],
        "Cost £": [False, False, False],
    }, index=df.index)

    pd.testing.assert_frame_equal(mask, expected)


def test_row_complementary_suppression_chooses_lowest_k_in_row():
    df = pd.DataFrame({
        "A": [1],
        "B": [10],
        "C": [2],
    }, index=["r1"])

    mask = build_suppression_mask(
        df,
        primary_threshold=2,
        k_per_row=2,
        k_per_col=0,
    )

    expected = pd.DataFrame({
        "A": [True],
        "B": [False],
        "C": [True],
    }, index=["r1"])

    pd.testing.assert_frame_equal(mask, expected)


def test_column_complementary_suppression_chooses_lowest_k_in_column():
    df = pd.DataFrame({
        "A": [1, 10, 2],
        "B": [8, 9, 10],
    }, index=["r1", "r2", "r3"])

    mask = build_suppression_mask(
        df,
        primary_threshold=2,
        k_per_row=0,
        k_per_col=2,
    )

    expected = pd.DataFrame({
        "A": [True, False, True],
        "B": [False, False, False],
    }, index=df.index)

    pd.testing.assert_frame_equal(mask, expected)


def test_iterative_row_column_propagation_reaches_fixed_point():
    df = pd.DataFrame({
        "A": [1, 100],
        "B": [2, 3],
        "C": [100, 4],
    }, index=["r1", "r2"])

    mask = build_suppression_mask(
        df,
        primary_threshold=2,
        k_per_row=2,
        k_per_col=2,
        max_iters=10,
    )

    expected = pd.DataFrame({
        "A": [True, True],
        "B": [True, True],
        "C": [True, True],
    }, index=df.index)

    pd.testing.assert_frame_equal(mask, expected)


def test_non_numeric_values_are_ignored_for_selection():
    df = pd.DataFrame({
        "A": [1],
        "B": ["x"],
        "C": [2],
    }, index=["r1"])

    mask = build_suppression_mask(
        df,
        primary_threshold=2,
        k_per_row=2,
        k_per_col=0,
    )

    expected = pd.DataFrame({
        "A": [True],
        "B": [False],
        "C": [True],
    }, index=df.index)

    pd.testing.assert_frame_equal(mask, expected)


def test_fewer_than_k_numeric_cells_suppresses_as_many_as_exist():
    df = pd.DataFrame({
        "A": [1],
        "B": ["x"],
        "C": [None],
    }, index=["r1"])

    mask = build_suppression_mask(
        df,
        primary_threshold=2,
        k_per_row=2,
        k_per_col=0,
    )

    expected = pd.DataFrame({
        "A": [True],
        "B": [False],
        "C": [False],
    }, index=df.index)

    pd.testing.assert_frame_equal(mask, expected)


def test_ties_are_broken_deterministically_by_column_order_for_rows():
    df = pd.DataFrame({
        "A": [1],
        "B": [1],
        "C": [5],
    }, index=["r1"])

    mask = build_suppression_mask(
        df,
        primary_threshold=1,
        k_per_row=0,
        k_per_col=0,
    )
    assert not mask.any().any()

    mask = build_suppression_mask(
        df,
        primary_threshold=2,
        k_per_row=2,
        k_per_col=0,
    )

    expected = pd.DataFrame({
        "A": [True],
        "B": [True],
        "C": [False],
    }, index=df.index)

    pd.testing.assert_frame_equal(mask, expected)


def test_integer_column_names_are_supported():
    df = pd.DataFrame({
        0: [1, 10],
        1: [2, 20],
        "Rate %": [0.1, 0.2],
    })

    mask = build_suppression_mask(
        df,
        primary_threshold=2,
        k_per_row=2,
        k_per_col=0,
    )

    expected = pd.DataFrame({
        0: [True, False],
        1: [True, False],
        "Rate %": [False, False],
    }, index=df.index)

    pd.testing.assert_frame_equal(mask, expected)


def test_k_per_row_zero_disables_row_enforcement():
    df = pd.DataFrame({
        "A": [1],
        "B": [2],
    })

    mask = build_suppression_mask(
        df,
        primary_threshold=2,
        k_per_row=0,
        k_per_col=0,
    )

    expected = pd.DataFrame({
        "A": [True],
        "B": [False],
    }, index=df.index)

    pd.testing.assert_frame_equal(mask, expected)


def test_k_per_col_zero_disables_column_enforcement():
    df = pd.DataFrame({
        "A": [1, 2, 3],
    })

    mask = build_suppression_mask(
        df,
        primary_threshold=2,
        k_per_row=0,
        k_per_col=0,
    )

    expected = pd.DataFrame({
        "A": [True, False, False],
    }, index=df.index)

    pd.testing.assert_frame_equal(mask, expected)


def test_custom_exclude_substrings():
    df = pd.DataFrame({
        "Count": [1, 10],
        "Rate pct": [0.1, 0.2],
    })

    mask = build_suppression_mask(
        df,
        primary_threshold=2,
        exclude_substrings=("pct",),
        k_per_row=0,
        k_per_col=0,
    )

    expected = pd.DataFrame({
        "Count": [True, False],
        "Rate pct": [False, False],
    }, index=df.index)

    pd.testing.assert_frame_equal(mask, expected)