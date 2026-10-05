"""Read-only stdio interface to AxiomWeave-CABS; three bounded tools."""
import argparse
import json
import pathlib
import sys
import compositional_search as C

TOOLS = [
    {"name": "cabs_catalog", "description": "List suite development grammars, costs and open evaluators.",
     "inputSchema": {"type": "object", "properties": {"provider": {"type": "string"}}, "additionalProperties": False}},
    {"name": "cabs_search", "description": "Search finite typed workflows or exact Laurent subsets; never promote a universal claim.",
     "inputSchema": {"type": "object", "properties": {"mode": {"type": "string", "enum": ["plan", "subsets"]},
                       "task": {"type": "object"}, "suite_id": {"type": "string"}}, "additionalProperties": False}},
    {"name": "cabs_compose_costs", "description": "Compose supplied conditional time/memory upper bounds; unknown stays unknown.",
     "inputSchema": {"type": "object", "properties": {"left": {"type": "object"}, "right": {"type": "object"},
                       "operator": {"type": "string", "enum": ["sequence", "portfolio", "nested"]}},
                     "required": ["left", "right", "operator"], "additionalProperties": False}}]
BY = {t["name"]: t for t in TOOLS}


def call(name, args):
    if name not in BY or not isinstance(args, dict):
        raise ValueError("Unknown tool or invalid arguments")
    sc = BY[name]["inputSchema"]
    if set(args) - set(sc["properties"]) or set(sc.get("required", [])) - set(args):
        raise ValueError("Unknown or missing arguments")
    C.bounded_json(args)
    for key, value in args.items():
        prop = sc["properties"][key]
        expected = {"string": str, "object": dict}[prop["type"]]
        if type(value) is not expected or ("enum" in prop and value not in prop["enum"]):
            raise ValueError("Wrong argument type or enum: " + key)
    if name == "cabs_catalog":
        return C.catalog(args)
    if name == "cabs_search":
        return C.search(args)
    return C.compose_costs(args["left"], args["right"], args["operator"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=pathlib.Path, default=C.REGISTRY)
    args = parser.parse_args()
    C.REGISTRY = args.registry
    initialized = ready = False
    supported = ["2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25"]
    while True:
        raw = sys.stdin.buffer.readline(65537)
        if not raw:
            break
        ident = None
        try:
            if len(raw) > 65536:
                raise ValueError("Message cap exceeded")
            req = json.loads(raw)
            if not isinstance(req, dict):
                raise ValueError("Request object required")
            ident, method, params = req.get("id"), req.get("method"), req.get("params", {})
            if req.get("jsonrpc") != "2.0" or not isinstance(method, str) or not isinstance(params, dict):
                raise ValueError("Malformed JSON-RPC")
            if ident is None:
                if method == "notifications/initialized" and initialized:
                    ready = True
                continue
            if method == "initialize":
                if initialized or not isinstance(params.get("protocolVersion"), str):
                    raise ValueError("Invalid initialize")
                initialized = True
                version = params["protocolVersion"]
                result = {"protocolVersion": version if version in supported else supported[-1],
                          "capabilities": {"tools": {"listChanged": False}},
                          "serverInfo": {"name": "axiomweave-cabs", "version": "0.1.0"},
                          "instructions": "C0 plans and C1 finite mechanics only; no universal completeness or base-model training."}
            elif method == "ping":
                result = {}
            elif not ready:
                raise ValueError("Initialize and initialized notification required")
            elif method == "tools/list":
                result = {"tools": [{**t, "annotations": {"readOnlyHint": True, "destructiveHint": False,
                                                           "openWorldHint": False}} for t in TOOLS]}
            elif method == "tools/call":
                try:
                    value = call(params.get("name"), params.get("arguments", {}))
                    result = {"content": [{"type": "text", "text": json.dumps(value)}], "isError": False}
                except (ValueError, TypeError, KeyError, ZeroDivisionError) as exc:
                    result = {"content": [{"type": "text", "text": str(exc)}], "isError": True}
            else:
                print(json.dumps({"jsonrpc": "2.0", "id": ident, "error": {"code": -32601, "message": "Method not found"}}), flush=True)
                continue
            print(json.dumps({"jsonrpc": "2.0", "id": ident, "result": result}), flush=True)
        except (ValueError, TypeError, AttributeError) as exc:
            print(json.dumps({"jsonrpc": "2.0", "id": ident, "error": {"code": -32600, "message": str(exc)}}), flush=True)


if __name__ == "__main__":
    main()
