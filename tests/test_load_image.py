import io
import os
from pathlib import Path

import pytest

from create_report import load_image

def test_load_image_file_relative_path(tmp_path):
    """Loads image from test relative path"""
    # Create a dummy image file
    base_dir = tmp_path
    img_path = tmp_path / "images" / "test.png"
    img_path.parent.mkdir()
    img_bytes = b"fake image data"
    img_path.write_bytes(img_bytes)

    source = {
        "type": "png",
        "path": "images/test.png",
    }

    result = load_image(source, base_dir=base_dir)

    assert isinstance(result, io.BytesIO)
    assert result.getvalue() == img_bytes
    

def test_load_image_file_absolute_path(tmp_path):
    """Loads image from test absolute path"""
    img_path = tmp_path / "test.jpg"
    img_bytes = b"jpeg bytes"
    img_path.write_bytes(img_bytes)

    source = {
        "type": "jpg",
        "path": str(img_path),
    }

    result = load_image(source, base_dir=Path("/some/other/base"))

    assert isinstance(result, io.BytesIO)
    assert result.getvalue() == img_bytes
    

def test_load_image_function_via_registry():
    """Creates dummy function to be called and tested via func_registry"""
    # Dummy function to be called
    def dummy_func(x, y):
        return x + y

    source = {
        "type": "function",
        "registry": "add_xy",
        "kwargs": {"x": 2, "y": 3},
    }
    func_registry = {"add_xy": dummy_func}

    result = load_image(source, func_registry=func_registry)

    assert result == 5
    
    
def test_load_image_file_not_found(tmp_path):
    """Loads image from fake path - Errors"""
    base_dir = tmp_path
    source = {
        "type": "png",
        "path": "does_not_exist.png",
    }

    with pytest.raises(FileNotFoundError) as excinfo:
        load_image(source, base_dir=base_dir)

    assert "was not found" in str(excinfo.value)
    

def test_load_image_function_missing_spec():
    """Passess function in func_registry with no spec"""
    source = {
        "type": "function",
    }

    with pytest.raises(ValueError) as excinfo:
        load_image(source)

    assert "Function source requires" in str(excinfo.value)


