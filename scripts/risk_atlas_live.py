"""Bounded, nonblocking diagnostic counters for an existing alert service.

No orders, credentials, state restore, strategy or sizing decisions.
"""
import collections
import json
import time


class Diagnostics:
    def __init__(self, clock=time.time, emit=print, interval=120):
        self.clock, self.emit, self.interval = clock, emit, interval
        self.started = self.last_report = clock()
        self.gates = collections.Counter()
        self.completed_scans = self.scan_errors = 0
        self.last_completed = None
        self.last_error = None

    def gate(self, asset, side, ident, predicate):
        try:
            if asset not in ('BTC', 'ETH', 'SOL', 'DOGE', 'XRP') or side not in ('YES', 'NO'):
                return
            key = f'{asset}:{side}:{ident}'
            if key not in self.gates and len(self.gates) >= 512:
                return
            self.gates[key] += 1
            self.report()
        except Exception:
            # Diagnostics cannot turn an otherwise valid selection into an error.
            return

    def scan(self, error=None):
        try:
            now = self.clock()
            if error is None:
                self.completed_scans += 1
                self.last_completed = now
            else:
                self.scan_errors += 1
                self.last_error = {'ts': now, 'type': type(error).__name__}
            self.report()
        except Exception:
            return

    def report(self, force=False):
        now = self.clock()
        if not force and now - self.last_report < self.interval:
            return
        value = {'timestamp': now, 'observed_seconds': max(0, now - self.started),
                 'completed_scans': self.completed_scans, 'scan_errors': self.scan_errors,
                 'last_completed_scan': self.last_completed, 'last_error': self.last_error,
                 'rejection_counts': dict(sorted(self.gates.items())),
                 'scope': 'cumulative observations since process start; repeated scans, not independent trades'}
        self.emit('[RISK ATLAS DIAGNOSTICS]: ' + json.dumps(value, allow_nan=False, separators=(',', ':')))
        self.last_report = now


_DIAGNOSTICS = Diagnostics()


def record_gate(asset, side, ident, predicate):
    _DIAGNOSTICS.gate(asset, side, ident, predicate)


def record_scan_completed():
    _DIAGNOSTICS.scan()


def record_scan_error(error):
    _DIAGNOSTICS.scan(error)
