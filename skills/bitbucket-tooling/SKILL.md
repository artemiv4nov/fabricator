---
name: bitbucket-tooling
description: "Use after git-tooling push to create or manage a PR on Bitbucket Server. Composes PR description, creates PR via API, handles review comments. Terminal delivery step. (5 supporting files)"
---

# bitbucket-tooling

> **Law:** follow every clause of the Fabricator Constitution.

## Purpose

All Bitbucket Server operations for the development lifecycle:
- Compose PR title + description from commits
- Create or update a pull request
- Post a review-bot context comment
- Fetch and filter unresolved review comments (pagination handled automatically)

## Inputs
- WORK_PATH (for artifact storage: pr-<JIRA-KEY>.md, review-<branch>-NNN.md, fix-list-<branch>-NNN.md)
- BB_TOKEN in macOS Keychain (see Setup)
- Git remote pointing to Bitbucket Server repository

## Setup

`SKILL_DIR` = directory of this SKILL.md file. The AI fills in the actual path.

```bash
SKILL_DIR="<absolute path to this skill's directory>"  # AI fills this in
# Run once per session
BB_TOKEN=$(security find-generic-password -a "$USER" -s "bb-token" -w 2>/dev/null)
REMOTE=$(git remote get-url origin)
BB_HOST=$(echo "$REMOTE" | sed -E 's|^[a-z+]+://||' | sed 's|^git@||' | sed -E 's|[:/].*||')
PROJECT=$(echo "$REMOTE" | sed -E 's|.*[:/]([^/]+)/[^/]+\.git$|\1|' | tr '[:lower:]' '[:upper:]')
REPO=$(echo "$REMOTE" | sed 's|.*/||' | sed 's|\.git$||')
BRANCH=$(git branch --show-current)
```

After running: verify `BB_TOKEN`, `BB_HOST`, `PROJECT`, `REPO`, and `BRANCH` are all non-empty.
If any variable is empty — stop and report which one failed before proceeding to any operation.

**Security note:** `$BB_TOKEN` is expanded into `curl` command-line arguments, which are
visible via `ps`. Acceptable on a single-user dev machine; on shared CI runners consider
passing the token via `curl -K <(printf -- '-H "Authorization: Bearer %s"' "$BB_TOKEN"')`
instead of `-H "Authorization: Bearer $BB_TOKEN"`.

If `BB_TOKEN` is empty — instruct the user to save it first:
```bash
security add-generic-password -a "$USER" -s "bb-token" -w "<token>"
# Generate in Bitbucket: Profile → Manage Account → Personal access tokens
```

## Operations

### compose_pr

AI task. No shell commands.

1. Run Setup (git commands only, no API calls needed yet)
2. Detect Jira ID from branch name (`[A-Z]+-[0-9]+`); ask if not found
3. Determine merge base (skip to step 4 if a full diff was already analyzed this session
   e.g. via the `git-tooling` skill):
   ```bash
   PARENT=$(git show-branch | grep '*' | grep -v "$BRANCH" | head -n1 | sed 's/.*\[\(.*\)\].*/\1/' | sed 's/[\^~].*//')
   ```
   If `PARENT` is empty — ask the user for the parent branch name; do not silently default to `master`.
   ```bash
   MERGE_BASE=$(git merge-base HEAD "$PARENT")
   git log --oneline $MERGE_BASE..HEAD
   git diff $MERGE_BASE..HEAD --stat
   git diff $MERGE_BASE..HEAD
   ```
4. Fill the PR description:
   - If a PR description standard is available in context (rules or repository files
     such as CONTRIBUTING.md), follow it for title format, description structure,
     and section-filling rules.
   - If no standard is present — ask the user for the PR format.
