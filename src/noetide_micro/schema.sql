-- TASK-001: persistence only. Business transitions are implemented in later tasks.

CREATE TABLE IF NOT EXISTS schema_metadata (
    metadata_key TEXT PRIMARY KEY,
    metadata_value TEXT NOT NULL
);

-- Source Vault
CREATE TABLE IF NOT EXISTS source_records (
    source_id TEXT PRIMARY KEY,
    append_receipt_id TEXT NOT NULL UNIQUE,
    source_kind TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS append_receipts (
    receipt_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL UNIQUE REFERENCES source_records(source_id),
    status TEXT NOT NULL CHECK (status IN ('stored', 'duplicate', 'rejected')),
    payload_json TEXT NOT NULL
);

-- Canonical Context
CREATE TABLE IF NOT EXISTS canonical_revisions (
    revision_id TEXT PRIMARY KEY,
    recorded_at TEXT NOT NULL,
    revision_kind TEXT NOT NULL CHECK (revision_kind IN ('seed', 'changeset'))
);

CREATE TABLE IF NOT EXISTS canonical_objects (
    object_id TEXT PRIMARY KEY,
    object_type TEXT NOT NULL CHECK (object_type IN (
        'entity', 'episode', 'assertion', 'relationship', 'state', 'hypothesis',
        'goal', 'commitment', 'decision', 'outcome', 'changeset', 'source'
    )),
    object_revision TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS canonical_evidence_refs (
    object_id TEXT NOT NULL REFERENCES canonical_objects(object_id),
    source_id TEXT NOT NULL REFERENCES source_records(source_id),
    locator_json TEXT NOT NULL,
    stance TEXT NOT NULL CHECK (stance IN ('supports', 'contradicts', 'contextual')),
    claim_ref TEXT NOT NULL,
    PRIMARY KEY (object_id, source_id, locator_json, stance, claim_ref)
);

-- Revision Ledger. TASK-001 establishes storage only; no ChangeSet behavior exists yet.
CREATE TABLE IF NOT EXISTS ledger_records (
    record_id TEXT PRIMARY KEY,
    revision_id TEXT REFERENCES canonical_revisions(revision_id),
    record_type TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

-- Derived Projection. Values are seeded only; projector/read behavior is deferred to TASK-007.
CREATE TABLE IF NOT EXISTS projection_rows (
    view_name TEXT PRIMARY KEY CHECK (view_name IN ('person_card', 'relationship_timeline')),
    data_revision TEXT NOT NULL REFERENCES canonical_revisions(revision_id),
    view_revision TEXT NOT NULL REFERENCES canonical_revisions(revision_id),
    freshness_status TEXT NOT NULL CHECK (freshness_status IN ('fresh', 'stale', 'updating', 'unavailable')),
    payload_json TEXT NOT NULL
);
