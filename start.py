"""Noetide development launcher: the single D0 entry command (synthetic data only).

Decided by ADR-0010 section 5.1. This script checks the runtime, creates a
declared synthetic dev data root, initializes the local database, runs a
minimal preflight smoke, and prints the local access entry. It never touches
the network, never reads or writes outside the declared data root, and never
modifies a damaged database file.
"""

from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

DEFAULT_DEV_ROOT = ROOT / "devdata"
MIN_PYTHON = (3, 12)
EXPECTED_REVISION = "rev_010"
EXPECTED_PRAGMAS = {"foreign_keys": 1, "journal_mode": "delete", "synchronous": 2}

EXIT_OK = 0
EXIT_RUNTIME_UNSUPPORTED = 2
EXIT_DATA_ROOT_UNUSABLE = 3
EXIT_DATABASE_CORRUPT = 4
EXIT_CLEAN_REFUSED = 5


def _eprint(message: str) -> None:
    print(message, file=sys.stderr)


def check_runtime() -> bool:
    return sys.version_info >= MIN_PYTHON


def resolve_data_root(argument: str | None) -> Path:
    return Path(argument).expanduser().resolve() if argument else DEFAULT_DEV_ROOT.resolve()


def ensure_data_root(root: Path) -> None:
    """Create the declared data root and prove it is writable."""
    root.mkdir(parents=True, exist_ok=True)
    probe = root / ".write_probe"
    probe.write_text("probe", encoding="utf-8")
    probe.unlink()


def clean_allowed(target: Path) -> bool:
    """--clean may only delete inside the default synthetic devdata root."""
    default = DEFAULT_DEV_ROOT.resolve()
    resolved = target.resolve()
    return resolved == default or default in resolved.parents


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Noetide dev launcher (synthetic data only)")
    parser.add_argument("--data-root", default=None, help="synthetic dev data root (default: <repo>/devdata)")
    parser.add_argument("--clean", action="store_true", help="delete the default synthetic devdata root after a path-prefix check")
    args = parser.parse_args(argv)

    if not check_runtime():
        _eprint(f"error: Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} or newer is required; current runtime is not supported.")
        return EXIT_RUNTIME_UNSUPPORTED

    data_root = resolve_data_root(args.data_root)

    if args.clean:
        if not clean_allowed(data_root):
            _eprint(f"error: --clean refused: {data_root} is outside the default synthetic devdata root {DEFAULT_DEV_ROOT.resolve()}.")
            _eprint("No files were deleted. Remove custom data roots manually if you own them.")
            return EXIT_CLEAN_REFUSED
        if data_root.exists():
            shutil.rmtree(data_root)
            print(f"Removed synthetic dev data root: {data_root}")
        else:
            print(f"Nothing to clean: {data_root} does not exist.")
        return EXIT_OK

    try:
        ensure_data_root(data_root)
    except OSError:
        _eprint(f"error: data root is not writable: {data_root}")
        _eprint("No files were written outside the declared data root. Choose a writable --data-root.")
        return EXIT_DATA_ROOT_UNUSABLE

    from noetide_micro.runtime import open_runtime

    try:
        runtime = open_runtime(data_root)
    except sqlite3.DatabaseError:
        _eprint(f"error: the database at {data_root} appears damaged; startup refused.")
        _eprint("The original file was left untouched and no repair was attempted. Restore from a backup or export.")
        return EXIT_DATABASE_CORRUPT
    except OSError:
        _eprint(f"error: data root is not writable: {data_root}")
        _eprint("No files were written outside the declared data root. Choose a writable --data-root.")
        return EXIT_DATA_ROOT_UNUSABLE

    try:
        revision = runtime.revision()
        pragmas = runtime._store.pragma_values()
    finally:
        runtime.close()

    if revision != EXPECTED_REVISION:
        _eprint(f"error: preflight smoke failed: expected revision {EXPECTED_REVISION}, got {revision}.")
        return EXIT_DATABASE_CORRUPT
    normalized = {key: (value.lower() if isinstance(value, str) else value) for key, value in pragmas.items()}
    if normalized != EXPECTED_PRAGMAS:
        _eprint(f"error: preflight smoke failed: unexpected SQLite pragmas {pragmas}.")
        return EXIT_DATABASE_CORRUPT

    print("Noetide dev environment ready (synthetic data only).")
    print(f"Data root: {data_root}")
    print(f"Preflight smoke: revision {revision}, pragmas OK.")
    print("Local access entry:")
    print('  python -m noetide_micro status --data-dir "' + str(data_root) + '"')
    print('  python -m noetide_micro guide --data-dir "' + str(data_root) + '"')
    return EXIT_OK


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
