"""Freeze a deliberately finite, extensible method ontology; no exhaustiveness claim."""
import json,pathlib,hashlib,datetime as dt
ROOT=pathlib.Path(__file__).resolve().parents[1]
GROUPS={
'formulation':('problem','specification',[('semantic_correspondence','Semantic correspondence audit'),('quantifier_audit','Quantifier and domain audit'),('dimensional_analysis','Dimensional and unit analysis'),('identifiability','Identifiability and observability'),('operationalization','Operational definitions'),('requirements','Constraint and requirement elicitation'),('causal_graph','Causal graph construction'),('decision_theory','Utility and decision framing')]),
'deduction':('proposition','certificate',[('kernel_replay','Formal kernel replay'),('induction','Induction and structural recursion'),('contradiction','Contradiction and contraposition'),('invariants','Invariant and conservation proofs'),('reduction','Reductions and equivalences'),('diagonalization','Diagonalization'),('constructive_witness','Constructive witness'),('proof_search','Resolution and automated proof search'),('model_checking','Finite-state model checking'),('abstract_interpretation','Abstract interpretation')]),
'search':('grammar','candidate',[('apriori','Apriori with proved hereditary predicate'),('cancellation_search','Cancellation-preserving combination search'),('exhaustive','Bounded exhaustive enumeration'),('beam','Beam search'),('branch_bound','Branch and bound'),('dynamic_programming','Dynamic programming'),('constraint_propagation','Constraint propagation'),('sat_smt','SAT and SMT solving'),('cegis','Counterexample-guided synthesis'),('egraph','Equality saturation'),('symmetry_reduction','Symmetry reduction'),('meet_middle','Meet in the middle'),('local_search','Local and tabu search'),('evolutionary','Evolutionary search'),('mcts','Monte Carlo tree search'),('program_synthesis','Typed program synthesis')]),
'algebra':('symbolic','identity',[('exact_arithmetic','Exact rational arithmetic'),('polynomial_identity','Polynomial identity certificates'),('groebner','Groebner basis elimination'),('resultants','Resultants and elimination'),('linear_algebra','Exact linear algebra'),('representation_theory','Representation theoretic decomposition'),('group_actions','Group actions and quotients'),('diophantine','Diophantine descent'),('selmer','Selmer and rank bounds'),('height_pairing','Canonical heights and independence'),('modular','Modular forms and local-global arithmetic')]),
'analysis':('analytic','bound',[('interval','Interval and ball enclosure'),('root_count','Argument principle and zero counts'),('energy_estimates','Energy and coercivity estimates'),('fixed_point','Fixed point and contraction'),('compactness','Compactness and weak convergence'),('regularity','Regularity and bootstrap'),('blowup','Blowup scaling and concentration'),('perturbation','Perturbation and residual correction'),('jets','Jet and all-order smoothness audit'),('spectral','Spectral and operator analysis'),('renormalization','Renormalization and multiscale limits'),('asymptotics','Asymptotic and error estimates'),('computer_assisted','Computer-assisted analytic proof')]),
'geometry':('geometric','geometric_certificate',[('homology','Homology and chain complexes'),('homotopy','Fundamental group and homotopy'),('cycle_class','Cycle class and intersection theory'),('geometric_flow','Geometric flow'),('deformation','Deformation and moduli'),('localization','Localization and sheaf gluing')]),
'optimization':('objective','optimum_bound',[('convex_duality','Convex duality and certificates'),('linear_programming','Linear programming'),('integer_programming','Integer programming'),('semidefinite','Semidefinite and sum of squares'),('optimal_control','Optimal control'),('robust_optimization','Robust optimization'),('pareto','Pareto tradeoffs'),('bayesian_optimization','Bayesian optimization')]),
'empirical':('observations','empirical_estimate',[('randomized_trial','Randomized experiment'),('quasi_experiment','Quasi-experiment'),('causal_identification','Causal identification and adjustment'),('bayesian_inference','Bayesian inference'),('frequentist','Frequentist estimation and tests'),('sequential','Sequential testing'),('active_learning','Active learning and experiment design'),('simulation','Simulation and Monte Carlo'),('ablation','Ablation and negative controls'),('sensitivity','Sensitivity and robustness'),('forecasting','Forecasting with untouched evaluation'),('system_identification','System identification')]),
'engineering':('system','validated_artifact',[('decomposition','Modular decomposition'),('differential_testing','Differential testing'),('property_testing','Property and metamorphic tests'),('fault_injection','Fault injection'),('reproducibility','Pinned reproducible replay'),('provenance','Provenance and evidence ledger'),('adversarial_review','Adversarial review'),('portfolio_routing','Budgeted solver portfolio'),('information_retrieval','Source retrieval and triangulation'),('analogy','Analogy and transfer hypothesis'),('human_review','Independent domain review')])}
SOURCES={
'formulation':['STATEMENT_CORRESPONDENCE.md','https://www.claymath.org/wp-content/uploads/2022/06/navierstokes.pdf'],
'deduction':['https://lean-lang.org/doc/reference/latest/Elaboration-and-Compilation/','https://www.cs.cmu.edu/~odonnell/15455-s17/turing-paper.pdf'],
'search':['sources/stack/run_symbolic_apriori_search.py','https://smt-lib.org/theories.shtml'],
'algebra':['https://doc.sagemath.org/html/en/reference/arithmetic_curves/index.html'],
'analysis':['https://arxiv.org/abs/2609.35406v2','https://flintlib.org/doc/arb.html'],
'geometry':['RESEARCH_AVENUES.md'],
'optimization':['https://web.stanford.edu/~boyd/cvxbook/'],
'empirical':['https://www.pywhy.org/dowhy/v0.13/user_guide/causal_tasks/estimating_causal_effects/index.html'],
'engineering':['https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle','STACK_INTEGRATION.md']}
IMPLEMENTED={'semantic_correspondence','apriori','cancellation_search','exhaustive','beam','exact_arithmetic','polynomial_identity','interval','sat_smt','provenance','portfolio_routing'}
LIMITS={
'semantic_correspondence':'Structured field equality only; not a semantic equivalence prover or Clay-to-Lean adjudicator.',
'apriori':'Rejecting an ancestor is sound only if rejection persists under every permitted extension.',
'cancellation_search':'Finite Laurent polynomial cancellation; no analytic convergence or arbitrary PDE smoothness certificate.',
'beam':'Heuristic incompleteness; exhaustive baseline must retain false-negative evidence.',
'interval':'Exact rational interval operations only; no Arb backend or zeta contour implementation.',
'sat_smt':'Small exhaustive CNF checker only; not a general SMT solver.',
'polynomial_identity':'Restricted exact polynomial grammar only; not arbitrary function equivalence.',
'kernel_replay':'Historical root replay passed; independent checker and correspondence gates remain open.',
'causal_identification':'Observational prediction cannot identify interventions without assumptions.',
'analogy':'A hypothesis generator; analogy does not transfer a proof.',
'selmer':'No descent backend implemented; rational point is not a generator certificate.'}
rows=[]
for group,(inp,out,items) in GROUPS.items():
    for ident,name in items:
        rows.append(dict(id=ident,name=name,family=group,input_type=inp,output_type=out,status='bounded_backend' if ident in IMPLEMENTED else 'catalog_only',claim_ceiling='C1 scoped mechanics' if ident in IMPLEMENTED else 'C0 proposed route',assumptions=['Typed finite task contract','Domain assumptions stated and checked'],certificate=out,falsifier=LIMITS.get(ident,'Independent checker disagreement, missing assumption, or failed negative control.'),budget={'max_candidates':512,'max_rounds':8,'wall_seconds':30},stop_rule='Abstain at cap, unsupported domain, failed certificate or unknown prerequisite.',evidence=SOURCES[group],limits=LIMITS.get(ident,'Catalog entry; specialized solver and independent evaluator still required.')))
