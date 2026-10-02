"""Scoped domain certificates. Optional numerical backend never silently degrades."""
import itertools,math,json,pathlib,shutil,subprocess
from fractions import Fraction as F
import research_systems as R
def flint_backend():
    try:
        import flint
        return flint
    except ImportError:return None
def unavailable(name):return {'status':'backend_unavailable','backend':name,'abstain':True,'universal_proof':False}
def zeta(args):
    heights=args.get('heights',[15,30,50,100]);prec=R.integer(args.get('precision_bits',128),64,512)
    if not isinstance(heights,list) or not 1<=len(heights)<=8:raise ValueError('Height list cap1..8')
    heights=[R.integer(h,1,200) for h in heights]
    f=flint_backend()
    if f is None:return unavailable('python-flint==0.9.0')
    old=f.ctx.prec;f.ctx.prec=prec
    try:
        rows=[]
        for h in heights:
            count_ball=f.arb(h).zeta_nzeros();n=count_ball.unique_fmpz()
            if n is None:rows.append({'height':h,'count_ball':str(count_ball),'abstain':True});continue
            n=int(n);R.integer(n,0,64);zeros=[f.acb.zeta_zero(i) for i in range(1,n+1)]
            line=all(z.real.is_exact() and z.real==f.arb(1)/2 for z in zeros)
            enclosed=all(z.imag>0 and z.imag<h for z in zeros)
            disjoint=all(zeros[i].imag<zeros[i+1].imag for i in range(len(zeros)-1))
            residuals=all(z.zeta().contains(0) for z in zeros)
            rows.append({'height':h,'certified_total_count':n,'count_ball':str(count_ball),'distinct_line_root_enclosures':len(zeros),'all_real_parts_exact_half':line,'within_height':enclosed,'disjoint':disjoint,'residual_enclosures_contain_zero':residuals,'bounded_consistency_check':line and enclosed and disjoint and residuals,'zero_enclosures':[str(z) for z in zeros],'abstain':False})
        ambiguous=f.arb('14.1 +/- 0.1').zeta_nzeros().unique_fmpz()
        return {'status':'executed','backend_version':f.__version__,'precision_bits':prec,'rows':rows,'ambiguous_height_negative_control':ambiguous is None,'trust_assumptions':['FLINT/Arb implementation and documented zero/count guarantees','Hardware and integer/ball arithmetic'],'claim_ceiling':'C1 bounded certified-library execution','global_RH_proved':False,'independent_kernel_certificate':False}
    finally:f.ctx.prec=old
def spectral(args):
    sizes=args.get('grid_sizes',[8,16,32,64,128]);prec=R.integer(args.get('precision_bits',128),64,512)
    if not isinstance(sizes,list) or not 2<=len(sizes)<=12:raise ValueError('2..12grid sizes required')
    sizes=[R.integer(n,2,4096) for n in sizes]
    if sizes!=sorted(set(sizes)):raise ValueError('Strictly increasing sizes required')
    f=flint_backend()
    if f is None:return unavailable('python-flint==0.9.0')
    old=f.ctx.prec;f.ctx.prec=prec
    try:
        rows=[]
        for n in sizes:
            gap=4*(f.arb.pi()/(2*(n+1))).sin()**2
            upper=f.arb.pi()**2/(n+1)**2
            rows.append({'N':n,'gap_ball':str(gap),'positive_certified':gap>0,'scaled_gap_ball':str(gap*(n+1)**2),'analytic_upper_bound_ball':str(upper),'bound_assumption':'sin(x)<=x for x>=0'})
        return {'status':'executed','model':'1DDirichlet chain, not gauge theory','rows':rows,'unscaled_limit_zero_argument':'0<gap_N<=pi^2/(N+1)^2; squeeze theorem','scaled_limit':'pi^2 by sin(x)/x->1','continuum_yang_mills_mass_gap_proved':False,'claim_ceiling':'C1 ball-enclosed finite spectra and known toy limit argument'}
    finally:f.ctx.prec=old
