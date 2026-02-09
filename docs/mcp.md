
### FastMCP Tool Usage
The server exposes a tool `list-boardgames-page` that allows agents to query the board game database with pagination.

**Usage:**
```bash
uv run python scripts/boardgames_mcp.py
```
This runs the MCP server over stdio.

**Probe:**
You can verify the tool works by running the probe script:
```bash
uv run scripts/mcp_probe.py
```
**Sample Output:**
```json
{
  "status": 200,
  "total": 5,
  "items": [
    {"id": 1, "name": "Catan", ...},
    {"id": 2, "name": "Carcassonne", ...}
  ]
}
```
