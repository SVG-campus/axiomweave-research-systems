"""Finite risk taxonomy, measured-input controls and bounded CABS composition.

Pure local calculations. No broker, credentials, network or generated code.
"""
from __future__ import annotations

import collections
import datetime as dt
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
from zoneinfo import ZoneInfo

import compositional_search as C
import risk_atlas_legacy as L

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'catalog/risk_atlas_240.json'
MANIFEST = ROOT / 'catalog/risk_atlas_manifest.json'
APPROVED_MANIFEST_SHA256 = hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
DOMAINS = ('prediction_markets', 'stocks', 'operations', 'general')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def number(x, label, lo=-1e15, hi=1e15):
    if type(x) not in (int, float) or not math.isfinite(x) or not lo <= x <= hi:
        raise ValueError(label + ': finite number in allowed range required')
    return float(x)


def integer(x, label, lo=0, hi=4096):
    if type(x) is not int or not lo <= x <= hi:
        raise ValueError(label + ': bounded integer required')
    return x


def text(x, label, limit=2048):
    if type(x) is not str or not 1 <= len(x) <= limit:
        raise ValueError(label + ': bounded nonempty text required')
    return x


def fields(value, allowed, required=()):
    if type(value) is not dict or set(value) - set(allowed) or set(required) - set(value):
        raise ValueError('Unknown or missing fields')


def load_catalog():
    manifest_bytes = MANIFEST.read_bytes()
    if hashlib.sha256(manifest_bytes).hexdigest() != APPROVED_MANIFEST_SHA256:
        raise ValueError('Source manifest changed since startup; restart the MCP client')
    manifest = json.loads(manifest_bytes)
    for name, expected in manifest['required_sources'].items():
        path = ROOT / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Source manifest stale: ' + name)
    data = json.loads(CATALOG.read_text(encoding='utf-8'))
    if len(data['scenarios']) != 240 or len({r['id'] for r in data['scenarios']}) != 240:
        raise ValueError('Catalog denominator/identity mismatch')
    return data


def scenario_probe(args):
    fields(args, ('scenario_ids', 'trade'), ('scenario_ids', 'trade'))
    ids = args['scenario_ids']
    if type(ids) is not list or not 1 <= len(ids) <= 40 or any(type(v) is not str for v in ids) or len(set(ids)) != len(ids):
        raise ValueError('Unique scenario ID list cap 40')
    data = load_catalog()
    by = {r['id']: r for r in data['scenarios']}
    if set(ids) - by.keys():
        raise ValueError('Unknown scenario ID')
    trade = args['trade']
    core = ('asset', 'side', 'price', 'rem', 'norm_lead', 'lead_bps')
    fields(trade, set(core) | set(L.SENSOR_TYPES), core)
    if trade['asset'] not in ('BTC', 'ETH', 'SOL', 'DOGE', 'XRP') or trade['side'] not in ('YES', 'NO'):
        raise ValueError('Unsupported asset/side')
    number(trade['price'], 'price fraction', .000001, .999999)
    number(trade['rem'], 'remaining minutes', .000001, 10080)
    number(trade['norm_lead'], 'normalized lead', 0, 1e6)
    number(trade['lead_bps'], 'basis-point lead', 0, 1e6)
    for key, value in trade.items():
        if key in core:
            continue
        if L.SENSOR_TYPES[key] == 'boolean':
            if type(value) is not bool:
                raise ValueError(key + ': boolean required')
        else:
            number(value, key, -1e12, 1e12)
    legacy = L.legacy_policy(trade)
    rows = []
    for ident in ids:
        row = by[ident]
        missing = sorted(set(row['synthetic_fields']) - set(trade))
        if row['status'] == 'catalog_only':
            status = 'catalog_only'
        elif missing or not row['synthetic_fields']:
            status = 'insufficient_measurements'
        else:
            status = 'legacy_policy_accepted' if legacy[0] else 'legacy_policy_rejected'
        rows.append({'id': ident, 'status': status, 'missing_synthetic_fields': missing,
                     'measurement_mapping': 'declared' if row['synthetic_fields'] else 'unmapped',
                     'correspondence_verified': False, 'execution_ready': False})
    return {'scenarios': rows, 'legacy_policy': {'accepted': bool(legacy[0]), 'reason': legacy[1]},
            'legacy_missing_sensor_count': len(set(L.SENSOR_TYPES) - set(trade)),
            'input_sha256': digest(args), 'claim_ceiling': 'C1 legacy synthetic diagnostics; C0 physical correspondence',
            'limitations': 'The policy uses defaults for absent optional fields. Diagnostic acceptance never means safe, profitable or physically implemented.',
            'trade_authorized': False}


