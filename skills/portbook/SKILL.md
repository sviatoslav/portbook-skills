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

Target **Portbook 0.2.0 or newer**. Install the binary separately; v0.1.0 is
incompatible. A compatible source build may also be used when authorized.
Inspect `portbook --version` and plain scoped help
(`--output table`) rather than trusting the version label alone. Require
`get SERVICE`, create-only `reserve SERVICE` (duplicate fails), and explicit names
for get/reserve and single-service release. If unavailable or unclear, stop and
request/build a compatible version as authorized; never fall back to old
create-or-return reserve behavior.

Before release or worktree teardown, also inspect plain `release --help`.
Require booking-only release (no TCP probe or busy-port refusal); bulk teardown
also requires exact-owner `release --all`. Older builds lack these features.
Report absent or unclear support before teardown; do not infer it from a version
label or pretend teardown ran.

## Read, then allocate only when permitted

For the documented owner and service, use argument-safe commands like:

```sh
portbook list --directory "$owner" --output json
portbook get --directory "$owner" -- "$service"
```

Validate list JSON as an object with `command: "list"` and a `bookings` array
(including `[]` when empty); check each row's directory, service, and port before
relying on it. Validate successful get output as one decimal TCP port in 1–65535.
Get success prints only the port and newline, including with JSON output; it reads a snapshot without allocation, locks, config reads, or probes.
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
corrupt/inaccessible state must not be repaired or bypassed.

Chat archive alone does not authorize worktree deletion or reservation removal.
Keep bookings stable for stopped servers and existing directories outside an
intended removal task. If the directory is already gone, report that release
requires an existing owner; do not invent flags or use global cleanup as a
worktree-deletion fallback. No periodic cleanup, hook, or daemon is needed.
