---
name: oce-mcp-integration
description: "Connect OpenConstructionERP to AI coding assistants via MCP (Model Context Protocol): expose costs, BOQ, BIM and catalog endpoints as MCP tools so Claude Code / Antigravity / OpenCode can drive the platform. Use when wiring an assistant to the ERP."
---

# MCP Integration for OpenConstructionERP

## Why MCP

MCP (Model Context Protocol) is the 2026 standard for giving AI assistants tools. Wrapping OpenConstructionERP's REST API in an MCP server turns the assistant from a chat partner into an operator: it can load a cost base, search items, build a BOQ and read validation results itself.

## What to expose (start with these)

| MCP tool | Underlying API | Notes |
|---|---|---|
| `list_cost_bases` | `GET /api/v1/costs/base-catalog` | families, variants, positions, loaded badge |
| `load_cost_base` | `POST /api/v1/costs/load-cwicr/{db_id}` | idempotent, returns imported/skipped |
| `search_cost_items` | `GET /api/v1/costs/?region=...&q=...` | SQL path, works without Qdrant |
| `get_cost_item` | `GET /api/v1/costs/{id}` | full components[] + classification |
| `category_tree` | `GET /api/v1/costs/category-tree/?region=...` | browsing |
| `suggest_for_element` | `POST /api/v1/costs/suggest-for-element` | BIM element → cost ranking |
| `create_boq` / `validate_boq` | `POST /api/v1/boqs`, `/boqs/{id}/validate/` | estimating |
| `import_catalog` | `POST /api/v1/catalog/import/{region}` | resource catalog |

## Reference implementation (TypeScript, fast)

```typescript
// mcp-server: FastMCP wrapper around the ERP's FastAPI backend
import { FastMCP } from "fastmcp";

const ERP = process.env.OPENESTIMATE_URL ?? "http://localhost:8000";
const server = new FastMCP({ name: "openconstructionerp" });

server.addTool({
  name: "load_cost_base",
  description: "Load a CWICR cost base (e.g. TR_NATIONAL, ZH_CHINA) into the ERP.",
  parameters: { db_id: { type: "string", required: true } },
  execute: async ({ db_id }) => {
    const r = await fetch(`${ERP}/api/v1/costs/load-cwicr/${db_id}`, {
      method: "POST",
      headers: { Authorization: `Bearer ${process.env.ERP_TOKEN}` },
    });
    return await r.json();
  },
});

server.addTool({
  name: "search_cost_items",
  description: "Search cost items in a region by keyword.",
  parameters: { region: { type: "string" }, q: { type: "string" } },
  execute: async ({ region, q }) => {
    const r = await fetch(`${ERP}/api/v1/costs/?region=${region}&q=${encodeURIComponent(q)}&limit=20`,
      { headers: { Authorization: `Bearer ${process.env.ERP_TOKEN}` } });
    return await r.json();
  },
});

server.start({ transportType: "stdio" });
```

## Auth & safety

- Reuse the ERP's JWT (register a service account; bootstrap admin only for setup).
- MCP tools must be idempotent and read-mostly: `load_cost_base` returns `already_loaded` on repeat.
- Never expose raw credentials in tool descriptions; use env vars (`ERP_TOKEN`).
- Rate-limit write tools; the ERP already enforces `api_rate_limit` (200/min default).

## Best practices

1. Start read-only (browse/search), add writes (BOQ create, link) after testing.
2. Wrap long operations (BIM conversion) in a progress-tool pattern instead of blocking.
3. Log every assistant action server-side (the platform's usage ledger pattern).
4. Publish the MCP server to the assistant marketplace (Claude Code registry, Antigravity, OpenCode).
