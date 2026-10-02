"""A frozen finite portfolio and final recheck, not an unbounded discovery claim."""
import datetime,itertools,json,pathlib,sys
import research_systems as R
import research_domains as D
def run(args):
    rounds=R.integer(args.get('rounds',3),1,3);rows=[]
    for r in range(1,rounds+1):
        sizes=[8,16,32,64,128][:r+2]
        facets=[list(x) for x in itertools.combinations(range(5),4)]
        result={
          'Navier_Stokes':{'symbolic':R.symbolic({'target':'3*b-2*a','beam_width':7}),'affine_obstruction':D.affine({}),'cancellation_control':R.cancellation({'terms':[[[-2,'1']],[[-2,'-1'],[2,'1']]]})},
          'Riemann':D.zeta({'heights':[15,30,50,100][:r+1]}),
          'P_vs_NP':{'finite_sat':R.sat({'variables':r+2,'clauses':[[1],[-1]]}),'barrier_check':D.barriers({'properties':{'constructive':True,'large':True}})},
          'BSD':{'exact_point_checks':D.elliptic({'primes':[5,7,11,13,17,19,23,29,31][:r*3]}),'descent':D.descent({})},
          'Hodge':D.product_cycles({'factors':r+2}),
          'Yang_Mills':D.spectral({'grid_sizes':sizes}),
          'Poincare':D.homology({'facets':facets})}
        rows.append({'round':r,'results':result,'new_universal_proofs':0,'expansion':'Larger finite windows, primes, rings, grids and SAT variables'})
    final={
      'false_identity_rejected':not R.identity({'left':'a','right':'a+1'})['equal_within_polynomial_domain'],
      'singular_term_cancellation_survives':R.cancellation({'terms':[[[-1,'1']],[[-1,'-1']]]})['finite_laurent_sum_extends_smoothly_at_zero'],
      'narrow_beam_misses_known_hit':not R.symbolic({'target':'3*b-2*a','beam_width':3})['exact_hits'],
      'ball_boundary_ambiguity':D.zeta({'heights':[15]}),
      'contractible_simplex_control':D.homology({'facets':[[0,1,2,3]]}),
      'energy_obstruction_rechecked':not D.affine({})['finite_energy_R3']}
    return {'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rounds':rows,'final_recheck':final,'stop_reason':'Frozen three-round expansion budget reached; no universal-proof gate reduction','exhaustive_method_discovery':False,'all_possible_questions_covered':False,'claim_ceiling':'C1 bounded portfolio execution','remaining':['Independent PDE theorem-to-statement review','Unlimited-height RH argument','Asymptotic complexity theorem','General BSD rank and leading coefficient','General algebraic cycle construction','Constructive 4D gauge theory and positive mass gap','Poincare already proved; homology alone is not sphere recognition']}
if __name__=='__main__':
    out=run({});path=R.ROOT/'receipts/domain-research-loop.json';path.parent.mkdir(exist_ok=True);path.write_text(json.dumps(out,indent=2));print(json.dumps({'receipt':str(path),'rounds':len(out['rounds']),'claim_ceiling':out['claim_ceiling']}))