def catalog(args):
    fields(args, ('family', 'query', 'offset', 'limit'))
    data = load_catalog()
    rows = data['scenarios']
    family = args.get('family')
    query = args.get('query')
    if family is not None:
        text(family, 'family', 180)
        rows = [r for r in rows if family.casefold() in r['family'].casefold()]
    if query is not None:
        text(query, 'query', 180)
        rows = [r for r in rows if query.casefold() in (r['name'] + ' ' + r['family'] + ' ' + r['id']).casefold()]
    offset = integer(args.get('offset', 0), 'offset', 0, 240)
    limit = integer(args.get('limit', 20), 'limit', 1, 40)
    page = rows[offset:offset + limit]
    return {'catalog_version': data['version'], 'catalog_sha256': hashlib.sha256(CATALOG.read_bytes()).hexdigest(),
            'declared_scenarios': 240, 'declared_families': 60, 'matched': len(rows), 'offset': offset,
            'scenarios': page, 'next_offset': offset + len(page) if offset + len(page) < len(rows) else None,
            'operational_checks': len(CHECKS), 'claim_ceiling': 'C0 taxonomy; C1 catalog mechanics',
            'coverage_scope': '240 declared labels only; no denominator for all real-world risks.',
            'universal_coverage': False, 'validated_exotic_backends': 0}


def framed_task(question, domain, strategy='exhaustive', cap=256):
    return {'problem': question, 'dimensions': {'domain': domain, 'authority': 'local research only'},
            'atoms': [
                {'id': 'frame_requirements', 'input': 'question', 'output': 'specification', 'capabilities': ['requirements'],
                 'time': {'terms': [{'n': 1}]}, 'space': {'terms': [{'n': 1}]}},
                {'id': 'atlas_probe', 'input': 'specification', 'output': 'observations', 'capabilities': ['risk_controls'],
                 'time': {'terms': [{'m': 1}]}, 'space': {'terms': [{'m': 1}]}},
                {'id': 'bounded_evaluation', 'input': 'observations', 'output': 'evidence', 'capabilities': ['evaluate'],
                 'time': {'terms': [{'n': 1, 'm': 1}]}, 'space': {'terms': [{'m': 1}]}},
                {'id': 'check_receipt', 'input': 'evidence', 'output': 'certificate', 'capabilities': ['check'],
                 'time': {'terms': [{'n': 1}]}, 'space': {'terms': [{'n': 1}]}}
            ], 'input_type': 'question', 'output_type': 'certificate',
            'required_capabilities': ['requirements', 'risk_controls', 'evaluate', 'check'],
            'operators': ['sequence', 'portfolio'], 'max_leaves': 4, 'strategy': strategy,
            'beam_width': 8, 'max_candidates': cap,
            'semantic_obligations': ['Typed workflow compatibility does not validate question meaning or scientific mechanisms.',
                                     'Supply independent market data, execution costs and later untouched evaluation for financial utility.']}


def frame_problem(args):
    fields(args, ('question', 'domain', 'evidence', 'assumptions', 'max_candidates'), ('question', 'domain'))
    question = text(args['question'], 'question')
    domain = args['domain']
    if domain not in DOMAINS:
        raise ValueError('Unsupported domain')
    evidence = args.get('evidence', [])
    assumptions = args.get('assumptions', [])
    for name, values in [('evidence', evidence), ('assumptions', assumptions)]:
        if type(values) is not list or len(values) > 24:
            raise ValueError(name + ': list cap 24')
        for val in values:
            text(val, name, 512)
    cap = integer(args.get('max_candidates', 256), 'max_candidates', 1, 4096)
    load_catalog()
    task = framed_task(question, domain, cap=cap)
    result = C.search({'mode': 'plan', 'task': task})
    return {'question': question, 'domain': domain, 'evidence': evidence, 'assumptions': assumptions,
            'cabs': result, 'task_sha256': digest(task), 'claim_ceiling': 'C1 composition; C0 domain proposal',
            'falsifier': 'Missing measurements, failed constraints, shuffled-label parity or a superior cash/simple baseline.',
            'budget': {'candidates': cap, 'seconds': 10, 'rounds': 3, 'external_spend': 0},
            'stop_rule': 'Stop on manifest drift, failed control, no improvement, or the frozen budget.',
            'open_obligations': result['semantic_obligations']}


