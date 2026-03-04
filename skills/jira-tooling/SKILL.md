---
name: jira-tooling
description: "Use at session start to pull Jira issue details into context, or post-delivery to create/update issues. Integrates with task-authoring (issue → task.md) and git-tooling (commit links). (2 supporting files)"
---

# jira-tooling

> **Law:** follow every clause of the Fabricator Constitution.

## Purpose

Jira Data Center operations for the development lifecycle:
- Read issue details (summary, status, description, assignee, etc.)
- Create new issues (Task, Bug, Story, Sub-task)

## Inputs
- WORK_PATH (for artifact storage: issue-KEY.md)
- JIRA_TOKEN in macOS Keychain (see Setup)
- Jira project key (from branch name, WORK_PATH artifacts, or user input)

## Setup

`SKILL_DIR` = directory of this SKILL.md file. The AI fills in the actual path.

```bash
SKILL_DIR="<absolute path to this skill's directory>"  # AI fills this in
# Run once per session
JIRA_TOKEN=$(security find-generic-password -a "$USER" -s "jira-token" -w 2>/dev/null)
JIRA_HOST=$(security find-generic-password -a "$USER" -s "jira-host" -w 2>/dev/null)
```

After running: verify `JIRA_TOKEN` and `JIRA_HOST` are both non-empty.
If any variable is empty — stop and report which one failed before proceeding.

**Security note:** `$JIRA_TOKEN` is expanded into `curl` command-line arguments, which are
visible via `ps`. Acceptable on a single-user dev machine; on shared CI runners consider
passing the token via `curl -K <(printf -- '-H "Authorization: Bearer %s"' "$JIRA_TOKEN")`.

If `JIRA_TOKEN` is empty — instruct the user to save it first:
```bash
security add-generic-password -a "$USER" -s "jira-token" -w "<token>"
# Generate in Jira: Profile → Personal Access Tokens → Create token
```

If `JIRA_HOST` is empty — instruct the user to save it first:
```bash
security add-generic-password -a "$USER" -s "jira-host" -w "jira.example.com"
# The hostname of your Jira Data Center instance (without https://)
```

## Operations

### read_issue

Read issue details by key (e.g. `PROJ-123`).

1. Run Setup
2. Determine issue key:
   - From user input (explicit key)
   - From branch name: `git branch --show-current | grep -oE '[A-Z]+-[0-9]+'`
   - From WORK_PATH artifacts (task.md, pr.md — look for Jira key references)
   - If not found — ask user
3. Fetch issue (with comment count via `renderedFields` for rendered description):
```bash
curl -s --connect-timeout 10 --max-time 60 \
  -H "Authorization: Bearer $JIRA_TOKEN" \
  "https://$JIRA_HOST/rest/api/2/issue/$ISSUE_KEY?fields=summary,status,issuetype,priority,assignee,reporter,description,labels,components,parent,comment"
```
4. Display in chat — always show these three prominently:
   - **Summary** (`fields.summary`) — the issue title
   - **Description** (`fields.description`) — full text
   - **Comments** (`fields.comment.total`) — number of comments

   Additional context (show in a compact block):
   - **Key**, **Status**, **Type**, **Priority**, **Assignee**, **Reporter**
   - **Labels**, **Components**, **Parent** (if sub-task)

5. Optionally write `issue-<KEY>.md` to WORK_PATH (written immediately — inside ARTIFACT_ROOT).
   Filename example: `issue-PROJ-123.md`.

---

### create_issue

Create a new issue in Jira.

**Language rules:**
- **Summary** (title): always in English.
- **Description**: written in COMMUNICATION_LANGUAGE.
  If COMMUNICATION_LANGUAGE is overridden (e.g. to `ru`), write the description in that language.

**Issue format:**
If a Jira issue standard is available in context (rules or repository files),
follow it for description structure, required fields, and project defaults.
If no standard is present — ask the user for the description format.

1. Run Setup
2. Fetch required fields for the project (some projects enforce components, priority, etc.):
```bash
curl -s --connect-timeout 10 --max-time 60 \
  -H "Authorization: Bearer $JIRA_TOKEN" \
  "https://$JIRA_HOST/rest/api/2/issue/createmeta?projectKeys=$PROJECT_KEY&issuetypeNames=$ISSUE_TYPE&expand=projects.issuetypes.fields" \
  | python3 -c "
import json, sys
d = json.load(sys.stdin)
projects = d.get('projects', [])
if not projects:
    print('ERROR: project not found or no permissions', file=sys.stderr); sys.exit(1)
fields = projects[0].get('issuetypes', [{}])[0].get('fields', {})
required = {k: v['name'] for k, v in fields.items() if v.get('required') and k not in ('project', 'issuetype', 'summary')}
if required:
    print('Additional required fields:')
    for k, name in required.items(): print(f'  - {name} ({k})')
else:
    print('No additional required fields beyond project/summary/issuetype.')
"
```
3. Gather required fields (ask user for any missing):
   - **Project key** (e.g. `PROJ`)
   - **Summary** (issue title)
   - **Issue type** (Task, Bug, Story, Sub-task; default: Task)
   - **Description** (multiline; may come from WORK_PATH artifacts)
   - **Components** (if required by project — discovered in step 2)
