import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from noetide_micro.store import SeedConflictError
from noetide_micro.testing_adapter import create_system

JsonObject = dict[str, Any]
DEFAULT_DATA_DIR = Path.home() / ".noetide" / "data"
FIXTURE_PATH = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "micro_relationship_v1" / "fixture.json"


def _load_fixture():
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_system(data_dir):
    fixture = _load_fixture()
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)
    return create_system(fixture, data_dir)


def _get_store(data_dir):
    system = _get_system(data_dir)
    return system, system.store


def cmd_init(args):
    data_dir = Path(args.data_dir) if args.data_dir else DEFAULT_DATA_DIR
    data_dir.mkdir(parents=True, exist_ok=True)
    fixture = _load_fixture()
    db_path = data_dir / "micro.sqlite3"
    if db_path.exists():
        print("Database exists:", db_path)
        return 0
    try:
        create_system(fixture, data_dir)
        print("Database initialized:", db_path)
        return 0
    except SeedConflictError as e:
        print("Conflict:", e)
        return 1


def cmd_status(args):
    data_dir = Path(args.data_dir) if args.data_dir else DEFAULT_DATA_DIR
    if not data_dir.exists():
        print("Data dir missing. Run init first.")
        return 1
    system, store = _get_store(data_dir)
    try:
        print("Current revision:", store.current_revision())
        return 0
    finally:
        store.close()


def cmd_intake(args):
    data_dir = Path(args.data_dir) if args.data_dir else DEFAULT_DATA_DIR
    if not data_dir.exists():
        print("Data dir missing. Run init first.")
        return 1
    system = _get_system(data_dir)
    fixture = _load_fixture()
    request = dict(fixture["intake_request"])
    if args.text:
        request["inline_content"] = args.text
        request["content_hash"] = _digest_text(args.text)
        request["byte_length"] = len(args.text.encode("utf-8"))
    try:
        result = system.intake(request)
        print("Intake status:", result["status"])
        print("Source ID:", result.get("source_id", "N/A"))
        return 0
    finally:
        system.store.close()


def cmd_propose(args):
    data_dir = Path(args.data_dir) if args.data_dir else DEFAULT_DATA_DIR
    if not data_dir.exists():
        print("Data dir missing. Run init first.")
        return 1
    system = _get_system(data_dir)
    try:
        proposal = system.propose_contact_changeset(args.source_id)
        print("ChangeSet proposed:", proposal["changeset_id"])
        print("Status:", proposal["status"])
        print("Base revision:", proposal["base_revision"])
        return 0
    finally:
        system.store.close()


def cmd_changesets(args):
    data_dir = Path(args.data_dir) if args.data_dir else DEFAULT_DATA_DIR
    if not data_dir.exists():
        print("Data dir missing. Run init first.")
        return 1
    system, store = _get_store(data_dir)
    try:
        cs = store.ledger_record("changeset_micro_001")
        if cs is None:
            print("No ChangeSet found.")
            return 0
        print("ChangeSet ID:", cs["changeset_id"])
        print("Status:", cs["status"])
        print("Base revision:", cs["base_revision"])
        print("Actor:", cs["actor"])
        print("Confirmation policy:", cs["confirmation_policy"])
        if cs.get("published_revision"):
            print("Published revision:", cs["published_revision"])
        if cs.get("receipt_id"):
            print("Receipt ID:", cs["receipt_id"])
        return 0
    finally:
        store.close()


def cmd_approve(args):
    data_dir = Path(args.data_dir) if args.data_dir else DEFAULT_DATA_DIR
    if not data_dir.exists():
        print("Data dir missing. Run init first.")
        return 1
    system = _get_system(data_dir)
    try:
        approved = system.approve_changeset(args.id, args.actor)
        print("ChangeSet approved:", approved["changeset_id"])
        print("Status:", approved["status"])
        if approved.get("approval"):
            print("Approved by:", approved["approval"]["actor"])
            print("Approved at:", approved["approval"]["recorded_at"])
        return 0
    finally:
        system.store.close()


def cmd_publish(args):
    data_dir = Path(args.data_dir) if args.data_dir else DEFAULT_DATA_DIR
    if not data_dir.exists():
        print("Data dir missing. Run init first.")
        return 1
    system = _get_system(data_dir)
    try:
        receipt = system.publish_changeset(args.id, args.idempotency_key)
        print("Publish status:", receipt["status"])
        if receipt.get("published_revision"):
            print("Published revision:", receipt["published_revision"])
        if receipt.get("receipt_id"):
            print("Receipt ID:", receipt["receipt_id"])
        return 0
    finally:
        system.store.close()


def cmd_revert(args):
    data_dir = Path(args.data_dir) if args.data_dir else DEFAULT_DATA_DIR
    if not data_dir.exists():
        print("Data dir missing. Run init first.")
        return 1
    system = _get_system(data_dir)
    try:
        receipt = system.revert_changeset(args.id, args.idempotency_key)
        print("Revert status:", receipt["status"])
        if receipt.get("compensation_revision"):
            print("Compensation revision:", receipt["compensation_revision"])
        if receipt.get("receipt_id"):
            print("Receipt ID:", receipt["receipt_id"])
        return 0
    finally:
        system.store.close()


