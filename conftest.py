"""Root conftest.py – adds src/ to sys.path so tests can import italianollama."""

import sys
from pathlib import Path

# Allow importing the package without installing it
sys.path.insert(0, str(Path(__file__).parent / "src"))