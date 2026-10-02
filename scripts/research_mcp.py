"""Legacy MCP stdio research server; bounded tools, explicit abstention."""
import json,sys
import research_systems as R
import research_domains as D
from proof_gate import summarize
def schema(props,required=()):return {'type':'object','properties':props,'required':list(required),'additionalProperties':False}
S={'type':'string'};I={'type':'integer'};A={'type':'array'};O={'type':'object'}
TOOLS=[
 ('method_catalog','Retrieve finite method contracts; catalog is not executable capability.',schema({'family':S,'status':S,'limit':I})),
 ('route_question','Select a proposed portfolio with missing backends disclosed.',schema({'question_type':{'type':'string','enum':list(R.ROUTES)}})),
 ('symbolic_search','Exact bounded polynomial combinatorial search; preserves finite hit certificates.',schema({'atoms':A,'target':S,'operations':A,'beam_width':I,'max_depth':I,'max_candidates':I},['target'])),
 ('check_identity','Check a restricted polynomial identity using exact normal forms.',schema({'left':S,'right':S},['left','right'])),
 ('check_cancellation','Sum finite Laurent polynomials; rejects termwise singularity pruning as a general rule.',schema({'terms':A},['terms'])),
 ('interval_operation','Exact rational arithmetic enclosure; not zeta or transcendental proof.',schema({'left':A,'right':A,'operation':S},['left','right','operation'])),
 ('check_finite_cnf','Exhaustive finite CNF decision at most8 variables; no complexity theorem.',schema({'variables':I,'clauses':A},['variables','clauses'])),
 ('compare_contracts','Compare seven explicit contract fields; semantic adjudication remains open.',schema({'reference':O,'submission':O},['reference','submission'])),
 ('audit_pruning','Check hereditary rejection on every subset of a frozen8-atom maximum lattice.',schema({'atoms':I,'accepted_masks':A},['atoms','accepted_masks'])),
 ('validation_status','Recompute recorded formal replay gates; does not execute Lean.',schema({}))]
TOOLS += [
 ('certify_elliptic_descent','Optional PARI descent rank bounds and conductor; fixed program, no supplied code.',schema({'A':I,'B':I})),
 ('certify_zeta_window','FLINT total-zero counts and root enclosures in bounded height windows; optional backend.',schema({'heights':A,'precision_bits':I})),
 ('certify_elliptic_example','Exact doubling and two independent finite-field counts; scoped Lutz-Nagell inference.',schema({'A':I,'B':I,'point':A,'primes':A})),
 ('check_chain_complex','Exact rational simplicial homology with boundary-squared controls; no fundamental group.',schema({'facets':A},['facets'])),
 ('check_product_cycles','Exact intersection pairing for the assumed cohomology ring of (P1)^n.',schema({'factors':I})),
 ('check_spectral_limit','Ball-enclosed Dirichlet chain spectra; optional backend; no gauge theory proof.',schema({'grid_sizes':A,'precision_bits':I})),
 ('audit_affine_pde','Fixed affine Navier-Stokes ansatz with pressure cancellation and energy obstruction.',schema({'coefficients':A})),
 ('audit_complexity_barriers','Conditional checklist, never automatic proof acceptance or rejection.',schema({'properties':O})),
 ('execute_method','Address any catalog entry; unsupported backends abstain with their contract.',schema({'method_id':S,'arguments':O},['method_id'])),
 ('run_research_loop','Bounded seven-problem portfolio, expanded controls and final recheck; no global proof promise.',schema({'rounds':I})),
 ('backend_capabilities','Report executable adapters and optional dependencies.',schema({}))]
ADAPTERS={'semantic_correspondence':'compare_contracts','apriori':'symbolic_search','polynomial_identity':'check_identity','cancellation_search':'check_cancellation','interval':'interval_operation','sat_smt':'check_finite_cnf','homology':'check_chain_complex','cycle_class':'check_product_cycles','spectral':'check_spectral_limit','energy_estimates':'audit_affine_pde','root_count':'certify_zeta_window','diophantine':'certify_elliptic_example'}
ADAPTERS.update({'exhaustive':'symbolic_search','beam':'symbolic_search','exact_arithmetic':'check_identity','portfolio_routing':'route_question','selmer':'certify_elliptic_descent'})
DOMAIN={'certify_elliptic_descent':D.descent,'certify_zeta_window':D.zeta,'certify_elliptic_example':D.elliptic,'check_chain_complex':D.homology,'check_product_cycles':D.product_cycles,'check_spectral_limit':D.spectral,'audit_affine_pde':D.affine,'audit_complexity_barriers':D.barriers}
BY={name:(desc,sc) for name,desc,sc in TOOLS}
def validate(args,sc):
    if not isinstance(args,dict) or set(args)-set(sc['properties']) or set(sc['required'])-set(args):raise ValueError('Unknown or missing arguments')
    types={'string':str,'array':list,'object':dict,'integer':int}
    for k,v in args.items():
        prop=sc['properties'][k]
        if type(v)!=types[prop['type']]:raise ValueError('Wrong argument type: '+k)
        if 'enum' in prop and v not in prop['enum']:raise ValueError('Invalid enum')
