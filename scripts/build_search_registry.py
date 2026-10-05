"""Build CABS contracts from literal tool inventories; new tools are unreviewed.

The profiles describe finite development grammars, not scientific achievements.
No source module is imported. Provider identity remains part of every suite ID.
"""
import argparse
import json
import pathlib
from compositional_search import ROOT, discover_source, extend_registry

# tool: (domain, representation, candidate objects, required certificate, gap, cost model)
PROFILES = {
    "method_catalog": ("method_routing", "Typed question and method contracts", "Ontology extensions, method subsets, compatibility edges", "Explicit domain/assumption/backend contract", "Catalog size is not universe coverage", "O(N) in serialized catalog bytes; retrieval only"),
    "route_question": ("method_routing", "Question type, evidence and resource constraints", "Budgeted solver portfolios and typed workflows", "Domain applicability and missing-backend audit", "Selecting a route does not solve its question", "O(N) catalog load plus fixed route; solver costs additional"),
    "symbolic_search": ("symbolic_algebra", "Exact rational polynomial grammar", "Atoms, coefficients, operations and expression trees", "Independent exact normal-form equality", "Beam misses, grammar caps and expression growth", "O(K*r*B^2*C_poly) expansions; coefficient bit cost additional"),
    "check_identity": ("symbolic_algebra", "Restricted exact polynomial AST", "Equivalent forms, substitutions and identity lemmas", "Exact coefficient comparison plus independent evaluations", "An identity does not establish intended domain/analytic meaning", "O(AST expansion + polynomial normal form); expression swell and bit cost explicit"),
    "check_cancellation": ("singular_algebra", "Finite Laurent coefficients and exponents", "Cancellation bundles, coefficients and jet constraints", "Recomputed exact bundle sum and regularity conditions", "Singular atoms can have a regular sum; no termwise pruning", "O(A*T*C_rational); A atoms, T terms; finite polynomial only"),
    "interval_operation": ("certified_numerics", "Rational endpoints with domain constraints", "Interval splits, arithmetic rearrangements and precision choices", "Outward enclosure and denominator exclusion", "Point samples and rational intervals do not prove transcendental bounds", "Constant rational operations per interval; bit complexity additional"),
    "check_finite_cnf": ("finite_logic", "Bounded clauses and Boolean variables", "Clauses, assignments, branching and resolution strategies", "Truth-table witness or exhaustive refutation", "A finite SAT result does not settle asymptotic P versus NP", "O(2^v*m*v) worst-case literal checks; memory O(m*v+v)"),
    "compare_contracts": ("semantic_correspondence", "Explicit domain/quantifier/boundary/regularity fields", "Alternative representations, assumptions and bridge lemmas", "Independent semantic correspondence review", "String field equality is not a theorem of semantic equivalence", "O(N) compared text; mathematical adjudication cost unknown"),
    "audit_pruning": ("pruning_validity", "Frozen predicate over a finite subset lattice", "Predicates, masks and witnessed hereditary rules", "Rejected-parent/accepted-child negative control", "Hereditary validity is restricted to the frozen lattice", "Existing adapter O(4^a); CABS immediate-subset audit O(a*2^a)"),
    "validation_status": ("evidence_gates", "Pinned receipts and their source identities", "Gate definitions, obligations and failure cases", "Raw evidence identity and checker replay", "Reading a receipt is separate from rerunning its validator", "O(N) receipt/log parsing; underlying proof replay excluded"),
    "as3r_symbolic_search": ("symbolic_algebra", "Exact restricted polynomial atoms and target", "Apriori subsets, expression trees and cancellation bundles", "Exact checked hit; exhaustive/random controls", "No invented fallback hits; arbitrary symbolic code is excluded", "O(K*r*B^2*C_poly) plus validation; all caps declared"),
    "audit_complexity_barriers": ("complexity_theory", "Formal proof-technique assumptions", "Reductions, oracle invariants and lower-bound strategies", "Formal barrier hypotheses and independent proof review", "A Boolean checklist cannot certify admissibility or impossibility", "O(1) checklist only; barrier-proof complexity unknown"),
    "check_spectral_gap_continuum": ("continuum_limits", "Grid family, scaling units and limiting quantifiers", "Hamiltonians, scaling laws and candidate uniform bounds", "Certified uniform estimates and continuum construction", "Finite positive gaps can vanish in the limit", "O(G) float evaluations for G grids; not a continuum certificate"),
    "query_epistemic_ledger": ("evidence_gates", "Hash-chained decisions and current receipts", "Evidence graphs, provenance links and promotion gates", "Manifest integrity and independent gate evidence", "A hash chain identifies records; it does not prove their claims", "O(N) scanned ledger bytes; memory O(N) in current implementation"),
    "audit_pde_blowup_scaling": ("pde_regularities", "Dimension, rational exponents and domain restrictions", "Ansatz/scaling/forcing/energy combinations", "Exact exponents plus full PDE and all-order admissibility", "A scaling inequality does not construct a solution", "Constant rational operations per ansatz; symbolic/bit costs additional"),
    "simulate_causal_intervention": ("causal_inference", "Observed/latent DAG, estimand and data assumptions", "Adjustment sets, interventions and identification formulas", "Correct identification proof plus held-out/prospective checks", "Directed reachability is not causal identifiability; legacy checker needs repair", "Simple-path enumeration can be exponential or worse; unknown full cost"),
    "compute_persistent_betti_loops": ("topological_inference", "Simplices, boundary maps and filtration", "Filtrations, complexes, generators and cycle bases", "Independent homology computation and persistence pairing", "Legacy graph-cycle count is not full persistent homology or homotopy", "Graph implementation upper O(v^2+e*v); true persistence matrix reduction differs"),
    "audit_dimensional_consistency": ("units_and_symmetry", "Typed dimensional vectors and expression operations", "Dimensionless products, invariant groups and unit-consistent forms", "Operation-aware dimension propagation", "Adding exponents checks products; addition needs matching dimensions", "O(T*D) dimension-map additions; T terms, D dimensions"),
    "audit_lyapunov_stability": ("dynamical_systems", "Dynamics, domain and candidate Lyapunov functions", "Lyapunov functions, multipliers and region decompositions", "Domain-wide positivity and derivative inequalities", "Finite samples cannot certify global or asymptotic stability", "O(S) legacy sample checks; global certificate generation unknown"),
    "calculate_quantum_fidelity": ("quantum_information", "Normalized pure states or specified density matrices", "States, channels, controls and circuit compositions", "Physical validity, norm checks and independent overlap calculation", "Current adapter covers pure vectors; mixed-state claims need another backend", "O(d) pure-state overlaps; general dense mixed-state algebra typically O(d^3)"),
    "audit_lean_formalization": ("formal_deduction", "Theorem statements, definitions and source pin", "Definitions, tactic/proof graphs and correspondence lemmas", "Real build, axiom closure, independent checker and statement review", "Regex declaration counts are not compiled or proved theorems", "O(N) source scan only; elaboration/kernel cost unmeasured"),
    "run_neural_surrogate_prelim": ("surrogate_learning", "Training data, architecture and untouched evaluation protocol", "Operators, losses, architectures and hyperparameters", "Frozen data split, uncertainty calibration and exact residual checks", "Training loss and cached reports are not scientific discovery or generalization", "Conditional O(E*N*log(N)*channel_cost); actual backend costs unknown"),
    "audit_chemical_reaction_kinetics": ("chemical_models", "Stoichiometry, thermodynamics, rates and units", "Reaction networks, rate laws and equilibrium hypotheses", "Conservation, units, model assumptions and independent experiment", "Scalar thermodynamic/kinetic formulas do not establish a chemical mechanism", "O(1) current scalar formulas; network solving can be stiff and costly"),
    "audit_protein_knot_topology": ("geometric_biology", "Closed curves, structural provenance and error bounds", "Curve topology, linking candidates and conformer combinations", "Certified topology plus independently measured structures", "Numerical linking estimates and synthetic curves are not biological validation", "O(n*m) segment-pair quadrature; certification/error cost additional"),
    "solve_dpll_sat": ("finite_logic", "Validated finite Boolean CNF", "Branch choices, clause learning and witness strategies", "Independent model check or proof-producing UNSAT verifier", "SAT instances are finite; worst-case complexity is not removed by beam search", "Loose O(2^v*m*v) search bound with clause-copy memory overhead"),
    "verify_exact_navier_stokes_solution": ("pde_regularities", "Velocity, pressure, forcing, domain and viscosity", "Ansatz, pressure cancellations and forcing bundles", "Full momentum/divergence/domain/regularity verification", "Legacy adapter samples divergence only and accepts empty samples", "O(S) divergence samples; exact PDE verification not implemented here"),
    "audit_scientific_benchmarks": ("empirical_evaluation", "Retrieved dataset, checksum, task and baseline", "Benchmark tasks, controls, splits and scientific hypotheses", "Real data provenance, held-out scoring and independent evaluation", "Named datasets and hardcoded/model constants do not prove dataset ingestion", "Unknown across heterogeneous benchmark definitions; retain separate task costs"),
    "audit_virtual_cluster_surrogate": ("distributed_computing", "Hardware, communication model and numerical workload", "Partitions, batch sizes, collectives and scheduling policies", "Measured hardware scaling and numerical parity", "CPU partitions cannot establish H100 performance or actual avoided spend", "Conditional compute+communication model; CPU emulation is not GPU timing"),
    "audit_mathlib_pr_readiness": ("software_and_formal_review", "Pinned source, license, build and upstream criteria", "Lemma packages, dependencies and documentation variants", "Successful build/check plus actual upstream review", "Headers and zero sorry text are not community acceptance or proof validity", "O(N) text checklist; build and reviewer time unknown"),
    "certify_elliptic_descent": ("arithmetic_geometry", "Exact curve coefficients and descent assumptions", "Curves, descent choices, Selmer constraints and generators", "Rank bounds, saturation and independent arithmetic replay", "PARI availability and narrow scope; general BSD stays open", "Backend-dependent; no unmeasured Big-O class asserted"),
    "certify_zeta_window": ("analytic_number_theory", "Bounded height windows and ball precision", "Contours, precision choices and enclosure decompositions", "Certified counts and complete root enclosures in the window", "Finite windows cannot establish all-height RH", "Depends on height and precision; backend-dependent"),
    "certify_elliptic_example": ("arithmetic_geometry", "Curve, exact rational point and finite-field primes", "Points, local factors and group-law identities", "Independent exact group law and finite-field census", "Local counts do not establish general rank, saturation or BSD", "O(P*p_max^2) brute-force pair census in unit arithmetic; bit cost extra"),
    "check_chain_complex": ("topological_inference", "Explicit rational chain complex and simplices", "Boundary maps, chain bases and homology witnesses", "Boundary-square zero and independent ranks", "Homology is not simple connectivity or sphere recognition", "O(s^3) dense unit-cost elimination after potentially exponential simplex expansion"),
    "check_product_cycles": ("algebraic_geometry", "Explicit assumed product cohomology ring", "Cycle bases, intersection matrices and relations", "Exact pairing plus theorem connecting model to geometric objects", "Conditional product family only; no general Hodge proof", "Exponential basis growth with factor count; exact bit costs additional"),
    "check_spectral_limit": ("continuum_limits", "Finite chain spectra and ball precision", "Grid/precision/scaling combinations and uniform-bound candidates", "Ball enclosures and separate limit theorem", "Toy chains are not four-dimensional gauge theory", "O(G*C_ball(precision)) for fixed chain formula; backend-dependent"),
    "audit_affine_pde": ("pde_regularities", "Fixed affine ansatz and domain assumptions", "Coefficients, pressure balances and admissibility restrictions", "Exact residual and energy/domain obstruction", "Fixed ansatz rejection does not reject all PDE solutions", "Fixed exact arithmetic count; coefficient bit complexity additional"),
    "execute_method": ("method_routing", "Qualified method contract and bounded arguments", "Applicable adapter choices and workflow compositions", "Adapter-specific certificate or explicit abstention", "Catalog-only methods have no executable adapter", "O(N) lookup plus selected adapter cost; unknown for missing backends"),
    "run_research_loop": ("research_portfolio", "Frozen domain tasks, controls and budget", "Question portfolios, adapter chains and remaining obligations", "Per-task receipts and final negative-control sweep", "Finite loop exhaustion does not exhaust research or possible questions", "Sum of selected domain adapter costs across bounded rounds"),
    "backend_capabilities": ("capability_inventory", "Current runtime and dependency state", "Task-scoped provider profiles and adapter inventories", "Actual handshake and positive/negative tool calls", "Static names do not establish live IDE discovery", "Fixed inventory/probe overhead; import/runtime costs conditional")}


