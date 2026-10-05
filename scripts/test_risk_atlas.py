"""Independent arithmetic, fault-injection and protocol controls; no market edge claim."""
import copy
from decimal import Decimal
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import risk_atlas as A
import risk_atlas_mcp as M


def healthy():
    values = {}
    for ident, field, kind, lo, hi, _ in A.CHECKS:
        values[field] = lo if kind in ('integer', 'boolean') else (lo + hi) / 2
    return values


def fault(row):
    _, _, kind, lo, hi, _ = row
    if row[0] == 'displayed_depth':
        return 0
    if kind == 'boolean':
        return not lo
    if kind == 'integer':
        return hi + 1
    return hi + max(1, abs(hi) / 10)


class RiskControls(unittest.TestCase):
    def test_exact_catalog_denominator_and_catalog_only(self):
        rows = []
        for offset in range(0, 240, 40):
            result = A.catalog({'offset': offset, 'limit': 40})
            rows += result['scenarios']
            self.assertFalse(result['universal_coverage'])
            self.assertEqual(result['validated_exotic_backends'], 0)
        self.assertEqual(len({r['id'] for r in rows}), 240)
        self.assertEqual(len({r['family'] for r in rows}), 60)
        self.assertEqual(sum(r['status'] == 'catalog_only' for r in rows), 24)
        self.assertEqual(sum(r.get('original_section7_label', False) for r in rows), 12)

    def test_every_operational_fault_and_every_missing_measurement(self):
        base = healthy()
        self.assertEqual(A.probe({'observations': base})['counts'], {'pass': 24})
        for row in A.CHECKS:
            with self.subTest(check=row[0]):
                obs = dict(base, **{row[1]: fault(row)})
                result = A.probe({'observations': obs})
                self.assertEqual(result['counts'], {'pass': 23, 'fail': 1})
                self.assertFalse(result['trade_authorized'])
                del obs[row[1]]
                result = A.probe({'observations': obs})
                self.assertEqual(result['counts'], {'pass': 23, 'unknown': 1})
                self.assertEqual(result['status'], 'insufficient_evidence')

    def test_complete_pairwise_operational_fault_universe(self):
        tested = 0
        for left, right in itertools.combinations(A.CHECKS, 2):
            obs = healthy()
            obs[left[1]], obs[right[1]] = fault(left), fault(right)
            result = A.probe({'observations': obs})
            self.assertEqual(result['counts'], {'pass': 22, 'fail': 2})
            tested += 1
        self.assertEqual(tested, 276)

    def test_numeric_type_finiteness_unknown_and_bool_controls(self):
        for val in [float('nan'), float('inf'), -float('inf'), True, '0']:
            with self.assertRaises(ValueError):
                A.probe({'observations': {'quote_age_seconds': val}})
        for obs in [{'quote_age_seconds': 0, 'catastrophe_ignored': True}, {'fills_verified': 1}, {'scan_error_count': 0.0}]:
            with self.assertRaises(ValueError):
                A.probe({'observations': obs})
        self.assertEqual(A.probe({'observations': {'quote_age_seconds': -1}, 'checks': ['quote_freshness']})['counts'], {'fail': 1})
        self.assertEqual(A.probe({'observations': {'basis_drift_bps': -15}, 'checks': ['feed_agreement']})['counts'], {'fail': 1})

    def test_real_source_manifest_drift_fails_closed(self):
        real = A.ROOT / 'catalog/risk_atlas_240.json'
        original = Path.read_bytes
        def altered(path):
            return original(path) + b' ' if path == real else original(path)
        with patch.object(Path, 'read_bytes', altered):
            with self.assertRaisesRegex(ValueError, 'manifest stale'):
                A.catalog({})

    def test_in_memory_runtime_rejects_refreshed_manifest(self):
        original = Path.read_bytes
        def refreshed(path):
            return original(path) + b' ' if path == A.MANIFEST else original(path)
        with patch.object(Path, 'read_bytes', refreshed):
            with self.assertRaisesRegex(ValueError, 'changed since startup'):
                M.dispatch('atlas_catalog', {}, M.Adapter())

    def test_legacy_boundary_blocks_unmeasured_and_malformed_inputs(self):
        trade = {'asset': 'BTC', 'side': 'YES', 'price': .62, 'rem': 6., 'norm_lead': 10., 'lead_bps': 10.}
        ident = A.load_catalog()['scenarios'][209]['id']
        result = A.scenario_probe({'scenario_ids': [ident], 'trade': trade})
        self.assertEqual(result['scenarios'][0]['status'], 'insufficient_measurements')
        self.assertTrue(result['scenarios'][0]['missing_synthetic_fields'])
        self.assertFalse(result['scenarios'][0]['execution_ready'])
        self.assertGreater(result['legacy_missing_sensor_count'], 100)
        for key, val in [('asset', 'UNKNOWN'), ('side', 'UNKNOWN'), ('price', float('nan')),
                         ('lead_bps', float('inf')), ('rem', True), ('catastrophic_hidden_flag', True)]:
            with self.assertRaises(ValueError):
                A.scenario_probe({'scenario_ids': [ident], 'trade': dict(trade, **{key: val})})
        new_id = A.load_catalog()['scenarios'][216]['id']
        self.assertEqual(A.scenario_probe({'scenario_ids': [new_id], 'trade': trade})['scenarios'][0]['status'], 'catalog_only')
        for key in ['exchange_circuit_breaker', 'is_shock', 'private_mempool_routed', 'terminal_settlement_dispute']:
            self.assertEqual(A.L.SENSOR_TYPES[key], 'boolean')
            for value in (True, False):
                result = A.scenario_probe({'scenario_ids': [ident], 'trade': dict(trade, **{key: value})})
                self.assertFalse(result['trade_authorized'])

    def test_portfolio_arithmetic_against_decimal_oracle(self):
        args = {'positions': [{'symbol': 'A', 'notional': 100}, {'symbol': 'B', 'notional': 200}], 'cash': 50,
                'max_loss': 30, 'scenarios': [{'id': 'gap', 'shocks': {'A': -.5, 'B': .1}, 'transaction_cost': 2}]}
        result = A.portfolio_stress(args)
        expected = Decimal('100') * Decimal('-.5') + Decimal('200') * Decimal('.1') - Decimal('2')
        self.assertEqual(result['scenarios'][0]['pnl'], float(expected))
        self.assertTrue(result['scenarios'][0]['loss_budget_failed'])
        self.assertEqual(result['cash_control']['pnl'], 0)
        for scenario in [{'id': 'bad', 'shocks': {'A': -.5}}, {'id': 'bad', 'shocks': {'A': -.5, 'B': .1, 'Z': 0}}]:
            with self.assertRaises(ValueError):
                A.portfolio_stress(dict(args, scenarios=[scenario]))

    def test_minimax_cash_baseline_budget_and_independent_order(self):
        args = {'scenario_ids': ['a', 'b'], 'max_loss': 5, 'max_compute_cost': 3, 'candidates': [
            {'id': 'hindsight_gain', 'scenario_scores': {'a': 100, 'b': -20}, 'compute_cost': 1},
            {'id': 'stable', 'scenario_scores': {'a': 2, 'b': 1}, 'compute_cost': 2},
            {'id': 'expensive', 'scenario_scores': {'a': 50, 'b': 50}, 'compute_cost': 4}]}
        result = A.robust_search(args)
        self.assertEqual(result['selected']['id'], 'stable')
        self.assertEqual({r['id'] for r in result['rejected']}, {'hindsight_gain', 'expensive'})
        self.assertEqual(A.robust_search(dict(args, candidates=args['candidates'][:1]))['selected']['id'], 'no_action')
        self.assertEqual(A.robust_search(args)['equal_budget_random_control'], result['equal_budget_random_control'])

    def test_cabs_actual_composition_and_apriori_negative_control(self):
        result = A.frame_problem({'question': 'Find missing stock-risk measurements', 'domain': 'stocks'})
        self.assertGreater(result['cabs']['plan_matches'], 0)
        self.assertFalse(result['cabs']['all_possible_questions_covered'])
        bad = {'atoms': [[[0, '1']], [[0, '2']]], 'target': [[0, '3']], 'strategy': 'apriori',
               'accepted_masks': [0, 3], 'max_items': 2, 'max_candidates': 4}
        with self.assertRaises(ValueError):
            A.C.search({'mode': 'subsets', 'task': bad})
        unknown = A.C.compose_costs({'terms': [{'n': 1}]}, {'unknown': True}, 'sequence')
        self.assertTrue(unknown['unknown'])

    def test_unified_and_bounded_external_frontiers(self):
        result = A.unified_probe({'question': 'Mitigate portfolio and alert failure', 'domain': 'stocks', 'observations': {}})
        self.assertEqual(result['risk_atlas']['counts'], {'unknown': 24})
        self.assertGreater(result['cabs_framing']['cabs']['plan_matches'], 0)
        self.assertEqual(len(A.frontier({'round': 3})['outside_frontiers']), 6)
        self.assertTrue(A.frontier({'round': 3})['stop'])
        with self.assertRaises(ValueError):
            A.frontier({'round': 4})

    def test_alert_quiet_exposure_and_half_open_boundary(self):
        start = 1791158400
        result = A.alert_activity({'timestamps': [start + 600], 'start': start, 'end': start + 7200})
        self.assertEqual(result['observed_hours'], 2)
        self.assertEqual(result['alerts_per_hour'], .5)
        self.assertAlmostEqual(sum(r['observed_hours'] for r in result['time_bands']), 2)
        with self.assertRaises(ValueError):
            A.alert_activity({'timestamps': [start + 7200], 'start': start, 'end': start + 7200})

    def test_historic_subminute_timezone_boundary(self):
        result = A.alert_activity({'timestamps': [24240], 'start': 24240, 'end': 24300, 'timezone': 'Africa/Monrovia'})
        self.assertEqual(result['time_bands'][0]['alerts'], 1)
        self.assertAlmostEqual(result['time_bands'][0]['observed_hours'], 30 / 3600, places=8)
        self.assertAlmostEqual(result['time_bands'][1]['observed_hours'], 30 / 3600, places=8)


