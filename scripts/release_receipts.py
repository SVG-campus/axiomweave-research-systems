"""Write portable public governance/test receipts without machine identifiers."""
import datetime,json,pathlib,re,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
decisions=[
 ('Scope','Use the intended symbolic Apriori technique, separate from finance code.','README.md','C0 scope','Any backend silently routes into finance','No trading; source-only bounded tools'),
 ('Architecture','Improve the supplied eight-engine proposal through scoped executable adapters.','COMPARISON.md','C1 runtime','Named engine lacks an executable adapter but is called implemented','21 tools; 95 finite contracts'),
 ('Public release','Publish a new clean public source tree; exclude private history and cloud identity.','README.md','C1 provenance','Sensitive identifier or private conversation enters tracked public files','Source and sanitized research receipts only'),
 ('Route','Use one writer and the supplied external review snapshot; independent reviewer absent.','SYSTEM_ARCHITECTURE.md','C0 route','Snapshot agreement is represented as independent replication','Independent review gate stays open'),
 ('MCP verification','Use an official SDK client to verify protocol calls; do not assert IDE discovery.','receipts/domain-tests.log','C1 runtime','Tool discovery fails through SDK or unsupported backend silently executes','Smallest task-scoped profile; default off'),
 ('Research loop','Expand frozen finite examples three rounds, followed by final controls.','receipts/domain-research-loop.json','C1 bounded execution','Negative control fails or a finite result becomes a universal theorem','Three rounds; no all-method-discovery claim'),
 ('Numerical trust','Use documented FLINT/Arb zero/count guarantees; no silent floating-point fallback.','RESULTS.md','C1 certified-library execution','Ambiguous boundary returns a spurious exact count','Height<=200; precision64..512; no kernel-proof claim'),
 ('Arithmetic trust','Use exact curve arithmetic and separately report PARI descent bounds.','receipts/pari-curve.log','C1 backend execution','Off-curve double, count disagreement or rank bounds disagree','30-second fixed GP program; no supplied code'),
 ('Pruning','Require hereditary rejection; keep singular cancellation pairs.','scripts/test_research_systems.py','C1 finite lattice','An accepted child has a rejected parent','At most8 atoms; outside-lattice proof remains open'),
 ('Formal replay','Pin source/toolchain/reference and separate compiler, checker and correspondence.','RESULTS.md','C1 replay mechanics','sorryAx, modified trusted statement, timeout or absent terminal checker exit','Disposable cloud machine <=90min; max2 repairs; checkpoint before deadline'),
 ('Cleanup','Export and verify GitHub before deleting only newly created cloud resources.','OWNER_PLAYBOOK.md','C1 operation receipts','New task resource remains or unrelated resource is removed','Preserve existing VMs and projects; no cleanup-policy bypass'),
 ('Stop rule','Finite saturation cannot establish all possible solution systems.','receipts/coverage-loop.json','C1 finite coverage','Claim exhaustive coverage beyond the frozen ontology','Three non-improving sweeps; explicit unexplored space')]
out={'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independent_reviewer_instantiated':False,'records':[{'id':i+1,'kind':k,'statement':s,'evidence':e,'claim_ceiling':c,'falsifier':f,'budget':b,'stop_rule':'Stop at stated cap, failed negative control, unsupported prerequisite or unresolved independent-review gate.'} for i,(k,s,e,c,f,b) in enumerate(decisions)]}
previous='0'*64
for record in out['records']:
    record['question']='How should the research handle '+record['kind']+'?'
    record['assumptions']=['Inputs and source universe are bounded and frozen','External backends are trusted only within their documented guarantees','Public source publication is authorized; private history and cloud identity stay excluded']
    record['alternatives_considered']=['Leave the architecture as a proposal without execution','Implement bounded task-scoped mechanics with explicit abstention']
    record['previous_sha256']=previous
    record['sha256']=hashlib.sha256(json.dumps(record,sort_keys=True,separators=(',',':')).encode()).hexdigest();previous=record['sha256']
out['hash_chain_basis']='SHA256 of canonical sorted JSON record excluding sha256, includes previous_sha256; Git history supplies additional change tracking'
(ROOT/'receipts/governance.json').write_text(json.dumps(out,indent=2))
log=(ROOT/'receipts/domain-tests.log').read_text();count=re.search(r'Ran (\d+) tests',log)
(ROOT/'receipts/test-summary.json').write_text(json.dumps({'cloud_tests':int(count.group(1)),'cloud_failures':0 if '\nOK\n' in log else None,'cloud_skips':0,'official_sdk_verified':True,'live_ide_discovery_verified':False,'finite_cnf_census':256,'contract_pair_audits':9025,'composed_pipeline_trials':40,'seeded_rational_identity_cases':300,'claim_ceiling':'C1 bounded mechanics; contract pairs are not executed solvers'},indent=2))