4. Gather optional fields (skip if not needed):
   - **Priority** (e.g. Major, Minor, Critical)
   - **Labels** (comma-separated)
   - **Components** (if not required — still useful)
   - **Assignee** (username)
   - **Parent** (issue key, required for Sub-task type)
5. Show preview of the issue to be created. Ask APPROVE / REJECT.
6. Create issue:
```bash
python3 "$SKILL_DIR/jira_make_issue_payload.py" \
    --project "$PROJECT_KEY" \
    --summary "$SUMMARY" \
    --issuetype "$ISSUE_TYPE" \
    [--priority "$PRIORITY"] \
    [--labels "$LABELS"] \
    [--components "$COMPONENTS"] \
    [--assignee "$ASSIGNEE"] \
    [--parent "$PARENT_KEY"] <<'DESCRIPTION' | curl -s -X POST \
    -H "Authorization: Bearer $JIRA_TOKEN" \
    -H "Content-Type: application/json" \
    "https://$JIRA_HOST/rest/api/2/issue" \
    --connect-timeout 10 --max-time 120 \
    -d @- \
  | python3 "$SKILL_DIR/jira_check_response.py"
<description content>
DESCRIPTION
```
7. Extract `ISSUE_KEY` from the `key=<value>` line in the output.
8. Construct and print the issue URL in chat:
   ```
   Created: https://$JIRA_HOST/browse/$ISSUE_KEY
   ```
9. Write `issue-<KEY>.md` to WORK_PATH (written immediately — inside ARTIFACT_ROOT).
   Filename example: `issue-PROJ-456.md`.

---

### find_project_issuetypes

Helper operation to discover available issue types for a project.
Useful before `create_issue` if the user is unsure about available types.

```bash
curl -s --connect-timeout 10 --max-time 60 \
  -H "Authorization: Bearer $JIRA_TOKEN" \
  "https://$JIRA_HOST/rest/api/2/project/$PROJECT_KEY" \
  | python3 -c "
import json, sys
d = json.load(sys.stdin)
if 'errorMessages' in d:
    for m in d['errorMessages']: print(f'ERROR: {m}', file=sys.stderr)
    sys.exit(1)
for it in d.get('issueTypes', []):
    print(f\"  - {it['name']} (subtask={it.get('subtask', False)})\")
"
```

## Outputs

- `ISSUE_KEY` — Jira issue key (e.g. `PROJ-123`), printed to stdout by `jira_check_response.py` as `key=PROJ-123`
- `ISSUE_URL` — derived as `https://$JIRA_HOST/browse/$ISSUE_KEY`, printed in chat and saved to `issue-<KEY>.md`
- `issue-<KEY>.md` — persistent artifact in WORK_PATH; the primary way to pass issue context between operations and skills
- Printed issue details in chat (from `read_issue`)

## WORK_PATH artifacts

All artifacts are written immediately (inside ARTIFACT_ROOT — no APPROVE required).

### `issue-<KEY>.md` — after `read_issue` or `create_issue`

Filename includes the issue key (e.g. `issue-PROJ-123.md`) to support multiple issues per WORK_PATH.

```markdown
# <ISSUE_KEY>: <summary>

- **Key:** <ISSUE_KEY>
- **URL:** https://<JIRA_HOST>/browse/<ISSUE_KEY>
- **Summary:** <summary>
- **Type:** <issuetype>
- **Status:** <status>
- **Priority:** <priority>
- **Assignee:** <assignee or "unassigned">
- **Project:** <project key>

## Description

<description text>
```

## Related skills
- **task-authoring** — invoke after read_issue to populate task.md with issue details
- **git-tooling** — used alongside to link commits or PRs back to a Jira issue
- **bitbucket-tooling** — used alongside when PR must reference the Jira issue key

## Completion criteria
- Requested operation completed (or explicitly stopped by user)
- Relevant WORK_PATH artifacts updated

Return control to Fabricator.
