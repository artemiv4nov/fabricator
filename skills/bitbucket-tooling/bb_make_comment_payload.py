#!/usr/bin/env python3
"""
Create a Bitbucket comment payload JSON.

Usage:
    python3 bb_make_comment_payload.py <<'EOF'
    comment text here
    EOF

Reads comment text from stdin. Output is JSON written to stdout.
"""

import json
import sys


def main():
    text = sys.stdin.read()
    json.dump({"text": text}, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
