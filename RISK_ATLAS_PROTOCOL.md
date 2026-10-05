# AxiomWeave Risk Atlas and Unified Research

This is a **finite risk taxonomy with compositional search, supplied-data stress tests, and bounded research iteration**. The catalog contains 240 declared scenarios across 60 named families. Catalog membership does not establish a working physical mechanism, market protection, or coverage of every possible risk.

## Names and tools

| MCP profile | Purpose | Tools |
|---|---|---|
| `axiomweave-risk-atlas` | Search the taxonomy, frame questions, probe measured controls, stress supplied positions, rank finite alternatives, suggest experiments and count alerts | Eight `atlas_*` tools |
| `axiomweave-unified-research` | Run actual CABS composition together with the atlas and an optional pinned AS3-R replay backend | Thirteen tools, including the atlas, `unified_probe`, `unified_as3r_replay`, and three `cabs_*` tools |
| `axiomweave-cabs` | Standalone Compositional Apriori-Beam Symbolic Search | `cabs_catalog`, `cabs_search`, `cabs_compose_costs` |

Use the unified profile for combined research. Its CABS functions call the canonical engine; its replay adapter starts the configured AS3-R executable, performs actual JSON-RPC calls, validates the response and closes that exact child. The executable path and SHA256 are startup configuration, never user tool arguments. AS3-R is an optional platform-specific backend. An absent or changed backend produces a tool error.

Suggested request:

> Use AxiomWeave Unified Research to frame this question, identify missing measurements, compare finite alternatives under my loss and compute budgets, retain the no-action baseline, and propose one falsifiable next experiment. Reapply the complete CABS framing before changing assumptions. Show the evidence, uncovered space, claim ceiling and stop rule.

`unified_probe` executes framing, operational probing, optional portfolio arithmetic and declarative next-step suggestions. Replay and minimax ranking remain explicit tool calls with supplied datasets and objectives. It does not automatically execute arbitrary generated workflows.

## What is implemented

The original 216 labels are searchable with strict diagnostic inputs. Historical terms such as quantum, ASIC, zero-loss or gravitational are retained provenance names. The legacy synthetic gate is diagnostic only: unknown inputs are rejected, missing scenario measurements are explicit, and physical correspondence remains unverified. Two original generator cases lack a mapped sensor and therefore remain `insufficient_measurements`.

The 24 operational checks cover quote/model/sensor freshness, spread/depth, units and clock integrity, exposure/concurrency, feed agreement, macro alarms, event duplication, settlement chronology, sales/fills/fees, source integrity, scan errors/liveness, delivery acknowledgments, held-out calibration, missing data and reservation reconciliation. Supplied missing observations stay `unknown`. The numerical thresholds are C0 experimental policy choices; evaluating the comparisons is C1 mechanics. A caller's assertion that a fill or calibration is verified is an input assertion, not independent broker or statistical verification.

Portfolio stress uses linear notional times supplied price shocks, less supplied transaction costs, with an all-cash control. It supports generic stock/sector symbols. It does not price options, liquidation waterfalls, borrow costs or correlated shock probabilities. Minimax search ranks at most 128 supplied alternatives over at most 256 supplied scenarios; it retains a no-action control and seeded random control. A finite optimum depends on those supplied scores, constraints and candidate universe.

Activity counting measures sent-alert events per observed hour, including quiet periods, with local six-hour bands and clipped timezone boundaries. An alert is not a placed bet. Authentic timestamps can support C2 historical counts; no future hourly rate or APY follows from counting.

## CABS and conditional Big-O

Question → typed requirements → measured controls → bounded evaluation → checked receipt.

CABS enumerates compatible typed syntax and composes declared costs. Types do not validate domain meaning. A full ordered binary tree grammar has an untyped denominator proportional to `Catalan(k-1) * r^(k-1) * a^k`, before typing; the actual engine caps atoms at eight, leaves at four, generated candidates at 4096, attempts at 100000 and search time at ten seconds. Beam search may miss solutions. Apriori requires a frozen downward-closed feasibility predicate and an audit; it is not valid for arbitrary truth or accuracy claims. See [CABS_PROTOCOL.md](CABS_PROTOCOL.md).

