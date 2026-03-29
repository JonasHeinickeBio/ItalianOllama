#!/usr/bin/env python
"""CLI entry point for Italian Tutor.

Usage:
    python cli.py --help
    python cli.py neo4j status
    python cli.py llm test
    python cli.py config show
"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from italianollama.cli.main import cli

if __name__ == "__main__":
    cli()
