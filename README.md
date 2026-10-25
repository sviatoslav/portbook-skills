# Portbook skills

Agent guidance for reusing stable local TCP ports with
[Portbook](https://github.com/sviatoslav/portbook).

## Install

Install [Portbook](https://github.com/sviatoslav/portbook/blob/master/docs/INSTALLING.md)
0.3.0 or newer and Node.js with npm/npx, then choose your agent:

```sh
portbook install-skills --agent codex
# Or use Claude Code:
portbook install-skills --agent claude-code
```

This installs the skill globally through the Vercel Skills CLI. Follow its
prompts and back up local skill edits before reinstalling.

## Project setup

In your project's `AGENTS.md`, define:

- Service names, such as `api` and `web`.
- Each service's owner directory, relative to the checkout.
- Permission to reserve a port when its booking is missing.
- The startup flag or environment variable that supplies the port.

The [skill](skills/portbook/SKILL.md) covers reading, allocation, and scoped
teardown. Keep bookings between service restarts.

## Compatibility checks

Run the documented command examples against a Portbook binary with Python 3.9+:

```sh
python3 scripts/check-compatibility.py /absolute/path/to/portbook
```

The check uses temporary state and owner directories, exercises reservation,
release, and pool reset, and validates installer examples with `--help`.
Keep executable Portbook examples in fenced `sh` blocks so the check includes them.

CI runs this check against the minimum supported release, v0.3.0, and current
Portbook `master` on macOS and Linux.

[MIT License](LICENSE), copyright 2026 Sviatoslav Yakymiv.
