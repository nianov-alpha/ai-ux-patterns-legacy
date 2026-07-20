#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai-ux — MCP Server (zero-dependency, stdio transport).

Exposes the AI-Native Interface Patterns database to any MCP-capable AI tool
(Claude Desktop, Cursor, Windsurf, Cline, ...) via the Model Context Protocol.

Transport: newline-delimited JSON-RPC 2.0 over stdio (UTF-8, LF).
Reuses ../search.py (standalone BM25). No external dependencies.

Register (e.g. Claude Desktop claude_desktop_config.json):
  { "mcpServers": { "ai-ux": {
      "command": "python",
      "args": ["/ABS/PATH/TO/mcp/server.py"] } } }

© Azka, MIT. BM25 engine adapted from ui-ux-pro-max (© Next Level Builder, MIT).
"""

import sys
import json
from pathlib import Path

# MCP speaks UTF-8 over stdio; force UTF-8 + LF so the wire is identical on every
# platform (Windows defaults to cp1252 + CRLF, which would corrupt the transport).
for _stream in (sys.stdin, sys.stdout):
    try:
        _stream.reconfigure(encoding="utf-8", newline="\n")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    import search as engine
except Exception as e:  # pragma: no cover
    engine = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "ai-ux"
SERVER_VERSION = "1.0.0"


def _log(*a):
    print(*a, file=sys.stderr, flush=True)


def _format_results(results, query):
    if not results:
        return f'No ai-ux patterns matched "{query}". Try broader keywords.'
    lines = [f'{len(results)} pattern(s) for "{query}":']
    for i, r in enumerate(results, 1):
        lines.append(f"\n### {i}. {r.get('Pattern Name','')} [{r.get('Pattern Category','')}]")
        for k, v in r.items():
            if k in ("Pattern Name", "Pattern Category"):
                continue
            if str(v).strip():
                lines.append(f"- **{k}:** {v}")
    return "\n".join(lines)


def _tools():
    return [
        {
            "name": "search_ai_ux_patterns",
            "description": (
                "Search the ai-ux database of AI-native interface UX patterns "
                "(streaming, tool-calls, citations, hallucination handling, memory, "
                "voice, prompt-injection, multi-agent, and more). Returns problem, "
                "solution, do/don't, a paste-ready code snippet, plus trust/severity."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string",
                              "description": "Pattern to find, e.g. 'stop button for streaming'."},
                    "max_results": {"type": "integer", "minimum": 1, "maximum": 10, "default": 3},
                },
                "required": ["query"],
            },
        },
        {
            "name": "list_ai_ux_categories",
            "description": "List all ai-ux pattern categories with the number of patterns in each.",
            "inputSchema": {"type": "object", "properties": {}},
        },
    ]


def _call_tool(name, args):
    if engine is None:
        return f"Search engine unavailable: {_IMPORT_ERROR}"
    args = args or {}
    if name == "search_ai_ux_patterns":
        q = args.get("query")
        if not q:
            raise ValueError("'query' is required")
        n = int(args.get("max_results", 3))
        return _format_results(engine.search(q, n), q)
    if name == "list_ai_ux_categories":
        cats = engine.categories()
        total = sum(cats.values())
        lines = [f"ai-ux — {total} patterns across {len(cats)} categories:"]
        lines += [f"- {c}: {n}" for c, n in cats.items()]
        return "\n".join(lines)
    raise ValueError(f"Unknown tool: {name}")


def _send(msg):
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _result(rid, result):
    _send({"jsonrpc": "2.0", "id": rid, "result": result})


def _error(rid, code, message):
    _send({"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message}})


def _handle(msg):
    method = msg.get("method")
    rid = msg.get("id")
    is_request = rid is not None

    if method == "initialize":
        ver = (msg.get("params") or {}).get("protocolVersion") or PROTOCOL_VERSION
        _result(rid, {
            "protocolVersion": ver,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        })
        return
    if method in ("notifications/initialized", "initialized"):
        return
    if method == "ping":
        if is_request:
            _result(rid, {})
        return
    if method == "tools/list":
        _result(rid, {"tools": _tools()})
        return
    if method == "tools/call":
        params = msg.get("params") or {}
        try:
            text = _call_tool(params.get("name"), params.get("arguments") or {})
            _result(rid, {"content": [{"type": "text", "text": text}], "isError": False})
        except ValueError as ve:
            _result(rid, {"content": [{"type": "text", "text": f"Input error: {ve}"}], "isError": True})
        except Exception as ex:  # pragma: no cover
            _log("tool error:", ex)
            _result(rid, {"content": [{"type": "text", "text": f"Internal error: {ex}"}], "isError": True})
        return
    if is_request:
        _error(rid, -32601, f"Method not found: {method}")


def main():
    _log(f"[{SERVER_NAME}] MCP server starting on stdio.")
    if _IMPORT_ERROR:
        _log(f"[{SERVER_NAME}] WARNING: search engine import failed: {_IMPORT_ERROR}")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            _log("bad JSON on stdin:", e)
            continue
        try:
            _handle(msg)
        except Exception as e:  # pragma: no cover
            _log("handler crashed:", e)
            if msg.get("id") is not None:
                _error(msg.get("id"), -32603, f"Internal error: {e}")


if __name__ == "__main__":
    main()
