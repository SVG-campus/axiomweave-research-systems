# AxiomWeave-CABS

**Compositional Apriori-Beam Symbolic Search**, with conditional Big-O accounting.
The objective is open-ended research across problem domains, representations and
dimensions. Millennium problems supplied initial examples, not the universe.

A question becomes a typed contract: meaning, dimensions, assumptions, candidate
grammar, objectives, constraints, evaluator, certificate, cost variables, authority
and stop rule. [catalog/problem_space.json](catalog/problem_space.json) is an open
multi-axis schema. Its examples are neither an exhaustive ontology nor validated
solvers for those domains.

## Implemented scope

* Typed, ordered binary workflow compositions using `sequence` and `portfolio`.
  The exact finite denominator counts compatible syntax trees, including both
  bracketings and repeated atoms. Capability labels express proposed operations;
  they do not establish that a scientific backend exists.
* Exact rational Laurent subset combinations with exhaustive, seeded random,
  beam and audited Apriori policies. Pair lookahead can preserve finite
  cancellations missed by a narrow beam. It does not make beam search complete.
* Conditional cost algebra: sequences add costs; nested operations multiply them;
  portfolios use a conservative serial bound. Time and memory are separate.
  Nonnegative multivariate terms use conservative componentwise dominance.
  `pow_n_d` means `n^d` and remains incomparable to `n^constant` without a bound on d.
  Unknown costs propagate and cannot dominate known costs by pretending to be zero.
* Literal source inventory without executing source. A new tool gets an
  `unreviewed` contract with unknown cost and a missing evaluator. Changed provider
  source invalidates its earlier review state on an inventory refresh. Dynamic
  declarations are reported as unresolved. This is source inventory, not runtime
  discovery, background monitoring, or automatic domain implementation.
* Per-section development profiles with representations, candidate objects,
  certificate obligations, negative controls and conditional complexity formulas.

The default portable registry has the public provider's 21 sections. Other
providers are supplied explicitly, preserving qualified identities such as
`research::check_identity` and `legacy::check_identity`. Custom typed tasks can
describe domains not present in either provider. New methods need a real evaluator
before they can be assessed as solutions.

## Reproduce

From this repository, using Python 3.11+:

```sh
python scripts/build_search_registry.py
python -m unittest discover -s scripts -p 'test*.py' -v
python scripts/compositional_search.py search --suite research::check_identity
python scripts/compositional_search.py search --mode subsets --task examples/cabs/cancellation.json
python scripts/compositional_search.py search --mode subsets --task examples/cabs/apriori.json
python scripts/compositional_search.py search --task examples/cabs/general_problem.json
python scripts/cabs_mcp.py
```

To register future literal tools without importing their code:

```sh
python scripts/compositional_search.py inventory --source new_provider.py --provider new_domain --output new_registry.json
python scripts/compositional_search.py search --registry new_registry.json --suite new_domain::new_tool
python scripts/cabs_mcp.py --registry new_registry.json
```

For multiple sources, repeat `--source PROVIDER FILE` with
`scripts/build_search_registry.py`. Use the same provider only when those files
really contribute to the same server. Distinct implementations retain distinct IDs.

MCP server name: **`axiomweave-cabs`**. Tools: `cabs_catalog`, `cabs_search`,
`cabs_compose_costs`. A default-off template is in
[configs/cabs-default-off.toml](configs/cabs-default-off.toml). The server is not
automatically registered or enabled in any IDE. The live client must separately
show discovery and pass actual calls. Close temporary clients and retain `off`.

Suggested query:

> Use AxiomWeave-CABS to frame this question across its relevant dimensions,
> generate compatible symbolic/workflow combinations, select audited Apriori or
> a bounded beam, compose conditional time and memory costs, compare exhaustive
> and random controls, and return checked certificates and uncovered space.

## Complexity and coverage

Let a be atom count, k maximum leaves/items, r binary operators, b beam width, and
C_eval the evaluator cost including exact arithmetic, proof checks and data access.

| Search | Conditional operation-count bound | Limit |
|---|---|---|
| Subsets, unrestricted | O(a 2^a C_rational) | Finite 8-atom cap in this implementation |
| Subsets up to k | Number of subsets is sum(j=0..k) binomial(a,j) | Ordered plans have a different denominator |
| Ordered binary trees with k leaves | Catalan(k-1) r^(k-1) a^k before typing | Types may reject many combinations |
| Binary workflow beam | O(k^2 b^2 r C_eval), plus ranking/sorting | Can miss a known valid pipeline |
| Subset beam | O(k b a C_eval), plus sorting | Optional pair lookahead adds O(a^2 C_eval) |
| Audited Apriori | Feasible subset search plus O(a 2^a) finite predicate audit | No universal speedup or soundness outside that lattice |
| d-dimensional full grid, q choices each | O(q^d C_eval) | Explicit dimensionality; no general escape from this growth |

The current limits are 8 atoms, 4 plan leaves, 4096 generated plans, 100000 attempted
compositions and 10 seconds per plan search; exact subsets use at most 256 masks.
Costs attached to suite contracts are C0 annotations, with units/bit precision
stated before comparison. Computational Big-O is separate from Laurent physical
scaling, sample complexity, communication cost and scientific validity.

Apriori pruning requires a complete frozen feasibility table and an audit that
each accepted child has its immediate subsets accepted. A missing or failed audit
rejects the Apriori request. Accuracy, truth, semantic validity, cancellation and
residual improvements are not assumed hereditary. The classic subset premise is
described in [Agrawal and Srikant's original paper](https://rsrikant.com/papers/vldb94.pdf).

Finite syntax coverage, registered sections, executed scientific backends and
independently settled questions have different denominators. None measures a
percentage of every possible question. In the general case, deciding every
expressible problem is impossible; see [Turing's decision-problem paper](https://londmathsoc.onlinelibrary.wiley.com/doi/abs/10.1112/plms/s2-42.1.230).

## Develop another section

1. Define its intended meaning and input domain, including open/infinite dimensions.
2. Supply finite typed atoms and allowed combinations. Keep ordered workflows
   distinct from commutative subsets.
3. Supply a real evaluator, an independently implemented checker, and negative
   controls. Missing backend or missing correspondence remains an open gate.
4. Bind cost variables to input sizes. Include coefficient bits, precision, data
   access, memory and communication. Retain unknown costs instead of inventing them.
5. Freeze a finite protocol. Run exhaustive/random controls before using a beam;
   audit the actual predicate before Apriori. Stop on a failed negative control.
6. Expand only the declared grammar for at most three rounds, then sweep its known
   universe. Freeze a new version when adding an axis/method. Preserve old receipts.
7. Use held-out and independent adjudication before utility or scientific promotion.

C0: section grammars and domain plans. C1: executed finite type, cost and exact
algebra controls. No held-out superiority, new general theorem, universal coverage,
model-weight change, operational authority or domain-independent truth score is claimed.
