"""Canonical UTF-8/LF digest manifest; identifies artifacts, not truth."""
import hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def files():
    for p in sorted(ROOT.rglob('*')):
        rel=p.relative_to(ROOT)
        if p.is_file() and not any(x in {'.git','__pycache__','.venv','runtime'} for x in rel.parts) and str(rel).replace('\\','/')!='receipts/artifact-manifest.json':yield p,rel.as_posix()
def digest(p):return hashlib.sha256(p.read_text(encoding='utf-8').replace('\r\n','\n').encode('utf-8')).hexdigest()
if __name__=='__main__':
    path=ROOT/'receipts/artifact-manifest.json'
    if '--verify' in sys.argv:
        recorded=json.loads(path.read_text())['files'];now={name:digest(p) for p,name in files()};assert now==recorded,'Artifact set/hash mismatch'
        previous='0'*64;records=json.loads((ROOT/'receipts/governance.json').read_text())['records']
        for row in records:
            entry=dict(row);saved=entry.pop('sha256');assert entry['previous_sha256']==previous
            assert saved==hashlib.sha256(json.dumps(entry,sort_keys=True,separators=(',',':')).encode()).hexdigest();previous=saved
        print(json.dumps({'verified':True,'artifacts':len(now),'governance_records':len(records),'basis':'UTF8/LF'}))
    else:
        path.parent.mkdir(exist_ok=True);path.write_text(json.dumps({'hash_basis':'UTF8 with normalized LF newlines','files':{name:digest(p) for p,name in files()}},indent=2));print('Manifest written')
