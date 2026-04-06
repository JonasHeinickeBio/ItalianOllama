# MCP Server Integration

This guide documents the Model Context Protocol (MCP) server integration for the ItalianOllama project, enabling the opencode AI agent with enhanced capabilities.

## Overview

The ItalianOllama project integrates 10 MCP servers to extend the opencode agent's capabilities with tools for Git operations, web content fetching, memory management, time conversions, web search, database access, browser automation, web scraping, and document conversion.

## Configured MCP Servers

All servers are configured in `~/.config/opencode/opencode.json` using `uvx` as the transport command.

### 1. Git Server
- **Package**: `git-mcp-server`
- **Command**: `uvx git-mcp-server`
- **Purpose**: Git repository operations and history analysis

### 2. Fetch Server
- **Package**: `fetch-mcp-server`
- **Command**: `uvx fetch-mcp-server`
- **Purpose**: Web content fetching and retrieval

### 3. Memory Server
- **Package**: `memory-mcp-server`
- **Command**: `uvx memory-mcp-server`
- **Purpose**: Knowledge graph memory management

### 4. Sequential Thinking Server
- **Package**: `sequentialthinking-mcp-server`
- **Command**: `uvx sequentialthinking-mcp-server`
- **Purpose**: Reflective problem-solving and reasoning

### 5. Time Server
- **Package**: `time-mcp-server`
- **Command**: `uvx time-mcp-server`
- **Purpose**: Timezone conversions and time operations

### 6. Brave Search Server
- **Package**: `brave-search-mcp-server`
- **Command**: `uvx brave-search-mcp-server`
- **Purpose**: Web search capabilities

### 7. PostgreSQL Server
- **Package**: `postgres-mcp-server`
- **Command**: `uvx postgres-mcp-server`
- **Purpose**: PostgreSQL database access and queries

### 8. Playwright Server
- **Package**: `@playwright/mcp`
- **Command**: `uvx @playwright/mcp`
- **Purpose**: Browser automation and web interaction

### 9. Firecrawl Server
- **Package**: `@microsoft/firecrawl-mcp`
- **Command**: `uvx @microsoft/firecrawl-mcp`
- **Purpose**: Web scraping and content extraction

### 10. MarkItDown Server
- **Package**: `markitdown`
- **Command**: `uvx markitdown`
- **Purpose**: Document format conversion

## Configuration

The MCP servers are defined in opencode's configuration file at `~/.config/opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": ["git-mcp-server"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["fetch-mcp-server"]
    },
    "memory": {
      "command": "uvx",
      "args": ["memory-mcp-server"]
    },
    "sequentialthinking": {
      "command": "uvx",
      "args": ["sequentialthinking-mcp-server"]
    },
    "time": {
      "command": "uvx",
      "args": ["time-mcp-server"]
    },
    "brave-search": {
      "command": "uvx",
      "args": ["brave-search-mcp-server"]
    },
    "postgres": {
      "command": "uvx",
      "args": ["postgres-mcp-server"]
    },
    "playwright": {
      "command": "uvx",
      "args": ["@playwright/mcp"]
    },
    "firecrawl": {
      "command": "uvx",
      "args": ["@microsoft/firecrawl-mcp"]
    },
    "markitdown": {
      "command": "uvx",
      "args": ["markitdown"]
    }
  }
}
```

## Integration with ItalianOllama

### Project Context
ItalianOllama is a FastAPI-based Italian language learning platform using:
- **LangGraph** for workflow orchestration
- **Neo4j** for persistent student data and vocabulary
- **LiteLLM** for LLM provider abstraction
- **uvx** for package execution without virtual environments

### MCP Configuration in Chainlit

The project has MCP transport enabled in Chainlit config files:
- `.chainlit/config.toml`
- `src/italianollama/frontend/streamlit/pages/.chainlit/config.toml`

MCP transport is disabled by default but can be enabled via environment variable:
```bash
CHAINLIT_MCP_TRANSPORT_ENABLED=true
```

## Usage

### Verify Configuration
```bash
# View opencode configuration with MCP servers
cat ~/.config/opencode/opencode.json
```

### Test MCP Server Connection
```bash
# Test uvx installation
uvx --version

# Test individual servers
uvx git-mcp-server --help
uvx fetch-mcp-server --help
```

### Use in opencode
Once configured, the MCP servers are automatically available to the opencode agent. The agent can:
- Analyze Git history and repository structure
- Fetch web content for research
- Query knowledge graphs for memory retrieval
- Perform timezone conversions
- Execute web searches
- Query PostgreSQL databases
- Automate browser interactions
- Scrape web content
- Convert documents to markdown

## Technical Details

### Transport Method
All MCP servers use `uvx` as the transport command, which:
- Runs Python packages without creating virtual environments
- Caches packages for faster subsequent runs
- Is compatible with the project's existing `uv` tooling

### Package Sources
- Most servers are published on PyPI with the `mcp-server` naming convention
- Some servers use scoped packages (e.g., `@playwright/mcp`, `@microsoft/firecrawl-mcp`)
- Server names typically follow the pattern `<package-name>-mcp-server`

### Path Requirements
Ensure `uvx` is in your system PATH:
```bash
which uvx
```

If not found, install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Related Files

- `~/.config/opencode/opencode.json` - Main opencode configuration
- `~/.gemini/antigravity/mcp_config.json` - Reference MCP config (currently empty)
- `.chainlit/config.toml` - Chainlit MCP transport config
- `src/italianollama/frontend/streamlit/pages/.chainlit/config.toml` - Streamlit Chainlit config

## Troubleshooting

### Server Not Found
If a server fails to start:
1. Verify the package name is correct
2. Check that `uvx` is installed and in PATH
3. Ensure the package is published on PyPI

### Connection Issues
If opencode cannot connect to MCP servers:
1. Check opencode logs for connection errors
2. Verify the configuration JSON is valid
3. Ensure no firewall rules block the connections

### Package Not Found
If `uvx` cannot find a package:
```bash
# Clear uvx cache
uv cache clean

# Reinstall the package
uvx <package-name>
```

## Future Enhancements

Potential additions to consider:
- Additional MCP servers for project-specific needs
- Custom MCP servers for ItalianOllama domain tools
- Server pooling for load balancing
- Server health monitoring

## References

- [MCP Documentation](https://modelcontextprotocol.io)
- [uvx Documentation](https://github.com/astral-sh/uv)
- [opencode Configuration Schema](https://opencode.ai/config.json)
- [ItalianOllama Main README](../README.md)
