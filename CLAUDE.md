# Minerva Vault Instructions (CLAUDE.md)

See [AGENTS.md](AGENTS.md) for full documentation standards, templates, and git author rules.

## Core Rules Summary
- **Worklogs**: Use `Templates/worklog.md` format (`created`, `date`, `project`, `type: worklog`, `status: completed`, `task_id`, `tags`).
- **Backlogs**: Use `Templates/backlog.md` (root project backlog) or `Templates/category-backlog.md` (category backlog). Add items using `Templates/backlog-item.md`.
- **Knowledge Distillation**: Do not distill worklog or backlog documents into `Dev/`. Only general evergreen knowledge belongs in `Dev/`.
- **Git Author**: ALWAYS commit with `EvoDmiK <93193661+EvoDmiK@users.noreply.github.com>`.
- **Normalization**: Run `python3 scripts/normalize_worklogs.py --apply` after adding/updating worklogs.
