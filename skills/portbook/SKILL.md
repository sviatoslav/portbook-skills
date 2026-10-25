---
name: portbook
description: Use Portbook to read and reuse stable local TCP ports for project services, reserve missing ports when authorized, and release bookings during scoped teardown.
---

# Portbook

## Select the owner and service

Read the project's `AGENTS.md` for the service name, owner directory, allocation
permission, and startup command. Resolve the owner to an existing absolute path
from the checkout. Each directory has its own bookings; pass `--directory` when
working from a subfolder. Ask for missing naming or ownership conventions.

Use Portbook 0.3.0 or newer, or a compatible source build. Check `portbook --version`
and scoped help when compatibility is unclear: get reads an existing booking,
reserve creates one, and release removes only the exact owner's records.
Report unsupported behavior before changing state.

## Read and reserve

For the documented owner and service:

```sh
portbook list --directory "$owner" --output json
portbook get --directory "$owner" -- "$service"
```

List returns an object with `command: "list"` and a `bookings` array. Check the
owner, service, and port in its rows. Successful get and reserve print one decimal
port in 1–65535. Supply that port through the project's startup interface.

Allocate only after an explicit `reservation not found` runtime diagnostic for
this owner and service, with repository or user authorization:

```sh
portbook reserve --directory "$owner" -- "$service"
```

Honor authorization already given. On `reservation already exists`, read the
same booking again; stop if that retry fails. Surface usage, storage, permission,
or malformed-output errors before further mutations. Keep an existing booking
when its port is busy, and verify process ownership before stopping a listener.
Start a newly reserved service promptly because other programs can bind its port.

## Release during teardown

Keep bookings between restarts. For authorized worktree deletion, release the
exact owner's bookings while its directory still exists:

```sh
portbook release --all --directory "$owner"
```

The deletion request authorizes this scoped release. Release removes booking
records even for busy ports; manage running services through the project's
shutdown procedure. Success is a plain confirmation; use exit status and stderr
to detect failure. Surface missing-booking or storage errors before removing the
directory. Keep chat archival separate from service or worktree teardown.

## Pool maintenance

Pool changes and global cleanup require their own task authorization. Missing
configuration already supplies ports 49152–65535. For a requested pool reset:

```sh
portbook config reset
```

This restores the default pool while preserving bookings and location selection;
`config path reset` clears the saved location choice instead. Resolve invalid
configuration before retrying.

For compatibility, use `--output table|json` only after `list`, `cleanup`,
`config show`, or `config path get`. Help and errors default to text in a terminal
and JSON when piped. Check scoped help for additional options.
