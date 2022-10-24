"""RESTful service for hosting machine learning models."""

from os.path import abspath, dirname, join

__all__ = ["__version__"]


try:
    with open(join(abspath(dirname(__file__)), "version.txt"), encoding="utf-8") as f:
        __version__ = f.read()
except Exception:
    __version__ = "N/A"
