# ai-ux — AI-Native Interface Patterns

A free, open-source, **searchable database of 100 UX patterns for AI products** —
the parts of the interface that classic design systems (Material, HIG) never
covered: streaming responses, tool-call visualization, citations, hallucination
handling, memory transparency, voice turn-taking, prompt-injection defense,
multi-agent handoffs, and more.

Every pattern pairs the **problem** with a concrete **do / don't** and a
**paste-ready code snippet**, plus a *trust impact* and *severity* rating.

- **100 patterns · 24 categories**
- **Zero dependencies** — pure Python 3.x standard library
- Ships with a **CLI**, an **MCP server**, and an **interactive gallery**
- **MIT licensed**

Why this exists: teams building AI products keep reinventing the same interface
decisions (how do I show the agent is working? how do I flag a low-confidence
answer? how do I let users interrupt a stream?). The knowledge is scattered
across blog posts; this makes it queryable and code-ready.

## Quick start

```bash
git clone https://github.com/<your-username>/ai-ux-patterns.git
cd ai-ux-patterns

# search
python search.py "how do I show the agent is calling a tool"
python search.py "stop button while streaming" -n 5

# list categories
python search.py --categories
```

No install, no `pip` — Python 3.x is the only requirement.

## Interactive gallery

Open [`gallery.html`](gallery.html) in any browser to browse, search, and filter
all 100 patterns visually. It is fully self-contained (no network, no build).
Rebuild it after editing the data with:

```bash
python scripts/build_gallery.py
```

## Use it inside your AI tools (MCP)

An [MCP](https://modelcontextprotocol.io) server lets Claude Desktop, Cursor,
Windsurf, Cline, and other MCP clients query the database directly. See
[`mcp/README.md`](mcp/README.md). Minimal config:

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

Tools exposed: `search_ai_ux_patterns`, `list_ai_ux_categories`.

## Categories

Streaming · Prompt Input · Tool Use · Trust & Safety · Feedback · Memory ·
Latency · Errors · Cost · Onboarding · Voice · Security · Evaluation · Steering ·
Collaboration · Accessibility · Retrieval · Multi-Agent · Generation ·
Personalization · Consent · Async · Discovery · Mobile

## Data format

`data/ai-ux-patterns.csv` — one pattern per row:

| Column | Meaning |
|--------|---------|
| Pattern Category / Pattern Name | grouping and title |
| Keywords | search terms |
| Problem / Solution | the user pain and the UX approach |
| Do / Don't | the concrete guidance |
| Code Example / Anti-Pattern | paste-ready snippet vs the wrong way |
| When to Use | context |
| Trust Impact / Severity | Low · Medium · High |

## Contributing

Patterns are just CSV rows — add one and open a PR. Keep the *Problem → Solution
→ Do → Don't → Code* shape, and prefer framework-neutral snippets.

## License

MIT © 2026 Azka. The BM25 search engine is adapted from
[ui-ux-pro-max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
(© Next Level Builder, MIT) — see [`NOTICE.md`](NOTICE.md).
