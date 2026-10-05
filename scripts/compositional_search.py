"""AxiomWeave-CABS: finite typed composition and exact symbolic subset search.

No candidate code, network, dynamic imports, IDE configuration, or promotion.
Plans are C0 research proposals; exact synthetic mechanics are C1.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import math
import pathlib
import random
import time
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "catalog/search_suites.json"
COST_SYMBOLS = frozenset({"n", "m", "d", "p", "bits", "epochs", "log_n",
                          "log_m", "log_bits", "exp_n", "exp_d", "pow_n_d"})


def bounded_int(value, lower, upper):
    if type(value) is not int or not lower <= value <= upper:
        raise ValueError(f"Integer required in [{lower}, {upper}]")
    return value


def bounded_text(value, limit=120):
    if type(value) is not str or not 1 <= len(value) <= limit:
        raise ValueError("Nonempty bounded text required")
    return value


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def bounded_json(value):
    if len(json.dumps(value)) > 65536:
        raise ValueError("Task/registry entry exceeds 64 KiB")


@dataclass(frozen=True)
class Cost:
    """Upper-bound annotations under independent positive size variables.

    Dominance is sufficient componentwise dominance, deliberately conservative.
    pow_n_d is an opaque n**d factor, never compared with n**constant.
    Unknown propagates; an annotation is not a measured or proved complexity.
    """
    terms: tuple
    unknown: bool = False

    @classmethod
    def read(cls, data):
        if data is None:
            return cls((), True)
        if not isinstance(data, dict) or set(data) - {"terms", "unknown", "big_o", "basis"}:
            raise ValueError("Cost needs terms and optional unknown")
        if type(data.get("unknown", False)) is not bool:
            raise ValueError("Boolean unknown required")
        rows = data.get("terms", [])
        if not isinstance(rows, list) or len(rows) > 32:
            raise ValueError("Cost term cap 32")
        result = []
        for row in rows:
            if not isinstance(row, dict) or set(row) - COST_SYMBOLS:
                raise ValueError("Unsupported cost symbol")
            values = {k: bounded_int(v, 0, 32) for k, v in row.items()}
            result.append(tuple(sorted((k, v) for k, v in values.items() if v != 0)))
        if not result and not data.get("unknown", False):
            raise ValueError("Known costs need at least one term; {} denotes O(1)")
        return cls.normalize(result, data.get("unknown", False))

    @classmethod
    def normalize(cls, terms, unknown=False):
        rows = set(terms)
        # A <= B only if each independent exponent in A is <= its exponent in B.
        kept = []
        for row in rows:
            a = dict(row)
            if not any(row != other and all(v <= dict(other).get(k, 0) for k, v in a.items())
                       for other in rows):
                kept.append(row)
        if len(kept) > 32:
            raise ValueError("Cost expression cap exceeded")
        return cls(tuple(sorted(kept)), unknown)

    def add(self, other):
        return Cost.normalize(self.terms + other.terms, self.unknown or other.unknown)

    def multiply(self, other):
        rows = []
        for a, b in itertools.product(self.terms, other.terms):
            row = dict(a)
            for key, val in b:
                row[key] = bounded_int(row.get(key, 0) + val, 0, 32)
            rows.append(tuple(sorted(row.items())))
        return Cost.normalize(rows, self.unknown or other.unknown)

    def no_larger_than(self, other):
        if self.unknown or other.unknown:
            return False
        return all(any(all(v <= dict(b).get(k, 0) for k, v in a) for b in other.terms)
                   for a in self.terms)

    def record(self):
        def term(row):
            parts = []
            for k, v in row:
                name = {"log_n": "log(n)", "log_m": "log(m)", "log_bits": "log(bits)",
                        "exp_n": "2^n", "exp_d": "2^d", "pow_n_d": "n^d"}.get(k, k)
                parts.append(name if v == 1 else f"({name})^{v}")
            return " * ".join(parts) or "1"
        expression = " + ".join(term(r) for r in self.terms)
        if self.unknown:
            expression = (expression + " + " if expression else "") + "unknown"
        return {"terms": [dict(r) for r in self.terms], "unknown": self.unknown,
                "big_o": "O(" + expression + ")", "basis": "conditional supplied upper-bound annotations"}


def compose_costs(left, right, operator):
    a, b = Cost.read(left), Cost.read(right)
    if operator in {"sequence", "portfolio"}:
        # For a fixed number of nonnegative costs, O(sum) = O(max).
        return a.add(b).record()
    if operator == "nested":
        return a.multiply(b).record()
    raise ValueError("Cost operator must be sequence, portfolio or nested")


def load_registry(path=None):
    selected = pathlib.Path(path or REGISTRY)
    if selected.stat().st_size > 2_000_000:
        raise ValueError("Registry size cap 2 MB")
    value = json.loads(selected.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("suites"), list):
        raise ValueError("Registry needs suites")
    if len(value["suites"]) > 256:
        raise ValueError("Registry suite cap 256")
    seen = set()
    for row in value["suites"]:
        bounded_json(row)
        for key in ["id", "name", "domain", "input_representation", "candidate_objects",
                    "certificate", "falsifier", "limits", "search_variant"]:
            bounded_text(row[key], 1000)
        if row["id"] in seen:
            raise ValueError("Duplicate qualified suite ID")
        seen.add(row["id"])
        if row.get("status") not in {"reviewed_contract", "unreviewed"}:
            raise ValueError("Suite status must describe a contract, not proof")
        Cost.read(row.get("time"))
        Cost.read(row.get("space"))
    return value


def catalog(args=None):
    args = args or {}
    if set(args) - {"provider"}:
        raise ValueError("Unknown catalog argument")
    registry = load_registry()
    rows = registry["suites"]
    if "provider" in args:
        rows = [r for r in rows if r["id"].split("::", 1)[0] == args["provider"]]
    return {"name": "AxiomWeave-CABS", "suites": rows, "listed_contracts": len(rows),
            "registry_sha256": digest(registry), "all_possible_questions_covered": False,
            "registry_complete_for_universe": False, "claim_ceiling": "C0 proposed suite grammars"}


def discover_source(path, provider):
    """Read literal TOOLS declarations without importing or executing source.

    Dynamic declarations are explicitly unsupported, not silently exhaustive.
    """
    provider = bounded_text(provider)
    source = pathlib.Path(path).read_bytes()
    if len(source) > 2_000_000:
        raise ValueError("Source size cap 2 MB")
    tree = ast.parse(source.decode("utf-8-sig"))
    names = []
    unresolved = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AugAssign):
            targets, value = [node.target], node.value
        elif (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
              and isinstance(node.value.func, ast.Attribute)
              and isinstance(node.value.func.value, ast.Name) and node.value.func.value.id == "TOOLS"):
            unresolved.append(node.lineno)
            continue
        else:
            continue
        if not any(isinstance(t, ast.Name) and t.id == "TOOLS" for t in targets):
            continue
        if not isinstance(value, (ast.List, ast.Tuple)):
            unresolved.append(node.lineno)
            continue
        for item in value.elts:
            name = None
            if isinstance(item, (ast.List, ast.Tuple)) and item.elts:
                name = item.elts[0]
            elif isinstance(item, ast.Dict):
                name = next((v for k, v in zip(item.keys, item.values)
                             if isinstance(k, ast.Constant) and k.value == "name"), None)
            if not isinstance(name, ast.Constant) or not isinstance(name.value, str):
                unresolved.append(item.lineno)
                continue
            names.append(bounded_text(name.value))
    if len(names) != len(set(names)):
        raise ValueError("Duplicate tool name in provider")
    return {"provider": provider, "source_file": pathlib.Path(path).name,
            "source_sha256": hashlib.sha256(source).hexdigest(), "tool_names": names,
            "unresolved_declaration_lines": unresolved, "runtime_discovery_verified": False}


def extend_registry(registry, inventory):
    """Every new section is visible immediately but has no trusted evaluator/cost."""
    rows = {r["id"]: dict(r) for r in registry["suites"]}
    new = []
    for name in inventory["tool_names"]:
        ident = inventory["provider"] + "::" + name
        if ident in rows:
            # A changed source cannot inherit earlier review status silently.
            previous = rows[ident].get("source_sha256")
            if previous and previous != inventory["source_sha256"]:
                rows[ident]["status"] = "unreviewed"
                rows[ident]["limits"] = "Provider source changed; re-audit grammar, evaluator and cost."
            rows[ident]["source_sha256"] = inventory["source_sha256"]
            continue
        new.append(ident)
        rows[ident] = {"id": ident, "name": name, "domain": "unclassified",
                       "status": "unreviewed", "input_representation": "Owner-defined typed task",
                       "candidate_objects": "Declarative candidate grammar still required",
                       "certificate": "Independent domain checker still required",
                       "falsifier": "Wrong type, missing checker or failed negative control",
                       "limits": "Visible registration only; no executable scientific evaluator",
                       "search_variant": "CABS[" + name + "]", "time": None, "space": None,
                       "source_sha256": inventory["source_sha256"]}
    return {**registry, "suites": list(rows.values())}, new


def suite_task(suite_id, registry=None):
    registry = registry or load_registry()
    row = next((r for r in registry["suites"] if r["id"] == suite_id), None)
    if row is None:
        raise ValueError("Unknown qualified suite")
    domain = row["domain"]
    # These are research operations with typed interfaces, not installed backends.
    atoms = [
        {"id": "generate", "input": "question:" + domain, "output": "candidate:" + domain,
         "capabilities": ["generate"], "time": None, "space": None},
        {"id": "normalize", "input": "candidate:" + domain, "output": "candidate:" + domain,
         "capabilities": ["normalize"], "time": None, "space": None},
        {"id": row["name"], "input": "candidate:" + domain, "output": "result:" + domain,
         "capabilities": [row["name"]], "time": row.get("time"), "space": row.get("space")},
        {"id": "independent_check", "input": "result:" + domain, "output": "certificate:" + domain,
         "capabilities": ["independent_check"], "time": None, "space": None}]
    return {"suite_id": suite_id, "atoms": atoms, "input_type": "question:" + domain,
            "output_type": "certificate:" + domain, "required_capabilities": [row["name"], "independent_check"],
            "operators": ["sequence", "portfolio"], "max_leaves": 3,
            "strategy": "exhaustive", "max_candidates": 4096,
            "domain_status": row["status"], "semantic_obligations": [row["certificate"], row["limits"]]}


@dataclass(frozen=True)
class Plan:
    expression: str
    input_type: str
    output_type: str
    capabilities: frozenset
    time_cost: Cost
    space_cost: Cost
    leaves: int

    def record(self):
        return {"expression": self.expression, "input": self.input_type, "output": self.output_type,
                "capabilities": sorted(self.capabilities), "time": self.time_cost.record(),
                "space": self.space_cost.record(), "leaves": self.leaves,
                "claim_ceiling": "C0 typed research plan; no domain execution"}


def join_plan(a, b, op):
    if op == "sequence" and a.output_type == b.input_type:
        inp, out = a.input_type, b.output_type
        memory = a.space_cost.add(b.space_cost)  # safe upper bound; streaming may improve it
    elif op == "portfolio" and (a.input_type, a.output_type) == (b.input_type, b.output_type):
        inp, out = a.input_type, a.output_type
        memory = a.space_cost.add(b.space_cost)
    else:
        return None
    return Plan(f"{op}({a.expression},{b.expression})", inp, out,
                a.capabilities | b.capabilities, a.time_cost.add(b.time_cost), memory, a.leaves + b.leaves)


def typed_universe(atoms, operators, max_leaves):
    """Exact count of ordered, typed binary trees; no commutativity assumption."""
    levels = {1: Counter((p.input_type, p.output_type) for p in atoms)}
    for size in range(2, max_leaves + 1):
        counts = Counter()
        for split in range(1, size):
            for (ai, ao), ac in levels[split].items():
                for (bi, bo), bc in levels[size - split].items():
                    if "sequence" in operators and ao == bi:
                        counts[(ai, bo)] += ac * bc
                    if "portfolio" in operators and (ai, ao) == (bi, bo):
                        counts[(ai, ao)] += ac * bc
        levels[size] = counts
    return sum(sum(c.values()) for c in levels.values())


def plan_search(task):
    bounded_json(task)
    raw = task.get("atoms")
    if not isinstance(raw, list) or not 1 <= len(raw) <= 8:
        raise ValueError("Plan atom cap 1..8")
    atoms = []
    for row in raw:
        caps = row.get("capabilities", [])
        if not isinstance(caps, list) or len(caps) > 16:
            raise ValueError("Capability cap")
        atoms.append(Plan(bounded_text(row["id"]), bounded_text(row["input"]), bounded_text(row["output"]),
                          frozenset(bounded_text(c) for c in caps), Cost.read(row.get("time")),
                          Cost.read(row.get("space")), 1))
    if len({p.expression for p in atoms}) != len(atoms):
        raise ValueError("Unique atom IDs required")
    ops = task.get("operators", ["sequence", "portfolio"])
    if not isinstance(ops, list) or not ops or len(set(ops)) != len(ops) or set(ops) - {"sequence", "portfolio"}:
        raise ValueError("Plan operators are sequence and portfolio")
    size = bounded_int(task.get("max_leaves", 3), 1, 4)
    cap = bounded_int(task.get("max_candidates", 4096), 1, 4096)
    beam = bounded_int(task.get("beam_width", 8), 1, 128)
    strategy = task.get("strategy", "exhaustive")
    if strategy not in {"exhaustive", "beam"}:
        raise ValueError("Plan search supports exhaustive/beam; Apriori is for audited subsets")
    required_raw = task.get("required_capabilities", [])
    if not isinstance(required_raw, list):
        raise ValueError("Required capabilities must be a list")
    required = frozenset(required_raw)
    if len(required) > 16 or any(not isinstance(c, str) for c in required):
        raise ValueError("Invalid required capabilities")
    inp, out = bounded_text(task["input_type"]), bounded_text(task["output_type"])
    universe = typed_universe(atoms, ops, size)
    start = time.monotonic()
    generated, pool, matches = [], {}, []
    attempts = 0
    stop = "finite grammar exhausted"

    def score(p):
        return (len(required - p.capabilities), p.output_type != out, p.input_type != inp,
                p.time_cost.unknown, p.leaves, p.expression)

    for leaves in range(1, size + 1):
        layer = []
        if leaves == 1:
            candidates = iter(atoms)
        else:
            def candidates_for_level():
                nonlocal attempts
                for split in range(1, leaves):
                    for a, b, op in itertools.product(pool[split], pool[leaves - split], ops):
                        attempts += 1
                        if attempts > 100000 or time.monotonic() - start > 10:
                            return
                        plan = join_plan(a, b, op)
                        if plan is not None:
                            yield plan
            candidates = candidates_for_level()
        for p in candidates:
            if len(generated) >= cap:
                stop = "candidate cap"
                break
            layer.append(p)
            generated.append(p)
            if p.input_type == inp and p.output_type == out and required <= p.capabilities:
                matches.append(p)
        pool[leaves] = sorted(layer, key=score)[:beam] if strategy == "beam" else layer
        if stop == "candidate cap" or attempts > 100000 or time.monotonic() - start > 10:
            if stop != "candidate cap":
                stop = "attempt/time cap"
            break
    frontier = []
    for p in sorted(matches, key=score):
        # Only compare equivalent declared coverage; no arbitrary quality score.
        dominated = any(q.capabilities == p.capabilities and q.time_cost.no_larger_than(p.time_cost)
                        and q.space_cost.no_larger_than(p.space_cost)
                        and (q.time_cost != p.time_cost or q.space_cost != p.space_cost) for q in matches)
        if not dominated:
            frontier.append(p)
    return {"mode": "typed_plan", "strategy": strategy, "task_sha256": digest(task),
            "typed_syntactic_universe": universe, "generated": len(generated),
            "finite_grammar_coverage": len(generated) / universe,
            "full_finite_enumeration": len(generated) == universe and strategy == "exhaustive",
            "beam_complete": False if strategy == "beam" else None,
            "compositions_attempted": attempts, "plan_matches": len(matches),
            "pareto_plans": [p.record() for p in frontier[:16]], "stop_reason": stop,
            "claim_ceiling": "C1 type/search mechanics; C0 domain plans",
            "validated_domain_solutions": [], "all_possible_questions_covered": False,
            "semantic_obligations": task.get("semantic_obligations", []),
            "cost_note": "Portfolio time uses a conservative serial bound; no processor speedup asserted.",
            "search_big_o": "Exhaustive ordered trees: O(Catalan(k-1)*r^(k-1)*a^k*C_eval); binary beam expansion O(k^2*b^2*r*C_eval) plus sorting; caps and returned counters govern this run"}


def laurent(rows):
    if not isinstance(rows, list) or len(rows) > 32:
        raise ValueError("Laurent term cap 32")
    result = {}
    for row in rows:
        if not isinstance(row, list) or len(row) != 2:
            raise ValueError("Use [integer exponent, rational coefficient]")
        exponent = bounded_int(row[0], -16, 16)
        if type(row[1]) not in {str, int} or len(str(row[1])) > 80:
            raise ValueError("Bounded rational coefficient required")
        value = Fraction(row[1])
        if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > 128:
            raise ValueError("Rational bit cap")
        result[exponent] = result.get(exponent, Fraction(0)) + value
    return {e: v for e, v in result.items() if v}


def sum_terms(atoms, mask):
    result = {}
    for i, atom in enumerate(atoms):
        if mask & (1 << i):
            for e, v in atom.items():
                result[e] = result.get(e, Fraction(0)) + v
    return {e: v for e, v in result.items() if v}


def pruning_audit(accepted, atoms):
    """Every accepted child must have all immediate subsets accepted."""
    for child in range(1 << atoms):
        if child not in accepted:
            continue
        for i in range(atoms):
            if child & (1 << i) and child ^ (1 << i) not in accepted:
                return {"hereditary": False, "rejected_parent": child ^ (1 << i), "accepted_child": child,
                        "finite_masks_checked": 1 << atoms, "outside_lattice_proved": False}
    return {"hereditary": True, "finite_masks_checked": 1 << atoms, "outside_lattice_proved": False}


def verify_subset_hit(task, certificate):
    """Recompute from the frozen atoms, never trust a generator's hit flag."""
    atoms = [laurent(row) for row in task["atoms"]]
    mask = bounded_int(certificate["mask"], 0, (1 << len(atoms)) - 1)
    recomputed = sum_terms(atoms, mask)
    encoded = [[e, str(v)] for e, v in sorted(recomputed.items())]
    return (certificate.get("task_sha256") == digest(task) and recomputed == laurent(task["target"])
            and certificate.get("sum") == encoded)


