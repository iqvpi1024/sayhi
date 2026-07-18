"""Small local CLI for the approved synthetic Micro demonstration."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .runtime import open_runtime


DEFAULT_DATA_DIR = Path.home() / ".noetide" / "data"


def _data_dir(args: argparse.Namespace) -> Path:
    return Path(args.data_dir) if args.data_dir else DEFAULT_DATA_DIR


def _with_runtime(args: argparse.Namespace, action):
    runtime = open_runtime(_data_dir(args))
    try:
        return action(runtime)
    finally:
        runtime.close()


def cmd_init(args: argparse.Namespace) -> int:
    _with_runtime(args, lambda runtime: runtime.revision())
    print(f"Initialized local data directory: {_data_dir(args)}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    revision = _with_runtime(args, lambda runtime: runtime.revision())
    print(f"Current revision: {revision}")
    return 0


def cmd_intake(args: argparse.Namespace) -> int:
    if args.text is not None:
        print("rejected: this Release Candidate accepts only its packaged synthetic demo Source", file=sys.stderr)
        return 2
    receipt = _with_runtime(args, lambda runtime: runtime.intake())
    print(f"Intake status: {receipt['status']}")
    print(f"Source ID: {receipt['source_id']}")
    return 0 if receipt["status"] in {"stored", "duplicate"} else 1


def cmd_propose(args: argparse.Namespace) -> int:
    proposal = _with_runtime(args, lambda runtime: runtime.propose(args.source_id))
    print(f"ChangeSet ID: {proposal['changeset_id']}")
    print(f"Status: {proposal['status']}")
    print(f"Base revision: {proposal['base_revision']}")
    return 0


def cmd_changesets(args: argparse.Namespace) -> int:
    changeset = _with_runtime(args, lambda runtime: runtime.changeset("changeset_micro_001"))
    if changeset is None:
        print("No ChangeSet found.")
        return 0
    for key in ("changeset_id", "status", "base_revision", "published_revision", "receipt_id"):
        if changeset.get(key) is not None:
            print(f"{key}: {changeset[key]}")
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    approved = _with_runtime(args, lambda runtime: runtime.approve(args.id, args.actor))
    print(f"ChangeSet ID: {approved['changeset_id']}")
    print(f"Status: {approved['status']}")
    return 0


def cmd_publish(args: argparse.Namespace) -> int:
    receipt = _with_runtime(args, lambda runtime: runtime.publish(args.id, args.idempotency_key))
    print(f"Publish status: {receipt['status']}")
    print(f"Published revision: {receipt.get('published_revision')}")
    return 0 if receipt["status"] == "published" else 1


def cmd_revert(args: argparse.Namespace) -> int:
    receipt = _with_runtime(args, lambda runtime: runtime.revert(args.id, args.idempotency_key))
    print(f"Revert status: {receipt['status']}")
    print(f"Compensation revision: {receipt.get('compensation_revision')}")
    return 0 if receipt["status"] == "published" else 1


def cmd_view(args: argparse.Namespace) -> int:
    view = _with_runtime(args, lambda runtime: runtime.view(args.view_name))
    print(f"Data revision: {view['data_revision']}")
    print(f"View revision: {view['view_revision']}")
    print(f"Freshness: {view['freshness_status']}")
    print(view["payload"])
    return 0

def cmd_c1(args: argparse.Namespace) -> int:
    value = _with_runtime(args, lambda runtime: getattr(runtime, f"create_demo_{args.command}")())
    print(f"{value['object_type']}: {value.get('decision_id') or value.get('outcome_id') or value.get('assertion_id')}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="noetide")
    parser.add_argument("--data-dir", help="local SQLite data directory")
    commands = parser.add_subparsers(dest="command", required=True)
    for name, handler in (("init", cmd_init), ("status", cmd_status), ("changesets", cmd_changesets)):
        command = commands.add_parser(name)
        command.set_defaults(handler=handler)
    intake = commands.add_parser("intake")
    intake.add_argument("--text")
    intake.set_defaults(handler=cmd_intake)
    propose = commands.add_parser("propose")
    propose.add_argument("source_id")
    propose.set_defaults(handler=cmd_propose)
    approve = commands.add_parser("approve")
    approve.add_argument("--id", required=True)
    approve.add_argument("--actor", default="person_alpha")
    approve.set_defaults(handler=cmd_approve)
    for name, handler, key in (("publish", cmd_publish, "cli_publish_001"), ("revert", cmd_revert, "cli_revert_001")):
        command = commands.add_parser(name)
        command.add_argument("--id", required=True)
        command.add_argument("--idempotency-key", default=key)
        command.set_defaults(handler=handler)
    for name, view_name in (("person-card", "person_card"), ("timeline", "relationship_timeline")):
        command = commands.add_parser(name)
        command.set_defaults(handler=cmd_view, view_name=view_name)
    for name in ("decision", "outcome", "scenario"):
        command = commands.add_parser(name)
        command.set_defaults(handler=cmd_c1)
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (KeyError, RuntimeError, ValueError, PermissionError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
