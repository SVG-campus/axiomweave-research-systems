"""Bounded, exact research primitives. No eval, shell, network or dynamic imports."""
import ast,itertools,json,pathlib
from fractions import Fraction as F
ROOT=pathlib.Path(__file__).resolve().parents[1]
VARS=('a','b','t');ZERO=(0,0,0)
def integer(x,lo,hi):
    if type(x)!=int or not lo<=x<=hi:raise ValueError('Integer outside bounded domain')
    return x
def rational(x):
    if type(x) not in (str,int) or len(str(x))>80:raise ValueError('Bounded exact rational required')
    y=F(x)
    if max(abs(y.numerator).bit_length(),y.denominator.bit_length())>128:raise ValueError('Rational too large')
    return y
def clean(p):
    p={k:v for k,v in p.items() if v}
    if len(p)>64 or any(sum(k)>16 or max(abs(v.numerator).bit_length(),v.denominator.bit_length())>256 for k,v in p.items()):raise ValueError('Polynomial cap exceeded')
    return p
def add(p,q,sign=1):
    r=p.copy()
    for k,v in q.items():r[k]=r.get(k,F(0))+sign*v
    return clean(r)
def mul(p,q):
    r={}
    for k,v in p.items():
        for l,w in q.items():
            m=tuple(x+y for x,y in zip(k,l));r[m]=r.get(m,F(0))+v*w
    return clean(r)
def parse(text):
    if not isinstance(text,str) or not 1<=len(text)<=256:raise ValueError('Expression length cap')
    tree=ast.parse(text,mode='eval')
    if len(list(ast.walk(tree)))>80:raise ValueError('AST cap')
    def visit(n):
        if isinstance(n,ast.Constant) and type(n.value)==int:return clean({ZERO:rational(n.value)})
        if isinstance(n,ast.Name) and n.id in VARS:
            return {tuple(int(x==n.id) for x in VARS):F(1)}
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.UAdd,ast.USub)):
            return {k:(-v if isinstance(n.op,ast.USub) else v) for k,v in visit(n.operand).items()}
        if isinstance(n,ast.BinOp):
            if isinstance(n.op,ast.Pow):
                if not isinstance(n.right,ast.Constant):raise ValueError('Literal exponent required')
                e=integer(n.right.value,0,8);p=visit(n.left);r={ZERO:F(1)}
                for _ in range(e):r=mul(r,p)
                return r
            p,q=visit(n.left),visit(n.right)
            if isinstance(n.op,ast.Add):return add(p,q)
            if isinstance(n.op,ast.Sub):return add(p,q,-1)
            if isinstance(n.op,ast.Mult):return mul(p,q)
            if isinstance(n.op,ast.Div) and set(q)=={ZERO}:
                return clean({k:v/q[ZERO] for k,v in p.items()})
        raise ValueError('Only bounded polynomial syntax and division by nonzero rational constants supported')
    return visit(tree.body)
def encode(p):return [[list(k),str(v)] for k,v in sorted(p.items())]
def residual(p,q):return sum(abs(x) for x in add(p,q,-1).values())
def symbolic(args):
    atoms=args.get('atoms',['0','a','b','2*a','2*b','3*a','3*b'])
    if not isinstance(atoms,list) or not 1<=len(atoms)<=12:raise ValueError('Atom cap1..12')
    pool=[(x,parse(x)) for x in atoms];target=parse(args['target']);cap=integer(args.get('max_candidates',512),1,512)
    beam=integer(args.get('beam_width',len(pool)),1,12);depth=integer(args.get('max_depth',1),1,2)
    ops=args.get('operations',['add','sub','mul'])
    if not isinstance(ops,list) or not ops or len(set(ops))!=len(ops) or any(x not in ['add','sub','mul'] for x in ops):raise ValueError('Invalid operation set')
    pool=sorted(pool,key=lambda x:(residual(x[1],target),x[0]))[:beam]
    truncated=len(pool)>cap;pool=pool[:cap]
    candidates=list(pool);used=len(pool);hits=[]
    funcs={'add':(add,'+'),'sub':(lambda p,q:add(p,q,-1),'-'),'mul':(mul,'*')}
    for _ in range(depth):
        new=[]
        for (x,p),(y,q),op in itertools.product(pool,pool,ops):
            if used>=cap:truncated=True;break
            fn,sym=funcs[op];new.append((f'({x}){sym}({y})',fn(p,q)));used+=1
        candidates+=new
        pool=sorted(candidates,key=lambda x:(residual(x[1],target),x[0]))[:beam]
        if truncated:break
    for x,p in candidates:
        if p==target:hits.append({'expression':x,'normal_form':encode(p)})
    best=min(candidates,key=lambda x:(residual(x[1],target),x[0]))
    return {'claim_ceiling':'C1 exact finite grammar','candidates':used,'truncated':truncated,'beam_width':beam,'operations':ops,'exact_hits':hits[:16],'best_expression':best[0],'exact_residual':str(residual(best[1],target)),'target_normal_form':encode(target),'universal_proof':False,'completeness':'Only generated candidates; beam and cap can omit valid expressions'}
def identity(args):
    p,q=parse(args['left']),parse(args['right'])
    return {'equal_within_polynomial_domain':p==q,'left':encode(p),'right':encode(q),'claim_ceiling':'C1 exact polynomial identity','analytic_extension_proved':False}