def subset_search(task):
    bounded_json(task)
    raw = task.get("atoms")
    if not isinstance(raw, list) or not 1 <= len(raw) <= 8:
        raise ValueError("Symbolic subset atom cap 1..8")
    atoms = [laurent(row) for row in raw]
    target = laurent(task["target"])
    n = len(atoms)
    depth = bounded_int(task.get("max_items", n), 1, n)
    cap = bounded_int(task.get("max_candidates", 256), 1, 256)
    beam = bounded_int(task.get("beam_width", 8), 1, 256)
    seed = bounded_int(task.get("seed", 78), 0, 2**32 - 1)
    strategy = task.get("strategy", "exhaustive")
    if strategy not in {"exhaustive", "beam", "apriori", "random"}:
        raise ValueError("Unknown subset strategy")
    universe = [m for m in range(1 << n) if m.bit_count() <= depth]
    accepted = set(range(1 << n))
    audit = None
    if "accepted_masks" in task:
        masks = task["accepted_masks"]
        if not isinstance(masks, list) or len(masks) > (1 << n):
            raise ValueError("Frozen predicate mask cap")
        accepted = {bounded_int(m, 0, (1 << n) - 1) for m in masks}
    if strategy == "apriori":
        if "accepted_masks" not in task:
            raise ValueError("Apriori needs a complete frozen feasibility predicate table")
        audit = pruning_audit(accepted, n)
        if not audit["hereditary"]:
            raise ValueError("Unsafe Apriori pruning: " + json.dumps(audit))
    evaluated, hits = [], []
    task_hash = digest(task)

    def rank(mask):
        value = sum_terms(atoms, mask)
        return (sum(abs(value.get(e, 0) - target.get(e, 0)) for e in set(value) | set(target)), mask)

    def consume(mask):
        if len(evaluated) >= cap:
            return False
        evaluated.append(mask)
        if mask in accepted and sum_terms(atoms, mask) == target:
            certificate = {"mask": mask, "task_sha256": task_hash,
                           "sum": [[e, str(v)] for e, v in sorted(target.items())]}
            if not verify_subset_hit(task, certificate):
                raise ValueError("Certificate recomputation failed")
            hits.append(certificate)
        return True

    safely_pruned = set()
    if strategy in {"exhaustive", "random"}:
        order = list(universe)
        if strategy == "random":
            random.Random(seed).shuffle(order)
        for mask in order:
            if not consume(mask):
                break
    else:
        frontier = [0]
        consume(0)
        for k in range(1, depth + 1):
            proposed = {m | (1 << i) for m in frontier for i in range(n) if not m & (1 << i)}
            if strategy == "beam" and k == 2 and task.get("preserve_pairs", False):
                # All pairs are a paid lookahead control, not a universal repair.
                proposed |= {sum(1 << i for i in inds) for inds in itertools.combinations(range(n), 2)}
            kept = []
            for mask in sorted(proposed):
                if strategy == "apriori" and mask not in accepted:
                    safely_pruned.add(mask)
                    continue
                if not consume(mask):
                    break
                kept.append(mask)
            frontier = sorted(kept, key=rank)[:beam] if strategy == "beam" else kept
            if len(evaluated) >= cap or not frontier:
                break
    valid_universe = len(set(universe) & accepted)
    found_valid = len(set(evaluated) & accepted)
    fully_checked = len(evaluated) == len(universe)
    return {"mode": "exact_laurent_subsets", "strategy": strategy, "task_sha256": task_hash,
            "finite_universe": len(universe), "evaluated": len(evaluated),
            "finite_grammar_coverage": len(evaluated) / len(universe),
            "feasible_universe": valid_universe, "feasible_candidates_checked": found_valid,
            "complete_on_frozen_feasible_universe": found_valid == valid_universe,
            "full_finite_enumeration": fully_checked, "apriori_audit": audit,
            "pruned_rejections": len(safely_pruned), "exact_hits": hits,
            "stop_reason": "finite search exhausted" if len(evaluated) < cap or fully_checked else "candidate cap",
            "scientific_scaling": "Laurent exponents describe t -> 0; they are not computational Big-O costs",
            "search_big_o": "O(a*2^a*C_rational) exhaustive; Apriori includes O(a*2^a) finite predicate audit; beam expansion O(k*b*a*C_eval) plus sorting and optional O(a^2*C_eval) pair preservation",
            "claim_ceiling": "C1 frozen exact algebra and search mechanics",
            "universal_proof": False, "all_possible_questions_covered": False}


