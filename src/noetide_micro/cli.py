"""Small local CLI for the approved synthetic Micro demonstration."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .alpha_explainability import (
    confirm_and_delete_data,
    create_reference_backup,
    export_roundtrip,
    paths_descriptor,
    uninstall_info,
)
from .app_shell import render_impact_preview, render_review
from .changesets import ChangeSetService
from .runtime import open_runtime
from .store import SemanticStore


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

def cmd_review(args: argparse.Namespace) -> int:
    candidates = _with_runtime(args, lambda runtime: runtime.review_candidates())
    for candidate in candidates:
        print(f"{candidate['candidate_id']}: {candidate['status']}")
    return 0


def cmd_web(args: argparse.Namespace) -> int:
    from .local_web import serve_local_web

    return serve_local_web(
        _data_dir(args),
        host=args.host,
        port=args.port,
        backup_dir=args.backup_dir,
    )


def _open_existing_store(args: argparse.Namespace) -> SemanticStore | None:
    path = _data_dir(args) / "noetide.sqlite3"
    if not path.exists():
        return None
    return SemanticStore(path)


def cmd_paths(args: argparse.Namespace) -> int:
    runtime = open_runtime(_data_dir(args))
    try:
        profile = str(runtime.fixture.get("synthetic_profile_id", "synthetic_demo_profile"))
    finally:
        runtime.close()
    info = paths_descriptor(_data_dir(args), profile)
    print(f"data root: {info['declared_data_root']}")
    print(f"synthetic profile: {info['synthetic_profile_id']}")
    print(f"separated from default real path: {info['synthetic_real_separated']}")
    return 0


def cmd_backup(args: argparse.Namespace) -> int:
    result = create_reference_backup(_data_dir(args), args.destination)
    if not result["backup_created"] or not result["manifest_verified"]:
        print("error: backup verification failed", file=sys.stderr)
        return 1
    print(f"backup pack: {result['pack_path']}")
    print(f"data revision: {result['data_revision']} ({result['entry_count']} entries, sha256 manifest verified)")
    print(f"roundtrip verified: {result['roundtrip']['roundtrip_verified']}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    result = export_roundtrip(_data_dir(args), args.destination)
    if result["first_status"] != "validated" or not result["roundtrip_stable"]:
        print("error: export round trip failed", file=sys.stderr)
        return 1
    print(f"export pack: {Path(args.destination).resolve()}")
    print(f"round trip stable: {result['roundtrip_stable']}; revision unchanged: {result['revision_unchanged']}")
    return 0


def cmd_uninstall_info(args: argparse.Namespace) -> int:
    info = uninstall_info(_data_dir(args))
    print("default uninstall keeps the user data directory; nothing is deleted.")
    print(f"data root preserved: {info['data_root_preserved_by_default']}")
    if args.confirm_delete:
        result = confirm_and_delete_data(
            _data_dir(args), confirm=True, backup_path=args.backup
        )
        if not result["deleted"]:
            print(f"deletion refused: {result['reason']}", file=sys.stderr)
            print("create a verified backup first: python -m noetide_micro backup <destination>")
            return 1
        print(f"data directory deleted; verified backup kept at {result['backup_verified_at']}")
    else:
        print("to delete data, pass --confirm-delete together with --backup <verified pack path>.")
    return 0


def cmd_guide(args: argparse.Namespace) -> int:
    def journey(runtime) -> int:
        clock = runtime.fixture["determinism"]["clock"]
        store = SemanticStore(_data_dir(args) / "noetide.sqlite3")
        try:
            receipt = runtime.intake()
            print(f"[record] Source {receipt['source_id']} stored (receipt {receipt['receipt_id']}).")
            proposal = runtime.propose("src_micro_001")
            relationship = store.canonical_object("rel_alpha_beta")
            labels = [
                store.canonical_object(ref)["canonical_label"]
                for ref in relationship["participant_refs"]
            ]
            item = render_review(proposal, labels)
            print(f"[review] {item['summary_text']}")
            print(f"[review] evidence: {', '.join(item['evidence_citations'])}")
            preview = render_impact_preview(proposal)
            print(f"[preview] {preview['impact_text']}")
            status = proposal["status"]
            if status in ("proposed", "approved"):
                if not args.yes:
                    answer = input("[confirm] type yes to publish this change: ")
                    if answer.strip().lower() != "yes":
                        print("cancelled: nothing was published.")
                        return 2
                if status == "proposed":
                    runtime.approve(proposal["changeset_id"], "person_alpha")
                published = runtime.publish(proposal["changeset_id"], args.publish_key)
            elif status == "published":
                published = ChangeSetService(store, runtime.fixture, clock).receipt(proposal["receipt_id"])
                print(f"[confirm] already published at {published.get('published_revision')}.")
            else:
                print(f"[confirm] ChangeSet status is {status}; nothing to publish.")
                published = None
            if published is not None:
                print(f"[confirm] publish {published['status']} -> {published.get('published_revision')} (receipt {published['receipt_id']}).")
            card = runtime.view("person_card")
            timeline = runtime.view("relationship_timeline")
            print(f"[read_view] person_card {card['freshness_status']} at {card['data_revision']}: {card['payload']}")
            print(f"[read_view] relationship_timeline {timeline['freshness_status']} at {timeline['data_revision']}: {len(timeline['payload']['history'])} history entries")
            if published is not None:
                print(f"[receipt] {published['receipt_id']} status={published['status']}")
            current = runtime.changeset("changeset_micro_001")
            if current is not None and current.get("status") == "published":
                if not args.yes:
                    answer = input("[revert] type yes to revert the published change: ")
                    if answer.strip().lower() != "yes":
                        print("revert skipped by user.")
                        return 0
                reverted = runtime.revert("changeset_micro_001", args.revert_key)
                print(f"[revert] compensation -> {reverted.get('compensation_revision')} (receipt {reverted['receipt_id']}).")
                card = runtime.view("person_card")
                timeline = runtime.view("relationship_timeline")
                print(f"[read_view] person_card {card['freshness_status']} at {card['data_revision']}: {card['payload']}")
                print(f"[read_view] relationship_timeline {timeline['freshness_status']} at {timeline['data_revision']}: {len(timeline['payload']['history'])} history entries")
            elif current is not None and current.get("status") == "reverted":
                print(f"[revert] already reverted (compensation {current.get('rollback_reference')}).")
            return 0
        finally:
            store.close()

    return _with_runtime(args, journey)


def cmd_receipts(args: argparse.Namespace) -> int:
    store = _open_existing_store(args)
    if store is None:
        print("No local data yet. Run `noetide init` first.")
        return 0
    try:
        receipts = store.ledger_records_of_type("receipt")
        if not receipts:
            print("No receipts found.")
            return 0
        for receipt in receipts:
            line = f"{receipt['receipt_id']}: status={receipt['status']}"
            if receipt.get("published_revision"):
                line += f" published_revision={receipt['published_revision']}"
            if receipt.get("compensation_revision"):
                line += f" compensation_revision={receipt['compensation_revision']}"
            print(line)
        return 0
    finally:
        store.close()


def cmd_history(args: argparse.Namespace) -> int:
    store = _open_existing_store(args)
    if store is None:
        print("No local data yet. Run `noetide init` first.")
        return 0
    try:
        changesets = store.ledger_records_of_type("changeset")
        receipts = store.ledger_records_of_type("receipt")
        events = store.ledger_records_of_type("audit_event")
        if not changesets and not receipts and not events:
            print("No history found.")
            return 0
        print("ChangeSets:")
        for item in changesets:
            print(f"  {item['changeset_id']}: status={item['status']}")
        print("Receipts:")
        for item in receipts:
            print(f"  {item['receipt_id']}: status={item['status']}")
        print("Audit events:")
        for item in events:
            print(f"  {item['changeset_id']}: {item['event_type']} at {item['revision']}")
        return 0
    finally:
        store.close()


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
    review = commands.add_parser("review")
    review.set_defaults(handler=cmd_review)
    web = commands.add_parser("web")
    web.add_argument("--host", default="127.0.0.1")
    web.add_argument("--port", type=int, default=8765)
    web.add_argument("--backup-dir", default=None)
    web.set_defaults(handler=cmd_web)
    guide = commands.add_parser("guide")
    guide.add_argument("--yes", action="store_true", help="skip interactive confirmations")
    guide.add_argument("--publish-key", default="cli_guide_publish_001")
    guide.add_argument("--revert-key", default="cli_guide_revert_001")
    guide.set_defaults(handler=cmd_guide)
    for name, handler in (("paths", cmd_paths), ("uninstall-info", cmd_uninstall_info)):
        command = commands.add_parser(name)
        command.set_defaults(handler=handler)
    uninstall = commands.choices["uninstall-info"]
    uninstall.add_argument("--confirm-delete", action="store_true")
    uninstall.add_argument("--backup", default=None)
    for name, handler in (("backup", cmd_backup), ("export", cmd_export)):
        command = commands.add_parser(name)
        command.add_argument("destination")
        command.set_defaults(handler=handler)
    for name, handler in (("receipts", cmd_receipts), ("history", cmd_history)):
        command = commands.add_parser(name)
        command.set_defaults(handler=handler)
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (KeyError, RuntimeError, ValueError, PermissionError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
