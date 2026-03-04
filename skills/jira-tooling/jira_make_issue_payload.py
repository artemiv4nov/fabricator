#!/usr/bin/env python3
"""
Create a Jira Data Center issue payload JSON.

Usage:
    echo "$DESCRIPTION" | python3 jira_make_issue_payload.py \\
        --project PROJ \\
        --summary "Issue title" \\
        --issuetype Task

    With optional fields:
    echo "$DESCRIPTION" | python3 jira_make_issue_payload.py \\
        --project PROJ \\
        --summary "Issue title" \\
        --issuetype Task \\
        --priority Major \\
        --labels "label1,label2" \\
        --components "Component1,Component2" \\
        --assignee username \\
        --parent PROJ-123

Description is read from stdin. Output is JSON written to stdout.
"""

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(description="Build Jira issue creation payload.")
    parser.add_argument("--project", required=True, help="Project key (e.g. PROJ)")
    parser.add_argument("--summary", required=True, help="Issue summary/title")
    parser.add_argument("--issuetype", required=True, help="Issue type name (e.g. Task, Bug, Story, Sub-task)")
    parser.add_argument("--priority", default=None, help="Priority name (e.g. Major, Minor, Critical)")
    parser.add_argument("--labels", default="", help="Comma-separated labels")
    parser.add_argument("--components", default="", help="Comma-separated component names")
    parser.add_argument("--assignee", default=None, help="Assignee username")
    parser.add_argument("--parent", default=None, help="Parent issue key (for sub-tasks)")
    args = parser.parse_args()

    description = sys.stdin.read().strip()

    fields = {
        "project": {"key": args.project},
        "summary": args.summary,
        "issuetype": {"name": args.issuetype},
    }

    if description:
        fields["description"] = description

    if args.priority:
        fields["priority"] = {"name": args.priority}

    if args.labels:
        fields["labels"] = [l.strip() for l in args.labels.split(",") if l.strip()]

    if args.components:
        fields["components"] = [
            {"name": c.strip()} for c in args.components.split(",") if c.strip()
        ]

    if args.assignee:
        fields["assignee"] = {"name": args.assignee}

    if args.parent:
        fields["parent"] = {"key": args.parent}

    payload = {"fields": fields}
    json.dump(payload, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