def cancellation(args):
    terms=args['terms']
    if not isinstance(terms,list) or not 1<=len(terms)<=32:raise ValueError('Term cap')
    result={};singular=[]
    for i,term in enumerate(terms):
        if not isinstance(term,list) or not 1<=len(term)<=32:raise ValueError('Laurent term cap')
        p={}
        for entry in term:
            if not isinstance(entry,list) or len(entry)!=2:raise ValueError('Expected exponent, rational pair')
            e=integer(entry[0],-16,16);p[e]=p.get(e,F(0))+rational(entry[1])
        p={e:v for e,v in p.items() if v}
        if any(e<0 for e in p):singular.append(i)
        for e,v in p.items():result[e]=result.get(e,F(0))+v
    result={e:v for e,v in result.items() if v}
    return {'sum':[[e,str(v)] for e,v in sorted(result.items())],'singular_terms':singular,'finite_laurent_sum_extends_smoothly_at_zero':all(e>=0 for e in result),'termwise_singularity_pruning_sound':False,'claim_ceiling':'C1 finite Laurent polynomial','infinite_series_convergence_proved':False}
def interval(args):
    def bounds(x):
        if not isinstance(x,list) or len(x)!=2:raise ValueError('Two endpoints required')
        a,b=map(rational,x)
        if a>b:raise ValueError('Reversed interval')
        return a,b
    a,b=bounds(args['left']);c,d=bounds(args['right']);op=args['operation']
    if op=='add':lo,hi=a+c,b+d
    elif op=='sub':lo,hi=a-d,b-c
    elif op=='mul':v=[a*c,a*d,b*c,b*d];lo,hi=min(v),max(v)
    elif op=='div':
        if c<=0<=d:raise ValueError('Denominator interval contains zero')
        v=[a/c,a/d,b/c,b/d];lo,hi=min(v),max(v)
    else:raise ValueError('Unsupported interval operation')
    return {'enclosure':[str(lo),str(hi)],'claim_ceiling':'C1 rational interval enclosure','zeta_zero_count_proved':False}
def sat(args):
    n=integer(args['variables'],1,8);clauses=args['clauses']
    if not isinstance(clauses,list) or len(clauses)>64:raise ValueError('Clause cap')
    for clause in clauses:
        if not isinstance(clause,list) or len(clause)>16:raise ValueError('Clause size cap')
        for lit in clause:
            integer(lit,-n,n)
            if lit==0:raise ValueError('Literal zero')
    def holds(bits):return all(any(bits[abs(x)-1]==(x>0) for x in cl) for cl in clauses)
    assignments=list(itertools.product([False,True],repeat=n));w=next((x for x in assignments if holds(x)),None)
    return {'sat':w is not None,'witness':list(w) if w is not None else None,'assignments_checked':len(assignments),'certificate_scope':f'exactly {n} variables and supplied CNF','claim_ceiling':'C1 finite exhaustive decision','p_vs_np_resolved':False}
FIELDS={'domain','quantifiers','boundary','regularity','forcing','energy','conclusion'}
def correspondence(args):
    r,s=args['reference'],args['submission']
    if not isinstance(r,dict) or not isinstance(s,dict) or set(r)!=FIELDS or set(s)!=FIELDS:raise ValueError('All seven contract fields required')
    if any(not isinstance(x,str) or not x.strip() or len(x)>500 for x in list(r.values())+list(s.values())):raise ValueError('Nonempty bounded contract fields required')
    differences=[k for k in sorted(FIELDS) if r[k]!=s[k]]
    return {'field_match':not differences,'differences':differences,'semantic_equivalence_proved':False,'independent_math_review_required':True,'claim_ceiling':'C1 structured contract comparison'}
def pruning(args):
    n=integer(args['atoms'],1,8);accepted=args['accepted_masks']
    if not isinstance(accepted,list) or len(accepted)>256:raise ValueError('Mask cap')
    accepted={integer(x,0,(1<<n)-1) for x in accepted}
    violation=next(((p,c) for c in sorted(accepted) for p in range(1<<n) if p&c==p and p not in accepted),None)
    return {'rejection_hereditary_on_frozen_lattice':violation is None,'counterexample_parent_child':violation,'coverage_masks':1<<n,'outside_lattice_proved':False,'claim_ceiling':'C1 complete finite subset lattice'}
ROUTES={
'pde':['semantic_correspondence','cancellation_search','energy_estimates','jets','kernel_replay','human_review'],
'number_theory':['exact_arithmetic','interval','root_count','kernel_replay','human_review'],
'complexity':['quantifier_audit','reduction','sat_smt','diagonalization','human_review'],
'arithmetic_geometry':['diophantine','selmer','height_pairing','modular','human_review'],
'topology':['homology','homotopy','geometric_flow','human_review'],
'algebraic_geometry':['cycle_class','linear_algebra','deformation','human_review'],
'quantum_field':['spectral','renormalization','compactness','human_review'],
'optimization':['requirements','convex_duality','branch_bound','robust_optimization'],
'causal':['causal_graph','causal_identification','randomized_trial','sensitivity'],
'prediction':['forecasting','frequentist','ablation','sensitivity'],
'software':['requirements','decomposition','property_testing','differential_testing'],
'decision':['decision_theory','pareto','robust_optimization','human_review'],
'symbolic':['apriori','cancellation_search','polynomial_identity','exhaustive'],
'unknown':['operationalization','information_retrieval','human_review']}
def catalog():return json.loads((ROOT/'catalog/methods.json').read_text(encoding='utf-8'))
def route(args):
    kind=args.get('question_type','unknown')
    if kind not in ROUTES:raise ValueError('Unknown question_type; use unknown')
    by={m['id']:m for m in catalog()['methods']};ids=ROUTES[kind]
    return {'route':[by[x] for x in ids],'question_type':kind,'unsupported_backends':[x for x in ids if by[x]['status']=='catalog_only'],'autonomous_solution_guaranteed':False,'claim_ceiling':'C0 proposed bounded portfolio'}