catalog={'version':1,'coverage_claim':'Finite seed ontology, not all possible methods or questions','methods':rows,'unexplored':['Noncomputable questions','Undecidable general truth and termination','Unspecified subjective goals','Methods outside this seed taxonomy','Higher-order and stochastic combinations not executed','Specialized backends marked catalog_only']}
import research_mcp as M
for row in rows:
    row['evidence']=[x if x.startswith('https://') else 'README.md' for x in row['evidence']]
    target=M.ADAPTERS.get(row['id'])
    row['status']=('optional_backend' if row['id'] in ['root_count','spectral','selmer'] else 'bounded_backend') if target else 'catalog_only'
    row['claim_ceiling']='C1 scoped mechanics when executed' if target else 'C0 proposed route'
    if target:row['adapter']=target;row['limits']=M.BY[target][0];row['falsifier']='Independent disagreement, failed domain control, or scope exceeded: '+row['limits']
    row['stop_rule']='Abstain at adapter cap (see implementation), unsupported domain, failed certificate or unknown prerequisite.'
out=ROOT/'catalog';out.mkdir(exist_ok=True)
(out/'methods.json').write_text(json.dumps(catalog,indent=2),encoding='utf-8')
md=['# Finite solution-method catalog','','Entries are retrieval/routing contracts. Catalog-only entries are not installed solvers.','Apriori is a search operator; hereditary pruning is a condition on a predicate; semantic correspondence is a validation obligation. They are not interchangeable.','','| ID | Method | Family | Execution status |','|---|---|---|---|']
md += [f"| {r['id']} | {r['name']} | {r['family']} | {r['status']} |" for r in rows]
md+=['','Each machine entry records assumptions, evidence, claim ceiling, certificate, falsifier, budget and stop rule. No enumeration can certify that every future method has been found.']
(ROOT/'METHOD_CATALOG.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps({'methods':len(rows),'families':len(GROUPS),'adapters':sum('adapter' in r for r in rows),'optional_backends':sum(r['status']=='optional_backend' for r in rows)}))
if __name__=='__main__':pass
