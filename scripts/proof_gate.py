"""Fail-closed certificate evidence gate; not a new theorem prover."""
import argparse,datetime as dt,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
THEOREMS=['NavierStokes.Comparator.navier_stokes_breakdown_R3','NavierStokes.Comparator.navier_stokes_breakdown_periodic']
ALLOWED={'propext','Classical.choice','Quot.sound'}
EXPECTED_REFERENCE={'ComparatorChallenges/NavierStokes.lean':'0cd193b8d5cbd0266e6e2f72e68dd5abcdcf2430ebd435dd9289737e9aa7da61','NavierStokes/ComparatorDefinitions.lean':'8d90e0f9eee14f8b01773852083a02fd58bda59d4de2abb60d1787bbc9f6ebf4','lake-manifest.json':'5ec1dc8e009008d0efb9601cd38f6ba54e753fd538b0e5f8c3e6c5ec72ee1e09'}
def read_text(folder,name):
    try:return (folder/name).read_text(encoding='utf-8',errors='replace')
    except OSError:return ''
def matches(folder,name,value):return read_text(folder,name).strip()==value
def read_exit(folder,name):
    try:return int(read_text(folder,name).strip())
    except ValueError:return None
def reference_matches(folder):
    try:
        rows=dict((line.split(None,1)[1].strip().lstrip('*'),line.split(None,1)[0]) for line in read_text(folder,'trusted-reference-before.sha256').splitlines())
        return rows==EXPECTED_REFERENCE
    except IndexError:return False
def axiom_gate(text,theorems=THEOREMS):
    found={}
    for name in theorems:
        match=re.search(re.escape(name)+r"['\"]?\s+depends on axioms:\s*\[([^\]]*)\]",text)
        if match:found[name]={v.strip() for v in match.group(1).split(',') if v.strip()}
    return len(found)==len(theorems) and all(v<=ALLOWED for v in found.values()),{k:sorted(v) for k,v in found.items()}
def summarize(folder):
    axiom_ok,axioms=axiom_gate(read_text(folder,'navier-axioms.log'))
    direct_axiom_ok=read_exit(folder,'axioms-exit-code.txt')==0 and axiom_ok
    embedded_ok,embedded_axioms=axiom_gate(read_text(folder,'cloud-build.log'))
    embedded_ok=embedded_ok and read_exit(folder,'navier-build-exit-code.txt')==0
    if not direct_axiom_ok and embedded_ok:axioms=embedded_axioms
    axiom_evidence='navier-axioms.log' if direct_axiom_ok else ('cloud-build.log (fresh root build)' if embedded_ok else 'missing')
    scale_ok,_=axiom_gate(read_text(folder,'scaling-lean.log'),['admissible_core_exponents','core_energy_exponent'])
    false_text=read_text(folder,'false-scaling.log')
    false_ok=read_exit(folder,'false-scaling-exit-code.txt')==1 and 'unsolved goals' in false_text and '\u22a2False' in ''.join(false_text.split())
    gates={'exact_toolchain_installed':read_exit(folder,'toolchain-exit-code.txt')==0 and matches(folder,'lean-toolchain.txt','leanprover/lean4:v4.34.0-rc2'),
      'exact_source_pin':matches(folder,'upstream-commit.txt','f9e8bc5b38b6e212696e8a30e3e91517af887bbd'),
      'pinned_cache_fetched':read_exit(folder,'cache-exit-code.txt')==0,
      'navier_submission_build':read_exit(folder,'navier-build-exit-code.txt')==0 and matches(folder,'navier-build-target.txt','NavierStokes.ComparatorSolution'),
      'root_axiom_check':direct_axiom_ok or embedded_ok,
      'independent_comparator_nanoda':read_exit(folder,'comparator-exit-code.txt')==0 and matches(folder,'checker-stage.txt','TERMINAL'),
      'trusted_reference_integrity':read_exit(folder,'reference-integrity-exit-code.txt')==0 and reference_matches(folder),
      'formal_scaling_controls':read_exit(folder,'scaling-exit-code.txt')==0 and scale_ok and false_ok,
      'independent_mathematical_correspondence_review':False}
    required=['exact_toolchain_installed','exact_source_pin','pinned_cache_fetched','navier_submission_build','root_axiom_check','independent_comparator_nanoda','trusted_reference_integrity']
    return {'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'gates':gates,'axioms':axioms,'root_axiom_evidence':axiom_evidence,'standalone_axiom_print_exit_code':read_exit(folder,'axioms-exit-code.txt'),'machine_replay_complete':all(gates[k] for k in required),'full_independent_validation':False,'claim_ceiling':'C1 execution mechanics and C2 source correspondence; inspect replay gates; no independent adjudication','open_gates':[k for k,v in gates.items() if not v]}
def controls():
    good='\n'.join("'"+t+"' depends on axioms: [propext, Classical.choice, Quot.sound]" for t in THEOREMS)
    assert axiom_gate(good)[0]
    assert not axiom_gate(good.replace('Quot.sound','sorryAx'))[0]
    assert not axiom_gate(good.splitlines()[0])[0]
    assert not axiom_gate('')[0]
if __name__=='__main__':
    controls();p=argparse.ArgumentParser();p.add_argument('--receipts',type=pathlib.Path,default=ROOT/'receipts');a=p.parse_args()
    result=summarize(a.receipts);result['gate_negative_controls_passed']=4
    (a.receipts/'validation-gates.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


