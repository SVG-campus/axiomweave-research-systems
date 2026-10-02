"""Finite seed expansion + bounded symbolic convergence; explicit unexplored space."""
import datetime as dt,hashlib,json,pathlib,time
import research_systems as R
ROOT=R.ROOT
start=time.monotonic();rows=R.catalog()['methods'];seen=set();rounds=[]
families=list(dict.fromkeys(r['family'] for r in rows))
for i in range(0,len(families),3):
    batch=[r['id'] for r in rows if r['family'] in families[i:i+3]];new=set(batch)-seen;seen.update(new)
    rounds.append({'phase':'seed_catalog_ingestion','new_ids':len(new),'total':len(seen),'families':families[i:i+3]})
for i in range(3):
    new={r['id'] for r in rows}-seen;seen.update(new)
    rounds.append({'phase':'duplicate_coverage_audit','new_ids':len(new),'total':len(seen),'round':i+1})
# Three zero increments prove saturation only of this frozen seed.
assert len(seen)==95 and all(x['new_ids']==0 for x in rounds[-3:])
search=[];zero=0;old=None
for width in [3,4,5,6,7,7,7,7]:
    out=R.symbolic({'target':'3*b-2*a','beam_width':width});current=out['exact_residual']
    improvement=old is None or R.rational(current)<R.rational(old)
    zero=0 if improvement else zero+1
    search.append({'beam':width,'residual':current,'exact_hit':bool(out['exact_hits']),'candidates':out['candidates'],'no_improvement_streak':zero})
    old=current
    if zero>=3:break
final=R.symbolic({'target':'3*b-2*a','beam_width':7,'max_candidates':512})
assert final['exact_hits'] and final['candidates']==154 and not final['truncated']
receipt={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-start,'frozen_catalog_sha256':hashlib.sha256((ROOT/'catalog/methods.json').read_text(encoding='utf-8').encode('utf-8')).hexdigest(),'hash_basis':'UTF8 with normalized LF newlines','catalog_rounds':rounds,'search_rounds':search,'final_sweep':{'catalog_ids':95,'full_known_symbolic_grammar_candidates':154,'exact_hit':True},'stop_reason':'Three zero increments within frozen seed / three non-improving symbolic expansions','unexplored':R.catalog()['unexplored'],'new_methods_discovered_by_loop':0,'all_tools_executed':False,'all_possible_systems_found':False,'claim_ceiling':'C1 bounded coverage mechanics; C0 external coverage hypothesis'}
(ROOT/'receipts/coverage-loop.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps({'methods':len(seen),'catalog_rounds':len(rounds),'search_rounds':len(search),'final_sweep':receipt['final_sweep'],'all_possible_systems_found':False}))
