"""SQLite persistence primitives limited to TASK-001."""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterator, Mapping


JsonObject = dict[str, Any]


class SeedConflictError(RuntimeError):
    """Raised when a fixture seed would overwrite a different database state."""


class SeedValidationError(ValueError):
    """Raised when the approved rev_010 fixture cannot be stored safely."""


class SemanticStore:
    """Owns SQLite setup, explicit transactions, and the rev_010 fixture seed."""

    def __init__(self, database_path: str | Path) -> None:
        path = Path(database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(path, isolation_level=None)
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.execute("PRAGMA journal_mode = DELETE")
        self._connection.execute("PRAGMA synchronous = FULL")
        self._connection.executescript(
            Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
        )

    def close(self) -> None:
        self._connection.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        self._connection.execute("BEGIN IMMEDIATE")
        try:
            yield self._connection
        except BaseException:
            self._connection.execute("ROLLBACK")
            raise
        else:
            self._connection.execute("COMMIT")

    def pragma_values(self) -> JsonObject:
        return {
            "foreign_keys": self._connection.execute("PRAGMA foreign_keys").fetchone()[0],
            "journal_mode": self._connection.execute("PRAGMA journal_mode").fetchone()[0],
            "synchronous": self._connection.execute("PRAGMA synchronous").fetchone()[0],
        }

    def seed_rev_010(self, fixture: Mapping[str, Any]) -> bool:
        """Persist the immutable initial fixture once, returning whether it was inserted."""
        self._validate_fixture(fixture)
        fixture_digest = _canonical_digest(fixture)
        marker_key = f"fixture_seed:{fixture['fixture_id']}"
        existing_marker = self._connection.execute(
            "SELECT metadata_value FROM schema_metadata WHERE metadata_key = ?",
            (marker_key,),
        ).fetchone()
        if existing_marker is not None:
            if existing_marker[0] != fixture_digest:
                raise SeedConflictError("fixture seed marker does not match the supplied fixture")
            return False

        occupied = self._connection.execute(
            "SELECT EXISTS(SELECT 1 FROM canonical_revisions) "
            "OR EXISTS(SELECT 1 FROM source_records)"
        ).fetchone()[0]
        if occupied:
            raise SeedConflictError("database is not empty and has no matching fixture seed marker")

        initial_state = fixture["initial_state"]
        canonical_objects = initial_state["canonical_objects"]
        sources_by_id = {item["source_id"]: item for item in fixture["source_records"]}
        referenced_source_ids = _referenced_source_ids(canonical_objects)

        with self.transaction() as connection:
            for source_id in sorted(referenced_source_ids):
                source = sources_by_id[source_id]
                connection.execute(
                    "INSERT INTO source_records "
                    "(source_id, append_receipt_id, source_kind, content_hash, payload_json) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (
                        source_id,
                        source["append_receipt_id"],
                        source["source_kind"],
                        source["content_hash"],
                        _canonical_json(source),
                    ),
                )
                receipt = {
                    "receipt_id": source["append_receipt_id"],
                    "source_id": source_id,
                    "status": "stored",
                    "actor": "fixture_seed",
                }
                connection.execute(
                    "INSERT INTO append_receipts (receipt_id, source_id, status, payload_json) "
                    "VALUES (?, ?, ?, ?)",
                    (receipt["receipt_id"], source_id, receipt["status"], _canonical_json(receipt)),
                )

            connection.execute(
                "INSERT INTO canonical_revisions (revision_id, recorded_at, revision_kind) "
                "VALUES (?, ?, 'seed')",
                (initial_state["data_revision"], fixture["determinism"]["clock"]),
            )
            for item in canonical_objects:
                object_id = _object_id(item)
                connection.execute(
                    "INSERT INTO canonical_objects "
                    "(object_id, object_type, object_revision, payload_json) VALUES (?, ?, ?, ?)",
                    (object_id, item["object_type"], item["object_revision"], _canonical_json(item)),
                )
                for evidence_ref in item.get("evidence_refs", []):
                    connection.execute(
                        "INSERT INTO canonical_evidence_refs "
                        "(object_id, source_id, locator_json, stance, claim_ref) VALUES (?, ?, ?, ?, ?)",
                        (
                            object_id,
                            evidence_ref["source_id"],
                            _canonical_json(evidence_ref["locator"]),
                            evidence_ref["stance"],
                            evidence_ref["claim_ref"],
                        ),
                    )

            for view_name, payload in initial_state["core_views"].items():
                connection.execute(
                    "INSERT INTO projection_rows "
                    "(view_name, data_revision, view_revision, freshness_status, payload_json) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (
                        view_name,
                        payload["data_revision"],
                        payload["view_revision"],
                        payload["freshness_status"],
                        _canonical_json(payload),
                    ),
                )
            connection.execute(
                "INSERT INTO schema_metadata (metadata_key, metadata_value) VALUES (?, ?)",
                (marker_key, fixture_digest),
            )
        return True

    def seed_snapshot(self) -> JsonObject:
        revision = self._connection.execute(
            "SELECT revision_id FROM canonical_revisions ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
        objects = {
            row[0]: json.loads(row[1])
            for row in self._connection.execute(
                "SELECT object_id, payload_json FROM canonical_objects ORDER BY object_id"
            )
        }
        projections = {
            row[0]: json.loads(row[1])
            for row in self._connection.execute(
                "SELECT view_name, payload_json FROM projection_rows ORDER BY view_name"
            )
        }
        return {
            "data_revision": revision[0] if revision else None,
            "objects": objects,
            "projections": projections,
        }

    def current_revision(self) -> str:
        value = self.seed_snapshot()["data_revision"]
        if not isinstance(value, str):
            raise RuntimeError("Canonical revision is absent")
        return value

    def canonical_object(self, object_id: str) -> JsonObject:
        row = self._connection.execute(
            "SELECT payload_json FROM canonical_objects WHERE object_id = ?", (object_id,)
        ).fetchone()
        if row is None:
            raise KeyError(object_id)
        return json.loads(row[0])

    def replace_canonical_object(self, object_id: str, payload: Mapping[str, Any]) -> None:
        cursor = self._connection.execute(
            "UPDATE canonical_objects SET object_revision = ?, payload_json = ? WHERE object_id = ?",
            (payload["object_revision"], _canonical_json(payload), object_id),
        )
        if cursor.rowcount != 1:
            raise KeyError(object_id)

    def add_canonical_object(self, object_id: str, payload: Mapping[str, Any]) -> None:
        self._connection.execute(
            "INSERT INTO canonical_objects (object_id, object_type, object_revision, payload_json) "
            "VALUES (?, ?, ?, ?)",
            (object_id, payload["object_type"], payload["object_revision"], _canonical_json(payload)),
        )

    def delete_canonical_object(self, object_id: str) -> None:
        self._connection.execute("DELETE FROM canonical_evidence_refs WHERE object_id = ?", (object_id,))
        cursor = self._connection.execute("DELETE FROM canonical_objects WHERE object_id = ?", (object_id,))
        if cursor.rowcount != 1:
            raise KeyError(object_id)

    def replace_evidence_refs(self, object_id: str, evidence_refs: list[Mapping[str, Any]]) -> None:
        self._connection.execute("DELETE FROM canonical_evidence_refs WHERE object_id = ?", (object_id,))
        for evidence_ref in evidence_refs:
            self._connection.execute(
                "INSERT INTO canonical_evidence_refs "
                "(object_id, source_id, locator_json, stance, claim_ref) VALUES (?, ?, ?, ?, ?)",
                (
                    object_id,
                    evidence_ref["source_id"],
                    _canonical_json(evidence_ref["locator"]),
                    evidence_ref["stance"],
                    evidence_ref["claim_ref"],
                ),
            )

    def add_revision(self, revision_id: str, recorded_at: str, revision_kind: str = "changeset") -> None:
        self._connection.execute(
            "INSERT INTO canonical_revisions (revision_id, recorded_at, revision_kind) VALUES (?, ?, ?)",
            (revision_id, recorded_at, revision_kind),
        )

    def projection_record(self, view_name: str) -> JsonObject:
        row = self._connection.execute(
            "SELECT data_revision, view_revision, freshness_status, payload_json "
            "FROM projection_rows WHERE view_name = ?",
            (view_name,),
        ).fetchone()
        if row is None:
            raise KeyError(view_name)
        return {
            "data_revision": row[0],
            "view_revision": row[1],
            "freshness_status": row[2],
            "payload": json.loads(row[3]),
        }

    def replace_projection(
        self,
        view_name: str,
        data_revision: str,
        view_revision: str,
        freshness_status: str,
        payload: Mapping[str, Any],
    ) -> None:
        cursor = self._connection.execute(
            "UPDATE projection_rows SET data_revision = ?, view_revision = ?, freshness_status = ?, "
            "payload_json = ? WHERE view_name = ?",
            (data_revision, view_revision, freshness_status, _canonical_json(payload), view_name),
        )
        if cursor.rowcount != 1:
            raise KeyError(view_name)

    def ledger_records_for(self, record_type: str, changeset_id: str) -> list[JsonObject]:
        rows = self._connection.execute(
            "SELECT payload_json FROM ledger_records WHERE record_type = ? ORDER BY rowid", (record_type,)
        )
        return [payload for (raw,) in rows if (payload := json.loads(raw)).get("changeset_id") == changeset_id]

    def seeded_source(self, source_id: str) -> JsonObject | None:
        row = self._connection.execute(
            "SELECT payload_json FROM source_records WHERE source_id = ?", (source_id,)
        ).fetchone()
        return json.loads(row[0]) if row else None

    def append_source(self, source: Mapping[str, Any], receipt: Mapping[str, Any]) -> None:
        """Store one Source and its receipt without touching Canonical Context."""
        with self.transaction() as connection:
            connection.execute(
                "INSERT INTO source_records "
                "(source_id, append_receipt_id, source_kind, content_hash, payload_json) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    source["source_id"],
                    source["append_receipt_id"],
                    source["source_kind"],
                    source["content_hash"],
                    _canonical_json(source),
                ),
            )
            connection.execute(
                "INSERT INTO append_receipts (receipt_id, source_id, status, payload_json) "
                "VALUES (?, ?, ?, ?)",
                (
                    receipt["receipt_id"],
                    source["source_id"],
                    receipt["status"],
                    _canonical_json(receipt),
                ),
            )

    def append_receipt(self, receipt_id: str) -> JsonObject | None:
        row = self._connection.execute(
            "SELECT payload_json FROM append_receipts WHERE receipt_id = ?", (receipt_id,)
        ).fetchone()
        return json.loads(row[0]) if row else None

    def ledger_record(self, record_id: str) -> JsonObject | None:
        row = self._connection.execute(
            "SELECT payload_json FROM ledger_records WHERE record_id = ?", (record_id,)
        ).fetchone()
        return json.loads(row[0]) if row else None

    def put_ledger_record(
        self, record_id: str, record_type: str, payload: Mapping[str, Any], revision_id: str | None = None
    ) -> None:
        self._connection.execute(
            "INSERT INTO ledger_records (record_id, revision_id, record_type, payload_json) "
            "VALUES (?, ?, ?, ?)",
            (record_id, revision_id, record_type, _canonical_json(payload)),
        )

    def replace_ledger_record(
        self, record_id: str, payload: Mapping[str, Any], revision_id: str | None = None
    ) -> None:
        cursor = self._connection.execute(
            "UPDATE ledger_records SET revision_id = ?, payload_json = ? WHERE record_id = ?",
            (revision_id, _canonical_json(payload), record_id),
        )
        if cursor.rowcount != 1:
            raise KeyError(record_id)

    def schema_objects(self) -> set[str]:
        return {
            row[0]
            for row in self._connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

    def _validate_fixture(self, fixture: Mapping[str, Any]) -> None:
        if fixture.get("fixture_id") != "micro_relationship_v1" or fixture.get("synthetic") is not True:
            raise SeedValidationError("TASK-001 only accepts the approved synthetic Micro fixture")
        initial_state = fixture.get("initial_state")
        if not isinstance(initial_state, Mapping) or initial_state.get("data_revision") != "rev_010":
            raise SeedValidationError("fixture must provide the approved rev_010 initial state")
        objects = initial_state.get("canonical_objects")
        source_records = fixture.get("source_records")
        core_views = initial_state.get("core_views")
        if not isinstance(objects, list) or not isinstance(source_records, list) or not isinstance(core_views, Mapping):
            raise SeedValidationError("fixture seed sections are incomplete")
        source_ids = {item.get("source_id") for item in source_records}
        if None in source_ids:
            raise SeedValidationError("fixture source record lacks source_id")
        for item in objects:
            _object_id(item)
            for evidence_ref in item.get("evidence_refs", []):
                if evidence_ref.get("source_id") not in source_ids:
                    raise SeedValidationError("canonical evidence refers to an absent fixture source")
        if set(core_views) != {"person_card", "relationship_timeline"}:
            raise SeedValidationError("fixture must seed exactly the two approved Micro projections")


    # A1 additive: Answer Safety fixture seed (AS-TASK-001)

    def seed_answer_safety_fixture(self, fixture):
        self._validate_answer_safety_fixture(fixture)
        fixture_digest = _canonical_digest(fixture)
        marker_key = 'fixture_seed:' + fixture['fixture_id']
        existing_marker = self._connection.execute(
            'SELECT metadata_value FROM schema_metadata WHERE metadata_key = ?',
            (marker_key,),
        ).fetchone()
        if existing_marker is not None:
            if existing_marker[0] != fixture_digest:
                raise SeedConflictError('fixture seed marker does not match the supplied fixture')
            return False

        with self.transaction() as connection:
            for case in fixture['cases']:
                initial = case['initial_state']
                data_revision = initial['data_revision']
                clock = fixture['determinism']['clock']

                connection.execute(
                    "INSERT OR IGNORE INTO canonical_revisions (revision_id, recorded_at, revision_kind) VALUES (?, ?, 'seed')",
                    (data_revision, clock),
                )

                for source in initial.get('source_records', []):
                    connection.execute(
                        'INSERT OR IGNORE INTO source_records (source_id, append_receipt_id, source_kind, content_hash, payload_json) VALUES (?, ?, ?, ?, ?)',
                        (
                            source['source_id'],
                            source.get('append_receipt_id', source['source_id'] + ':receipt'),
                            source['source_kind'],
                            source.get('content_hash', _canonical_digest(source)),
                            _canonical_json(source),
                        ),
                    )
                    receipt = {
                        'receipt_id': source.get('append_receipt_id', source['source_id'] + ':receipt'),
                        'source_id': source['source_id'],
                        'status': 'stored',
                        'actor': 'fixture_seed',
                    }
                    connection.execute(
                        'INSERT OR IGNORE INTO append_receipts (receipt_id, source_id, status, payload_json) VALUES (?, ?, ?, ?)',
                        (receipt['receipt_id'], source['source_id'], receipt['status'], _canonical_json(receipt)),
                    )

                for item in initial.get('canonical_objects', []):
                    object_id = _object_id(item)
                    connection.execute(
                        'INSERT OR IGNORE INTO canonical_objects (object_id, object_type, object_revision, payload_json) VALUES (?, ?, ?, ?)',
                        (object_id, item['object_type'], item.get('object_revision', data_revision), _canonical_json(item)),
                    )
                    for evidence_ref in item.get('evidence_refs', []):
                        connection.execute(
                            'INSERT OR IGNORE INTO canonical_evidence_refs (object_id, source_id, locator_json, stance, claim_ref) VALUES (?, ?, ?, ?, ?)',
                            (
                                object_id,
                                evidence_ref['source_id'],
                                _canonical_json(evidence_ref.get('locator', {})),
                                evidence_ref.get('stance', 'supports'),
                                evidence_ref.get('claim_ref', ''),
                            ),
                        )

                for cw in initial.get('coverage_windows', []):
                    connection.execute(
                        'INSERT OR IGNORE INTO coverage_windows (coverage_window_id, scope_ref, coverage_start, coverage_end, continuity, gaps_json, export_completeness) VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (
                            cw['coverage_window_id'],
                            cw['scope_ref'],
                            cw['coverage_start'],
                            cw['coverage_end'],
                            cw['continuity'],
                            _canonical_json(cw.get('gaps', [])),
                            cw['export_completeness'],
                        ),
                    )

                for lr in initial.get('ledger_records', []):
                    connection.execute(
                        'INSERT OR IGNORE INTO ledger_records (record_id, revision_id, record_type, payload_json) VALUES (?, ?, ?, ?)',
                        (lr['record_id'], lr.get('revision_id'), lr['record_type'], _canonical_json(lr)),
                    )

                for pr in initial.get('projection_rows', []):
                    connection.execute(
                        'INSERT OR IGNORE INTO projection_rows (view_name, data_revision, view_revision, freshness_status, payload_json) VALUES (?, ?, ?, ?, ?)',
                        (
                            pr['view_name'],
                            pr.get('data_revision', data_revision),
                            pr.get('view_revision', data_revision),
                            pr.get('freshness_status', 'fresh'),
                            _canonical_json(pr),
                        ),
                    )

            connection.execute(
                'INSERT INTO schema_metadata (metadata_key, metadata_value) VALUES (?, ?)',
                (marker_key, fixture_digest),
            )

        return True

    def a1_seed_snapshot(self, scenario_id=None):
        conn = self._connection
        source_rows = conn.execute('SELECT payload_json FROM source_records').fetchall()
        canonical_rows = conn.execute('SELECT payload_json FROM canonical_objects').fetchall()
        ledger_rows = conn.execute('SELECT payload_json FROM ledger_records').fetchall()
        projection_rows = conn.execute('SELECT payload_json FROM projection_rows').fetchall()
        coverage_rows = conn.execute('SELECT coverage_window_id, scope_ref, coverage_start, coverage_end, continuity, gaps_json, export_completeness FROM coverage_windows').fetchall()

        def _rows_digest(rows):
            import hashlib, json
            payloads = [json.loads(r[0]) for r in rows]
            return hashlib.sha256(json.dumps(payloads, ensure_ascii=False, sort_keys=True, separators=(chr(44), chr(58))).encode('utf-8')).hexdigest()

        result = {
            'source': {'count': len(source_rows), 'digest': _rows_digest(source_rows)},
            'canonical': {'count': len(canonical_rows), 'digest': _rows_digest(canonical_rows)},
            'ledger': {'count': len(ledger_rows), 'digest': _rows_digest(ledger_rows)},
            'projection': {'count': len(projection_rows), 'digest': _rows_digest(projection_rows)},
            'coverage': {'count': len(coverage_rows), 'digest': hashlib.sha256(json.dumps(coverage_rows, ensure_ascii=False, sort_keys=True, separators=(chr(44), chr(58))).encode('utf-8')).hexdigest()},
        }

        if scenario_id:
            result['scenario_id'] = scenario_id

        return result

    def coverage_window(self, window_id):
        row = self._connection.execute(
            'SELECT coverage_window_id, scope_ref, coverage_start, coverage_end, continuity, gaps_json, export_completeness FROM coverage_windows WHERE coverage_window_id = ?',
            (window_id,),
        ).fetchone()
        if row is None:
            return None
        import json
        return {
            'coverage_window_id': row[0],
            'scope_ref': row[1],
            'coverage_start': row[2],
            'coverage_end': row[3],
            'continuity': row[4],
            'gaps': json.loads(row[5]),
            'export_completeness': row[6],
        }

    def _validate_answer_safety_fixture(self, fixture):
        if fixture.get('fixture_id') != 'answer_safety_v1' or fixture.get('synthetic') is not True:
            raise SeedValidationError('TASK-001 only accepts the approved synthetic A1 fixture')
        if not isinstance(fixture.get('cases'), list):
            raise SeedValidationError('fixture must contain cases list')
        for case in fixture['cases']:
            initial = case.get('initial_state')
            if not isinstance(initial, dict):
                raise SeedValidationError('case initial_state must be a mapping')
            for cw in initial.get('coverage_windows', []):
                required = ('coverage_window_id', 'scope_ref', 'coverage_start', 'coverage_end', 'continuity', 'export_completeness')
                for field in required:
                    if field not in cw:
                        raise SeedValidationError('coverage_window missing required field: ' + field)

def _object_id(item: Mapping[str, Any]) -> str:
    for key in (
        "entity_id",
        "relationship_id",
        "state_id",
        "assertion_id",
        "hypothesis_id",
        "changeset_id",
        "source_id",
    ):
        value = item.get(key)
        if isinstance(value, str) and value:
            return value
    raise SeedValidationError("canonical object has no supported stable identifier")


def _referenced_source_ids(objects: list[Mapping[str, Any]]) -> set[str]:
    return {
        evidence_ref["source_id"]
        for item in objects
        for evidence_ref in item.get("evidence_refs", [])
    }


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _canonical_digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()
