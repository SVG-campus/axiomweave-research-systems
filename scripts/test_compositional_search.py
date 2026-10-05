"""Independent finite controls for composition, cancellation and coverage claims."""
import copy
import itertools
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
import compositional_search as C
import cabs_mcp as M


class CabsTests(unittest.TestCase):
    def task(self):
        return {"atoms": [
            {"id": "gen", "input": "question", "output": "candidate", "capabilities": ["generate"],
             "time": {"terms": [{"n": 1}]}, "space": {"terms": [{"n": 1}]}},
            {"id": "tool", "input": "candidate", "output": "result", "capabilities": ["solve"],
             "time": {"terms": [{"n": 2}]}, "space": {"terms": [{"n": 1}]}},
            {"id": "check", "input": "result", "output": "certificate", "capabilities": ["check"],
             "time": {"terms": [{"n": 1}]}, "space": {"terms": [{}]}}],
            "input_type": "question", "output_type": "certificate", "required_capabilities": ["solve", "check"],
            "operators": ["sequence", "portfolio"], "max_leaves": 3}

    def test_exact_cost_composition_and_unknowns(self):
        linear = {"terms": [{"n": 1}]}
        square = {"terms": [{"n": 2}]}
        log = {"terms": [{"log_n": 1}]}
        self.assertEqual(C.compose_costs(linear, square, "sequence")["terms"], [{"n": 2}])
        self.assertEqual(C.compose_costs(square, log, "nested")["terms"], [{"log_n": 1, "n": 2}])
        composed = C.compose_costs(linear, square, "sequence")
        self.assertEqual(C.compose_costs(composed, log, "nested")["terms"], [{"log_n": 1, "n": 2}])
        self.assertTrue(C.compose_costs({"unknown": True}, linear, "sequence")["unknown"])
        self.assertFalse(C.Cost.read(None).no_larger_than(C.Cost.read(square)))
        self.assertFalse(C.Cost.read({"terms": [{"n": 1}]}).no_larger_than(C.Cost.read({"terms": [{"m": 1}]})))
        self.assertFalse(C.Cost.read({"terms": [{"pow_n_d": 1}]}).no_larger_than(C.Cost.read(square)))
        for bad in [True, False, -1, 100, 1.2]:
            with self.assertRaises(ValueError):
                C.Cost.read({"terms": [{"n": bad}]})

    def test_type_count_against_independent_binary_tree_oracle(self):
        task = self.task()
        atoms = task["atoms"]
        def oracle(left, right, op):
            if op == "sequence" and left[1] == right[0]:
                return left[0], right[1]
            if op == "portfolio" and left == right:
                return left
            return None
        count = len(atoms)
        types = [(r["input"], r["output"]) for r in atoms]
        for left, right, op in itertools.product(types, types, task["operators"]):
            count += oracle(left, right, op) is not None
        for a, b, c, op1, op2 in itertools.product(types, types, types, task["operators"], task["operators"]):
            ab, bc = oracle(a, b, op1), oracle(b, c, op2)
            count += ab is not None and oracle(ab, c, op2) is not None
            count += bc is not None and oracle(a, bc, op1) is not None
        result = C.plan_search(task)
        self.assertEqual(result["typed_syntactic_universe"], count)
        self.assertEqual(result["generated"], count)
        self.assertEqual(result["plan_matches"], 2)
        self.assertTrue(result["full_finite_enumeration"])
        self.assertEqual(result["validated_domain_solutions"], [])
        self.assertFalse(result["all_possible_questions_covered"])
        for plan in result["pareto_plans"]:
            self.assertEqual(plan["time"]["terms"], [{"n": 2}])

    def test_beam_misses_known_plan_and_cap_is_reported(self):
        task = self.task()
        full = C.plan_search(task)
        narrow = C.plan_search({**task, "strategy": "beam", "beam_width": 1})
        self.assertGreater(full["plan_matches"], narrow["plan_matches"])
        self.assertFalse(narrow["beam_complete"])
        capped = C.plan_search({**task, "max_candidates": 1})
        self.assertFalse(capped["full_finite_enumeration"])
        self.assertEqual(capped["stop_reason"], "candidate cap")

    def test_cancellation_preserved_and_nonhereditary_pruning_refused(self):
        task = {"atoms": [[[-2, "1"]], [[-2, "-1"], [2, "1"]]], "target": [[2, "1"]]}
        result = C.subset_search(task)
        self.assertEqual([h["mask"] for h in result["exact_hits"]], [3])
        self.assertTrue(result["full_finite_enumeration"])
        for t in [Fraction(1, 2), Fraction(1, 3), Fraction(2), Fraction(7)]:
            self.assertEqual(t**-2 + (-t**-2 + t**2), t**2)
        with self.assertRaisesRegex(ValueError, "Unsafe Apriori"):
            C.subset_search({**task, "strategy": "apriori", "accepted_masks": [0, 3]})
        with self.assertRaisesRegex(ValueError, "predicate"):
            C.subset_search({**task, "strategy": "apriori"})

    def test_apriori_differential_and_false_target_controls(self):
        atoms = [[[0, str(i)]] for i in [1, 2, 4, 8]]
        # Nonnegative total weight <= 6 is downward closed.
        accepted = [m for m in range(16) if sum(v for i, v in enumerate([1, 2, 4, 8]) if m >> i & 1) <= 6]
        for target in range(16):
            task = {"atoms": atoms, "target": [[0, str(target)]], "accepted_masks": accepted}
            exact = C.subset_search(task)
            apriori = C.subset_search({**task, "strategy": "apriori"})
            self.assertEqual([h["mask"] for h in exact["exact_hits"]], [h["mask"] for h in apriori["exact_hits"]])
            self.assertTrue(apriori["apriori_audit"]["hereditary"])
            self.assertTrue(apriori["complete_on_frozen_feasible_universe"])
        self.assertFalse(C.subset_search({"atoms": atoms, "target": [[0, "99"]]})["exact_hits"])

    def test_symbolic_beam_pair_lookahead_and_tampered_certificate(self):
        task = {"atoms": [[[0, "9"]], [[0, "10"]], [[0, "-9"]]], "target": [[0, "1"]],
                "strategy": "beam", "beam_width": 1, "max_items": 2}
        self.assertFalse(C.subset_search(task)["exact_hits"])
        preserved = {**task, "preserve_pairs": True}
        out = C.subset_search(preserved)
        self.assertEqual([h["mask"] for h in out["exact_hits"]], [6])
        certificate = out["exact_hits"][0]
        self.assertTrue(C.verify_subset_hit(preserved, certificate))
        self.assertFalse(C.verify_subset_hit(preserved, {**certificate, "mask": 1}))
        self.assertFalse(C.verify_subset_hit(preserved, {**certificate, "sum": [[0, "99"]]}))
        changed = copy.deepcopy(preserved)
        changed["atoms"][1] = [[0, "12"]]
        self.assertFalse(C.verify_subset_hit(changed, certificate))

    def test_seed_and_hostile_or_unbounded_tasks(self):
        task = {"atoms": [[[0, "1"]], [[0, "2"]], [[0, "3"]]], "target": [[0, "3"]],
                "strategy": "random", "seed": 20261005, "max_candidates": 4}
        self.assertEqual(C.subset_search(task), C.subset_search(task))
        for key, value in [("max_candidates", True), ("max_items", 9), ("max_candidates", 257), ("seed", -1)]:
            with self.assertRaises(ValueError):
                C.subset_search({**task, key: value})
        for coefficient in ["__import__('os')", "1/0", "1" * 100]:
            with self.assertRaises((ValueError, ZeroDivisionError)):
                C.subset_search({"atoms": [[[0, coefficient]]], "target": []})
        with self.assertRaises(ValueError):
            C.plan_search({**self.task(), "strategy": "apriori"})

    def test_new_tool_inventory_is_nonexecuting_and_quarantines_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = pathlib.Path(temp)
            source = directory / "source.py"
            marker = directory / "executed.txt"
            source.write_text(f"open({str(marker)!r}, 'w').write('must not run')\nTOOLS=[{{'name':'new_domain_tool'}}]\nTOOLS.extend(dynamic())\n")
            inv = C.discover_source(source, "future")
            self.assertFalse(marker.exists())
            self.assertEqual(inv["tool_names"], ["new_domain_tool"])
            self.assertTrue(inv["unresolved_declaration_lines"])
            reg, new = C.extend_registry({"suites": []}, inv)
            self.assertEqual(new, ["future::new_domain_tool"])
            self.assertEqual(reg["suites"][0]["status"], "unreviewed")
            self.assertIsNone(reg["suites"][0]["time"])
            reg["suites"][0]["status"] = "reviewed_contract"
            changed, _ = C.extend_registry(reg, {**inv, "source_sha256": "changed"})
            self.assertEqual(changed["suites"][0]["status"], "unreviewed")

    def test_all_registered_suites_have_workable_development_grammars(self):
        registry = C.load_registry()
        self.assertEqual(len(registry["suites"]), 21)
        for row in registry["suites"]:
            task = C.suite_task(row["id"], registry)
            result = C.plan_search(task)
            self.assertGreater(result["plan_matches"], 0, row["id"])
            self.assertTrue(result["full_finite_enumeration"])
            self.assertFalse(result["all_possible_questions_covered"])
            self.assertTrue(result["pareto_plans"][0]["time"]["unknown"])

    def test_actual_stdio_protocol_and_negative_calls(self):
        reqs = [{"jsonrpc": "2.0", "id": 0, "method": "tools/list"},
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25"}},
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}]
        examples = [("cabs_catalog", {}), ("cabs_search", {"suite_id": "research::check_identity"}),
                    ("cabs_compose_costs", {"left": {"terms": [{"n": 1}]}, "right": {"terms": [{"n": 2}]}, "operator": "sequence"})]
        for i, (name, args) in enumerate(examples, 3):
            reqs.append({"jsonrpc": "2.0", "id": i, "method": "tools/call", "params": {"name": name, "arguments": args}})
        reqs.append({"jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": {"name": "cabs_search", "arguments": {"suite_id": "unknown"}}})
        result = subprocess.run([sys.executable, str(C.ROOT / "scripts/cabs_mcp.py")],
                                input="\n".join(map(json.dumps, reqs)) + "\n", capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        replies = {r["id"]: r for r in map(json.loads, result.stdout.splitlines())}
        self.assertIn("error", replies[0])
        self.assertEqual(len(replies[2]["result"]["tools"]), 3)
        for i in range(3, 6):
            self.assertFalse(replies[i]["result"]["isError"])
        self.assertTrue(replies[9]["result"]["isError"])
        self.assertNotIn(None, replies)


if __name__ == "__main__":
    unittest.main()
