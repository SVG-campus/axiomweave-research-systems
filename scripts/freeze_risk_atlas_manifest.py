"""Explicit owner source-pin refresh; hashing does not validate financial/scientific claims."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ('scripts/compositional_search.py', 'scripts/cabs_mcp.py', 'catalog/search_suites.json',
           'scripts/risk_atlas.py', 'scripts/risk_atlas_legacy.py', 'scripts/risk_atlas_mcp.py', 'catalog/risk_atlas_240.json')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Replace only the atlas manifest after owner review; restart existing clients')
    args = parser.parse_args()
    manifest = {'version': 'risk-atlas-v1-20261005', 'claim_ceiling': 'C1 finite mechanics; C0 correspondence',
                'required_sources': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCES}}
    encoded = json.dumps(manifest, indent=2) + '\n'
    if args.write:
        target = ROOT / 'catalog/risk_atlas_manifest.json'
        temporary = target.with_suffix('.json.owner-refresh-tmp')
        with temporary.open('x', encoding='utf-8', newline='\n') as file:
            file.write(encoded)
        temporary.replace(target)
    print(encoded, end='')


if __name__ == '__main__':
    main()
