#!/usr/bin/env python3
"""
Add a reaction (emoji) to a Bitbucket comment.

Usage:
    BB_TOKEN="<token>" python3 bb_add_reaction.py \\
        --url "https://{host}/rest/comment-likes/latest/projects/{project}/repos/{repo}/pull-requests/{pr}/comments/{comment}/reactions/{reaction}"

Reads BB_TOKEN from environment.
Sends PUT request to add the reaction.
Prints "success" on successful addition, "ERROR" on failure.
"""

import os
import sys
import urllib.request
import urllib.error


def main():
    if "--url" not in sys.argv:
        print("ERROR: --url argument is required", file=sys.stderr)
        sys.exit(1)
    
    idx = sys.argv.index("--url")
    if idx + 1 >= len(sys.argv):
        print("ERROR: --url requires a value", file=sys.stderr)
        sys.exit(1)
    
    url = sys.argv[idx + 1]
    token = os.environ.get("BB_TOKEN")
    
    if not token:
        print("ERROR: BB_TOKEN environment variable is not set", file=sys.stderr)
        sys.exit(1)
    
    try:
        req = urllib.request.Request(url, method="PUT")
        req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=60) as response:
            if response.status in (200, 201, 204):
                print("success")
            else:
                print(f"ERROR: HTTP {response.status}", file=sys.stderr)
                sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"ERROR: HTTP {e.code} {e.reason}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
