#!/usr/bin/env python3
"""
Create a Bitbucket pull request payload JSON.

Usage:
    echo "$DESCRIPTION" | python3 bb_make_pr_payload.py \\
        --title "PROJ-1234 | Fix something" \\
        --branch feature/my-branch \\
        --repo my-repo \\
        --project MYPROJECT \\
        --target master

Description is read from stdin. Output is JSON written to stdout.
"""

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--version", type=int, default=None,
                        help="PR version for optimistic locking (required for PUT updates)")
    parser.add_argument("--reviewers", default="",
                        help="Comma-separated Bitbucket slugs to add as reviewers")
    parser.add_argument("--draft", action="store_true",
                        help="Create as a draft pull request")
    args = parser.parse_args()

    description = sys.stdin.read()
    payload = {
        "title": args.title,
        "description": description,
        "fromRef": {
            "id": f"refs/heads/{args.branch}",
            "repository": {"slug": args.repo, "project": {"key": args.project}},
        },
        "toRef": {
            "id": f"refs/heads/{args.target}",
            "repository": {"slug": args.repo, "project": {"key": args.project}},
        },
    }
    if args.version is not None:
        payload["version"] = args.version
    if args.reviewers:
        payload["reviewers"] = [
            {"user": {"slug": s.strip()}}
            for s in args.reviewers.split(",") if s.strip()
        ]
    if args.draft:
        payload["draft"] = True
    json.dump(payload, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