# Each check has explicit units/semantics. Unknown observations are not imputed.
CHECKS = [
    ('quote_freshness', 'quote_age_seconds', 'number', 0, 5, 'Refresh executable quote.'),
    ('model_freshness', 'model_age_seconds', 'number', 0, 45, 'Recompute from fresh observations.'),
    ('expiry_buffer', 'seconds_to_close', 'number', 48, 86400, 'Defer near the settlement boundary.'),
    ('valid_spread', 'spread_usd', 'number', 0.000001, .04, 'Refresh uncrossed bid/ask and depth.'),
    ('clock_integrity', 'clock_skew_ms', 'abs_number', 0, 1000, 'Verify clock synchronization.'),
    ('displayed_depth', 'displayed_quantity', 'number', 0.000001, 1e12, 'Verify executable displayed quantity.'),
    ('exposure_budget', 'exposure_ratio', 'number', 0, .20, 'Reconcile aggregate exposure against the frozen cap.'),
    ('concurrency', 'concurrent_positions', 'integer', 0, 1, 'Check correlated positions and reservations.'),
    ('feed_agreement', 'basis_drift_bps', 'abs_number', 0, 14, 'Compare independent timestamped feeds.'),
    ('sensor_freshness', 'sensor_age_seconds', 'number', 0, 60, 'Refresh the explicitly required sensor.'),
    ('no_macro_alarm', 'macro_shock', 'boolean', False, False, 'Defer during the declared macro alarm.'),
    ('no_duplicate_event', 'duplicate_event', 'boolean', False, False, 'Use a stable idempotency key.'),
    ('settlement_chronology', 'chronology_verified', 'boolean', True, True, 'Reconcile buy/sell/settlement chronology.'),
    ('sale_accounting', 'sale_accounting_verified', 'boolean', True, True, 'Reconcile remaining quantity and realized proceeds.'),
    ('fill_evidence', 'fills_verified', 'boolean', True, True, 'Separate alerts from broker-confirmed fills.'),
    ('fee_evidence', 'fees_verified', 'boolean', True, True, 'Obtain actual venue fee/cost evidence.'),
    ('source_integrity', 'source_manifest_verified', 'boolean', True, True, 'Refresh hashes and rerun changed-source controls.'),
    ('measurement_units', 'units_verified', 'boolean', True, True, 'Check dollars, basis points, fractions and timestamps.'),
    ('scan_errors', 'scan_error_count', 'integer', 0, 0, 'Inspect failing scan branches and reproduce exceptions.'),
    ('scan_liveness', 'scan_age_seconds', 'number', 0, 120, 'Inspect service heartbeat and recent completed scans.'),
    ('delivery_evidence', 'delivery_acknowledged', 'boolean', True, True, 'Inspect Telegram acknowledgment/retry evidence.'),
    ('calibration_evidence', 'calibration_heldout', 'boolean', True, True, 'Freeze a later untouched calibration protocol.'),
    ('missing_data_guard', 'input_complete', 'boolean', True, True, 'Collect missing data instead of safe default values.'),
    ('budget_reservations', 'reservations_reconciled', 'boolean', True, True, 'Reconcile reservation IDs without restoring financial state.')
]
CHECK_IDS = {r[0] for r in CHECKS}
OBS_FIELDS = {r[1] for r in CHECKS}


