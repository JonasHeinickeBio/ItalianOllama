#!/usr/bin/env python
"""ItalianOllama CLI - Command line interface for ItalianOllama.

Usage:
    python cli.py --help                    # Show all commands
    python cli.py start api                 # Start API server
    python cli.py neo4j status              # Check Neo4j connection
    python cli.py llm list                  # List LLM providers
    python cli.py llm test                  # Test LLM connection
    python cli.py vocab add <word> <trans>  # Add vocabulary
    python cli.py vocab list                # List vocabulary
    python cli.py config show               # Show configuration
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from italianollama.cli.main import cli

if __name__ == "__main__":
    cli()
