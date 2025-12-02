import pytest
import toml
from create_report import load_toml


def test_load_toml_nested(tmp_path):
    """Loads basic TOML"""
    file = tmp_path / "basic.toml"
    file.write_text(
        """
        [defaults]
        table_style = "Table Style Medium 1"
        spacing_rows = 2
        """
    )

    result = load_toml(file)

    assert "defaults" in result
    assert result["defaults"]["table_style"] == "Table Style Medium 1"
    assert result["defaults"]["spacing_rows"] == 2


def test_load_toml_nonexistent_file():
    """Raise FileNotFoundError when file does not exist"""
    with pytest.raises(FileNotFoundError):
        load_toml("does_not_exist.toml")


def test_load_toml_invalid_toml(tmp_path):
    """Invalid TOML raises a decoding error"""
    file = tmp_path / "bad.toml"
    file.write_text("not = !!! valid = toml")

    with pytest.raises(toml.TomlDecodeError):
        load_toml(file)
