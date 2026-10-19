# Portbook skills

Reusable agent guidance for coordinating stable local TCP ports across projects,
worktrees, and coding agents with [Portbook](https://github.com/sviatoslav/portbook).
The canonical skill is [skills/portbook/SKILL.md](skills/portbook/SKILL.md).

## Availability and requirements

The skill targets **Portbook 0.2.0 or newer**. Portbook v0.2.0 is being prepared
but is not tagged or published yet; Homebrew and release downloads still provide
v0.1.0, which is incompatible. The skill is already independently installable.
Until the binary release is available, use only an authorized compatible source
build from the Portbook repository.

Check `portbook --version` and scoped `--output table` help. Require read-only
`get SERVICE`, create-only `reserve SERVICE`, explicit service names, record-only
release without probes, and exact-owner `release --all`. Do not trust a version
label alone or fall back to old create-or-return behavior. An unavailable or
unclear feature must be reported before allocation or teardown.

Current Portbook source includes these features and `install-skills`; see the
[release preparation guide](https://github.com/sviatoslav/portbook/blob/master/docs/RELEASING.md).

## Install

Install the Portbook binary separately; the skill does not provide it. With
Node.js/npm/npx installed, the third-party
[Vercel Skills CLI](https://github.com/vercel-labs/skills) handles installation:

```sh
npx --yes skills add sviatoslav/portbook-skills --skill portbook --global --agent codex
# Or target Claude Code:
npx --yes skills add sviatoslav/portbook-skills --skill portbook --global --agent claude-code
```

These select only `portbook`, globally for the current user. The first `--yes`
authorizes npm to fetch/run the installer. Skills CLI normally asks for
confirmation; it may skip prompts inside coding agents. Adding a final `--yes`
skips its confirmations explicitly. Reinstallation can replace user-edited
skill files; review or back up edits first. Upstream controls agent destinations
and copy/symlink behavior. No maintenance guarantee is implied.

The pending Portbook v0.2.0 source includes `portbook install-skills` (default
Codex) and `portbook install-skills --agent claude-code`. It delegates to the same
command with a five-minute timeout, process-group cancellation, and inherited
confirmation/stdio. Published v0.1.0 has no installer command; use npx directly
to install the public skill. Installation is separate from binary compatibility.

For local development, substitute an absolute checkout path for
`sviatoslav/portbook-skills`. Development tests must isolate HOME/XDG and
agent-specific paths; do not install into real user skill directories.

See official [Codex skills guidance](https://learn.chatgpt.com/docs/build-skills)
and [Claude Code skills guidance](https://code.claude.com/docs/en/skills).

## Project setup

Document stable explicit service names, the intended owner directory/worktree
scope, allocation permissions, and startup port flags/environment variables in
AGENTS.md or linked repository documentation. Even one-port projects need an
explicit documented name. No `.portbook.json` manifest is required. Use
checkout-relative scope descriptions rather than developer-machine paths.

Agents inspect scoped bookings and read the documented name using `get`;
allocation requires a positive missing result plus permission. Stopping a server
does not release its reservation. Naming conventions and permissions are agent
instructions, not CLI enforcement.

For authorized worktree deletion, a compatible build should automatically run
`portbook release --all --directory "$owner"` before directory removal. This
removes only that exact owner's booking data, including busy ports, without
stopping listeners; stopping services is a separate responsibility. It does not
need another permission request for the already-authorized scoped teardown.
Missing bookings still report an error. Surface failures before deleting the
directory. Chat archive alone does not authorize teardown. Never substitute
global cleanup, and keep bookings stable for stopped servers and existing
directories outside an intended removal task. No scheduler, hook, or daemon is
included.

## License

[MIT](LICENSE), copyright 2026 Sviatoslav Yakymiv.
