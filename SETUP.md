# Connect a client

Clone the public repository into a location you intend to retain. Use an absolute Python executable and script path appropriate to your operating system. The repository skill is at `.agents/skills/axiomweave-research-systems/SKILL.md`.

## Codex

In Settings → MCP servers add a STDIO server named `axiomweave-research-systems`, using Python as the command and the absolute `scripts/research_mcp.py` path as its argument. Restart the client after saving. Check `/mcp` for discovery. Enable only for the research task and restore off afterward.

Alternatively prepare this entry in the user or trusted project `config.toml`:

```toml
[mcp_servers.axiomweave-research-systems]
command = "python"
args = ["/ABSOLUTE/PATH/axiomweave-research-systems/scripts/research_mcp.py"]
enabled = false
```

Change command to your venv's Python for optional backends. These are templates; this run did not mutate global client configuration. The official [Codex MCP documentation](https://developers.openai.com/codex/mcp) describes setup and `/mcp`; [skills documentation](https://developers.openai.com/codex/skills) describes discovery and invocation.

## Antigravity and OpenCode

Use the same STDIO command and argument in each client's supported MCP configuration. Client configuration formats vary; do not paste the Codex TOML into another client. Keep the entry disabled until needed, restart or refresh discovery, inspect the listed 21 tools, call `backend_capabilities`, then call a known positive and negative identity check. Authentication from one IDE does not transfer to another.

Portable command contract:

```json
{"name":"axiomweave-research-systems","transport":"stdio","command":"python","args":["/ABSOLUTE/PATH/axiomweave-research-systems/scripts/research_mcp.py"],"default_state":"off"}
```

This is an interchange description, not an asserted native schema for every client. Official SDK verification establishes protocol operation, not live IDE discovery or model utility.

Do not leave a configuration pointing at an ephemeral directory after cleanup. Public GitHub storage preserves source, not a continuously running MCP service. Hosting a persistent service is a separate deployment with authentication, isolation and operating-cost requirements.
