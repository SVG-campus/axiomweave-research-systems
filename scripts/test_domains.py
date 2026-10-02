import asyncio,itertools,json,sys,unittest
import research_domains as D
import research_mcp as M
class DomainTests(unittest.TestCase):
    def test_elliptic_exact_and_negative(self):
        x=D.elliptic({});self.assertEqual(x['double'],['129/100','-383/1000']);self.assertTrue(x['rank_lower_bound_at_least_one_under_lutz_nagell'])
        self.assertEqual([r['points'] for r in x['local_factors']],[6,7,12,19,18,27,24,30,28])
        for bad in [{'point':['3','6']},{'primes':[9]},{'A':0,'B':0}]:
            with self.assertRaises(ValueError):D.elliptic(bad)
    def test_homology_independent_known_cases(self):
        for n in [2,3,4]:
            out=D.homology({'facets':[list(s) for s in itertools.combinations(range(n+1),n)]})
            self.assertTrue(out['boundary_squared_zero']);self.assertEqual(out['betti'],[1]+[0]*(n-2)+[1])
        self.assertEqual(D.homology({'facets':[[0,1,2,3]]})['betti'],[1,0,0,0])
        self.assertEqual(D.homology({'facets':[[0],[1]]})['betti'],[2])
    def test_ring_pairings(self):
        for n in range(1,7):self.assertTrue(all(r['full_rank'] for r in D.product_cycles({'factors':n})['rows']))
    @unittest.skipIf(D.shutil.which('gp') is None,'Optional PARI backend absent')
    def test_pari_descent(self):
        x=D.descent({});self.assertEqual((x['rank_lower'],x['rank_upper'],x['conductor'],x['torsion_order']),(1,1,1728,1));self.assertFalse(x['point_is_generator_certified'])
    def test_affine_independent_symbolic_derivatives(self):
        import sympy as s
        t,T=s.symbols('t T');xs=s.symbols('x y z');cs=[1,1,-2];u=[c*x/(T-t) for c,x in zip(cs,xs)]
        p=-sum((c+c*c)*x*x/2 for c,x in zip(cs,xs))/(T-t)**2
        for i in range(3):self.assertEqual(s.simplify(s.diff(u[i],t)+sum(u[j]*s.diff(u[i],xs[j]) for j in range(3))+s.diff(p,xs[i])),0)
        out=D.affine({});self.assertTrue(out['divergence_free']);self.assertFalse(out['finite_energy_R3'])
    def test_barrier_abstention(self):
        x=D.barriers({'properties':{'constructive':True,'large':True}});self.assertEqual(x['potential_obligations'],[]);self.assertFalse(x['strategy_admissible_certified'])
    def test_every_catalog_entry_addressable(self):
        for row in M.R.catalog()['methods']:
            if row['id'] not in M.ADAPTERS:self.assertTrue(M.call('execute_method',{'method_id':row['id']})['abstain'])
        with self.assertRaises(ValueError):M.call('execute_method',{'method_id':'invented'})
    @unittest.skipIf(D.flint_backend() is None,'Optional FLINT backend absent')
    def test_certified_windows_and_spectra(self):
        z=D.zeta({'heights':[15,30,50,100]});self.assertEqual([r['certified_total_count'] for r in z['rows']],[1,3,10,29]);self.assertTrue(z['ambiguous_height_negative_control'])
        self.assertTrue(all(r['bounded_consistency_check'] for r in z['rows']))
        self.assertTrue(all(r['positive_certified'] for r in D.spectral({})['rows']))
    def test_official_sdk_runtime(self):
        async def check():
            from mcp import ClientSession,StdioServerParameters
            from mcp.client.stdio import stdio_client
            async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(M.R.ROOT/'scripts/research_mcp.py')])) as (read,write):
                async with ClientSession(read,write) as client:
                    await client.initialize();tools=await client.list_tools();self.assertEqual(len(tools.tools),len(M.TOOLS))
                    for name,args in [('certify_elliptic_example',{}),('check_chain_complex',{'facets':[[0,1],[1,2],[0,2]]}),('execute_method',{'method_id':'human_review'}),('backend_capabilities',{})]:
                        out=await client.call_tool(name,args);self.assertFalse(out.isError);json.loads(out.content[0].text)
        try:import mcp
        except ImportError:self.skipTest('Optional official MCP SDK absent')
        asyncio.run(check())
if __name__=='__main__':unittest.main(verbosity=2)