def elliptic(args):
    a=R.integer(args.get('A',0),-1000,1000);b=R.integer(args.get('B',-2),-1000,1000)
    if 4*a**3+27*b*b==0:raise ValueError('Singular curve')
    point=args.get('point',['3','5'])
    if not isinstance(point,list) or len(point)!=2:raise ValueError('Two rational coordinates required')
    x,y=map(R.rational,point)
    if y*y!=x*x*x+a*x+b:raise ValueError('Point not on curve')
    if y==0:double=None
    else:
        slope=(3*x*x+a)/(2*y);xx=slope*slope-2*x;yy=slope*(x-xx)-y
        assert yy*yy==xx**3+a*xx+b;double=[str(xx),str(yy)]
    nonintegral=double is not None and any(F(v).denominator!=1 for v in double)
    primes=args.get('primes',[5,7,11,13,17,19,23,29,31])
    if not isinstance(primes,list) or not 1<=len(primes)<=32:raise ValueError('Prime list cap')
    rows=[]
    for p in primes:
        R.integer(p,3,251)
        if any(p%d==0 for d in range(2,math.isqrt(p)+1)):raise ValueError('Composite prime input')
        if (4*a**3+27*b*b)%p==0:raise ValueError('Bad-reduction prime')
        count=1+sum((yy*yy-xx**3-a*xx-b)%p==0 for xx,yy in itertools.product(range(p),repeat=2))
        squares={yy*yy%p for yy in range(p)}
        count2=1+sum(1 if (v:=(xx**3+a*xx+b)%p)==0 else 2 if v in squares else 0 for xx in range(p))
        assert count==count2 and (p+1-count)**2<=4*p
        rows.append({'p':p,'points':count,'trace':p+1-count,'two_counting_methods_agree':True})
    return {'status':'executed','curve':{'A':a,'B':b},'point':[str(x),str(y)],'double':double,'nonintegral_double':nonintegral,'rank_lower_bound_at_least_one_under_lutz_nagell':nonintegral,'theorem_assumptions':['Integral nonsingular short Weierstrass model','Every rational torsion point has integral coordinates (Lutz-Nagell)','If P is torsion then2P is torsion or infinity'],'generator_or_rank_upper_bound_proved':False,'bsd_proved':False,'local_factors':rows,'claim_ceiling':'C1 exact arithmetic certificate plus explicitly cited theorem inference'}
def rank(matrix):
    if not matrix:return 0
    a=[list(map(F,row)) for row in matrix];r=0
    for c in range(len(a[0])):
        pivot=next((i for i in range(r,len(a)) if a[i][c]),None)
        if pivot is None:continue
        a[r],a[pivot]=a[pivot],a[r];v=a[r][c];a[r]=[x/v for x in a[r]]
        for i in range(len(a)):
            if i!=r and a[i][c]:
                v=a[i][c];a[i]=[x-v*y for x,y in zip(a[i],a[r])]
        r+=1
        if r==len(a):break
    return r

def descent(args):
    a=R.integer(args.get('A',0),-1000,1000);b=R.integer(args.get('B',-2),-1000,1000)
    if 4*a**3+27*b*b==0:raise ValueError('Singular curve')
    gp=shutil.which('gp')
    if gp is None:return unavailable('PARI/GP')
    # Only checked integers interpolate into this fixed program; no supplied GP code.
    program=f'E=ellinit([0,0,0,{a},{b}]);r=ellrank(E);print(ellglobalred(E)[1]);print(r[1]);print(r[2]);print(elltors(E)[1]);\n'
    try:p=subprocess.run([gp,'-q','-f'],input=program,text=True,capture_output=True,timeout=30)
    except subprocess.TimeoutExpired:return {'status':'budget_exhausted','abstain':True,'seconds':30}
    lines=p.stdout.splitlines()
    if p.returncode or p.stderr.strip() or len(lines)!=4 or any(not s.isdigit() for s in lines):return {'status':'backend_error','abstain':True}
    conductor,lower,upper,torsion=map(int,lines)
    return {'status':'executed','curve':{'A':a,'B':b},'conductor':conductor,'rank_lower':lower,'rank_upper':upper,'rank_determined':lower==upper,'torsion_order':torsion,'certificate_scope':'PARI ellrank descent bounds, not independently kernel checked','point_is_generator_certified':False,'bsd_proved':False,'claim_ceiling':'C1 backend execution with PARI correctness assumptions','source':'https://pari.math.u-bordeaux.fr/dochtml/html/Elliptic_curves.html#ellrank'}