For the combined operations, conditional time is `O(CABS_search + c + s*p)`, where c is supplied check count, s supplied stress scenarios and p supplied positions. Finite minimax ranking costs `O(a*s + a*log(a))`. Unknown backend costs remain unknown. These are computational bounds, not evidence of financial utility, a universal speedup or an optimum over all possible solutions.

## Original Section 7 expansion

The next twelve labels preserve every original Section 7 proposal. Twelve additional labels ask whether each proposed mechanism can be measured and validated. All 24 are `catalog_only` and C0:

| Family | Original two scenario labels | Added validation work |
|---|---|---|
| AdS/CFT limit-order-book mapping | Bulk Black Hole Horizon Evaporation; Boundary Conformal Symmetry Rupture | Market correspondence and matched null baseline |
| Majorana memory registers | Non-Abelian Anyonic Braiding Phase Decoherence; Topological Gap Collapse | Measured memory overhead and sensor failure |
| Landauer reversible logic | Landauer Thermal Runaway Throttling; Reversible Logic Pipeline Desynchronization | Energy calibration and ordinary-compute comparison |
| Interferometric seismic compensation | Tidal Earth Crust Seismic Strain Drift; Interferometric Reference Arm Phase Squeeze | Measured latency correspondence and cost utility |
| Trans-Earth neutrino communications | Neutrino Detector Scintillation Poisson Jitter; Core-Mantle Density Variation Beam Dispersion | Demonstrated throughput and end-to-end latency |
| Quantum Darwinism equilibrium selection | Environmental Pointer State Decoherence Delay; Quantum Zeno Freezing Trap | Explicit market mapping and untouched null comparison |

The cited physics references in the catalog establish their respective scientific topics; they do not establish a financial advantage. No exotic hardware backend is implemented by this MCP.

## Practical next frontiers

Prioritize evidence-bearing expansions: broker-confirmed buy/sell/settlement replay; actual executable fees and quote depth; untouched chronological calibration and regime-shift evaluation; partial API outages and duplicate delivery; crash-safe reservation/state handling; clock and disk failures; independent feed-spoof controls; stock gaps, halts, delisting and corporate actions; concentration and correlated losses; and nonlinear instrument pricing through a separately checked backend.

For each experiment, freeze an input universe, evaluator, target metric, simpler or no-action baseline, evidence references, C0-C6 ceiling, falsifier, cost/risk budget and stop rule before execution. Observe both gains and abstention/availability costs. Frontier suggestions have at most three declared rounds and do not create background jobs. Stop on a failed control, source drift, no improvement or exhausted budget. A later untouched evaluator is required before asserting improved market performance.

## Install and verify

Python 3.11+ runs the stdlib server. Use the provided default-off templates after replacing placeholder paths with absolute paths. The owner installation stores actual commands privately and registers Codex, OpenCode V2 and both relevant Antigravity config locations. Codex uses `enabled = false`; OpenCode V2 and Antigravity use `disabled: true`. These are local server profiles; plugin/hosted tools have separate lifecycle controls. Official setup references: [Codex MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli), [OpenCode V2 MCP](https://opencode.ai/v2/docs/mcp-servers).

```sh
python -m unittest discover -s scripts -p test_risk_atlas.py -v
python -m unittest discover -s scripts -p test_compositional_search.py -v
python scripts/risk_atlas_mcp.py --profile atlas
python scripts/risk_atlas_mcp.py --profile unified
```

Only enable the smallest profile needed for a task. Close temporary clients, inspect the IDE's MCP state (`/mcp` in Codex, `/mcps` in OpenCode), then restore off. Disk registration, SDK calls, native client discovery and model use are separate receipts. Configured Antigravity requires its own refresh/discovery check. Source/manifest changes invalidate a running atlas until restart; an executable change invalidates the AS3-R pin.

After deliberately reviewing source or registry changes, `python scripts/freeze_risk_atlas_manifest.py --write` refreshes the seven source pins. Rerun controls and restart clients. A freshly written hash manifest alone is not an approval of changed behavior or evidence of financial/scientific utility.

The owner live repair is separately bounded to one demonstrated weekend variable error and best-effort rejection/scan diagnostics. Diagnostics use synchronous output and catch local exceptions; they are not a guarantee of nonblocking IO. New strategy thresholds and speculative mechanisms are not promoted by the repair. Before/after archives include sources and stopped-service state snapshots; source rollback never restores financial ledgers. Public verification receipts contain no private chat contents, host paths, account IDs or credentials.