def cmd_person_card(args):
    data_dir = Path(args.data_dir) if args.data_dir else DEFAULT_DATA_DIR
    if not data_dir.exists():
        print("Data dir missing. Run init first.")
        return 1
    system = _get_system(data_dir)
    try:
        view = system.read_core_view("person_card", "cli_session_001")
        payload = view["payload"]
        print("=== Person Card ===")
        print("Data revision:", view.get("data_revision", "N/A"))
        print("View freshness:", view.get("freshness_status", "N/A"))
        print("Contact state:", payload.get("contact_state", "N/A"))
        if view.get("source") == "canonical_fallback":
            print("(View from canonical fallback)")
        return 0
    finally:
        system.store.close()


def cmd_timeline(args):
    data_dir = Path(args.data_dir) if args.data_dir else DEFAULT_DATA_DIR
    if not data_dir.exists():
        print("Data dir missing. Run init first.")
        return 1
    system = _get_system(data_dir)
    try:
        view = system.read_core_view("relationship_timeline", "cli_session_001")
        payload = view["payload"]
        print("=== Relationship Timeline ===")
        print("Data revision:", view.get("data_revision", "N/A"))
        print("View freshness:", view.get("freshness_status", "N/A"))
        print("Current contact state:", payload.get("current_contact_state", "N/A"))
        history = payload.get("history", [])
        if history:
            print("\nHistory:")
            for item in history:
                start_val = item.get("valid_time", {}).get("start", {}).get("value", "N/A")
                print("  [" + start_val + "] -> " + item.get("value", "N/A"))
        else:
            print("No history entries.")
        if view.get("source") == "canonical_fallback":
            print("(View from canonical fallback)")
        return 0
    finally:
        system.store.close()


def cmd_export(args):
    data_dir = Path(args.data_dir) if args.data_dir else DEFAULT_DATA_DIR
    if not data_dir.exists():
        print("Data dir missing. Run init first.")
        return 1
    system, store = _get_store(data_dir)
    try:
        snapshot = store.seed_snapshot()
        export_data = {
            "export_version": "noetide.export.v1",
            "exported_at": "2031-10-15T02:00:00Z",
            "data_revision": snapshot["data_revision"],
            "objects": list(snapshot["objects"].values()),
            "projections": snapshot["projections"],
        }
        output_path = Path(args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        print("Exported to:", output_path)
        print("Objects:", len(export_data["objects"]))
        print("Projections:", len(export_data["projections"]))
        return 0
    finally:
        store.close()


def _digest_text(text: str) -> str:
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main():
    parser = argparse.ArgumentParser(prog="noetide", description="Noetide CLI")
    parser.add_argument("--data-dir", help="Data directory")
    subparsers = parser.add_subparsers(dest="command")

    init_p = subparsers.add_parser("init", help="Initialize database")
    init_p.set_defaults(func=cmd_init)

    status_p = subparsers.add_parser("status", help="Show status")
    status_p.set_defaults(func=cmd_status)

    intake_p = subparsers.add_parser("intake", help="Intake text source")
    intake_p.add_argument("--text", help="Text content to intake")
    intake_p.set_defaults(func=cmd_intake)

    propose_p = subparsers.add_parser("propose", help="Propose ChangeSet from source")
    propose_p.add_argument("source_id", help="Source ID")
    propose_p.set_defaults(func=cmd_propose)

    changesets_p = subparsers.add_parser("changesets", help="List ChangeSets")
    changesets_p.set_defaults(func=cmd_changesets)

    approve_p = subparsers.add_parser("approve", help="Approve a ChangeSet")
    approve_p.add_argument("--id", required=True, help="ChangeSet ID")
    approve_p.add_argument("--actor", default="person_alpha", help="Actor ID")
    approve_p.set_defaults(func=cmd_approve)

    publish_p = subparsers.add_parser("publish", help="Publish a ChangeSet")
    publish_p.add_argument("--id", required=True, help="ChangeSet ID")
    publish_p.add_argument("--idempotency-key", default="cli_publish_001", help="Idempotency key")
    publish_p.set_defaults(func=cmd_publish)

    revert_p = subparsers.add_parser("revert", help="Revert a published ChangeSet")
    revert_p.add_argument("--id", required=True, help="ChangeSet ID")
    revert_p.add_argument("--idempotency-key", default="cli_revert_001", help="Idempotency key")
    revert_p.set_defaults(func=cmd_revert)

    person_card_p = subparsers.add_parser("person-card", help="Show person card")
    person_card_p.set_defaults(func=cmd_person_card)

    timeline_p = subparsers.add_parser("timeline", help="Show relationship timeline")
    timeline_p.set_defaults(func=cmd_timeline)

    export_p = subparsers.add_parser("export", help="Export data")
    export_p.add_argument("--output", required=True, help="Output file path")
    export_p.set_defaults(func=cmd_export)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