def homology(args):
    facets=args['facets']
    if not isinstance(facets,list) or not 1<=len(facets)<=32:raise ValueError('Facet cap')
    cells=set()
    for facet in facets:
        if not isinstance(facet,list) or not 1<=len(facet)<=5 or len(set(facet))!=len(facet):raise ValueError('Invalid simplex')
        for v in facet:R.integer(v,0,15)
        for k in range(1,len(facet)+1):cells.update(itertools.combinations(sorted(facet),k))
    if len(cells)>128:raise ValueError('Closure exceeds128simplices')
    dim=max(len(x) for x in cells)-1;groups={k:sorted(x for x in cells if len(x)==k+1) for k in range(dim+1)}
    boundaries={};ranks={0:0,dim+1:0};composes=True
    for k in range(1,dim+1):
        lower={x:i for i,x in enumerate(groups[k-1])};m=[[0]*len(groups[k]) for _ in lower]
        for j,cell in enumerate(groups[k]):
            for i in range(k+1):m[lower[cell[:i]+cell[i+1:]]][j]=(-1)**i
        boundaries[k]=m;ranks[k]=rank(m)
        if k>1:
            prev=boundaries[k-1]
            comp=[[sum(prev[i][h]*m[h][j] for h in range(len(m))) for j in range(len(m[0]))] for i in range(len(prev))]
            composes &= all(v==0 for row in comp for v in row)
    betti=[len(groups[k])-ranks[k]-ranks[k+1] for k in range(dim+1)]
    return {'status':'executed','coefficient_field':'Q','simplices':[len(groups[k]) for k in range(dim+1)],'boundary_ranks':ranks,'boundary_squared_zero':composes,'betti':betti,'fundamental_group_certified':False,'sphere_recognition_proved':False,'claim_ceiling':'C1 exact finite chain complex'}
def product_cycles(args):
    n=R.integer(args.get('factors',4),1,6);rows=[]
    for k in range(n+1):
        basis=list(itertools.combinations(range(n),k));complements=[tuple(i for i in range(n) if i not in s) for s in basis]
        matrix=[[int(not set(s)&set(t) and len(set(s)|set(t))==n) for t in complements] for s in basis]
        r=rank(matrix);rows.append({'codimension':k,'dimension':len(basis),'pairing_rank':r,'full_rank':r==math.comb(n,k)})
    return {'status':'executed','family':'(P1)^n','factors':n,'rows':rows,'assumptions':['Known rational cohomology ring Q[h1,...,hn]/(hi^2)','Coordinate divisors and their products give the stated cycle classes'],'general_hodge_proved':False,'cycle_map_formalized':False,'claim_ceiling':'C1 exact pairings conditional on known product ring'}
def affine(args):
    coefficients=args.get('coefficients',['1','1','-2'])
    if not isinstance(coefficients,list) or len(coefficients)!=3:raise ValueError('Three coefficients required')
    c=list(map(R.rational,coefficients));momentum=[v+v*v for v in c]
    return {'status':'executed','ansatz':'u_i=c_i*x_i/(T-t) onR3','divergence_coefficient':str(sum(c)),'divergence_free':sum(c)==0,'momentum_residual_coefficients':[str(v) for v in momentum],'pressure_coefficients_for_zero_force':[str(-v/2) for v in momentum],'pressure_formula':'p=sum_i p_i*x_i^2/(T-t)^2','force_can_be_zero_with_this_pressure':True,'finite_energy_R3':all(v==0 for v in c),'rapidly_decaying_initial_data':all(v==0 for v in c),'nontrivial_clay_counterexample':False,'claim_ceiling':'C1 exact fixed-affine-ansatz algebra; nonzero fields fail energy/decay'}
def barriers(args):
    flags=args.get('properties',{})
    names={'relativizes','constructive','large','useful_against_target','algebrizes','strong_prf_assumption'}
    if not isinstance(flags,dict) or set(flags)-names or any(type(v)!=bool for v in flags.values()):raise ValueError('Known boolean properties only')
    possible=[]
    if flags.get('relativizes'):possible.append('Relativization: requires proof of oracle-invariant steps and target scope')
    if all(flags.get(k) for k in ['constructive','large','useful_against_target','strong_prf_assumption']):possible.append('Conditional natural-proofs obstacle for specified circuit class and hardness assumption')
    if flags.get('algebrizes'):possible.append('Algebrization: verify precise asymmetric algebraic oracle definition')
    return {'status':'checklist_only','potential_obligations':possible,'strategy_admissible_certified':False,'properties_independently_verified':False,'claim_ceiling':'C0 conditional barrier obligations','abstain_from_automatic_proof_rejection':True}
