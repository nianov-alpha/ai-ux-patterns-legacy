# ai-ux — MCP Server

Expose the AI-Native Interface Patterns database to any MCP-capable AI tool —
Claude Desktop, Cursor, Windsurf, Cline, and others — via the
[Model Context Protocol](https://modelcontextprotocol.io).

- **Zero dependencies.** Pure Python 3.x; reuses `../search.py`.
- **Transport:** newline-delimited JSON-RPC 2.0 over stdio (UTF-8, LF).

## Tools

| Tool | What it does |
|------|--------------|
| `search_ai_ux_patterns` | Search the 100 patterns; returns problem, solution, do/don't, a paste-ready snippet, plus trust/severity. |
| `list_ai_ux_categories` | List all categories with pattern counts. |

## Register with a client

Use the **absolute path** to `server.py`. On Windows use `python`; on
macOS/Linux use `python3`.

```json
{
  "mcpServers": {
    "ai-ux": {
      "command": "python",
      "args": ["/ABSOLUTE/PATH/TO/ai-ux-patterns/mcp/server.py"]
    }
  }
}
```

A ready-to-edit copy is in [`config.example.json`](./config.example.json).

## Verify by hand

```bash
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05"}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"search_ai_ux_patterns","arguments":{"query":"stop button while streaming","max_results":1}}}' \
  | python mcp/server.py
```

You should get three JSON-RPC responses: server info, the tool list, and one
matching pattern.
