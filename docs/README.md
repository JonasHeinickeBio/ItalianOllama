# ItalianOllama Documentation

Welcome to the ItalianOllama documentation. This folder contains comprehensive guides for understanding, developing, and deploying the Italian Tutor application.

## Documentation Structure

```
docs/
├── README.md                           # This file
├── STRUCTURE.md                        # Documentation organization
├── getting-started/                   # Quick start guides
│   ├── installation.md
│   ├── configuration.md
│   └── quick-start.md
├── architecture/                      # System design docs
│   ├── overview.md
│   ├── frontend.md
│   ├── backend.md
│   ├── database.md
│   └── llm-providers.md
├── development/                       # Developer guides
│   ├── setup.md
│   ├── coding-standards.md
│   ├── testing.md
│   ├── debugging.md
│   └── mcp-integration.md
├── deployment/                        # Deployment guides
│   ├── production.md
│   ├── docker.md
│   └── nginx.md
├── api/                               # API documentation
│   ├── endpoints.md
│   └── authentication.md
├── features/                          # Feature guides
│   ├── INDEX.md                       # Features index (primary reference)
│   ├── flashcard-review.md           # Flashcard system with spaced repetition
│   ├── session-tracking.md           # Neo4j session tracking system
│   ├── progress-tracking.md          # Student progress metrics
│   ├── dashboard.md                  # Analytics dashboard
│   ├── chat-interface.md
│   └── exercises.md
├── vocabulary/                        # Vocabulary system docs
│   ├── README.md                     # Vocabulary learning system overview
│   ├── architecture.md               # Architecture details
│   └── best-practices.md            # Best practices and examples
├── cli/                               # CLI documentation
│   ├── README.md                      # CLI overview (primary reference)
│   ├── COMMANDS.md                    # Deprecated (content in README)
│   ├── QUICK_REFERENCE.md             # Quick reference card
│   ├── QUICK_START.md                 # CLI quick start guide
│   └── improvements.md                # Technical improvements
└── troubleshooting/                   # Problem solving
    ├── common-issues.md
    └── faq.md
```

## Quick Links

- [Installation Guide](getting-started/installation.md)
- [Architecture Overview](architecture/overview.md)
- [API Endpoints](api/endpoints.md)
- [Deployment Guide](deployment/production.md)
- [MCP Server Integration](development/mcp-integration.md) - AI agent tool integration
- [CLI Documentation](cli/README.md) - Docker Compose CLI (primary reference)
- [CLI Quick Start](cli/QUICK_START.md) - Quick reference for CLI commands
- [Troubleshooting](troubleshooting/common-issues.md) - Common issues and solutions
- [Documentation Structure](STRUCTURE.md) - Documentation organization
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - System implementation overview
- [Vocabulary Learning System](vocabulary/README.md) - Complete vocabulary system guide

## Feature Documentation

### Flashcard Review System
Comprehensive guide to the flashcard review system with spaced repetition:
- **SM-2 Algorithm** - Intelligent review scheduling
- **Confidence Assessment** - Self-reported mastery levels
- **Session Tracking** - Complete progress tracking in Neo4j
- **Analytics Dashboard** - Visual progress visualization

[Read Flashcard Review Documentation](features/flashcard-review.md)

### Session Tracking System
Complete guide to Neo4j-based session tracking for monitoring learning progress:
- **Session History** - Track all learning activities
- **Real-time Metrics** - Accuracy, words reviewed, duration
- **Analytics Dashboard** - Progress visualization
- **Spaced Repetition Integration** - Review scheduling

[Read Session Tracking Documentation](features/session-tracking.md)

### Progress Tracking
Student progress tracking across multiple dimensions using Neo4j graph database.

[Read Progress Tracking Documentation](features/progress-tracking.md)

### Vocabulary Learning System
Complete guide to the vocabulary learning system with flashcards, Neo4j session tracking, and progress analytics:
- **Flashcard Review** - Confidence-based spaced repetition
- **Vocabulary Management** - Add, organize, and search words
- **Session Tracking** - Complete progress tracking in Neo4j
- **Analytics Dashboard** - Visual progress visualization

[Read Vocabulary Documentation](vocabulary/README.md)

### Dashboard Features
Streamlit-based analytics dashboard with comprehensive insights into learning progress.

[Read Dashboard Documentation](features/dashboard.md)

## Feature Overview

All features are documented in the [Features Index](features/INDEX.md) with:
- Feature comparisons
- Use cases
- Getting started guides
- Developer reference

## CLI Documentation

The project includes two CLI systems:

### Docker Compose CLI

A modular, scalable command-line interface for managing ItalianOllama services and Docker Compose infrastructure:

- **Docker Compose Management** - Start/stop/restart services with profiles
- **System Diagnostics** - Check Neo4j, LLM providers, and configuration
- **Helper Commands** - Reusable helper functions for common tasks

### Local Service CLI

Commands for managing local Python services directly:

- **Service Management** - Start/stop/restart API, Chainlit, and Streamlit services

### Quick CLI Start

```bash
# View all commands
python cli.py --help

# Docker Compose commands
python cli.py docker --help

# Local service commands
python cli.py service --help

# System check
python cli.py docker helpers check
python cli.py neo4j status
python cli.py llm test
python cli.py config show
```

For detailed CLI documentation, see the [CLI README](cli/README.md).

## Additional Resources

- [Main README](../README.md)
- [Tutorial README](../README_TUTOR.md)
- [GitHub Issues](https://github.com/JonasHeinickeBio/ItalianOllama/issues)