def call(name,args):
    if name not in BY:raise ValueError('Unknown tool')
    validate(args,BY[name][1])
    if name in DOMAIN:return DOMAIN[name](args)
    if name=='backend_capabilities':return {'server':'axiomweave-research-systems','tool_count':len(TOOLS),'adapters':ADAPTERS,'flint_available':D.flint_backend() is not None,'arbitrary_code_execution':False,'all_catalog_methods_executable':False}
    if name=='run_research_loop':
        from research_loop import run
        return run(args)
    if name=='execute_method':
        row=next((m for m in R.catalog()['methods'] if m['id']==args['method_id']),None)
        if row is None:raise ValueError('Unknown catalog ID')
        target=ADAPTERS.get(row['id'])
        if not target:return {'status':'catalog_only','abstain':True,'method':row,'reason':'No executable adapter for this method','universal_proof':False}
        return {'method_id':row['id'],'adapter':target,'scope':BY[target][0],'result':call(target,args.get('arguments',{}))}
    if name=='method_catalog':
        limit=R.integer(args.get('limit',95),1,95);c=R.catalog()
        for key in ['family','status']:
            if key in args:c['methods']=[x for x in c['methods'] if x[key]==args[key]]
        c['total_matches']=len(c['methods']);c['methods']=c['methods'][:limit];return c
    if name=='validation_status':return summarize(R.ROOT/'receipts')
    handlers={'route_question':R.route,'symbolic_search':R.symbolic,'check_identity':R.identity,'check_cancellation':R.cancellation,'interval_operation':R.interval,'check_finite_cnf':R.sat,'compare_contracts':R.correspondence,'audit_pruning':R.pruning}
    return handlers[name](args)
def main():
    initialized=False;ready=False
    while True:
        raw=sys.stdin.buffer.readline(65537)
        if not raw:break
        ident=None
        try:
            if len(raw)>65536:raise ValueError('Message cap exceeded')
            req=json.loads(raw);ident=req.get('id');method=req.get('method');params=req.get('params',{})
            if req.get('jsonrpc')!='2.0' or not isinstance(method,str) or not isinstance(params,dict):raise ValueError('Malformed JSON-RPC')
            if method=='notifications/initialized':
                if initialized:ready=True
                continue
            if ident is None:continue
            if method=='initialize':
                if initialized:raise ValueError('Already initialized')
                version=params.get('protocolVersion');supported=['2024-11-05','2025-03-26','2025-06-18','2025-11-25']
                if not isinstance(version,str):raise ValueError('Protocol version required')
                initialized=True
                result={'protocolVersion':version if version in supported else supported[-1],'capabilities':{'tools':{'listChanged':False}},'serverInfo':{'name':'axiomweave-research-systems','version':'0.1.0'},'instructions':'Finite tools only. Catalog-only entries abstain. No general solver, cloud action or arbitrary candidate execution.'}
            elif method=='ping':result={}
            elif not ready:raise ValueError('Initialize and initialized notification required')
            elif method=='tools/list':result={'tools':[{'name':n,'description':d,'inputSchema':s,'annotations':{'readOnlyHint':True,'destructiveHint':False,'openWorldHint':False}} for n,d,s in TOOLS]}
            elif method=='tools/call':
                try:
                    output=call(params.get('name'),params.get('arguments',{}))
                    result={'content':[{'type':'text','text':json.dumps(output)}],'isError':False}
                except (ValueError,KeyError,TypeError,ZeroDivisionError,SyntaxError) as e:
                    result={'content':[{'type':'text','text':str(e)}],'isError':True}
            else:
                print(json.dumps({'jsonrpc':'2.0','id':ident,'error':{'code':-32601,'message':'Method not found'}}),flush=True);continue
            print(json.dumps({'jsonrpc':'2.0','id':ident,'result':result}),flush=True)
        except (ValueError,TypeError,AttributeError) as e:
            print(json.dumps({'jsonrpc':'2.0','id':ident,'error':{'code':-32600,'message':str(e)}}),flush=True)
if __name__=='__main__':main()
