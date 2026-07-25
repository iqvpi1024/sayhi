"""A6 hardening testing adapter: 21 sequential scenarios on one reference profile.

This adapter only dispatches scenario cases to already-verified journey helpers
(a6_journey), the D0 launcher (start.py), and the alpha explainability probes
(alpha_explainability / portability). It adds no new business, recovery,
permission, or candidate-generation semantics. Sandbox scenarios never touch
the shared reference-profile state.
"""

from __future__ import annotations

import atexit
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping

from . import a6_journey as journey
from . import alpha_explainability as explain
from .candidate import ContactCandidateBuilder
from .changesets import ChangeSetService
from .intake import IntakeService
from .portability import ContextPackExporter, ContextPackVerifier
from .runtime import demo_fixture, open_runtime
from .store import SemanticStore
from .views import CoreViewReader

JsonObject = dict[str, Any]

ROOT = Path(__file__).resolve().parents[2]
START_SCRIPT = ROOT / "start.py"
_CHANGESET_ID = "changeset_micro_001"
_APPROVE_ACTOR = "person_alpha"

_FAILURE_REQUIREMENTS = {
    "A6-014": "corrupt_db_file",
    "A6-015": "unwritable_data_dir",
    "A6-016": "mid_publish",
    "A6-017": "l2_projection",
}


def create_system(fixture: Mapping[str, Any]) -> "A6System":
    return A6System(fixture)


