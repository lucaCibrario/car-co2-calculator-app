"""Resolve versioned model data and documentation independent of the working directory."""

import sys
from pathlib import Path


def resource_path(relative_path: str | Path) -> str:
    """Return an absolute path to a bundled application resource."""
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return str(root / relative_path)
