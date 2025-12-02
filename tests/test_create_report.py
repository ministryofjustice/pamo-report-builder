import unittest
import pandas as pd
import io
import re
from pathlib import Path
from create_report import (
    load_toml, load_image, load_dataframe, resolve_callable,
    infer_format_name, build_format, autosize_width,
    dataframe_to_table_data, add_excel_table, set_column_formats_and_widths
)

class TestExcelHelpers(unittest.TestCase):

    def test_infer_format_name_matches(self):
        matchers = [(re.compile(r"salary"), "currency"), (re.compile(r"date"), "date_fmt")]
        self.assertEqual(infer_format_name("base_salary", matchers, "default"), "currency")
        self.assertEqual(infer_format_name("start_date", matchers, "default"), "date_fmt")
        self.assertEqual(infer_format_name("unknown_column", matchers, "default"), "default")

    def test_autosize_width_basic(self):
        series = pd.Series(["short", "medium length", "a very very long string"])
        width = autosize_width(series)
        self.assertTrue(10 <= width <= 40)

    def test_dataframe_to_table_data_nan_handling(self):
        df = pd.DataFrame({"A": [1, None], "B": [None, "y"]})
        data = dataframe_to_table_data(df)
        self.assertEqual(data, [[1, ""], ["", "y"]])

    def test_load_dataframe_csv(self):
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        temp_path = Path("temp_test.csv")
        df.to_csv(temp_path, index=False)
        source = {"type": "csv", "path": str(temp_path)}
        loaded_df = load_dataframe(source)
        pd.testing.assert_frame_equal(df, loaded_df)
        temp_path.unlink()

    def test_load_dataframe_excel(self):
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        temp_path = Path("temp_test.xlsx")
        df.to_excel(temp_path, index=False, sheet_name="Sheet1")
        source = {"type": "excel", "path": str(temp_path), "sheet": "Sheet1"}
        loaded_df = load_dataframe(source)
        pd.testing.assert_frame_equal(df, loaded_df)
        temp_path.unlink()

    def test_resolve_callable_valid(self):
        # Assuming there's a dummy function in a test module
        func = resolve_callable("math.sqrt")
        self.assertTrue(callable(func))
        self.assertEqual(func(4), 2.0)

    def test_load_toml_valid(self):
        toml_content = """
        [workbook]
        output = "test.xlsx"
        """
        temp_path = Path("temp_config.toml")
        temp_path.write_text(toml_content)
        cfg = load_toml(temp_path)
        self.assertEqual(cfg["workbook"]["output"], "test.xlsx")
        temp_path.unlink()

if __name__ == "__main__":
    unittest.main()
