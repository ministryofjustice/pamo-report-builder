import types
import sys
from pathlib import Path
import pytest
from create_report import resolve_callable


def test_resolve_callable_simple_dotted():
    """Dotted path resolves"""
    func = resolve_callable("math.sqrt")
    import math

    assert func is math.sqrt
    assert callable(func)
    assert func(9) == 3

    
def test_resolve_callable_colon_syntax():
    """Resolves colon to dotted path"""
    func = resolve_callable("math:sqrt")
    import math

    assert func is math.sqrt
    assert func(16) == 4


def test_resolve_callable_invalid_path_raises_value_error():
    """Invalid path flags ValueError"""
    with pytest.raises(ValueError) as excinfo:
        resolve_callable("justname")

    assert "Invalid dotted path 'justname'" in str(excinfo.value)


def test_resolve_callable_missing_attribute_raises_attribute_error():
    """Missing function flags AttributeError"""
    with pytest.raises(AttributeError) as excinfo:
        resolve_callable("math.fake_function")
        
    assert "'math.fake_function' is not a callable." in str(excinfo.value)

    
def test_resolve_callable_attribute_not_callable():
    """Non-callable attribute flags AttributeError"""
    with pytest.raises(AttributeError) as excinfo:
        resolve_callable("math.pi")

    assert "'math.pi' is not a callable." in str(excinfo.value)

    
