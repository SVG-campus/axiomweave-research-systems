# AxiomWeave Research Systems

A portable, evidence-bounded research harness: **21 MCP tools**, **95 method contracts**, exact symbolic Apriori/combinatorial search, optional certified numerical backends, and a three-round Millennium-problem portfolio with final negative controls. It improves an earlier eight-engine Antigravity architecture by implementing selected bounded operations and exposing missing capabilities explicitly.

This is research infrastructure, not a universal problem solver. No new Millennium solution is claimed. Model weights are not changed. Agreement between assistants is not independent mathematical validation.

## Names to use in a model query

* MCP server: **`axiomweave-research-systems`**.
* Companion skill: **`$axiomweave-research-systems`**, when the checked-in skill is installed or discovered by the client.
* The symbolic technique is called **symbolic Apriori/combinatorial search**. It is separate from finance implementations also called AS³-R.

Example query after enabling the server:

> Use axiomweave-research-systems to investigate this question. Route applicable methods, audit hereditary pruning and semantic correspondence, execute supported checks, and report certificates, negative controls, missing backends, and remaining proof obligations.

For the finite portfolio:

> Use axiomweave-research-systems.run_research_loop with rounds=3, then explain which results are finite checks, which use external theorem assumptions, and which proof gates remain open.

Client-visible names may have an MCP namespace prefix. Requesting the server by name does not configure it. The official MCP SDK handshake and calls passed; discovery in a live Codex, Antigravity, or OpenCode session has not been verified. See [SETUP.md](SETUP.md).

## Reproduce

Requires Python 3.11 or newer. The server and core exact tools use only the standard library. Optional FLINT supplies rigorous balls and zeta count/root routines; optional PARI/GP supplies descent bounds. Dependencies are optional and missing ones return explicit abstention.

```sh
git clone https://github.com/SVG-campus/axiomweave-research-systems.git
cd axiomweave-research-systems
python -m venv .venv
# Activate .venv for your shell, then:
python -m pip install -r requirements-research.txt
python -m unittest discover -s scripts -p 'test*.py' -v
python scripts/research_loop.py
python scripts/research_mcp.py
```

On Debian, `pari-gp` is an optional system package. Do not install or download the large Lean/mathlib stack on a nearly full device. The Navier–Stokes replay is a separate pinned upstream project, not part of these Python checks.

## Evidence and limits

* [RESULTS.md](RESULTS.md): seven-problem results, interpretation and next research.
* [COMPARISON.md](COMPARISON.md): Antigravity/Codex strengths, corrections and open comparison.
* [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md): typed routing, backend scope, proof gates and stopping rules.
* [METHOD_CATALOG.md](METHOD_CATALOG.md), [catalog/methods.json](catalog/methods.json): the finite taxonomy.
* [receipts/domain-research-loop.json](receipts/domain-research-loop.json): executed expanding portfolio and final controls.
* [receipts/domain-tests.log](receipts/domain-tests.log): cloud tests including optional backends and official MCP SDK.
* [OWNER_PLAYBOOK.md](OWNER_PLAYBOOK.md): how to continue without upgrading finite evidence into proof.

All 95 entries are MCP-addressable with `execute_method`. Entries without adapters return their contract and abstain. An adapter implements only the documented narrow domain, not the entire mathematical method. The catalog's final sweep checks the frozen seed universe, not all possible discoveries. Large pairwise contract audits are not 9,025 executed mathematical solvers.

Public provenance excludes private conversations, account identifiers, credentials and cloud metadata. External source projects keep their own licenses; they are linked, not relicensed here.