def probe(args):
    fields(args, ('observations', 'checks', 'evidence'), ('observations',))
    obs = args['observations']
    fields(obs, OBS_FIELDS)
    requested = args.get('checks', [r[0] for r in CHECKS])
    if type(requested) is not list or not 1 <= len(requested) <= len(CHECKS) or any(type(v) is not str for v in requested) or len(set(requested)) != len(requested) or set(requested) - CHECK_IDS:
        raise ValueError('Checks must be unique registered IDs, cap 24')
    evidence = args.get('evidence', [])
    if type(evidence) is not list or len(evidence) > 24:
        raise ValueError('Evidence reference cap 24')
    for ref in evidence:
        text(ref, 'evidence reference', 512)
    # Validate even unselected supplied fields so hidden malformed values cannot pass.
    for _, key, kind, _, _, _ in CHECKS:
        if key not in obs:
            continue
        if kind == 'boolean':
            if type(obs[key]) is not bool:
                raise ValueError(key + ': boolean required')
        elif kind == 'integer':
            integer(obs[key], key, 0, 10**9)
        else:
            number(obs[key], key, -1e12, 1e12)
    rows = []
    for ident, key, kind, lo, hi, mitigation in CHECKS:
        if ident not in requested:
            continue
        if key not in obs:
            status = 'unknown'
            value = None
        else:
            value = obs[key]
            val = abs(value) if kind == 'abs_number' else value
            status = 'pass' if (val is lo if kind == 'boolean' else lo <= val <= hi) else 'fail'
        rows.append({'id': ident, 'field': key, 'status': status, 'observed': value,
                     'policy_bounds': [lo, hi], 'mitigation': mitigation if status != 'pass' else None})
    counts = dict(collections.Counter(r['status'] for r in rows))
    return {'checks': rows, 'counts': counts, 'checked_denominator': len(rows), 'registered_denominator': 24,
            'status': 'failed_controls' if counts.get('fail') else 'insufficient_evidence' if counts.get('unknown') else 'supplied_controls_passed',
            'evidence': evidence, 'input_sha256': digest(args), 'claim_ceiling': 'C1 supplied-input mechanics',
            'limitations': 'Threshold compliance is not a forecast, verified measurement provenance, coverage of unknown hazards, or trading authorization.',
            'trade_authorized': False, 'guaranteed_win_rate': None}


def portfolio_stress(args):
    fields(args, ('positions', 'scenarios', 'cash', 'max_loss'), ('positions', 'scenarios'))
    positions, scenarios = args['positions'], args['scenarios']
    if type(positions) is not list or not 1 <= len(positions) <= 64 or type(scenarios) is not list or not 1 <= len(scenarios) <= 256:
        raise ValueError('Positions cap 1..64 and scenarios cap 1..256')
    notionals = {}
    for row in positions:
        fields(row, ('symbol', 'notional'), ('symbol', 'notional'))
        symbol = text(row['symbol'], 'symbol', 32)
        if symbol in notionals:
            raise ValueError('Duplicate position symbol')
        notionals[symbol] = number(row['notional'], 'notional', -1e12, 1e12)
    cash = number(args.get('cash', 0), 'cash', 0, 1e12)
    equity = cash + sum(notionals.values())
    if equity <= 0:
        raise ValueError('Positive starting equity required')
    max_loss = number(args.get('max_loss', equity), 'max_loss', 0, 1e12)
    rows, ids = [], set()
    for scenario in scenarios:
        fields(scenario, ('id', 'shocks', 'transaction_cost'), ('id', 'shocks'))
        ident = text(scenario['id'], 'scenario id', 120)
        if ident in ids:
            raise ValueError('Unique scenario IDs required')
        ids.add(ident)
        fields(scenario['shocks'], notionals.keys(), notionals.keys())
        pnl = sum(notionals[s] * number(v, 'fractional shock', -1, 10) for s, v in scenario['shocks'].items())
        cost = number(scenario.get('transaction_cost', 0), 'transaction cost', 0, 1e12)
        pnl -= cost
        rows.append({'id': ident, 'pnl': pnl, 'ending_equity': equity + pnl,
                     'loss_fraction': max(0, -pnl) / equity, 'loss_budget_failed': -pnl > max_loss})
    worst = min(rows, key=lambda r: (r['pnl'], r['id']))
    return {'initial_equity': equity, 'gross_exposure': sum(abs(v) for v in notionals.values()),
            'worst_declared_scenario': worst, 'scenarios': rows, 'input_sha256': digest(args),
            'cash_control': {'pnl': 0, 'scope': 'all-cash with no investment or transaction costs'},
            'claim_ceiling': 'C1 linear supplied-scenario accounting', 'time_complexity': 'O(s * p)', 'space_complexity': 'O(s + p)',
            'limitations': 'No scenario probabilities, VaR confidence, options/nonlinear pricing, broker fills or future profit are inferred.',
            'trade_authorized': False}


