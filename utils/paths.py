import os
import sys

from utils.logger import log_error


def resource_path(relative_path):
    """Returns the absolute path to the file (for normal execution and for PyInstaller)."""
    try:
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
    except Exception as e:
        log_error("resource_path", e)
        return relative_path
