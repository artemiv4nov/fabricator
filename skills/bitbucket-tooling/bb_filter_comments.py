#!/usr/bin/env python3
"""
Fetch and filter unresolved review comments from Bitbucket PR activities.

Usage (recommended — handles pagination automatically):
    python3 bb_filter_comments.py <current_user_slug> \\
        --url <activities_base_url> --token <bb_token>

Legacy usage (single page only, reads from stdin):
    curl ... /activities?limit=100 | python3 bb_filter_comments.py <current_user_slug>

Options:
    --bot-slugs   comma-separated Bitbucket slugs treated as bots (default: "")
    --ack-marker  reply text that counts as acknowledgment (default: ":white_check_mark:")

A comment is considered unresolved if:
    1. comment.state != "RESOLVED"
    2. None of its replies contain <ack-marker> authored by <current_user_slug>
"""

import argparse
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError

_REQUEST_TIMEOUT = 30


def fetch_all_activities(base_url, token):
    """Fetch all pages of PR activities and return a combined list."""
    activities = []
    next_url = base_url + "?limit=100"
    while next_url:
        try:
            req = Request(next_url, headers={"Authorization": f"Bearer {token}"})
            with urlopen(req, timeout=_REQUEST_TIMEOUT) as resp:
                data = json.loads(resp.read().decode())
        except URLError as e:
            print(f"ERROR: Request failed: {e}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"ERROR: Could not parse API response as JSON: {e}", file=sys.stderr)
            sys.exit(1)
        activities.extend(data.get("values", []))
        if data.get("isLastPage", True):
            break
        next_url = base_url + f"?limit=100&start={data['nextPageStart']}"
    return activities


def filter_comments(activities, current_user_slug, bot_slugs, ack_marker):
    comments = []
    for a in activities:
        if a.get("action") != "COMMENTED":
            continue
        c = a.get("comment", {})
        if c.get("state") == "RESOLVED":
            continue
        replies = c.get("comments", [])
        acknowledged = any(
            ack_marker in r.get("text", "")
            and r.get("author", {}).get("slug", "") == current_user_slug
            for r in replies
        )
        if acknowledged:
            continue
        author = c.get("author", {}).get("displayName", "")
        author_slug = c.get("author", {}).get("slug", "")
        is_bot = author_slug in bot_slugs
        anchor = a.get("commentAnchor", {})
        location = anchor.get("path", "general")
        line = anchor.get("line")
        if line:
            location += ":" + str(line)
        comments.append({
            "id": c.get("id"),
            "author": author,
            "author_slug": author_slug,
            "location": location,
            "text": c.get("text", ""),
            "replies": replies,
            "bot": is_bot,
        })
    return comments


def main():
    parser = argparse.ArgumentParser(description="Filter unresolved Bitbucket PR comments.")
    parser.add_argument("current_user_slug", nargs="?", default="")
    parser.add_argument("--url", help="Base URL for activities endpoint (enables pagination)")
    parser.add_argument("--token", default=os.environ.get("BB_TOKEN", ""),
                        help="Bitbucket personal access token (default: $BB_TOKEN env var)")
    parser.add_argument("--bot-slugs", default="",
                        help="Comma-separated Bitbucket slugs treated as bots")
    parser.add_argument("--ack-marker", default=":white_check_mark:",
                        help="Reply text that counts as acknowledgment")
    args = parser.parse_args()

    bot_slugs = set(s.strip() for s in args.bot_slugs.split(",") if s.strip())
    ack_marker = args.ack_marker

    if args.url and args.token:
        activities = fetch_all_activities(args.url, args.token)
    else:
        try:
            data = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"ERROR: Could not parse API response as JSON: {e}", file=sys.stderr)
            sys.exit(1)
        activities = data.get("values", [])

    comments = filter_comments(activities, args.current_user_slug, bot_slugs, ack_marker)

    print(f"Unresolved comments: {len(comments)}")
    for i, c in enumerate(comments, 1):
        tag = "[BOT]" if c["bot"] else "[HUMAN]"
        print(f"\n--- [{i}] {tag} {c['author']} @ {c['location']} (id={c['id']}) ---")
        print(c["text"])
        if c["replies"]:
            print(f"  Replies: {len(c['replies'])}")
            for r in c["replies"]:
                rauthor = r.get("author", {}).get("displayName", "?")
                print(f"  - {rauthor}: {r.get('text', '')}")


if __name__ == "__main__":
    main()