def search(args):
    if not isinstance(args, dict) or set(args) - {"mode", "task", "suite_id"}:
        raise ValueError("Search accepts mode, task and suite_id")
    mode = args.get("mode", "plan")
    if "suite_id" in args:
        if "task" in args or mode != "plan":
            raise ValueError("suite_id creates a default plan; supply task for custom grammars")
        task = suite_task(args["suite_id"])
    else:
        task = args.get("task")
    if not isinstance(task, dict):
        raise ValueError("Task object required")
    if mode == "plan":
        return plan_search(task)
    if mode == "subsets":
        return subset_search(task)
    raise ValueError("mode must be plan or subsets")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("catalog")
    run = sub.add_parser("search")
    run.add_argument("--task", type=pathlib.Path)
    run.add_argument("--suite")
    run.add_argument("--mode", choices=["plan", "subsets"], default="plan")
    run.add_argument("--registry", type=pathlib.Path, default=REGISTRY)
    discover = sub.add_parser("inventory")
    discover.add_argument("--source", type=pathlib.Path, required=True)
    discover.add_argument("--provider", required=True)
    discover.add_argument("--registry", type=pathlib.Path, default=REGISTRY)
    discover.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    if args.command == "catalog":
        result = catalog()
    elif args.command == "inventory":
        inventory = discover_source(args.source, args.provider)
        registry, new = extend_registry(load_registry(args.registry), inventory)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
        result = {"inventory": inventory, "new_unreviewed_suites": new}
    elif args.suite:
        result = plan_search(suite_task(args.suite, load_registry(args.registry)))
    else:
        if not args.task or args.task.stat().st_size > 65536:
            parser.error("Supply --suite or a task JSON <= 64 KiB")
        result = search({"mode": args.mode, "task": json.loads(args.task.read_text(encoding="utf-8"))})
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