class A6System:
    """One system instance per reference profile execution (contract protocol)."""

    def __init__(self, fixture: Mapping[str, Any]) -> None:
        if fixture.get("synthetic") is not True or fixture.get("external_data_used") is not False:
            raise ValueError("A6 adapter only accepts explicitly synthetic fixtures")
        if fixture.get("reference_profile", {}).get("profile_id") != journey.PROFILE_ID:
            raise ValueError("unexpected reference profile for the A6 adapter")
        self._fixture = fixture
        self._store = journey.new_profile_store()
        self._journey_start = journey.layer_snapshot(self._store)
        self._baseline_revision = self._store.current_revision()
        self._intake_revision: str | None = None
        self._proposal: JsonObject | None = None
        self._pre_publish_card_value: Any = None
        self._injected: set[str] = set()
        self._slo = journey.SloCollector()
        self._temp = Path(tempfile.mkdtemp(prefix="noetide_a6_"))
        atexit.register(shutil.rmtree, self._temp, True)

    # -- protocol ---------------------------------------------------------

    def layer_snapshot(self) -> JsonObject:
        return journey.layer_snapshot(self._store)

    def inject_failure(self, failure_point: str) -> None:
        self._injected.add(failure_point)

    def run_scenario(self, case: Mapping[str, Any]) -> JsonObject:
        scenario_id = str(case.get("scenario_id"))
        handler = getattr(self, f"_scenario_{scenario_id.lower().replace('-', '_')}", None)
        if handler is None:
            raise KeyError(f"unknown A6 scenario: {scenario_id}")
        required = _FAILURE_REQUIREMENTS.get(scenario_id)
        if required is not None and required not in self._injected:
            raise RuntimeError(f"{scenario_id} requires injected failure point {required}")
        return handler()

    # -- shared journey scenarios -----------------------------------------

    def _scenario_a6_001(self) -> JsonObject:
        result = journey.record_source(self._store)
        self._intake_revision = self._store.current_revision()
        return result

    def _scenario_a6_002(self) -> JsonObject:
        self._proposal = journey.propose_candidate(self._store)
        return journey.candidate_visibility(self._store, self._proposal)

    def _scenario_a6_003(self) -> JsonObject:
        if self._intake_revision is None:
            raise RuntimeError("A6-003 requires A6-001 to have recorded a source first")
        return journey.write_path_audit(self._store, self._baseline_revision, self._intake_revision)

    def _scenario_a6_004(self) -> JsonObject:
        if self._proposal is None:
            raise RuntimeError("A6-004 requires the A6-002 proposal")
        self._pre_publish_card_value = self._store.canonical_object("state_contact_001")["value"]
        return journey.preview_publish_consistency(self._store, self._proposal)

    def _scenario_a6_005(self) -> JsonObject:
        return journey.read_core_views(self._store)

    def _scenario_a6_006(self) -> JsonObject:
        return journey.revert_and_audit(self._store, self._pre_publish_card_value)

    def _scenario_a6_007(self) -> JsonObject:
        sandbox = journey.new_profile_store()
        try:
            return journey.run_answer_battery(sandbox)
        finally:
            sandbox.close()

    def _scenario_a6_008(self) -> JsonObject:
        return journey.bitemporal_probe(self._store)

    def _scenario_a6_009(self) -> JsonObject:
        sandbox = journey.new_profile_store()
        try:
            return journey.conflict_probe(sandbox)
        finally:
            sandbox.close()

    def _scenario_a6_010(self) -> JsonObject:
        return journey.merge_split_cycle(self._store)

    def _scenario_a6_011(self) -> JsonObject:
        return journey.restricted_query_probe()

    def _scenario_a6_012(self) -> JsonObject:
        return journey.cross_cutting_check(
            self._journey_start, journey.layer_snapshot(self._store), self._store
        )

    # -- sandbox launcher scenarios ----------------------------------------

    def _run_start(self, data_root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(START_SCRIPT), "--data-root", str(data_root)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )

    def _scenario_a6_013(self) -> JsonObject:
        declared = self._temp / "a6_013_clean_root"
        proc = self._run_start(declared)
        return {
            "exit_code": proc.returncode,
            "data_dir_created_at_declared_path": (declared / "noetide.sqlite3").is_file(),
            "preflight_smoke_passed": "Preflight smoke" in proc.stdout,
        }

    def _scenario_a6_014(self) -> JsonObject:
        root = self._temp / "a6_014_corrupt_root"
        root.mkdir(parents=True)
        db_path = root / "noetide.sqlite3"
        marker = b"SYNTHETIC_CORRUPT_MARKER_A6_014"
        db_path.write_bytes(marker * 4)
        before = db_path.read_bytes()
        proc = self._run_start(root)
        after = db_path.read_bytes()
        output = proc.stdout + proc.stderr
        return {
            "exit_code_nonzero": proc.returncode != 0,
            "error_non_leaking": marker.decode() not in output,
            "original_file_untouched": before == after,
            "silent_repair_attempted": not (
                before == after and "no repair was attempted" in output.lower()
            ),
        }

    def _scenario_a6_015(self) -> JsonObject:
        base = self._temp / "a6_015_unwritable_base"
        base.mkdir(parents=True)
        blocker = base / "blocked"
        blocker.write_text("synthetic blocker file", encoding="utf-8")
        declared = blocker / "sub"
        before = sorted(str(p.relative_to(base)) for p in base.rglob("*"))
        proc = self._run_start(declared)
        after = sorted(str(p.relative_to(base)) for p in base.rglob("*"))
        return {
            "exit_code_nonzero": proc.returncode != 0,
            "clear_error": "not writable" in proc.stderr.lower() and proc.returncode == 3,
            "wrote_outside_declared_root": before != after,
        }

    # -- failure injection scenarios (isolated probe stores) ---------------

    def _scenario_a6_016(self) -> JsonObject:
        sandbox = journey.new_profile_store()
        try:
            return journey.publish_with_injected_failure(sandbox)
        finally:
            sandbox.close()

    def _scenario_a6_017(self) -> JsonObject:
        sandbox = journey.new_profile_store()
        try:
            return journey.read_view_with_l2_failure(sandbox)
        finally:
            sandbox.close()

    # -- alpha explainability scenarios -------------------------------------

    def _scenario_a6_018(self) -> JsonObject:
        declared = self._temp / "a6_018_profile_data"
        info = explain.paths_descriptor(declared, journey.PROFILE_ID)
        return {
            "data_path_discoverable": info["paths_discoverable"],
            "synthetic_real_paths_differ": info["declared_data_root"] != info["default_real_data_root"],
            "separation_verifiable": info["synthetic_real_separated"],
        }

    def _scenario_a6_019(self) -> JsonObject:
        pack = self._temp / "a6_019_pack"
        ContextPackExporter(explain.EXPORTED_AT).export(self._store, pack)
        verifier = ContextPackVerifier()
        first = verifier.verify(pack)
        second = verifier.verify(pack)
        manifest_check = explain.verify_backup_manifest(pack)
        return {
            "backup_artifact_exists": (pack / "manifest.json").is_file()
            and (pack / "checksums.sha256").is_file(),
            "checksum_manifest_verifiable": manifest_check["artifacts_present"]
            and manifest_check["checksums_all_match"],
            "export_round_trip": first.get("status") == "validated" and first == second,
        }

    def _scenario_a6_020(self) -> JsonObject:
        data_dir = self._temp / "a6_020_data"
        runtime = open_runtime(data_dir)
        runtime.close()
        info = explain.uninstall_info(data_dir)
        default_preserved = (
            not info["default_uninstall_deletes_data"]
            and (data_dir / "noetide.sqlite3").exists()
        )
        without_confirm = explain.confirm_and_delete_data(data_dir, confirm=False)
        without_backup = explain.confirm_and_delete_data(data_dir, confirm=True)
        backup_pack = self._temp / "a6_020_backup"
        explain.create_reference_backup(data_dir, backup_pack)
        deleted = explain.confirm_and_delete_data(data_dir, confirm=True, backup_path=backup_pack)
        return {
            "default_uninstall_preserves_data": default_preserved,
            "delete_requires_independent_confirmation": without_confirm["reason"] == "confirmation_required"
            and without_backup["reason"] == "backup_required_before_deletion"
            and deleted["deleted"],
            "backup_export_copies_mentioned": without_backup["reason"] == "backup_required_before_deletion",
        }

    # -- SLO observations ----------------------------------------------------

    def _scenario_a6_021(self) -> JsonObject:
        fixture = demo_fixture()
        clock = journey._clock()
        self._slo.measure(
            "canonical_query_p95", lambda: self._store.canonical_object("rel_alpha_beta")
        )

        def publish_cycle() -> None:
            sandbox = journey.new_profile_store()
            try:
                IntakeService(sandbox, fixture).append(fixture["intake_request"])
                builder = ContactCandidateBuilder(sandbox, fixture, clock)
                builder.propose("src_micro_001")
                builder.approve(_CHANGESET_ID, _APPROVE_ACTOR)
                ChangeSetService(sandbox, fixture, clock).publish(
                    _CHANGESET_ID, "a6_slo_publish_001", set()
                )
            finally:
                sandbox.close()

        self._slo.measure("changeset_publish_p95", publish_cycle)
        self._slo.measure(
            "core_view_read_after_publish",
            lambda: CoreViewReader(self._store, fixture).read("person_card", "a6_slo_session"),
        )

        def stale_visibility() -> JsonObject:
            sandbox = journey.new_profile_store()
            try:
                return journey.read_view_with_l2_failure(sandbox)
            finally:
                sandbox.close()

        self._slo.measure("l3_stale_visibility", stale_visibility)
        return journey.slo_report(self._slo)
