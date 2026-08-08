"""SQLite persistence primitives limited to TASK-001."""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sqlite3
import threading
from typing import Any, Iterator, Mapping


JsonObject = dict[str, Any]


class _LockedCursor:
    """Materialized cursor: rows are fetched while the store lock is held.

    A lazy sqlite3.Cursor lets another thread's statement interleave with
    iteration on the shared connection (2026-08-09 并行分析实测:懒迭代读到
    None 行 / 审计序号主键碰撞)。物化后读结果在锁内成形,迭代在锁外也安全。
    支持既有调用点用到的 fetchone/fetchall/迭代/rowcount/description。
    """

    def __init__(self, rows: list[Any], description: Any, rowcount: int) -> None:
        self._rows = rows
        self._pos = 0
        self.description = description
        self.rowcount = rowcount

    def fetchone(self) -> Any:
        if self._pos >= len(self._rows):
            return None
        row = self._rows[self._pos]
        self._pos += 1
        return row

    def fetchall(self) -> list[Any]:
        return list(self._rows)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._rows)


class _LockedConnection:
    """Serialize every statement on the store lock.

    The local Web runtime opens the store with check_same_thread=False and
    shares one connection across HTTP handler threads; routing all statements
    through the store-level RLock keeps a concurrent writer from interleaving
    statements into another thread's open transaction.
    """

    def __init__(self, connection: sqlite3.Connection, lock: threading.RLock) -> None:
        self._raw = connection
        self._lock = lock

    def execute(self, sql: str, parameters: Any = ()) -> _LockedCursor:
        with self._lock:
            cursor = self._raw.execute(sql, parameters)
            return _LockedCursor(cursor.fetchall(), cursor.description, cursor.rowcount)

    def executescript(self, script: str) -> _LockedCursor:
        with self._lock:
            cursor = self._raw.executescript(script)
            return _LockedCursor(cursor.fetchall(), cursor.description, cursor.rowcount)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._raw, name)


class SeedConflictError(RuntimeError):
    """Raised when a fixture seed would overwrite a different database state."""


class SeedValidationError(ValueError):
    """Raised when the approved rev_010 fixture cannot be stored safely."""


