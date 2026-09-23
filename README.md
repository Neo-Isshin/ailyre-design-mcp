# Ailyre Design MCP

Open source MCP code and authored, text-only design knowledge. It helps agents choose design patterns, Props Schemas, CSS tokens, anatomy and interaction constraints, then write fresh code in the user's stack.

The hosted service is available at `https://www.ailyre.com/api/mcp` with a personal Ailyre key. This repository is a clean source mirror: it contains 10 authored patterns and routing decisions for 126 references, but no collected source repositories, screenshots, media, research notes or credentials. The hosted instance may offer a small audited source-file allowlist; that private mirror is intentionally not included here.

## Run Locally

Requires Python 3.13. From the repository root:

```bash
python3 -m venv .venv
.venv/bin/pip install -r api/requirements.txt
cd api
SITE_COLLECTION_DATA=.. ../.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8787
```

Use `http://127.0.0.1:8787/mcp` as a Streamable HTTP MCP URL. For a local client, no key is needed unless `PUBLIC_REQUIRE_API_KEY=1` is set. This mirror only reads the authored pattern layer and sanitized source registry; `list_open_source_files` is empty because the optional private archive is not distributed.

## Main Tools

- `route_design_request`: prefer authored patterns, then return optional user-direct provider routes and source links.
- `find_patterns` / `get_pattern`: retrieve anatomy, Props Schema, tokens, states, accessibility notes and credits.
- `route_item`: inspect the decision for one of the 126 references. Provider endpoints are documentation, not server-side proxies.
- `recommend_design` / `list_catalog`: compatibility catalog tools.

Pattern text is licensed under [CC BY 4.0](knowledge/LICENSE); API code is [MIT](LICENSE). Upstream projects retain their own rights. [Sources and credits](knowledge/SOURCES.md) travel with every pattern response. The [routing audit](knowledge/ROUTING_AUDIT.md) records inclusion and provider decisions for every source.
