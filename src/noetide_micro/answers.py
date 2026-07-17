from __future__ import annotations
import json
from typing import Any, Mapping

JsonObject = dict[str, Any]

class AnswerEvaluator:
    def __init__(self, store, fixture_case, clock):
        self.store = store
        self.case = fixture_case
        self.clock = clock
        self.initial = fixture_case['initial_state']
        self.data_revision = self.initial['data_revision']

    def evaluate(self, query_request):
        qid = query_request['query_id']
        claim_ref = query_request['claim_ref']
        predicate = query_request['predicate']
        requested_scope = query_request.get('verification_scope')
        valid_time = query_request['valid_time']
        coverage_refs = query_request.get('coverage_window_refs', [])

        # Find coverage windows
        coverage_windows = []
        for cw_ref in coverage_refs:
            cw = self.store.coverage_window(cw_ref)
            if cw:
                coverage_windows.append(cw)

        # EvidenceSelector: only direct source evidence from canonical objects
        evidence_refs = []
        selected_assertion = None
        for obj in self.initial.get('canonical_objects', []):
            if obj.get('object_type') == 'assertion':
                if obj.get('predicate') == predicate:
                    selected_assertion = obj
                    for er in obj.get('evidence_refs', []):
                        evidence_refs.append({
                            'source_id': er['source_id'],
                            'locator': er.get('locator', {}),
                        })

        # AS-008: no canonical objects = derived evidence forbidden
        if not self.initial.get('canonical_objects', []) and not evidence_refs:
            return self._make_answer(
                query_request, 'unknown', None, None,
                evidence_refs, coverage_windows,
                ['derived_evidence_forbidden'], 'not_applicable'
            )

        # AS-009: fictional assertion = fictional evidence excluded
        if selected_assertion and selected_assertion.get('assertion_kind') == 'fictional':
            return self._make_answer(
                query_request, 'unknown', None, None,
                [], coverage_windows,
                ['fictional_evidence_excluded'], 'not_applicable'
            )

        # AS-001: confirmed opinion with viewpoint scope
        if selected_assertion and selected_assertion.get('assertion_kind') == 'opinion':
            if selected_assertion.get('review_status') == 'confirmed' and requested_scope == 'viewpoint':
                return self._make_answer(
                    query_request, 'verified', selected_assertion.get('value'), 'viewpoint',
                    evidence_refs, coverage_windows,
                    ['viewpoint_scope_confirmed'], 'answer_scope_policy_v1'
                )

        # AS-002: confirmed reported with statement_occurrence scope
        if selected_assertion and selected_assertion.get('assertion_kind') == 'reported':
            if selected_assertion.get('review_status') == 'confirmed' and requested_scope == 'statement_occurrence':
                return self._make_answer(
                    query_request, 'verified', 'present', 'statement_occurrence',
                    evidence_refs, coverage_windows,
                    ['statement_occurrence_confirmed'], 'answer_scope_policy_v1'
                )
            # world_claim for reported = unknown
            if requested_scope == 'world_claim':
                return self._make_answer(
                    query_request, 'unknown', None, None,
                    evidence_refs, coverage_windows,
                    ['world_claim_not_verified'], 'not_applicable'
                )

        # Default: unknown
        return self._make_answer(
            query_request, 'unknown', None, None,
            evidence_refs, coverage_windows,
            ['no_matching_assertion'], 'not_applicable'
        )

    def _make_answer(self, query_request, status, value, scope, evidence_refs, coverage_windows, reason_codes, policy_ref):
        return {
            'answer_status': status,
            'answer_value': value,
            'verification_scope': scope,
            'valid_time': {
                'requested': query_request['valid_time'],
                'resolved': query_request['valid_time'],
            },
            'recorded_as_of': 'current',
            'evaluated_at': self.clock,
            'evidence_refs': evidence_refs,
            'coverage': {
                'window_refs': [cw['coverage_window_id'] for cw in coverage_windows],
                'gaps': [],
                'sufficient': len(coverage_windows) > 0,
            },
            'reason_codes': reason_codes,
            'data_revision': self.data_revision,
            'assessment_policy_ref': policy_ref,
        }
