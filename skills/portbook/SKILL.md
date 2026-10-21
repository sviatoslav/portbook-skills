---
name: portbook
description: Use Portbook to discover and reuse stable local TCP ports for project services across worktrees and coding agents, and allocate or release reservations when authorized.
---

# Portbook

## Establish the project contract

Read the project's AGENTS.md and linked repository documentation for stable service
names, the intended owner directory/worktree scope, and permission to allocate.
Every service needs an explicit name, even in a single-port project. Names belong
in repository documentation; no Portbook manifest is needed. If the name or owner
scope is unclear, ask before choosing a new convention. Existing bookings can aid
discovery but do not authorize selecting an unrelated name.

Use the intended existing absolute owner directory with `--directory`, especially
when working from a subfolder. Portbook defaults to the current directory, does
not discover Git roots, and canonicalizes directory aliases. Derive paths from
the current checkout; do not commit developer-machine paths. Repository naming
and scope conventions are instructions for agents, not CLI enforcement.

## Check compatibility

Target **Portbook 0.3.0 or newer**. Install the binary separately; earlier
versions have different command/output contracts. A compatible source build may also be used when authorized.
Inspect `portbook --version` and scoped `get --help`, `reserve --help`, and
`release --help` rather than trusting the version label alone. Help is text in a
terminal and JSON when piped. Do not append `--output` to these commands. Require
`get SERVICE`, create-only `reserve SERVICE` (duplicate fails), and explicit names
for get/reserve and single-service release. If unavailable or unclear, stop and
request/build a compatible version as authorized; never fall back to old
create-or-return reserve behavior.

Before release or worktree teardown, also inspect `release --help`.
Require booking-only release (no TCP probe or busy-port refusal); bulk teardown
also requires exact-owner `release --all`. Older builds lack these features.
Report absent or unclear support before teardown; do not infer it from a version
label or pretend teardown ran. `--output table|json` is supported only on `list`,
`cleanup`, and the `config` subtree, after the command name; root-prefix output
flags are invalid.

## Read, then allocate only when permitted

For the documented owner and service, use argument-safe commands like:

```sh
portbook list --directory "$owner" --output json
portbook get --directory "$owner" -- "$service"
```

Validate list JSON as an object with `command: "list"` and a `bookings` array
(including `[]` when empty); check each row's directory, service, and port before
relying on it. Validate successful get output as one decimal TCP port in 1–65535.
Get success prints only the port and newline on terminals and pipes; it reads a
snapshot without allocation, locks, config reads, or probes.
Reuse that port and supply it through the project's appropriate startup flag or
environment variable. A listener on that port does not prove process ownership;
do not kill it or allocate a replacement merely because it is occupied.

Only an explicit `reservation not found` runtime diagnostic for this owner/name
establishes absence. Exit status 1 or `runtime_error` alone is insufficient.
Usage, corruption, access, malformed output, and unknown failures must surface
without mutation. Never use unconditional `get || reserve`.

If positively missing, follow the repository's allocation permission rule and
existing user authorization. Ask when creation lacks authorization; do not repeat
approval already granted for this work. If permitted:

```sh
portbook reserve --directory "$owner" -- "$service"
```

Validate and use the returned port. If a concurrent agent wins and reserve reports
`reservation already exists`, get that same name again (at most two read retries).
Stop on other errors or persistent failure; do not loop allocations. New bookings
use the lowest globally unbooked, TCP-bindable allowed port. Missing configuration
already provides 49152–65535; do not change the pool just to start a service.

## Preserve reservations and tear down the intended owner

Stopping a server does not release its stable port. Release removes booking data
only, even for busy or uncertain ports; it neither stops a listener nor proves
ownership of its process. Stopping services is a separate, task-specific action,
not a prerequisite for deleting a booking. Use release only for intended,
authorized removal. Do not rewrite the registry, create a per-project substitute,
change the global pool, or kill processes to bypass failures.

For an authorized worktree deletion, automatically remove that exact owner's
bookings before removing its directory, once the compatibility gate above passes:

```sh
portbook release --all --directory "$owner"
```

Alternatively run `portbook release --all` from the intended owner directory.
Do not rely on cwd when running in a subfolder. Deletion authorization covers
this scoped teardown; do not ask again just because a port is occupied. Bulk
release removes only that exact owner's bookings under one lock and atomic save,
preserving other owners. Single-service release still requires its explicit name.
A missing single booking or empty bulk target reports an error; surface failures
before directory removal rather than assuming teardown succeeded. In particular,
corrupt/inaccessible state must not be repaired or bypassed. Release success is
always a plain confirmation; use exit status and stderr, not JSON parsing, to
detect failure. Do not pass `--output` to single or bulk release.

Chat archive alone does not authorize worktree deletion or reservation removal.
Keep bookings stable for stopped servers and existing directories outside an
intended removal task. If the directory is already gone, report that release
requires an existing owner; do not invent flags or use global cleanup as a
worktree-deletion fallback. No periodic cleanup, hook, or daemon is needed.

## Restore defaults only when requested

For an explicitly requested pool reset, use `portbook config reset` (optionally
`--output json` after `config` or `reset`). It atomically persists 49152–65535
in the selected config and preserves bookings and location selection. It does
not repair corrupt evidence. `config path reset` changes location selection,
not pool contents. Do not reset or expand the pool to bypass allocation failures.
