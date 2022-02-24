"""Helper functions."""
from typing import Type
import importlib


def load_type(class_path: str) -> Type:
    """Load a type.

    Args:
        class_path: Path of the type.

    Returns:
        Type

    """
    # splitting the class_path into module path and class name
    module_path = ".".join(class_path.split(".")[:-1])
    class_name = class_path.split(".")[-1]

    # importing the model class
    _module = importlib.import_module(module_path)
    _class = getattr(_module, class_name)
    return _class
