# AGENTS.md

This repository contains the Fabricator methodology for Windsurf Cascade.

## Structure

- `fabricator.md` — core workflow, invoked as `/fabricator`
- `skills/` — reusable multi-step skills, each in `<name>/SKILL.md`
- `README.md` — full methodology documentation, installation guide, skill catalog

## Conventions

- All file content is in English
- Skills follow the SKILL.md frontmatter format (name, description)
- Workflow and skills are markdown-only (no build step)

## Adding a skill

1. Create `skills/<skill-name>/SKILL.md`
2. Add frontmatter: `name` and `description`
3. Place any support scripts next to SKILL.md
4. Update the skill catalog table in README.md

## Verification

No build or test commands — this is a documentation/methodology repository.
Validate markdown formatting and link integrity manually.
