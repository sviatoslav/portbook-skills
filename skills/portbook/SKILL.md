---
name: portbook
description: "Best practices for integrating Portbook with worktree-based development: reserve during setup, read during startup, and release during removal."
---

# Portbook

## Project integration

Read the project's `AGENTS.md` or linked workflow documentation for service names,
default ports, creation and removal scripts, and startup flags or environment
variables. Keep these project-specific settings and commands in that documentation.

Run Portbook commands from the checkout root. Portbook uses the current directory
for bookings; package subdirectories have separate bookings. Use
`--directory /absolute/path/to/checkout` when a command runs elsewhere.

Prefer direct CLI calls in existing scripts and hooks. Adapt the following pattern
to the project's workflow. The examples use Portbook 0.3.0 or newer; consult scoped
help when compatibility is unclear.

## Recommended worktree workflow

### Creation script

Reserve all required service ports in the setup script or hook that runs
automatically during worktree creation, after the new directory exists. Reuse
existing bookings when setup is repeated. Inspect them with:

```sh
portbook list --output json
```

For each missing service:

```sh
portbook reserve -- "$service"
```

Keep setup errors visible. If setup fails partway through, keep successful
bookings so the next attempt can reuse them.

### During use

Read the booked port and pass it through the service's startup flag or environment
variable. Successful `get` and `reserve` print a decimal port:

```sh
portbook get -- "$service"
```

For projects with default ports:

```sh
api_port="$(portbook get api 2>/dev/null || printf '8080\n')"
```

This falls back whenever lookup fails. A main checkout without bookings can use
its defaults. After setup, startup commands only read bookings. Keep bookings
through service restarts and closed terminals. A reservation does not hold a
listening socket; keep the booking stable while resolving a port conflict.

### Removal script

Stop remaining worktree services through their usual shutdown commands. Detached
services can outlive their terminals; target them through the service's own stop
command or a tracked process identity.

In the worktree removal script or hook, release its bookings before deleting the
directory:

```sh
portbook release --all
```

Release removes only this directory's records, even for busy ports, and does not
stop processes. A checkout with no bookings needs no release. Keep cleanup errors
visible and resolve them before removing the directory.