class ProtocolControls(unittest.TestCase):
    script = Path(M.__file__)

    def rpc(self, lines):
        payload = '\n'.join(v if isinstance(v, str) else json.dumps(v) for v in lines) + '\n'
        r = subprocess.run([sys.executable, str(self.script)], input=payload, capture_output=True, text=True, timeout=20)
        self.assertEqual(r.returncode, 0, r.stderr)
        return [json.loads(line) for line in r.stdout.splitlines()]

    def init(self):
        return [{'jsonrpc': '2.0', 'id': 'hello', 'method': 'initialize', 'params': {'protocolVersion': '2025-11-25'}},
                {'jsonrpc': '2.0', 'method': 'notifications/initialized'}]

    def test_real_protocol_lifecycle_notifications_and_tool_call(self):
        rows = self.rpc(self.init() + [
            {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list', 'params': {'cursor': None, '_meta': {}}},
            {'jsonrpc': '2.0', 'method': 'notifications/ignored'},
            {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call', 'params': {'name': 'atlas_probe', 'arguments': {'observations': {}}}}])
        self.assertEqual(len(rows), 3)
        self.assertEqual(len(rows[1]['result']['tools']), 8)
        self.assertEqual(rows[2]['result']['structuredContent']['counts'], {'unknown': 24})

    def test_unknown_fields_fail_closed_and_initialization_gate(self):
        rows = self.rpc([{'jsonrpc': '2.0', 'id': 0, 'method': 'tools/list'}])
        self.assertIn('error', rows[0])
        rows = self.rpc(self.init() + [{'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params':
                                       {'name': 'atlas_probe', 'arguments': {'observations': {}, 'execute_order': True}}}])
        self.assertTrue(rows[-1]['result']['isError'])

    def test_json_parse_duplicate_nan_and_frame_recovery(self):
        rows = self.rpc(['{bad}', '{"jsonrpc":"2.0","id":1,"id":2,"method":"ping"}',
                         '{"jsonrpc":"2.0","id":3,"method":"ping","params":{"x":NaN}}',
                         ' ' * (M.FRAME_CAP + 10), {'jsonrpc': '2.0', 'id': 4, 'method': 'ping'}])
        self.assertEqual(rows[0]['error']['code'], -32700)
        self.assertTrue(all('error' in r for r in rows[:4]))
        self.assertEqual(rows[-1]['result'], {})

    def test_unavailable_and_changed_as3_adapter(self):
        with self.assertRaises(ValueError):
            M.Adapter().replay({'trades': []})
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'fixture.exe'
            p.write_bytes(b'not executable')
            with self.assertRaisesRegex(ValueError, 'manifest stale'):
                M.Adapter(p, '0' * 64).replay({'trades': []})

    def test_malformed_child_outputs_fail_as_tool_errors(self):
        outputs = [[], {'jsonrpc': '2.0', 'id': 2, 'result': []},
                   {'jsonrpc': '2.0', 'id': 2, 'result': {'content': []}},
                   {'jsonrpc': '2.0', 'id': 2, 'result': {'content': [7]}},
                   {'jsonrpc': '2.0', 'id': 2, 'result': {'content': [{'type': 'text', 'text': '7'}]}},
                   {'jsonrpc': '2.0', 'id': 2, 'result': {'content': [{'type': 'text', 'text': '{"x":NaN}'}]}}]
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'fixture.exe'
            p.write_bytes(b'fixture')
            adapter = M.Adapter(p, hashlib.sha256(p.read_bytes()).hexdigest())
            for output in outputs:
                child = subprocess.CompletedProcess([], 0, stdout=json.dumps(output) + '\n', stderr='')
                with self.subTest(output=output), patch.object(M.subprocess, 'run', return_value=child):
                    with self.assertRaises(ValueError):
                        adapter.replay({'trades': []})


if __name__ == '__main__':
    unittest.main()
