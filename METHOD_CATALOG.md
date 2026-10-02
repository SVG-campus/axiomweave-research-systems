# Finite solution-method catalog

Entries are retrieval/routing contracts. Catalog-only entries are not installed solvers.
Apriori is a search operator; hereditary pruning is a condition on a predicate; semantic correspondence is a validation obligation. They are not interchangeable.

| ID | Method | Family | Execution status |
|---|---|---|---|
| semantic_correspondence | Semantic correspondence audit | formulation | bounded_backend |
| quantifier_audit | Quantifier and domain audit | formulation | catalog_only |
| dimensional_analysis | Dimensional and unit analysis | formulation | catalog_only |
| identifiability | Identifiability and observability | formulation | catalog_only |
| operationalization | Operational definitions | formulation | catalog_only |
| requirements | Constraint and requirement elicitation | formulation | catalog_only |
| causal_graph | Causal graph construction | formulation | catalog_only |
| decision_theory | Utility and decision framing | formulation | catalog_only |
| kernel_replay | Formal kernel replay | deduction | catalog_only |
| induction | Induction and structural recursion | deduction | catalog_only |
| contradiction | Contradiction and contraposition | deduction | catalog_only |
| invariants | Invariant and conservation proofs | deduction | catalog_only |
| reduction | Reductions and equivalences | deduction | catalog_only |
| diagonalization | Diagonalization | deduction | catalog_only |
| constructive_witness | Constructive witness | deduction | catalog_only |
| proof_search | Resolution and automated proof search | deduction | catalog_only |
| model_checking | Finite-state model checking | deduction | catalog_only |
| abstract_interpretation | Abstract interpretation | deduction | catalog_only |
| apriori | Apriori with proved hereditary predicate | search | bounded_backend |
| cancellation_search | Cancellation-preserving combination search | search | bounded_backend |
| exhaustive | Bounded exhaustive enumeration | search | bounded_backend |
| beam | Beam search | search | bounded_backend |
| branch_bound | Branch and bound | search | catalog_only |
| dynamic_programming | Dynamic programming | search | catalog_only |
| constraint_propagation | Constraint propagation | search | catalog_only |
| sat_smt | SAT and SMT solving | search | bounded_backend |
| cegis | Counterexample-guided synthesis | search | catalog_only |
| egraph | Equality saturation | search | catalog_only |
| symmetry_reduction | Symmetry reduction | search | catalog_only |
| meet_middle | Meet in the middle | search | catalog_only |
| local_search | Local and tabu search | search | catalog_only |
| evolutionary | Evolutionary search | search | catalog_only |
| mcts | Monte Carlo tree search | search | catalog_only |
| program_synthesis | Typed program synthesis | search | catalog_only |
| exact_arithmetic | Exact rational arithmetic | algebra | bounded_backend |
| polynomial_identity | Polynomial identity certificates | algebra | bounded_backend |
| groebner | Groebner basis elimination | algebra | catalog_only |
| resultants | Resultants and elimination | algebra | catalog_only |
| linear_algebra | Exact linear algebra | algebra | catalog_only |
| representation_theory | Representation theoretic decomposition | algebra | catalog_only |
| group_actions | Group actions and quotients | algebra | catalog_only |
| diophantine | Diophantine descent | algebra | bounded_backend |
| selmer | Selmer and rank bounds | algebra | optional_backend |
| height_pairing | Canonical heights and independence | algebra | catalog_only |
| modular | Modular forms and local-global arithmetic | algebra | catalog_only |
| interval | Interval and ball enclosure | analysis | bounded_backend |
| root_count | Argument principle and zero counts | analysis | optional_backend |
| energy_estimates | Energy and coercivity estimates | analysis | bounded_backend |
| fixed_point | Fixed point and contraction | analysis | catalog_only |
| compactness | Compactness and weak convergence | analysis | catalog_only |
| regularity | Regularity and bootstrap | analysis | catalog_only |
| blowup | Blowup scaling and concentration | analysis | catalog_only |
| perturbation | Perturbation and residual correction | analysis | catalog_only |
| jets | Jet and all-order smoothness audit | analysis | catalog_only |
| spectral | Spectral and operator analysis | analysis | optional_backend |
| renormalization | Renormalization and multiscale limits | analysis | catalog_only |
| asymptotics | Asymptotic and error estimates | analysis | catalog_only |
| computer_assisted | Computer-assisted analytic proof | analysis | catalog_only |
| homology | Homology and chain complexes | geometry | bounded_backend |
| homotopy | Fundamental group and homotopy | geometry | catalog_only |
| cycle_class | Cycle class and intersection theory | geometry | bounded_backend |
| geometric_flow | Geometric flow | geometry | catalog_only |
| deformation | Deformation and moduli | geometry | catalog_only |
| localization | Localization and sheaf gluing | geometry | catalog_only |
| convex_duality | Convex duality and certificates | optimization | catalog_only |
| linear_programming | Linear programming | optimization | catalog_only |
| integer_programming | Integer programming | optimization | catalog_only |
| semidefinite | Semidefinite and sum of squares | optimization | catalog_only |
| optimal_control | Optimal control | optimization | catalog_only |
| robust_optimization | Robust optimization | optimization | catalog_only |
| pareto | Pareto tradeoffs | optimization | catalog_only |
| bayesian_optimization | Bayesian optimization | optimization | catalog_only |
| randomized_trial | Randomized experiment | empirical | catalog_only |
| quasi_experiment | Quasi-experiment | empirical | catalog_only |
| causal_identification | Causal identification and adjustment | empirical | catalog_only |
| bayesian_inference | Bayesian inference | empirical | catalog_only |
| frequentist | Frequentist estimation and tests | empirical | catalog_only |
| sequential | Sequential testing | empirical | catalog_only |
| active_learning | Active learning and experiment design | empirical | catalog_only |
| simulation | Simulation and Monte Carlo | empirical | catalog_only |
| ablation | Ablation and negative controls | empirical | catalog_only |
| sensitivity | Sensitivity and robustness | empirical | catalog_only |
| forecasting | Forecasting with untouched evaluation | empirical | catalog_only |
| system_identification | System identification | empirical | catalog_only |
| decomposition | Modular decomposition | engineering | catalog_only |
| differential_testing | Differential testing | engineering | catalog_only |
| property_testing | Property and metamorphic tests | engineering | catalog_only |
| fault_injection | Fault injection | engineering | catalog_only |
| reproducibility | Pinned reproducible replay | engineering | catalog_only |
| provenance | Provenance and evidence ledger | engineering | catalog_only |
| adversarial_review | Adversarial review | engineering | catalog_only |
| portfolio_routing | Budgeted solver portfolio | engineering | bounded_backend |
| information_retrieval | Source retrieval and triangulation | engineering | catalog_only |
| analogy | Analogy and transfer hypothesis | engineering | catalog_only |
| human_review | Independent domain review | engineering | catalog_only |

Each machine entry records assumptions, evidence, claim ceiling, certificate, falsifier, budget and stop rule. No enumeration can certify that every future method has been found.
