"""Read-only stdio MCP profiles: risk atlas and combined CABS/AS3-R research."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import cabs_mcp as CAB
import risk_atlas as A

SUPPORTED = ('2024-11-05', '2025-03-26', '2025-06-18', '2025-11-25')
FRAME_CAP = 262144


def schema(properties, required=()):
    return {'type': 'object', 'properties': properties, 'required': list(required), 'additionalProperties': False}


STRING = {'type': 'string', 'minLength': 1, 'maxLength': 2048}
OBJECT = {'type': 'object'}
INT = {'type': 'integer'}
REFERENCES = {'type': 'array', 'maxItems': 24, 'items': {'type': 'string', 'maxLength': 512}}
MEASUREMENTS = schema({key: {'type': 'boolean' if kind == 'boolean' else 'integer' if kind == 'integer' else 'number'}
                       for _, key, kind, *_ in A.CHECKS})
PORTFOLIO = schema({'positions': {'type': 'array', 'minItems': 1, 'maxItems': 64, 'items':
                                  schema({'symbol': STRING, 'notional': {'type': 'number'}}, ('symbol', 'notional'))},
                    'scenarios': {'type': 'array', 'minItems': 1, 'maxItems': 256, 'items':
                                  schema({'id': STRING, 'shocks': {'type': 'object', 'additionalProperties': {'type': 'number'}},
                                          'transaction_cost': {'type': 'number'}}, ('id', 'shocks'))},
                    'cash': {'type': 'number'}, 'max_loss': {'type': 'number'}}, ('positions', 'scenarios'))


def tool(name, description, input_schema):
    return {'name': name, 'description': description, 'inputSchema': input_schema,
            'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': False, 'idempotentHint': True}}


TOOLS = [
    tool('atlas_catalog', 'Page through all 240 declared scenarios and 60 families, with explicit unimplemented mechanisms.',
         schema({'family': STRING, 'query': STRING, 'offset': {'type': 'integer', 'minimum': 0, 'maximum': 240},
                 'limit': {'type': 'integer', 'minimum': 1, 'maximum': 40}})),
    tool('atlas_frame_problem', 'Run actual bounded CABS composition for a typed question; returns assumptions, obligations and stop rules.',
         schema({'question': STRING, 'domain': {'type': 'string', 'enum': list(A.DOMAINS)}, 'evidence': REFERENCES,
                 'assumptions': REFERENCES, 'max_candidates': {'type': 'integer', 'minimum': 1, 'maximum': 4096}}, ('question', 'domain'))),
    tool('atlas_probe', 'Evaluate 24 operational checks on supplied measurements. Missing evidence stays unknown; no trading permission.',
         schema({'observations': MEASUREMENTS, 'checks': {'type': 'array', 'minItems': 1, 'maxItems': 24,
                                                        'uniqueItems': True, 'items': {'type': 'string', 'enum': sorted(A.CHECK_IDS)}},
                 'evidence': REFERENCES}, ('observations',))),
    tool('atlas_scenario_probe', 'Inspect specific declared scenarios through a strictly validated legacy synthetic gate. Physical correspondence remains unverified.',
         schema({'scenario_ids': {'type': 'array', 'minItems': 1, 'maxItems': 40, 'uniqueItems': True, 'items': STRING},
                 'trade': OBJECT}, ('scenario_ids', 'trade'))),
    tool('atlas_portfolio_stress', 'Compute linear spot/notional P&L and worst supplied scenario for stocks or other positions. Does not estimate scenario probabilities.', PORTFOLIO),
    tool('atlas_robust_search', 'Exhaustive finite minimax ranking under loss/compute budgets, with no-action and seeded equal-budget random controls.',
         schema({'candidates': {'type': 'array', 'minItems': 1, 'maxItems': 128, 'items':
                               schema({'id': STRING, 'scenario_scores': {'type': 'object', 'additionalProperties': {'type': 'number'}},
                                       'compute_cost': {'type': 'number'}}, ('id', 'scenario_scores', 'compute_cost'))},
                 'scenario_ids': {'type': 'array', 'minItems': 1, 'maxItems': 256, 'uniqueItems': True, 'items': STRING},
                 'max_loss': {'type': 'number'}, 'max_compute_cost': {'type': 'number'}, 'seed': INT},
                ('candidates', 'scenario_ids', 'max_loss', 'max_compute_cost'))),
    tool('atlas_frontiers', 'Suggest falsifiable expansions within and outside the taxonomy; at most three declared rounds, no autonomous background actions.',
         schema({'round': {'type': 'integer', 'minimum': 1, 'maximum': 3}, 'observations': MEASUREMENTS,
                 'max_suggestions': {'type': 'integer', 'minimum': 1, 'maximum': 16}})),
    tool('atlas_alert_activity', 'Count supplied sent-alert events per observed hour and local time band, including quiet exposure. Alerts are distinct from filled bets.',
         schema({'timestamps': {'type': 'array', 'maxItems': 10000, 'items': {'type': 'number'}},
                 'start': {'type': 'number'}, 'end': {'type': 'number'}, 'timezone': STRING}, ('timestamps', 'start', 'end')))
]
COMBINED = tool('unified_probe', 'Execute actual CABS framing plus measured Risk Atlas controls and optional portfolio stress; return bounded next experiments and conditional costs.',
                schema({'question': STRING, 'domain': {'type': 'string', 'enum': list(A.DOMAINS)}, 'observations': MEASUREMENTS,
                        'portfolio': PORTFOLIO, 'evidence': REFERENCES, 'max_candidates': INT, 'round': INT}, ('question', 'domain', 'observations')))
REPLAY = tool('unified_as3r_replay', 'Call the configured SHA256-pinned AS3-R executable through actual JSON-RPC. Supplied historical outcomes yield simulation, not future income.',
              schema({'trades': {'type': 'array', 'maxItems': 2000, 'items': OBJECT}, 'rules': {'type': 'array', 'maxItems': 32, 'items': OBJECT},
                      **{k: {'type': 'number'} for k in ('initial_cash', 'move', 'fee', 'capacity', 'exposure_limit', 'stake_limit', 'minimum_principal')},
                      'include_ledger': {'type': 'boolean'}}, ('trades',)))


class Adapter:
    def __init__(self, executable=None, expected_hash=None):
        self.executable = Path(executable).resolve() if executable else None
        self.expected_hash = expected_hash

    def replay(self, args):
        A.fields(args, REPLAY['inputSchema']['properties'], ('trades',))
        if self.executable is None or not self.expected_hash:
            raise ValueError('AS3-R adapter unavailable; configure a pinned executable at server startup')
        actual = hashlib.sha256(self.executable.read_bytes()).hexdigest()
        if actual != self.expected_hash:
            raise ValueError('AS3-R source/executable manifest stale')
        if type(args['trades']) is not list or len(args['trades']) > 2000:
            raise ValueError('Replay trade cap 2000')
        # Reject unknown nested fields before invoking the independently pinned backend.
        trade_fields = ('ticker', 'asset', 'side', 'price', 'lead', 'minutes', 'time', 'close', 'settled', 'win', 'cushion_ratio')
        rule_fields = ('asset', 'side', 'price_min', 'price_max', 'lead_min_bps', 'minutes_max', 'normalized_lead_min', 'cushion_ratio_min')
        for row in args['trades']:
            A.fields(row, trade_fields, ('ticker', 'asset', 'side', 'price', 'lead', 'minutes', 'time', 'close', 'win'))
        if 'rules' in args:
            if type(args['rules']) is not list or len(args['rules']) > 32:
                raise ValueError('Rule cap 32')
            for row in args['rules']:
                A.fields(row, rule_fields)
        messages = [
            {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2025-11-25', 'capabilities': {}, 'clientInfo': {'name': 'risk-atlas-pinned-adapter', 'version': '1'}}},
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
            {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/call', 'params': {'name': 'as3r_fast_replay', 'arguments': args}}
        ]
        payload = '\n'.join(json.dumps(r, allow_nan=False) for r in messages) + '\n'
        if len(payload.encode()) > FRAME_CAP:
            raise ValueError('Replay frame budget exceeded')
        # run() kills and waits for this exact child on timeout; no broad helper cleanup.
        result = subprocess.run([str(self.executable)], input=payload, capture_output=True, text=True, timeout=15, shell=False)
        if result.returncode or len(result.stdout) > 4_000_000:
            raise ValueError('Pinned replay process failed or output budget exceeded')
        replies = [json.loads(line, parse_constant=reject_constant, object_pairs_hook=unique_object)
                   for line in result.stdout.splitlines()]
        if any(type(r) is not dict or r.get('jsonrpc') != '2.0' for r in replies):
            raise ValueError('Malformed pinned replay JSON-RPC frame')
        reply = next((r for r in replies if r.get('id') == 2), None)
        if reply is None or 'error' in reply:
            raise ValueError('Pinned replay returned no valid tool result')
        value = reply.get('result')
        if type(value) is not dict or type(value.get('content')) is not list or not value['content']:
            raise ValueError('Malformed pinned replay tool result')
        content = value['content'][0]
        if type(content) is not dict or content.get('type') != 'text' or type(content.get('text')) is not str:
            raise ValueError('Malformed pinned replay text content')
        if value.get('isError'):
            raise ValueError(content['text'][:400])
        data = json.loads(content['text'], parse_constant=reject_constant, object_pairs_hook=unique_object)
        if type(data) is not dict:
            raise ValueError('Pinned replay data object required')
        validate_json(data)
        return {'as3r_replay': data, 'executable_sha256': actual, 'input_sha256': A.digest(args),
                'transport': 'actual JSON-RPC stdio child, closed after call', 'temporary_client_closed': True,
                'claim_ceiling': 'C1 mechanics; C2 for supplied historical data', 'trade_authorized': False}


def reject_constant(value):
    raise ValueError('Non-finite JSON number: ' + value)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON object key')
        result[key] = value
    return result


def validate_json(value, depth=0):
    if depth > 24:
        raise ValueError('JSON nesting cap 24')
    if isinstance(value, dict):
        if len(value) > 512:
            raise ValueError('Object field cap 512')
        for item in value.values():
            validate_json(item, depth + 1)
    elif isinstance(value, list):
        if len(value) > 10000:
            raise ValueError('Array cap 10000')
        for item in value:
            validate_json(item, depth + 1)
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        A.number(value, 'JSON number', -1e15, 1e15)


def dispatch(name, args, adapter):
    validate_json(args)
    A.load_catalog()
    routes = {'atlas_catalog': A.catalog, 'atlas_frame_problem': A.frame_problem, 'atlas_probe': A.probe,
              'atlas_scenario_probe': A.scenario_probe, 'atlas_portfolio_stress': A.portfolio_stress,
              'atlas_robust_search': A.robust_search, 'atlas_frontiers': A.frontier,
              'atlas_alert_activity': A.alert_activity, 'unified_probe': A.unified_probe,
              'unified_as3r_replay': adapter.replay}
    if name.startswith('cabs_'):
        return CAB.call(name, args)
    if name not in routes:
        raise ValueError('Unknown tool')
    return routes[name](args)


def serve(profile, adapter):
    name = 'axiomweave-risk-atlas' if profile == 'atlas' else 'axiomweave-unified-research'
    tools = TOOLS if profile == 'atlas' else TOOLS + [COMBINED, REPLAY] + [tool(t['name'], t['description'], t['inputSchema']) for t in CAB.TOOLS]
    by = {t['name']: t for t in tools}
    initialized = ready = False

    def emit(value):
        print(json.dumps(value, allow_nan=False), flush=True)

    while True:
        raw = sys.stdin.buffer.readline(FRAME_CAP + 1)
        if not raw:
            break
        ident, has_id = None, True
        try:
            if len(raw) > FRAME_CAP:
                # Drain this exact oversized frame; do not reinterpret the remainder.
                while raw and not raw.endswith(b'\n'):
                    raw = sys.stdin.buffer.readline(FRAME_CAP + 1)
                raise ValueError('Message cap 256 KiB')
            request = json.loads(raw, parse_constant=reject_constant, object_pairs_hook=unique_object)
            if type(request) is not dict:
                raise ValueError('JSON-RPC request object required')
            ident, has_id = request.get('id'), 'id' in request
            if has_id and ident is not None and type(ident) not in (str, int):
                raise ValueError('JSON-RPC id must be string, integer or null')
            method, params = request.get('method'), request.get('params', {})
            if request.get('jsonrpc') != '2.0' or type(method) is not str or type(params) is not dict:
                raise ValueError('Malformed JSON-RPC')
            if not has_id:
                if method == 'notifications/initialized' and initialized:
                    ready = True
                continue
            if method == 'initialize':
                if initialized or type(params.get('protocolVersion')) is not str:
                    raise ValueError('Invalid initialize')
                initialized = True
                version = params['protocolVersion']
                result = {'protocolVersion': version if version in SUPPORTED else SUPPORTED[-1],
                          'capabilities': {'tools': {'listChanged': False}}, 'serverInfo': {'name': name, 'version': '1.0.0'},
                          'instructions': 'C0 hypotheses and C1 local mechanics; supplied history at most C2. No orders, guarantees, universal coverage or model training. Local default-off.'}
            elif method == 'ping':
                result = {}
            elif not ready:
                raise ValueError('Initialization and initialized notification required')
            elif method == 'tools/list':
                A.fields(params, ('cursor', '_meta'))
                if params.get('cursor') not in (None, ''):
                    raise ValueError('Tool inventory has one page; unknown cursor')
                result = {'tools': tools}
            elif method == 'tools/call':
                try:
                    A.fields(params, ('name', 'arguments', '_meta'), ('name',))
                    if params['name'] not in by:
                        raise ValueError('Unknown tool in this profile')
                    args = params.get('arguments', {})
                    A.fields(args, by[params['name']]['inputSchema']['properties'], by[params['name']]['inputSchema'].get('required', ()))
                    value = dispatch(params['name'], args, adapter)
                    result = {'content': [{'type': 'text', 'text': json.dumps(value, allow_nan=False)}],
                              'structuredContent': value, 'isError': False}
                except (ValueError, TypeError, KeyError, OSError, OverflowError, RecursionError, subprocess.SubprocessError) as exc:
                    result = {'content': [{'type': 'text', 'text': str(exc)[:400]}], 'isError': True}
            else:
                emit({'jsonrpc': '2.0', 'id': ident, 'error': {'code': -32601, 'message': 'Method not found'}})
                continue
            emit({'jsonrpc': '2.0', 'id': ident, 'result': result})
        except json.JSONDecodeError:
            emit({'jsonrpc': '2.0', 'id': None, 'error': {'code': -32700, 'message': 'Parse error'}})
        except (ValueError, TypeError, RecursionError, OverflowError) as exc:
            if has_id:
                emit({'jsonrpc': '2.0', 'id': ident, 'error': {'code': -32600, 'message': str(exc)[:400]}})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=('atlas', 'unified'), default='atlas')
    parser.add_argument('--as3-executable', type=Path)
    parser.add_argument('--as3-sha256')
    args = parser.parse_args()
    serve(args.profile, Adapter(args.as3_executable, args.as3_sha256))


if __name__ == '__main__':
    main()
