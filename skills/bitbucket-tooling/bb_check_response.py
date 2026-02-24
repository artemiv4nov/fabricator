#!/usr/bin/env python3
"""
Parse a Bitbucket REST API response and report success or error.

Usage:
    curl -X POST ... | python3 bb_check_response.py [--field <field>]

Prints:
    On success: "<field>=<value>"  (default field: id)
    On error:   error messages from the 'errors' array
"""

import json
import sys


_MISSING = object()


def resolve_path(data, path):
    """Resolve a dotted path like 'values.0.slug' into data['values'][0]['slug'].

    Returns _MISSING if any key along the path is absent.
    Returns None if a key exists but its value is null/None.
    """
    for key in path.split("."):
        if isinstance(data, list):
            try:
                data = data[int(key)]
            except (IndexError, ValueError):
                return _MISSING
        elif isinstance(data, dict):
            if key not in data:
                return _MISSING
            data = data[key]
        else:
            return _MISSING
    return data


def main():
    path = "id"
    if "--field" in sys.argv:
        idx = sys.argv.index("--field")
        if idx + 1 < len(sys.argv):
            path = sys.argv[idx + 1]

    try:
        d = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not parse API response as JSON: {e}", file=sys.stderr)
        sys.exit(1)
    if "errors" in d:
        for e in d["errors"]:
            print(f"ERROR: {e.get('message', e)}", file=sys.stderr)
        sys.exit(1)

    value = resolve_path(d, path)
    if value is _MISSING:
        print(f"ERROR: path '{path}' not found. Top-level keys: {list(d.keys())}", file=sys.stderr)
        sys.exit(1)
    label = path.split(".")[-1]
    print(f"{label}={value}")


if __name__ == "__main__":
    main()