class SemanticStore:
    """Owns SQLite setup, explicit transactions, and the rev_010 fixture seed."""

    def __init__(self, database_path: str | Path, *, check_same_thread: bool = True) -> None:
        path = Path(database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._transaction_depth = 0
        self._connection = _LockedConnection(
            sqlite3.connect(path, isolation_level=None, check_same_thread=check_same_thread),
            self._lock,
        )
        try:
            self._connection.execute("PRAGMA foreign_keys = ON")
            self._connection.execute("PRAGMA journal_mode = DELETE")
            self._connection.execute("PRAGMA synchronous = FULL")
            self._connection.executescript(
                Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
            )
        except BaseException:
            self._connection.close()
            raise

    def close(self) -> None:
        self._connection.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """Run statements as one atomic unit; nested calls join via SAVEPOINT.

        The store lock is held for the whole transaction body so no other
        thread can write into the open transaction. A nested transaction()
        reuses the outer transaction through a savepoint instead of failing
        with "cannot start a transaction within a transaction".
        """
        with self._lock:
            depth = self._transaction_depth
            savepoint = f"noetide_sp_{depth}" if depth > 0 else None
            if savepoint is None:
                self._connection.execute("BEGIN IMMEDIATE")
            else:
                self._connection.execute(f"SAVEPOINT {savepoint}")
            self._transaction_depth = depth + 1
            try:
                yield self._connection
            except BaseException:
                self._transaction_depth = depth
                if savepoint is None:
                    self._connection.execute("ROLLBACK")
                else:
                    self._connection.execute(f"ROLLBACK TO {savepoint}")
                    self._connection.execute(f"RELEASE {savepoint}")
                raise
            else:
                self._transaction_depth = depth
                if savepoint is None:
                    self._connection.execute("COMMIT")
                else:
                    self._connection.execute(f"RELEASE {savepoint}")

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

    def canonical_object_or_none(self, object_id: str) -> JsonObject | None:
        row = self._connection.execute(
            "SELECT payload_json FROM canonical_objects WHERE object_id = ?", (object_id,)
        ).fetchone()
        return json.loads(row[0]) if row else None

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

    def next_revision(self, prefix: str = "rev") -> str:
        """Allocate the next ``{prefix}_NNN`` revision id from the revisions table.

        Takes the global maximum numeric suffix across every known revision id,
        so non-numeric ids (``rev_c1_*``, ``rev_011_test``) are skipped instead
        of crashing the caller. Call inside ``transaction()`` for race-free
        allocation when several writers share one store.
        """
        marker = prefix + "_"
        numbers = [
            int(revision_id[len(marker):])
            for revision_id in self.revision_ids()
            if revision_id.startswith(marker) and revision_id[len(marker):].isdigit()
        ]
        return f"{marker}{max(numbers) + 1:03d}" if numbers else f"{marker}001"

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

    def put_episode_record(
        self,
        episode_id: str,
        object_revision: str,
        episode_kind: str,
        valid_start: str,
        valid_end: str,
        recorded_at: str,
        synthetic_profile_id: str,
        source_refs: list[Mapping[str, Any]],
    ) -> None:
        """Persist B2 metadata after its Canonical Episode was published."""
        canonical = self.canonical_object(episode_id)
        if canonical.get("object_type") != "episode":
            raise ValueError("episode record requires a Canonical Episode")
        if not source_refs:
            raise ValueError("episode record requires at least one direct Source reference")
        self._connection.execute(
            "INSERT INTO episodes (episode_id, object_revision, episode_kind, valid_start, valid_end, "
            "recorded_at, synthetic_profile_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (episode_id, object_revision, episode_kind, valid_start, valid_end, recorded_at, synthetic_profile_id),
        )
        for ref in source_refs:
            self._connection.execute(
                "INSERT INTO episode_source_refs (episode_id, source_id, locator_json) VALUES (?, ?, ?)",
                (episode_id, ref["source_id"], _canonical_json(ref["locator"])),
            )

    def episode_record(self, episode_id: str) -> JsonObject:
        row = self._connection.execute(
            "SELECT object_revision, episode_kind, valid_start, valid_end, recorded_at, synthetic_profile_id "
            "FROM episodes WHERE episode_id = ?",
            (episode_id,),
        ).fetchone()
        if row is None:
            raise KeyError(episode_id)
        refs = [
            {"source_id": source_id, "locator": json.loads(locator_json)}
            for source_id, locator_json in self._connection.execute(
                "SELECT source_id, locator_json FROM episode_source_refs WHERE episode_id = ? ORDER BY source_id, locator_json",
                (episode_id,),
            )
        ]
        return {
            "episode_id": episode_id,
            "object_revision": row[0],
            "episode_kind": row[1],
            "valid_start": row[2],
            "valid_end": row[3],
            "recorded_at": row[4],
            "synthetic_profile_id": row[5],
            "source_refs": refs,
        }

    def delete_episode_record(self, episode_id: str) -> None:
        self._connection.execute("DELETE FROM episode_source_refs WHERE episode_id = ?", (episode_id,))
        cursor = self._connection.execute("DELETE FROM episodes WHERE episode_id = ?", (episode_id,))
        if cursor.rowcount != 1:
            raise KeyError(episode_id)

    def episode_records(self) -> list[JsonObject]:
        return [self.episode_record(row[0]) for row in self._connection.execute(
            "SELECT episode_id FROM episodes ORDER BY episode_id"
        )]

    def put_summary_projection(
        self,
        projection_id: str,
        projection_kind: str,
        data_revision: str,
        view_revision: str,
        freshness_status: str,
        dependency_set: Mapping[str, Any],
        payload: Mapping[str, Any],
        generated_at: str,
        generator_policy_id: str,
    ) -> None:
        self._connection.execute(
            "INSERT INTO summary_projections (projection_id, projection_kind, data_revision, view_revision, "
            "freshness_status, dependency_json, payload_json, generated_at, generator_policy_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (projection_id, projection_kind, data_revision, view_revision, freshness_status,
             _canonical_json(dependency_set), _canonical_json(payload), generated_at, generator_policy_id),
        )

    def replace_summary_projection(
        self, projection_id: str, projection_kind: str, data_revision: str, view_revision: str,
        freshness_status: str, dependency_set: Mapping[str, Any], payload: Mapping[str, Any],
        generated_at: str, generator_policy_id: str,
    ) -> None:
        self._connection.execute(
            "INSERT INTO summary_projections (projection_id, projection_kind, data_revision, view_revision, "
            "freshness_status, dependency_json, payload_json, generated_at, generator_policy_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(projection_id) DO UPDATE SET "
            "projection_kind=excluded.projection_kind, data_revision=excluded.data_revision, "
            "view_revision=excluded.view_revision, freshness_status=excluded.freshness_status, "
            "dependency_json=excluded.dependency_json, payload_json=excluded.payload_json, "
            "generated_at=excluded.generated_at, generator_policy_id=excluded.generator_policy_id",
            (projection_id, projection_kind, data_revision, view_revision, freshness_status,
             _canonical_json(dependency_set), _canonical_json(payload), generated_at, generator_policy_id),
        )

    def summary_projections(self) -> list[JsonObject]:
        return [self.summary_projection(row[0]) for row in self._connection.execute(
            "SELECT projection_id FROM summary_projections ORDER BY projection_id"
        )]

    def mark_summary_projections_stale(self, data_revision: str) -> int:
        return self._connection.execute(
            "UPDATE summary_projections SET data_revision = ?, freshness_status = 'stale' "
            "WHERE view_revision != ? AND freshness_status = 'fresh'",
            (data_revision, data_revision),
        ).rowcount

    def put_derived_rebuild_receipt(
        self, receipt_id: str, projection_id: str, data_revision: str, status: str, payload: Mapping[str, Any]
    ) -> None:
        self._connection.execute(
            "INSERT INTO derived_rebuild_receipts (receipt_id, projection_id, data_revision, status, payload_json) "
            "VALUES (?, ?, ?, ?, ?)",
            (receipt_id, projection_id, data_revision, status, _canonical_json(payload)),
        )

    def derived_rebuild_receipts(self) -> list[JsonObject]:
        return [
            {"receipt_id": row[0], "projection_id": row[1], "data_revision": row[2], "status": row[3], "payload": json.loads(row[4])}
            for row in self._connection.execute(
                "SELECT receipt_id, projection_id, data_revision, status, payload_json "
                "FROM derived_rebuild_receipts ORDER BY receipt_id"
            )
        ]

    def summary_projection(self, projection_id: str) -> JsonObject:
        row = self._connection.execute(
            "SELECT projection_kind, data_revision, view_revision, freshness_status, dependency_json, payload_json, "
            "generated_at, generator_policy_id FROM summary_projections WHERE projection_id = ?",
            (projection_id,),
        ).fetchone()
        if row is None:
            raise KeyError(projection_id)
        return {
            "projection_id": projection_id,
            "projection_kind": row[0],
            "data_revision": row[1],
            "view_revision": row[2],
            "freshness_status": row[3],
            "dependency_set": json.loads(row[4]),
            "payload": json.loads(row[5]),
            "generated_at": row[6],
            "generator_policy_id": row[7],
        }

    def delete_summary_projections(self) -> int:
        """Delete all B2 Derived rows without touching Canonical or Ledger data."""
        with self.transaction():
            self._connection.execute("DELETE FROM derived_rebuild_receipts")
            return self._connection.execute("DELETE FROM summary_projections").rowcount

    # B3 additive: Commitment Canonical metadata and Derived due-status projection storage.
    # Business lifecycle and projection policy remain in later B3 tasks.

    def put_commitment_record(
        self,
        commitment_id: str,
        object_revision: str,
        commitment_kind: str,
        responsible_ref: str,
        statement_source_id: str,
        statement_locator: Mapping[str, Any],
        due_time: str,
        valid_start: str,
        valid_end: str | None,
        recorded_at: str,
        status: str,
        cancel_reason: str | None,
        review_status: str,
        synthetic_profile_id: str,
    ) -> None:
        """Persist B3 metadata after its Canonical Commitment was published."""
        canonical = self.canonical_object(commitment_id)
        if canonical.get("object_type") != "commitment":
            raise ValueError("commitment record requires a Canonical Commitment")
        if not responsible_ref or not statement_source_id or not due_time:
            raise ValueError("commitment record requires responsible_ref, direct Source and due_time")
        if status == "cancelled" and not cancel_reason:
            raise ValueError("cancelled commitment requires a non-empty cancel_reason")
        self._connection.execute(
            "INSERT INTO commitments (commitment_id, object_revision, commitment_kind, responsible_ref, "
            "statement_source_id, statement_locator_json, due_time, valid_start, valid_end, recorded_at, "
            "status, cancel_reason, review_status, synthetic_profile_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (commitment_id, object_revision, commitment_kind, responsible_ref, statement_source_id,
             _canonical_json(statement_locator), due_time, valid_start, valid_end, recorded_at,
             status, cancel_reason, review_status, synthetic_profile_id),
        )

    def commitment_record(self, commitment_id: str) -> JsonObject:
        row = self._connection.execute(
            "SELECT object_revision, commitment_kind, responsible_ref, statement_source_id, statement_locator_json, "
            "due_time, valid_start, valid_end, recorded_at, status, cancel_reason, review_status, synthetic_profile_id "
            "FROM commitments WHERE commitment_id = ?",
            (commitment_id,),
        ).fetchone()
        if row is None:
            raise KeyError(commitment_id)
        return {
            "commitment_id": commitment_id,
            "object_revision": row[0],
            "commitment_kind": row[1],
            "responsible_ref": row[2],
            "statement_source_id": row[3],
            "statement_locator": json.loads(row[4]),
            "due_time": row[5],
            "valid_start": row[6],
            "valid_end": row[7],
            "recorded_at": row[8],
            "status": row[9],
            "cancel_reason": row[10],
            "review_status": row[11],
            "synthetic_profile_id": row[12],
        }

    def commitment_records(self) -> list[JsonObject]:
        return [self.commitment_record(row[0]) for row in self._connection.execute(
            "SELECT commitment_id FROM commitments ORDER BY commitment_id"
        )]

    def update_commitment_status(
        self, commitment_id: str, object_revision: str, status: str, cancel_reason: str | None = None
    ) -> None:
        """Update Commitment lifecycle fields after a ChangeSet published a new revision."""
        if status == "cancelled" and not cancel_reason:
            raise ValueError("cancelled commitment requires a non-empty cancel_reason")
        cursor = self._connection.execute(
            "UPDATE commitments SET object_revision = ?, status = ?, cancel_reason = ? WHERE commitment_id = ?",
            (object_revision, status, cancel_reason, commitment_id),
        )
        if cursor.rowcount != 1:
            raise KeyError(commitment_id)

    def put_due_status_projection(
        self,
        projection_id: str,
        commitment_id: str,
        data_revision: str,
        view_revision: str,
        freshness_status: str,
        due_status: str,
        clock_instant: str,
        payload: Mapping[str, Any],
        generated_at: str,
        generator_policy_id: str,
    ) -> None:
        self._connection.execute(
            "INSERT INTO due_status_projections (projection_id, commitment_id, data_revision, view_revision, "
            "freshness_status, due_status, clock_instant, payload_json, generated_at, generator_policy_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (projection_id, commitment_id, data_revision, view_revision, freshness_status, due_status,
             clock_instant, _canonical_json(payload), generated_at, generator_policy_id),
        )

    def replace_due_status_projection(
        self, projection_id: str, commitment_id: str, data_revision: str, view_revision: str,
        freshness_status: str, due_status: str, clock_instant: str, payload: Mapping[str, Any],
        generated_at: str, generator_policy_id: str,
    ) -> None:
        self._connection.execute(
            "INSERT INTO due_status_projections (projection_id, commitment_id, data_revision, view_revision, "
            "freshness_status, due_status, clock_instant, payload_json, generated_at, generator_policy_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(projection_id) DO UPDATE SET "
            "commitment_id=excluded.commitment_id, data_revision=excluded.data_revision, "
            "view_revision=excluded.view_revision, freshness_status=excluded.freshness_status, "
            "due_status=excluded.due_status, clock_instant=excluded.clock_instant, "
            "payload_json=excluded.payload_json, generated_at=excluded.generated_at, "
            "generator_policy_id=excluded.generator_policy_id",
            (projection_id, commitment_id, data_revision, view_revision, freshness_status, due_status,
             clock_instant, _canonical_json(payload), generated_at, generator_policy_id),
        )

    def due_status_projection(self, projection_id: str) -> JsonObject:
        row = self._connection.execute(
            "SELECT commitment_id, data_revision, view_revision, freshness_status, due_status, clock_instant, "
            "payload_json, generated_at, generator_policy_id FROM due_status_projections WHERE projection_id = ?",
            (projection_id,),
        ).fetchone()
        if row is None:
            raise KeyError(projection_id)
        return {
            "projection_id": projection_id,
            "commitment_id": row[0],
            "data_revision": row[1],
            "view_revision": row[2],
            "freshness_status": row[3],
            "due_status": row[4],
            "clock_instant": row[5],
            "payload": json.loads(row[6]),
            "generated_at": row[7],
            "generator_policy_id": row[8],
        }

    def due_status_projections(self) -> list[JsonObject]:
        return [self.due_status_projection(row[0]) for row in self._connection.execute(
            "SELECT projection_id FROM due_status_projections ORDER BY projection_id"
        )]

    def mark_due_status_projections_stale(self, data_revision: str) -> int:
        return self._connection.execute(
            "UPDATE due_status_projections SET data_revision = ?, freshness_status = 'stale' "
            "WHERE view_revision != ? AND freshness_status = 'fresh'",
            (data_revision, data_revision),
        ).rowcount

    def put_due_rebuild_receipt(
        self, receipt_id: str, projection_id: str, data_revision: str, status: str, payload: Mapping[str, Any]
    ) -> None:
        self._connection.execute(
            "INSERT INTO due_rebuild_receipts (receipt_id, projection_id, data_revision, status, payload_json) "
            "VALUES (?, ?, ?, ?, ?)",
            (receipt_id, projection_id, data_revision, status, _canonical_json(payload)),
        )

    def due_rebuild_receipts(self) -> list[JsonObject]:
        return [
            {"receipt_id": row[0], "projection_id": row[1], "data_revision": row[2], "status": row[3], "payload": json.loads(row[4])}
            for row in self._connection.execute(
                "SELECT receipt_id, projection_id, data_revision, status, payload_json "
                "FROM due_rebuild_receipts ORDER BY receipt_id"
            )
        ]

    def delete_due_status_projections(self) -> int:
        """Delete all B3 Derived rows without touching Canonical or Ledger data."""
        with self.transaction():
            self._connection.execute("DELETE FROM due_rebuild_receipts")
            return self._connection.execute("DELETE FROM due_status_projections").rowcount

    # A2 additive: current_state Core View projection helpers (Derived only).

    def canonical_object_summaries(self) -> list[JsonObject]:
        """Read-only listing of Canonical objects for Derived projection computation."""
        return [
            {"object_id": row[0], "object_type": row[1], "object_revision": row[2], "payload": json.loads(row[3])}
            for row in self._connection.execute(
                "SELECT object_id, object_type, object_revision, payload_json FROM canonical_objects ORDER BY object_id"
            )
        ]

    def upsert_projection(
        self, view_name: str, data_revision: str, view_revision: str, freshness_status: str, payload: Mapping[str, Any]
    ) -> None:
        """Insert or replace a Derived projection row; required for views absent from the seed."""
        self._connection.execute(
            "INSERT INTO projection_rows (view_name, data_revision, view_revision, freshness_status, payload_json) "
            "VALUES (?, ?, ?, ?, ?) ON CONFLICT(view_name) DO UPDATE SET data_revision=excluded.data_revision, "
            "view_revision=excluded.view_revision, freshness_status=excluded.freshness_status, "
            "payload_json=excluded.payload_json",
            (view_name, data_revision, view_revision, freshness_status, _canonical_json(payload)),
        )

    def put_a2_view_receipt(
        self, receipt_id: str, view_name: str, data_revision: str, status: str, payload: Mapping[str, Any]
    ) -> None:
        self._connection.execute(
            "INSERT INTO a2_view_rebuild_receipts (receipt_id, view_name, data_revision, status, payload_json) "
            "VALUES (?, ?, ?, ?, ?)",
            (receipt_id, view_name, data_revision, status, _canonical_json(payload)),
        )

    def a2_view_receipts(self) -> list[JsonObject]:
        return [
            {"receipt_id": row[0], "view_name": row[1], "data_revision": row[2], "status": row[3], "payload": json.loads(row[4])}
            for row in self._connection.execute(
                "SELECT receipt_id, view_name, data_revision, status, payload_json "
                "FROM a2_view_rebuild_receipts ORDER BY receipt_id"
            )
        ]

    def mark_current_state_stale(self, data_revision: str) -> int:
        return self._connection.execute(
            "UPDATE projection_rows SET freshness_status = 'stale' "
            "WHERE view_name = 'current_state' AND view_revision != ? AND freshness_status = 'fresh'",
            (data_revision,),
        ).rowcount

    def mark_all_projections_stale(self, data_revision: str) -> int:
        """Mark every fresh Core View projection stale after a Canonical merge/split publish."""
        return self._connection.execute(
            "UPDATE projection_rows SET freshness_status = 'stale' "
            "WHERE view_revision != ? AND freshness_status = 'fresh'",
            (data_revision,),
        ).rowcount

    def delete_current_state_projection(self) -> int:
        """Delete the A2 Derived view row and its receipts without touching Canonical or Ledger data."""
        with self.transaction():
            self._connection.execute("DELETE FROM a2_view_rebuild_receipts WHERE view_name = 'current_state'")
            return self._connection.execute("DELETE FROM projection_rows WHERE view_name = 'current_state'").rowcount

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

    def source_hashes_by_kind(self, source_kind: str) -> set[str]:
        """Narrow read-only helper (ADR-0020): content hashes of one source_kind."""
        return {
            row[0]
            for row in self._connection.execute(
                "SELECT content_hash FROM source_records WHERE source_kind = ?", (source_kind,)
            )
        }

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

    def ledger_records_of_type(self, record_type: str) -> list[JsonObject]:
        return [
            json.loads(row[0])
            for row in self._connection.execute(
                "SELECT payload_json FROM ledger_records WHERE record_type = ? ORDER BY rowid",
                (record_type,),
            )
        ]

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

    def delete_ledger_record(self, record_id: str) -> None:
        # ADR-0015: Derived-only deletion (review reports / phase comparisons); never for Canonical audit rows.
        cursor = self._connection.execute("DELETE FROM ledger_records WHERE record_id = ?", (record_id,))
        if cursor.rowcount != 1:
            raise KeyError(record_id)

    def schema_objects(self) -> set[str]:
        return {
            row[0]
            for row in self._connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

    def portability_snapshot(self) -> JsonObject:
        """Return the authoritative layers needed for a private Context Pack.

        Projection rows are intentionally excluded: they are Derived and cannot
        become evidence by travelling through a portability export.
        """
        revision = self.current_revision()
        return {
            "data_revision": revision,
            "sources": [
                json.loads(row[0])
                for row in self._connection.execute(
                    "SELECT payload_json FROM source_records ORDER BY source_id"
                )
            ],
            "canonical": [
                json.loads(row[0])
                for row in self._connection.execute(
                    "SELECT payload_json FROM canonical_objects ORDER BY object_id"
                )
            ],
            "ledger": [
                json.loads(row[0])
                for row in self._connection.execute(
                    "SELECT payload_json FROM ledger_records ORDER BY record_id"
                )
            ],
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
                    receipt_id = source.get('append_receipt_id')
                    if receipt_id is None:
                        receipt_id = source['source_id'] + ':receipt'
                    connection.execute(
                        'INSERT OR IGNORE INTO source_records (source_id, append_receipt_id, source_kind, content_hash, payload_json) VALUES (?, ?, ?, ?, ?)',
                        (
                            source['source_id'],
                            receipt_id,
                            source['source_kind'],
                            source.get('content_hash', _canonical_digest(source)),
                            _canonical_json(source),
                        ),
                    )
                    receipt = {
                        'receipt_id': receipt_id,
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
            # Sort by stable identifier for deterministic digest
            def _sort_key(x):
                for key in ('source_id', 'assertion_id', 'object_id', 'record_id', 'view_name', 'coverage_window_id'):
                    if key in x:
                        return x[key]
                return ''
            payloads.sort(key=_sort_key)
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

    def put_merge_record(
        self,
        merge_id: str,
        source_entity_ref: str,
        target_entity_ref: str,
        pre_merge_references: list[Mapping[str, Any]],
        published_revision: str,
        recorded_at: str,
        synthetic_profile_id: str,
    ) -> None:
        """Persist an A3 merge audit record; records are append-only and immutable."""
        if not merge_id or not source_entity_ref or not target_entity_ref:
            raise ValueError("merge record requires merge_id and both entity refs")
        if source_entity_ref == target_entity_ref:
            raise ValueError("merge record source and target must differ")
        if not isinstance(pre_merge_references, list):
            raise ValueError("merge record requires a pre_merge_references list")
        self._connection.execute(
            "INSERT INTO merge_records (merge_id, source_entity_ref, target_entity_ref, "
            "pre_merge_references_json, published_revision, recorded_at, synthetic_profile_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (merge_id, source_entity_ref, target_entity_ref,
             _canonical_json(pre_merge_references), published_revision, recorded_at, synthetic_profile_id),
        )

    def merge_record(self, merge_id: str) -> JsonObject:
        row = self._connection.execute(
            "SELECT source_entity_ref, target_entity_ref, pre_merge_references_json, "
            "published_revision, recorded_at, synthetic_profile_id FROM merge_records WHERE merge_id = ?",
            (merge_id,),
        ).fetchone()
        if row is None:
            raise KeyError(merge_id)
        return {
            "merge_id": merge_id,
            "source_entity_ref": row[0],
            "target_entity_ref": row[1],
            "pre_merge_references": json.loads(row[2]),
            "published_revision": row[3],
            "recorded_at": row[4],
            "synthetic_profile_id": row[5],
        }

    def merge_record_or_none(self, merge_id: str) -> JsonObject | None:
        try:
            return self.merge_record(merge_id)
        except KeyError:
            return None

    def merge_records(self) -> list[JsonObject]:
        return [self.merge_record(row[0]) for row in self._connection.execute(
            "SELECT merge_id FROM merge_records ORDER BY merge_id"
        )]

    def put_split_record(
        self,
        split_id: str,
        merge_ref: str,
        published_revision: str,
        recorded_at: str,
    ) -> None:
        """Persist an A3 split compensation record; append-only."""
        if not split_id or not merge_ref:
            raise ValueError("split record requires split_id and merge_ref")
        if self.merge_record_or_none(merge_ref) is None:
            raise ValueError("split record requires an existing merge record")
        self._connection.execute(
            "INSERT INTO split_records (split_id, merge_ref, published_revision, recorded_at) "
            "VALUES (?, ?, ?, ?)",
            (split_id, merge_ref, published_revision, recorded_at),
        )

    def split_record_for_merge(self, merge_ref: str) -> JsonObject | None:
        row = self._connection.execute(
            "SELECT split_id, published_revision, recorded_at FROM split_records WHERE merge_ref = ?",
            (merge_ref,),
        ).fetchone()
        if row is None:
            return None
        return {
            "split_id": row[0],
            "merge_ref": merge_ref,
            "published_revision": row[1],
            "recorded_at": row[2],
        }

    def split_records(self) -> list[JsonObject]:
        return [self.split_record_for_merge(row[0]) for row in self._connection.execute(
            "SELECT merge_ref FROM split_records ORDER BY split_id"
        )]


    # A4 additive: read-only policy label and digest helpers for query-time access
    # policy evaluation. These helpers never write; policy decisions stay Derived.

    # B4 additive: read-only listing helpers for the reconciliation detector.
    # These helpers never write; reconciliation findings stay Derived.

    def revision_ids(self) -> list[str]:
        """Read-only listing of Canonical revision ids in stable order."""
        return [
            row[0]
            for row in self._connection.execute(
                "SELECT revision_id FROM canonical_revisions ORDER BY revision_id"
            )
        ]

    def projection_records(self) -> list[JsonObject]:
        """Read-only listing of every Derived projection row, including view_name."""
        return [
            {**self.projection_record(row[0]), "view_name": row[0]}
            for row in self._connection.execute(
                "SELECT view_name FROM projection_rows ORDER BY view_name"
            )
        ]

    def object_policy_labels(self, object_id: str) -> JsonObject | None:
        """Read-only S1 policy labels for one Canonical object, or None if absent."""
        payload = self.canonical_object_or_none(object_id)
        if payload is None:
            return None
        compartments = payload.get("compartments")
        return {
            "object_id": object_id,
            "sensitivity": payload.get("sensitivity"),
            "compartments": list(compartments) if isinstance(compartments, list) else [],
            "owner_ref": payload.get("owner_ref"),
        }

    def policy_labeled_objects(self) -> list[JsonObject]:
        """Read-only listing of Canonical objects carrying S1 policy labels."""
        labeled: list[JsonObject] = []
        for summary in self.canonical_object_summaries():
            payload = summary["payload"]
            if "sensitivity" in payload or "compartments" in payload:
                compartments = payload.get("compartments")
                labeled.append(
                    {
                        "object_id": summary["object_id"],
                        "object_type": summary["object_type"],
                        "sensitivity": payload.get("sensitivity"),
                        "compartments": list(compartments) if isinstance(compartments, list) else [],
                        "owner_ref": payload.get("owner_ref"),
                    }
                )
        return labeled

    def canonical_object_digest(self, object_id: str) -> str:
        """Deterministic SHA-256 digest of one Canonical object payload."""
        return _canonical_digest(self.canonical_object(object_id))

    def canonical_layer_digest(self) -> str:
        """Deterministic digest over all Canonical objects for zero-write checks."""
        snapshot = self.seed_snapshot()
        return _canonical_digest({"data_revision": snapshot["data_revision"], "objects": snapshot["objects"]})


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