def frontier(args):
    fields(args, ('round', 'observations', 'max_suggestions'))
    round_no = integer(args.get('round', 1), 'round', 1, 3)
    limit = integer(args.get('max_suggestions', 8), 'max_suggestions', 1, 16)
    result = probe({'observations': args.get('observations', {})})
    suggestions = [
        {'kind': 'within', 'question': r['mitigation'], 'evidence': [r['id'], result['input_sha256']],
         'claim_ceiling': 'C0 hypothesis', 'falsifier': 'Fail the corresponding frozen control or lose advantage to a simpler baseline.',
         'cost_risk_budget': 'local supplied-data test; zero financial writes', 'stop_rule': 'one frozen experiment, preserve failure'}
        for r in result['checks'] if r['status'] != 'pass'
    ]
    outside = [
        ('stocks', 'Concentration, correlated gap-down shocks, trading halts, delisting and corporate-action adjustments.'),
        ('operations', 'Partial API outages, duplicate delivery, disk exhaustion, state races and deployment rollback.'),
        ('research', 'Selection bias, outcome leakage, missing sensors, behaviorally duplicate rules and stale manifests.'),
        ('model_risk', 'Regime shift, probability miscalibration, adversarial feeds and out-of-distribution decisions.'),
        ('security', 'Least privilege, credential exposure, supply-chain provenance and prompt/tool input boundaries.'),
        ('exotic_frontiers', 'Require measured hardware/physical correspondence before any Section 7 mechanism promotion.')
    ]
    suggestions += [{'kind': 'outside', 'domain': domain, 'question': q, 'evidence': ['declared frontier v1'],
                     'claim_ceiling': 'C0 hypothesis', 'falsifier': 'No executable evaluator, no measurement mapping, or no held-out gain.',
                     'cost_risk_budget': 'zero spend; no external mutation', 'stop_rule': 'three rounds total, frozen declared scope'} for domain, q in outside]
    return {'round': round_no, 'max_rounds': 3, 'suggestions': suggestions[:limit],
            'outside_frontiers': suggestions[-len(outside):], 'remaining_unlisted': max(0, len(suggestions) - limit),
            'stop': round_no == 3, 'claim_ceiling': 'C0 research questions; C1 bounded routing',
            'unbounded_iteration': False, 'global_optimum_claim': False}


def unified_probe(args):
    fields(args, ('question', 'domain', 'observations', 'portfolio', 'evidence', 'max_candidates', 'round'), ('question', 'domain', 'observations'))
    framing = frame_problem({k: args[k] for k in ('question', 'domain', 'evidence', 'max_candidates') if k in args})
    risk = probe({'observations': args['observations'], 'evidence': args.get('evidence', [])})
    stress = portfolio_stress(args['portfolio']) if 'portfolio' in args else None
    followup = frontier({'round': args.get('round', 1), 'observations': args['observations']})
    return {'cabs_framing': framing, 'risk_atlas': risk, 'portfolio_stress': stress, 'frontiers': followup,
            'input_sha256': digest(args), 'claim_ceiling': 'C1 finite composition/accounting; C0 domain hypotheses',
            'big_o': {'cabs_search': framing['cabs']['search_big_o'], 'risk_controls': 'O(c)', 'portfolio': 'O(s*p)',
                      'total': 'O(CABS_search + c + s*p); no domain-independent speedup or optimum.'},
            'decision': 'Research receipt only; unresolved controls and budgets remain explicit.', 'trade_authorized': False}