# Conservative annotations for the narrow operations whose loop structure is known.
# These remain C0 upper-bound models, with mathematical meaning excluded.
ANNOTATIONS = {
    "method_catalog": ({"n": 1}, {"n": 1}),
    "route_question": ({"n": 1}, {"n": 1}),
    "check_finite_cnf": ({"exp_n": 1, "m": 1, "n": 1}, {"m": 1, "n": 1}),
    "compare_contracts": ({"n": 1}, {"n": 1}),
    "query_epistemic_ledger": ({"n": 1}, {"n": 1}),
    "audit_dimensional_consistency": ({"n": 1, "d": 1}, {"d": 1}),
    "audit_lyapunov_stability": ({"n": 1}, {"n": 1}),
    "calculate_quantum_fidelity": ({"n": 1}, {"n": 1}),
    "audit_lean_formalization": ({"n": 1}, {"n": 1}),
    "audit_mathlib_pr_readiness": ({"n": 1}, {"n": 1})}


def reviewed_profile(provider, name, source_sha256):
    if name not in PROFILES:
        return None
    domain, representation, candidates, certificate, gap, formula = PROFILES[name]
    time_cost = space_cost = None
    if name in ANNOTATIONS:
        a, b = ANNOTATIONS[name]
        time_cost, space_cost = {"terms": [a]}, {"terms": [b]}
    return {"id": provider + "::" + name, "name": name, "domain": domain,
            "status": "reviewed_contract", "search_variant": "CABS[" + domain + ":" + name + "]",
            "input_representation": representation, "candidate_objects": candidates,
            "certificate": certificate, "falsifier": "Failed independent check, false positive control, missing assumption or exceeded domain",
            "limits": gap, "time": time_cost, "space": space_cost,
            "cost_formula": formula, "cost_ceiling": "C0 conditional operation-count model",
            "time_variables": "n/m/d must be bound to the stated input sizes for each task; no common cross-domain scale assumed",
            "source_sha256": source_sha256, "domain_evaluator_verified": False,
            "stop_rule": "Finite grammar, 4096 candidates, 4 leaves, 10 seconds; stop on negative-control failure",
            "claim_ceiling": "C0 development grammar; C1 only for exercised engine mechanics"}


