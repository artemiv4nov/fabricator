#!/usr/bin/env python3
"""
Parse a Jira Data Center REST API response and report success or error.

Usage:
    curl ... | python3 jira_check_response.py [--field <field>]

Prints:
    On success: "<field>=<value>"  (default field: key)
    On error:   error messages from 'errorMessages' and/or 'errors' fields

Jira DC error format:
    {"errorMessages": ["msg1"], "errors": {"field": "msg"}}
"""

import json
import sys


_MISSING = object()


def resolve_path(data, path):
    """Resolve a dotted path like 'fields.status.name' into nested dict access.

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
    path = "key"
    if "--field" in sys.argv:
        idx = sys.argv.index("--field")
        if idx + 1 < len(sys.argv):
            path = sys.argv[idx + 1]

    try:
        d = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not parse API response as JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Jira DC returns errors in two possible fields
    has_errors = False
    if "errorMessages" in d and d["errorMessages"]:
        for msg in d["errorMessages"]:
            print(f"ERROR: {msg}", file=sys.stderr)
        has_errors = True
    if "errors" in d and d["errors"]:
        for field, msg in d["errors"].items():
            print(f"ERROR: {field}: {msg}", file=sys.stderr)
        has_errors = True
    if has_errors:
        sys.exit(1)

    value = resolve_path(d, path)
    if value is _MISSING:
        print(f"ERROR: path '{path}' not found. Top-level keys: {list(d.keys())}", file=sys.stderr)
        sys.exit(1)
    label = path.split(".")[-1]
    print(f"{label}={value}")


if __name__ == "__main__":
    main()
