# Documentation Structure

This document explains the documentation structure for the ItalianOllama project.

## Overview

The documentation is organized to support different user types:

- **End Users**: Getting started guides and feature documentation
- **Developers**: Architecture and development guides
- **DevOps**: Deployment and operations documentation
- **CLI Users**: Command-line interface documentation

## Main Documentation Files

```
docs/
├── README.md                        # Main entry point
├── IMPLEMENTATION_SUMMARY.md        # Implementation overview
├── IMPROVED_DATA_MODEL.md           # Data model details
├── NEO4J_BEST_PRACTICES.md         # Neo4j guidance
├── BACKEND_STREAMLIT_INTEGRATION.md # Integration guide
├── QUICK_START.md                   # Quick start guide
├── DEVELOPMENT.md                   # Development roadmap
├── docker-compose.yml               # Docker configuration
└── deployment/                      # Deployment guides
    ├── production.md                # Production deployment
    ├── docker.md                    # Docker specifics (updated to use CLI)
    └── nginx.md                     # Nginx configuration
```

## Feature Documentation

```
docs/features/
├── INDEX.md                         # Features index (primary reference)
├── flashcard-review.md              # Flashcard review system
├── session-tracking.md              # Session tracking system
├── progress-tracking.md             # Analytics and metrics
├── dashboard.md                     # Dashboard features
├── chat-interface.md                # Chat interface guide
├── exercises.md                     # Exercise types
└── openrouter.md                    # OpenRouter integration
```

## Getting Started

```
docs/getting-started/
├── installation.md                  # Installation guide (updated)
├── configuration.md                 # Configuration options
└── quick-start.md                   # Quick start guide
```

## Architecture

```
docs/architecture/
├── overview.md                      # Architecture overview
├── frontend.md                      # Frontend architecture
├── backend.md                       # Backend architecture
├── database.md                      # Database schema
└── llm-providers.md                 # LLM provider integration
```

## Development

```
docs/development/
├── setup.md                         # Development setup
├── coding-standards.md              # Code style guide
├── testing.md                       # Testing documentation
└── debugging.md                     # Debugging guide
```

## CLI Documentation

```
docs/cli/
├── README.md                        # CLI main documentation (primary reference)
├── COMMANDS.md                      # Deprecated (content merged to README)
├── QUICK_REFERENCE.md               # Quick reference card
└── improvements.md                  # Technical improvements
```

## Troubleshooting

```
docs/troubleshooting/
├── common-issues.md                 # Common issues and solutions
└── faq.md                           # Frequently asked questions
```

## Documentation Principles

1. **Single Source of Truth**: Each piece of information appears in one primary location
2. **Clear Navigation**: Link related documentation across sections
3. **Up-to-Date**: Documentation is updated when code changes
4. **User-Focused**: Organized by user needs, not code structure
5. **Consistent**: Same format and style across all documentation

## Implementation Documentation

The `IMPLEMENTATION_SUMMARY.md` file provides:
- **System Architecture** - Component breakdown and data flow
- **Code Changes** - Detailed list of modified files
- **Data Models** - Neo4j schema and relationships
- **Integration Details** - Frontend, API, and database integration
- **Best Practices** - Usage guidelines and patterns
- **Troubleshooting** - Common issues and solutions

## Updating Documentation

When adding new features or changing existing ones:

1. Update relevant documentation files
2. Link to related documentation
3. Update this structure document if needed
4. Test that all links work correctly

## Related Documentation

- [Main README](../README.md) - Project overview
- [DEVELOPMENT.md](../DEVELOPMENT.md) - Development roadmap
- [DEPLOYMENT.md](../DEPLOYMENT.md) - Deployment guide