def build(sources):
    registry = {"name": "AxiomWeave-CABS", "version": 1, "suites": [],
                "coverage_claim": "Only explicitly inventoried providers; open to new problem domains and dimensions",
                "all_possible_questions_covered": False}
    inventories = []
    for provider, path in sources:
        inv = discover_source(path, provider)
        inventories.append(inv)
        registry, _ = extend_registry(registry, inv)
        known = {r["id"]: r for r in registry["suites"]}
        for name in inv["tool_names"]:
            profile = reviewed_profile(provider, name, inv["source_sha256"])
            if profile is not None:
                known[profile["id"]] = profile
        registry["suites"] = list(known.values())
    registry["inventories"] = inventories
    return registry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", nargs=2, metavar=("PROVIDER", "FILE"))
    parser.add_argument("--output", type=pathlib.Path, default=ROOT / "catalog/search_suites.json")
    args = parser.parse_args()
    sources = args.source or [("research", ROOT / "scripts/research_mcp.py")]
    registry = build(sources)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"suite_contracts": len(registry["suites"]),
                      "providers": sorted({r["id"].split("::")[0] for r in registry["suites"]}),
                      "unreviewed": sum(r["status"] == "unreviewed" for r in registry["suites"]),
                      "all_possible_questions_covered": False}))


if __name__ == "__main__":
    main()