def robust_search(args):
    fields(args, ('candidates', 'scenario_ids', 'max_loss', 'max_compute_cost', 'seed'), ('candidates', 'scenario_ids', 'max_loss', 'max_compute_cost'))
    candidates, scenarios = args['candidates'], args['scenario_ids']
    if type(candidates) is not list or not 1 <= len(candidates) <= 128 or type(scenarios) is not list or not 1 <= len(scenarios) <= 256:
        raise ValueError('Finite caps: 128 candidates and 256 scenarios')
    for ident in scenarios:
        text(ident, 'scenario id', 120)
    if len(set(scenarios)) != len(scenarios):
        raise ValueError('Unique scenario IDs required')
    max_loss = number(args['max_loss'], 'loss budget', 0, 1e12)
    cost_budget = number(args['max_compute_cost'], 'compute budget', 0, 1e12)
    seed = integer(args.get('seed', 42), 'seed', 0, 2**31 - 1)
    scored, ids = [], {'no_action'}
    for candidate in candidates:
        fields(candidate, ('id', 'scenario_scores', 'compute_cost'), ('id', 'scenario_scores', 'compute_cost'))
        ident = text(candidate['id'], 'candidate id', 120)
        if ident in ids:
            raise ValueError('Candidate IDs must be unique; no_action is reserved')
        ids.add(ident)
        values = candidate['scenario_scores']
        fields(values, scenarios, scenarios)
        scores = [number(values[s], 'scenario score', -1e12, 1e12) for s in scenarios]
        cost = number(candidate['compute_cost'], 'compute cost', 0, 1e12)
        worst = min(scores)
        scored.append({'id': ident, 'worst_score': worst, 'mean_score': sum(scores) / len(scores),
                       'compute_cost': cost, 'feasible': max(0, -worst) <= max_loss and cost <= cost_budget})
    feasible = [r for r in scored if r['feasible']]
    cash = {'id': 'no_action', 'worst_score': 0.0, 'mean_score': 0.0, 'compute_cost': 0.0, 'feasible': True}
    ranked = sorted(feasible + [cash], key=lambda r: (-r['worst_score'], r['compute_cost'], -r['mean_score'], r['id']))
    random_control = random.Random(seed).choice(feasible + [cash])
    return {'selected': ranked[0], 'finite_candidates': len(candidates) + 1, 'scenarios': len(scenarios),
            'ranked': ranked, 'rejected': [r for r in scored if not r['feasible']], 'no_action_control': cash,
            'equal_budget_random_control': random_control, 'seed': seed, 'input_sha256': digest(args),
            'criterion': 'Maximize worst supplied scenario score; ties prefer lower compute cost, then mean score.',
            'time_complexity': 'O(a*s + a*log(a))', 'space_complexity': 'O(a + s) excluding supplied score matrix',
            'claim_ceiling': 'C1 finite minimax accounting; C0 real-world utility',
            'falsifier': 'Independent checker disagreement, held-out score reversal, missing scenario or better simpler baseline.',
            'stop_rule': 'One frozen finite enumeration; no retuning from unseen outcomes.', 'global_optimum_claim': False,
            'trade_authorized': False}


def alert_activity(args):
    fields(args, ('timestamps', 'start', 'end', 'timezone'), ('timestamps', 'start', 'end'))
    timestamps = args['timestamps']
    if type(timestamps) is not list or len(timestamps) > 10000:
        raise ValueError('Timestamp list cap 10000')
    start = number(args['start'], 'start', 0, 253402214400)
    end = number(args['end'], 'end', 0, 253402214400)
    if not start < end or end - start > 366 * 86400:
        raise ValueError('Positive observation horizon at most 366 days')
    tz = ZoneInfo(args.get('timezone', 'America/Los_Angeles'))
    rows = [number(v, 'timestamp', 0, 253402214400) for v in timestamps]
    if any(not start <= v < end for v in rows):
        raise ValueError('Alert timestamps must be within [start, end)')
    exposures = [0.0] * 4
    point = start
    while point < end:
        following = min(end, (math.floor(point / 60) + 1) * 60)
        band = dt.datetime.fromtimestamp(point, tz).hour // 6
        last_band = dt.datetime.fromtimestamp(max(point, following - 0.00001), tz).hour // 6
        if band != last_band:
            # Locate an actual local-band boundary, including historic second offsets and DST.
            left, right = point, following
            for _ in range(40):
                middle = (left + right) / 2
                if dt.datetime.fromtimestamp(middle, tz).hour // 6 == band:
                    left = middle
                else:
                    right = middle
            exposures[band] += right - point
            exposures[last_band] += following - right
        else:
            exposures[band] += following - point
        point = following
    bands = []
    for index, (lo, hi) in enumerate([(0, 6), (6, 12), (12, 18), (18, 24)]):
        exposure = exposures[index]
        count = sum(lo <= dt.datetime.fromtimestamp(v, tz).hour < hi for v in rows)
        bands.append({'local_hours': f'{lo:02}:00-{hi:02}:00', 'observed_hours': exposure / 3600,
                      'alerts': count, 'alerts_per_hour': count / (exposure / 3600) if exposure else None})
    return {'timezone': str(tz), 'alerts': len(rows), 'observed_hours': (end - start) / 3600,
            'alerts_per_hour': len(rows) / ((end - start) / 3600), 'time_bands': bands,
            'counts_are': 'Supplied sent-alert events; not broker-confirmed bets.', 'claim_ceiling': 'C1 counting; C2 if authentic historical timestamps',
            'forecast': None}
