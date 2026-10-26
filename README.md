# Portbook skills

Agent best practices for worktree development with
[Portbook](https://github.com/sviatoslav/portbook).

## Install

Install [Portbook](https://github.com/sviatoslav/portbook/blob/main/docs/INSTALLING.md)
0.3.0 or newer and Node.js with npm/npx, then choose your agent:

```sh
portbook install-skills --agent codex
# Or use Claude Code:
portbook install-skills --agent claude-code
```

This installs the skill globally through the Vercel Skills CLI. Follow its
prompts and back up local skill edits before reinstalling.

## Project setup

The [Portbook skill](skills/portbook/SKILL.md) contains the recommended worktree
workflow. Keep service names, default ports, and hook commands in each project's
`AGENTS.md` or linked documentation. See the
[integration examples](https://github.com/sviatoslav/portbook/blob/main/docs/AGENT-SETUP.md)
for setup, startup, and removal scripts.

## Compatibility checks

Run the documented command examples against a Portbook binary with Python 3.9+:

```sh
python3 scripts/check-compatibility.py /absolute/path/to/portbook
```

The check uses temporary state and owner directories, exercises reservation,
release, and pool reset, and validates installer examples with `--help`.
Keep executable Portbook examples in fenced `sh` blocks so the check includes them.

CI runs this check against the minimum supported release, v0.3.0, and current
Portbook `main` on macOS and Linux.

[MIT License](LICENSE), copyright 2026 Sviatoslav Yakymiv.
