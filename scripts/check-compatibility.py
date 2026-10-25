#!/usr/bin/env python3
"""Exercise documented Portbook examples without touching user state."""
import argparse
import json
import os
from pathlib import Path
import re
import shlex
import socket
import subprocess
import sys
import tempfile


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def read_examples(root):
    examples = {}
    for relative in ("README.md", "skills/portbook/SKILL.md"):
        text = (root / relative).read_text(encoding="utf-8")
        for block in re.finditer(r"```sh\n(.*?)```", text, re.S):
            for offset, line in enumerate(block.group(1).splitlines()):
                args = shlex.split(line, comments=True)
                if not args or args[0] != "portbook":
                    continue
                location = f"{relative}:{text.count(chr(10), 0, block.start(1)) + offset + 1}"
                args = args[1:]
                require(args, f"{location}: expected a Portbook command")
                name = " ".join(args[:2]) if args[0] == "config" else args[0]
                examples.setdefault(name, []).append((location, args))
    required = {"list", "get", "reserve", "release", "config reset", "install-skills"}
    require(set(examples) == required, "Add coverage for missing or new command examples: "
            + repr(set(examples) ^ required))
    for name, commands in examples.items():
        if name != "install-skills":
            require(len(commands) == 1, f"Add a scenario for additional {name} examples")
    return examples


def check(binary, root):
    examples = read_examples(root)
    with tempfile.TemporaryDirectory(prefix="portbook-skill-check-") as directory:
        temporary = Path(directory).resolve()
        owner = temporary / "project with spaces"
        neighbor = temporary / "other project"
        child = owner / "nested project"
        for path in (owner, neighbor, child):
            path.mkdir()
        service = "-api"
        env = dict(os.environ, HOME=str(temporary / "home"),
                   XDG_CONFIG_HOME=str(temporary / "xdg"),
                   PORTBOOK_CONFIG_DIR=str(temporary / "pool"))

        def run(args, code=0, location="check setup"):
            result = subprocess.run([str(binary), *args], cwd=temporary, env=env,
                                    capture_output=True, text=True, timeout=15)
            require(result.returncode == code,
                    f"{location}: {shlex.join(args)}: expected exit {code}, "
                    f"got {result.returncode}\n{result.stderr}")
            require(not result.stderr if code == 0 else not result.stdout,
                    f"{location}: unexpected output stream: {result}")
            return result.stdout if code == 0 else result.stderr

        def example(name, selected_owner=owner, code=0):
            location, args = examples[name][0]
            variables = {"$owner": str(selected_owner), "$service": service}
            return run([variables.get(arg, arg) for arg in args], code, location)

        def failure(name, diagnostic):
            error = json.loads(example(name, code=1))["error"]
            require(error["code"] == "runtime_error" and diagnostic in error["message"],
                    f"{name}: expected {diagnostic!r}, got {error!r}")

        def port(output):
            require(re.fullmatch(r"[0-9]+\n", output) is not None
                    and 1 <= int(output) <= 65535, f"Invalid port output: {output!r}")
            return int(output)

        def bookings():
            return json.loads(run(["list", "--all", "--output", "json"]))["bookings"]

        version = run(["--version"]).strip()
        for location, args in examples["install-skills"]:
            run([*args, "--help"], location=location)

        empty = json.loads(example("list"))
        require(empty == {"command": "list", "bookings": []}, "Expected an empty list")
        failure("get", "reservation not found")
        reserved = port(example("reserve"))
        require(port(example("get")) == reserved, "Get changed the reserved port")
        failure("reserve", "reservation already exists")
        row = {"directory": str(owner), "service": service, "port": reserved}
        require(json.loads(example("list")) == {"command": "list", "bookings": [row]},
                "Scoped list did not return the documented booking shape")
        port(example("reserve", neighbor))
        port(example("reserve", child))
        before = bookings()
        require(len({row["port"] for row in before}) == 3, "Reservations overlap")

        run(["config", "remove", "--all"])
        require(port(example("get")) == reserved, "Get lost a booking outside the pool")
        example("config reset")
        pool = json.loads(run(["config", "show", "--output", "json"]))
        require(pool["ranges"] == [{"start": 49152, "end": 65535}]
                and pool["total"] == 16384, "Reset did not restore the default pool")
        require(bookings() == before, "Reset changed existing bookings")

        with socket.socket() as listener:
            listener.bind(("127.0.0.1", reserved))
            listener.listen(1)
            require(port(example("get")) == reserved, "Get failed for a busy port")
            require(example("release").startswith("Released "),
                    "Release success must be a plain confirmation")
        require(bookings() == [row for row in before if row["directory"] != str(owner)],
                "Bulk release changed another owner or a descendant")
        require(json.loads(example("list"))["bookings"] == [], "Release left bookings")
        failure("release", "reservation not found")
        print(f"PASS: {version}; documented examples, lifecycle, and pool reset")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path, help="Path to a Portbook executable")
    args = parser.parse_args()
    try:
        check(args.binary.resolve(strict=True), Path(__file__).resolve().parent.parent)
    except (OSError, RuntimeError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