5. Show title + description. Ask APPROVE (final) / REJECT (revise)
6. Write `pr-<JIRA-KEY>.md` to WORK_PATH (written immediately — inside ARTIFACT_ROOT).
   Filename example: `pr-PROJ-123.md`. See [Branch & key slugs](#branch--key-slugs) for naming.

---

### create_pr

Detect the target branch (local ref, no network):
```bash
TARGET=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||')
```
If `TARGET` is empty or looks wrong — ask the user for the target branch name.

```bash
python3 "$SKILL_DIR/bb_make_pr_payload.py" \
    --title "<title>" \
    --branch "$BRANCH" \
    --repo "$REPO" \
    --project "$PROJECT" \
    --target "$TARGET" <<'DESCRIPTION' | curl -s -X POST \
    -H "Authorization: Bearer $BB_TOKEN" \
    -H "Content-Type: application/json" \
    "https://$BB_HOST/rest/api/1.0/projects/$PROJECT/repos/$REPO/pull-requests" \
    --connect-timeout 10 --max-time 120 \
    -d @- \
  | python3 "$SKILL_DIR/bb_check_response.py"
<PR description content>
DESCRIPTION
```

Extract `PR_ID` from the `id=<value>` line in the output:
```bash
PR_ID=<value>  # AI reads the numeric value from the output above and assigns it
```

Update `pr-<JIRA-KEY>.md` in WORK_PATH: append PR metadata (ID, URL, branch, state)
under a `## PR` heading (written immediately — inside ARTIFACT_ROOT).

---

### update_pr

Update title or description of an existing PR. Requires `PR_ID` (from `pr-<JIRA-KEY>.md` or `find_open_pr`).

First fetch the current PR version (Bitbucket uses optimistic locking):
```bash
curl -s --connect-timeout 10 --max-time 60 \
  -H "Authorization: Bearer $BB_TOKEN" \
  "https://$BB_HOST/rest/api/1.0/projects/$PROJECT/repos/$REPO/pull-requests/$PR_ID" \
  | python3 "$SKILL_DIR/bb_check_response.py" --field version
VERSION=<value from output>
```

Edit title or description (reuse `pr-<JIRA-KEY>.md` as starting point). Show diff. Ask APPROVE / REJECT.

```bash
python3 "$SKILL_DIR/bb_make_pr_payload.py" \
    --title "<updated title>" \
    --branch "$BRANCH" \
    --repo "$REPO" \
    --project "$PROJECT" \
    --target "$TARGET" \
    --version "$VERSION" <<'DESCRIPTION' | curl -s -X PUT \
    -H "Authorization: Bearer $BB_TOKEN" \
    -H "Content-Type: application/json" \
    "https://$BB_HOST/rest/api/1.0/projects/$PROJECT/repos/$REPO/pull-requests/$PR_ID" \
    --connect-timeout 10 --max-time 120 \
    -d @- \
  | python3 "$SKILL_DIR/bb_check_response.py"
<updated PR description content>
DESCRIPTION
```

Update `pr-<JIRA-KEY>.md` with the new content (written immediately — inside ARTIFACT_ROOT).

---

### post_comment

Use heredoc to safely pass multiline text:
```bash
python3 "$SKILL_DIR/bb_make_comment_payload.py" <<'COMMENT' | curl -s -X POST \
    -H "Authorization: Bearer $BB_TOKEN" \
    -H "Content-Type: application/json" \
    "https://$BB_HOST/rest/api/1.0/projects/$PROJECT/repos/$REPO/pull-requests/$PR_ID/comments" \
    --connect-timeout 10 --max-time 120 \
    -d @- \
  | python3 "$SKILL_DIR/bb_check_response.py"
<comment text here>
COMMENT
```

---

### reply_to_comment

Reply to a specific comment in a PR. Requires `PR_ID` and `COMMENT_ID` (from `review-<branch>-NNN.md`
or `fetch_review_comments` output).

The `COMMENT_ID` is the numeric id of the comment being replied to. It can target any
repository and PR — set `PROJECT`, `REPO`, and `PR_ID` accordingly before calling.

```bash
python3 "$SKILL_DIR/bb_make_comment_payload.py" --parent $COMMENT_ID <<'COMMENT' | curl -s -X POST \
    -H "Authorization: Bearer $BB_TOKEN" \
    -H "Content-Type: application/json" \
    "https://$BB_HOST/rest/api/1.0/projects/$PROJECT/repos/$REPO/pull-requests/$PR_ID/comments" \
    --connect-timeout 10 --max-time 120 \
    -d @- \
  | python3 "$SKILL_DIR/bb_check_response.py"
<reply text here>
COMMENT
```

---

### add_reaction

Add a reaction (emoji) to a comment. Requires `PR_ID` and `COMMENT_ID`.

The `REACTION` is the emoji short name (e.g., `white_check_mark`, `thumbsup`, `heart`).

```bash
BB_TOKEN="$BB_TOKEN" python3 "$SKILL_DIR/bb_add_reaction.py" \
  --url "https://$BB_HOST/rest/comment-likes/latest/projects/$PROJECT/repos/$REPO/pull-requests/$PR_ID/comments/$COMMENT_ID/reactions/$REACTION"
```

Prints "success" on successful addition, "ERROR" on failure.

Common reactions:
- `white_check_mark` — ✅ (resolved/done)
- `thumbsup` — 👍 (agree)
- `heart` — ❤️ (like)
- `thinking_face` — 🤔 (hmm)

---

### post_bot_review_context

AI task + API call.

Precondition: `pr-<JIRA-KEY>.md` must exist in WORK_PATH (i.e. `compose_pr` was already run).
If absent — run `compose_pr` first.

Compose a comment in English based on commits and diff already analyzed in `compose_pr`.
The bot reads AGENTS.md, PR title, and description automatically — do not repeat them.
Focus only on what the bot cannot infer.

Format:
```
@bot Please review this PR.

Please respond in the same language as the PR description.

**Key implementation details:**
<non-obvious decisions that look suspicious but are intentional; brief reasoning>

**Please focus on:**
- <specific correctness concerns from the diff>
- Error handling and edge cases

**Known intentional patterns (do not flag):**
<deliberate choices, known trade-offs; omit section if nothing applies>
```

Show to user. Ask APPROVE / REJECT. Then use `post_comment` to send.

---

### fetch_review_comments

Detect current user slug from git email (e.g. `user@company.com` → `user`):
```bash
CURRENT_USER_SLUG=$(git config user.email | cut -d@ -f1)
```
If empty — ask the user for their Bitbucket username slug.

```bash
BB_TOKEN="$BB_TOKEN" python3 "$SKILL_DIR/bb_filter_comments.py" "$CURRENT_USER_SLUG" \
  --url "https://$BB_HOST/rest/api/1.0/projects/$PROJECT/repos/$REPO/pull-requests/$PR_ID/activities"
```
The script fetches all pages automatically and handles pagination internally.

---

### triage_comments

AI task. No shell commands.

Takes the output of `fetch_review_comments` and produces a structured fix list.
Process all comments — both `[HUMAN]` and `[BOT]`.

After each fix is implemented, update the corresponding `review-<branch>-NNN.md` item:
- `[x]` — fixed and committed
- `[ ] ~~text~~ — deliberately not fixed: <reason>` — rejected with rationale

1. Group comments by category:
   - **Logic errors** — bugs, incorrect behavior, missed edge cases
   - **Code quality** — naming, structure, duplication, style
   - **Architecture** — design concerns, abstraction issues
   - **Tests** — missing or incorrect test coverage
   - **Documentation** — missing or incorrect comments/docs
   - **Other**
2. For each comment produce a task line:
   ```
   - [ ] `<file>:<line or "general">` — <concise description>
   ```
3. Show the grouped list. If no unresolved comments — report and stop.
4. Write `fix-list-<branch>-NNN.md` to WORK_PATH (written immediately — inside ARTIFACT_ROOT).

---

### find_open_pr

First check if `pr-<JIRA-KEY>.md` already exists in WORK_PATH and contains a `## PR` section with `PR_ID`.
If found, read `PR_ID` from it and skip the API call.

Otherwise, URL-encode the branch name (slashes in branch names like `feature/foo` must be encoded):
```bash
BRANCH_ENCODED=$(echo "$BRANCH" | sed 's|/|%2F|g')
curl -s --connect-timeout 10 --max-time 60 \
  -H "Authorization: Bearer $BB_TOKEN" \
  "https://$BB_HOST/rest/api/1.0/projects/$PROJECT/repos/$REPO/pull-requests?at=refs%2Fheads%2F${BRANCH_ENCODED}&state=OPEN&limit=1" \
  | python3 "$SKILL_DIR/bb_check_response.py" --field values.0.id
```

## Outputs

- `PR_ID` — integer ID of the created or found PR
- `CURRENT_USER_SLUG` — Bitbucket username of the token owner
- Printed list of unresolved comments (from `bb_filter_comments.py`)

## WORK_PATH artifacts

All artifacts are written immediately (inside ARTIFACT_ROOT — no APPROVE required).

### Branch & key slugs

- **JIRA_KEY**: detected from branch name (`[A-Z]+-[0-9]+`), e.g. `PROJ-123`.
- **BRANCH_SLUG**: branch name with `/` replaced by `-`, e.g. `feature/auth` → `feature-auth`.

### `pr-<JIRA-KEY>.md` — after `compose_pr`, updated by `create_pr`

Single file per PR. Created by `compose_pr` with title + description;
`create_pr` appends a `## PR` section with metadata.

Filename example: `pr-PROJ-123.md`.

```markdown
# <title>

<PR description content>

## PR

- **ID:** <PR_ID>
- **URL:** https://<BB_HOST>/projects/<PROJECT>/repos/<REPO>/pull-requests/<PR_ID>
- **Branch:** <branch> → <target>
- **Jira:** <JIRA-KEY>
- **State:** OPEN
```

### `review-<BRANCH_SLUG>-NNN.md` — after each `fetch_review_comments` run

`NNN` = next number (001, 002, …) among existing `review-<BRANCH_SLUG>-*.md` in WORK_PATH.

Filename example: `review-feature-auth-001.md`.

```markdown
# Review <BRANCH_SLUG> NNN

Fetched: <ISO timestamp>

## Unresolved comments

<bb_filter_comments.py output formatted as a list>
```

### `fix-list-<BRANCH_SLUG>-NNN.md` — written by AI after analyzing `review-<BRANCH_SLUG>-NNN.md`

Same `NNN` as the review file. Mark items `[x]` when implemented.

Filename example: `fix-list-feature-auth-001.md`.

```markdown
# Fix list <BRANCH_SLUG> NNN

Derived from: review-<BRANCH_SLUG>-NNN.md
Progress: 0/<total> fixed

## <Category>

- [ ] `<file>:<line>` — <description>
```

## Related skills
- **git-tooling** — must precede this skill; push must succeed before PR operations
- **jira-tooling** — used alongside to link PR to a Jira issue or read issue context

## Completion criteria
- Requested operation completed (or explicitly stopped by user)
- Relevant WORK_PATH artifacts updated

Return control to Fabricator.

