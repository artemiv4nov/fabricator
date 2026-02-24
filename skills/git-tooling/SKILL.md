---
name: git-tooling
description: "Analyze staged diff, compose a semantic commit message following project conventions, commit, and push. Chains into bitbucket-tooling if PR creation is needed."
---

# git-tooling

## Purpose

Stage verification → semantic message composition → commit → push → optional PR creation.

## Inputs
- Staged changes in the current git repository
- Project commit conventions (from AGENTS.md or DEVELOPMENT.md)

## Steps

### 1. Check staged changes

```bash
git diff --cached --stat
```

If output is empty — tell the user nothing is staged and stop.

### 2. Get full staged diff

```bash
git diff --cached
```

### 3. Compose commit message

Analyze the diff. Propose a semantic message following project conventions:

- **Format:** `type(scope): title`  or  `type: title`
- **Types:** `feat`, `fix`, `enhance`, `refactor`, `chore`, `docs`
- **Scope:** module/feature name if change is localized (e.g., `vpn`, `billing`, `auth`);
  omit for cross-cutting changes
- **Title:** imperative mood, lowercase start, no trailing period, ≤72 chars
- **Body** (optional, separated by blank line): include **only** when the title alone is
  insufficient — i.e. multiple unrelated changes in one commit, a non-obvious design decision,
  or a breaking/migration note. Do NOT add a body that just restates or bullet-points what the
  title already says.

Show proposed message:
```
type(scope): title

optional body
```

### 4. Review

- **APPROVE** → proceed to commit
- **REJECT** → ask what to change, revise and re-propose from step 3
- **STOP** → terminate

### 5. Commit

```bash
git commit -m "type(scope): title"
```

If body is present:
```bash
git commit -m "type(scope): title" -m "body"
```

Show output.

On failure (non-zero exit): show full output + exit code. Common causes:
- Pre-commit hook rejected: fix the reported issue, then retry from step 1.
- Nothing to commit: staged files may have been reset; verify with step 1.
Do not proceed to step 6 until commit succeeds.

### 6. Push

Ask: "Push to remote? **APPROVE** (optionally add branch name), **REJECT** to skip."

If **APPROVE**:
```bash
git push
# or: git push origin <branch>
```

Show output. Note whether Bitbucket prints a PR creation URL.

### 7. Continue to PR

After a successful push, offer to invoke `bitbucket-tooling` skill:
- `compose_pr` → analyze commits, fill PR template, get APPROVE
- `create_pr` → create PR via API
- `post_bot_review_context` → post @bot comment

Ask: "Continue with PR creation? **APPROVE** to invoke bitbucket-tooling, **REJECT** to stop."

## Completion criteria
- Commit created (or user stopped early)
- Push completed (or user declined)

Return control to Fabricator.
