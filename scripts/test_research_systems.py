"""Independent evaluations, adversarial controls and actual stdio protocol replay."""
import datetime as dt,itertools,json,pathlib,random,subprocess,sys,time,unittest
from fractions import Fraction as F
import research_systems as R
import research_mcp as M
ROOT=R.ROOT
class Tests(unittest.TestCase):
    def test_identity_with_independent_evaluation(self):
        self.assertTrue(R.identity({'left':'(a+b)*(a-b)','right':'a**2-b**2'})['equal_within_polynomial_domain'])
        self.assertFalse(R.identity({'left':'3*b-2*a','right':'3*b-3*a'})['equal_within_polynomial_domain'])
        for a,b in itertools.product(range(-4,5),repeat=2):self.assertEqual((a+b)*(a-b),a*a-b*b)
    def test_hostile_expressions(self):
        for text in ["__import__('os')",'a.__class__','a[0]','a**999999','1/0','a/b','lambda:1','True','a**-1','[a]*1000']:
            with self.assertRaises((ValueError,SyntaxError,ZeroDivisionError)):R.parse(text)
    def test_search_settings_and_false_negative(self):
        for target in ['3*b-2*a','3*b-3*a','b-2*a']:
            full=R.symbolic({'target':target});self.assertTrue(full['exact_hits']);self.assertEqual(full['candidates'],154)
        self.assertFalse(R.symbolic({'target':'3*b-2*a','beam_width':3})['exact_hits'])
        self.assertTrue(R.symbolic({'target':'3*b-2*a','max_candidates':8})['truncated'])
        self.assertFalse(R.symbolic({'target':'a*b','atoms':['a','b'],'operations':['add']})['exact_hits'])
    def test_cancellation_and_pruning(self):
        result=R.cancellation({'terms':[[[-2,'1']],[[-2,'-1'],[2,'1']]]})
        self.assertTrue(result['finite_laurent_sum_extends_smoothly_at_zero']);self.assertEqual(result['sum'],[[2,'1']])
        self.assertFalse(R.cancellation({'terms':[[[-2,'1']]]})['finite_laurent_sum_extends_smoothly_at_zero'])
        self.assertFalse(R.pruning({'atoms':2,'accepted_masks':[0,3]})['rejection_hereditary_on_frozen_lattice'])
        self.assertTrue(R.pruning({'atoms':2,'accepted_masks':[0,1,2]})['rejection_hereditary_on_frozen_lattice'])
    def test_interval_independent_samples(self):
        for op in ['add','sub','mul','div']:
            out=R.interval({'left':['-2','3'],'right':['1','4'],'operation':op});lo,hi=map(F,out['enclosure'])
            for x,y in itertools.product(range(-2,4),range(1,5)):
                z={'add':lambda:x+y,'sub':lambda:x-y,'mul':lambda:x*y,'div':lambda:F(x,y)}[op]()
                self.assertLessEqual(lo,z);self.assertLessEqual(z,hi)
        with self.assertRaises(ValueError):R.interval({'left':['1','2'],'right':['-1','1'],'operation':'div'})
    def test_sat_census_independent_bitmask(self):
        clauses=[list(x) for x in itertools.product([1,-1],[2,-2],[3,-3])];count=0
        for mask in range(256):
            formula=[c for i,c in enumerate(clauses) if mask>>i&1]
            result=R.sat({'variables':3,'clauses':formula})
            oracle=any(all(any(bool(bits>>(abs(l)-1)&1)==(l>0) for l in c) for c in formula) for bits in range(8))
            self.assertEqual(result['sat'],oracle);count+=result['sat']
        self.assertEqual(count,255)
    def test_contract_mutations(self):
        base={x:x for x in R.FIELDS}
        self.assertTrue(R.correspondence({'reference':base,'submission':base})['field_match'])
        for key in R.FIELDS:
            changed=dict(base);changed[key]+='changed'
            self.assertEqual(R.correspondence({'reference':base,'submission':changed})['differences'],[key])
        with self.assertRaises(ValueError):R.correspondence({'reference':{},'submission':{}})
    def test_catalog_and_combinations(self):
        rows=R.catalog()['methods'];self.assertEqual(len(rows),95);self.assertEqual(len({r['id'] for r in rows}),95)
        for a,b in itertools.product(rows,repeat=2):
            # 9,025 contract combinations, not executions of 95 solvers.
            for r in [a,b]:
                for field in ['assumptions','certificate','falsifier','budget','stop_rule','evidence','limits']:self.assertTrue(r[field])
            self.assertLessEqual(min(a['budget']['max_candidates'],b['budget']['max_candidates']),512)
        for kind in R.ROUTES:self.assertFalse(R.route({'question_type':kind})['autonomous_solution_guaranteed'])
    def test_composed_frozen_pipeline(self):
        # All8 bounded analytical backends in a single audited chain.
        for i in range(1,41):
            route=M.call('route_question',{'question_type':'symbolic'});self.assertTrue(route['route'])
            hit=M.call('symbolic_search',{'target':'3*b-2*a'})['exact_hits'][0]['expression']
            self.assertTrue(M.call('check_identity',{'left':hit,'right':'3*b-2*a'})['equal_within_polynomial_domain'])
            self.assertTrue(M.call('check_cancellation',{'terms':[[[-2,'1']],[[-2,'-1'],[2,str(i)]]]})['finite_laurent_sum_extends_smoothly_at_zero'])
            self.assertFalse(M.call('audit_pruning',{'atoms':2,'accepted_masks':[0,3]})['rejection_hereditary_on_frozen_lattice'])
            self.assertEqual(M.call('interval_operation',{'left':['1','2'],'right':['2','3'],'operation':'mul'})['enclosure'],['2','6'])
            self.assertFalse(M.call('check_finite_cnf',{'variables':1,'clauses':[[1],[-1]]})['sat'])
            base={x:x for x in R.FIELDS};self.assertFalse(M.call('compare_contracts',{'reference':base,'submission':base})['semantic_equivalence_proved'])
            self.assertFalse(M.call('validation_status',{})['full_independent_validation'])
    def test_protocol_runtime(self):
        reqs=[{'jsonrpc':'2.0','id':0,'method':'tools/list'}, {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'test','version':'1'}}},{'jsonrpc':'2.0','method':'notifications/initialized'},{'jsonrpc':'2.0','id':2,'method':'tools/list'}]
        for idx,(name,_) in enumerate(list(M.BY.items())[:10],3):
            examples={'method_catalog':{},'route_question':{'question_type':'pde'},'symbolic_search':{'target':'3*b-2*a'},'check_identity':{'left':'a+a','right':'2*a'},'check_cancellation':{'terms':[[[-1,'1']],[[-1,'-1']]]},'interval_operation':{'left':['1','2'],'right':['2','3'],'operation':'mul'},'check_finite_cnf':{'variables':1,'clauses':[[1]]},'compare_contracts':{'reference':{x:x for x in R.FIELDS},'submission':{x:x for x in R.FIELDS}},'audit_pruning':{'atoms':1,'accepted_masks':[0,1]},'validation_status':{}}
            reqs.append({'jsonrpc':'2.0','id':idx,'method':'tools/call','params':{'name':name,'arguments':examples[name]}})
        reqs += [{'jsonrpc':'2.0','id':90,'method':'tools/call','params':{'name':'symbolic_search','arguments':{'target':"__import__('os')"}}},{'jsonrpc':'2.0','id':91,'method':'tools/call','params':{'name':'symbolic_search','arguments':{'target':'a','max_candidates':True}}},{'jsonrpc':'2.0','id':92,'method':'no/such/method'}]
        p=subprocess.run([sys.executable,str(ROOT/'scripts/research_mcp.py')],input='\n'.join(map(json.dumps,reqs))+'\n',text=True,capture_output=True,timeout=30)
        self.assertEqual(p.returncode,0);self.assertEqual(p.stderr,'');out={r['id']:r for r in map(json.loads,p.stdout.splitlines())}
        self.assertIn('error',out[0]);self.assertEqual(out[1]['result']['protocolVersion'],'2025-11-25');self.assertEqual(len(out[2]['result']['tools']),len(M.TOOLS))
        for i in range(3,13):self.assertFalse(out[i]['result']['isError'])
        self.assertTrue(out[90]['result']['isError']);self.assertTrue(out[91]['result']['isError']);self.assertEqual(out[92]['error']['code'],-32601)
        self.assertNotIn(None,out)
    def test_larger_exact_polynomial_compositions(self):
        import math
        for k in range(9):
            p=R.parse(f'(a+b)**{k}')
            expected={(j,k-j,0):F(math.comb(k,j)) for j in range(k+1)}
            self.assertEqual(p,expected)
        p=R.parse('(a+b+t)**8');self.assertEqual(len(p),45)
        for (i,j,k),coefficient in p.items():
            self.assertEqual(coefficient,F(math.factorial(8),math.factorial(i)*math.factorial(j)*math.factorial(k)))
        with self.assertRaises(ValueError):R.parse('(a+b+t)**8*(a-b+t)**8')
    def test_seeded_rational_identity_controls(self):
        rng=random.Random(20261003)
        for _ in range(300):
            u,v,w=[F(rng.randrange(-20,21),rng.randrange(1,11)) for _ in range(3)]
            left=f'(({u})*a+({v})*b)*({w})'
            right=f'({u*w})*a+({v*w})*b'
            self.assertTrue(R.identity({'left':left,'right':right})['equal_within_polynomial_domain'])
            self.assertFalse(R.identity({'left':left,'right':f'({right})+1'})['equal_within_polynomial_domain'])
    def test_validation_cannot_promote_correspondence(self):
        status=M.call('validation_status',{})
        self.assertIsInstance(status['gates']['navier_submission_build'],bool)
        self.assertIsInstance(status['gates']['root_axiom_check'],bool)
        self.assertFalse(status['gates']['independent_comparator_nanoda'])
        self.assertFalse(status['machine_replay_complete'])
        with self.assertRaises(ValueError):M.call('validation_status',{'complete':True})
    def test_budget_type_and_range_controls(self):
        for cap in [1,2,3,7,8,154,512]:
            result=R.symbolic({'target':'3*b-2*a','max_candidates':cap})
            self.assertLessEqual(result['candidates'],cap)
        for bad in [0,513,True,-1,1.5,'512']:
            with self.assertRaises(ValueError):R.symbolic({'target':'a','max_candidates':bad})
        self.assertTrue(R.symbolic({'target':'a**4','atoms':['a'],'max_depth':2,'beam_width':1,'max_candidates':512})['candidates']<=512)
        with self.assertRaises(ValueError):R.sat({'variables':9,'clauses':[]})
        with self.assertRaises(ValueError):R.pruning({'atoms':9,'accepted_masks':[]})
if __name__=='__main__':
    start=time.monotonic();suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests);result=unittest.TextTestRunner(verbosity=2).run(suite)
    receipt={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'passed':result.wasSuccessful(),'elapsed_seconds':time.monotonic()-start,'contract_pairs':9025,'finite_cnf_cases':256,'composed_pipeline_trials':40,'seeded_rational_identity_cases':300,'seed':20261003,'live_stdio_tools':20,'claim_ceiling':'C1 bounded runtime and synthetic controls','ide_panel_discovery_verified':False,'all_possible_questions_validated':False}
    (ROOT/'receipts/research-systems-tests.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    sys.exit(0 if result.wasSuccessful() else 1)
