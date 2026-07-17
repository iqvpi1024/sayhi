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

        # CoverageEvaluator: check coverage before assertion evaluation
        coverage_result = self._evaluate_coverage(valid_time, coverage_windows)
        if coverage_result['status'] == 'not_covered':
            return self._make_answer(
                query_request, 'not_covered', None, None,
                [], coverage_windows,
                coverage_result['reason_codes'], 'not_applicable'
            )

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

        # AS-008: derived inputs present but no direct canonical objects = derived evidence forbidden
        if not self.initial.get('canonical_objects', []) and self.initial.get('derived_inputs', []):
            return self._make_answer(
                query_request, 'unknown', None, None,
                evidence_refs, coverage_windows,
                ['derived_evidence_forbidden'], 'not_applicable'
            )

        # AS-003: unconfirmed candidate present = unconfirmed
        candidates = self.initial.get('candidates', [])
        if candidates and not selected_assertion:
            return self._make_answer(
                query_request, 'unconfirmed', None, None,
                [], coverage_windows,
                ['unreviewed_candidate_present'], 'not_applicable'
            )

        # AS-007: coverage sufficient but no assertion = unknown
        if coverage_result['status'] == 'ok' and not selected_assertion:
            return self._make_answer(
                query_request, 'unknown', None, None,
                evidence_refs, coverage_windows,
                ['coverage_sufficient_no_safe_conclusion'], 'not_applicable'
            )

        # AS-004: conflict detection for multiple assertions with same predicate and overlapping valid_time
        assertions = [obj for obj in self.initial.get('canonical_objects', [])
                      if obj.get('object_type') == 'assertion' and obj.get('predicate') == predicate]
        if len(assertions) > 1:
            conflict = self._evaluate_conflict(assertions, valid_time)
            if conflict['is_conflict']:
                all_evidence = []
                for a in assertions:
                    for er in a.get('evidence_refs', []):
                        all_evidence.append({
                            'source_id': er['source_id'],
                            'locator': er.get('locator', {}),
                        })
                all_evidence.sort(key=lambda x: x['source_id'])
                return self._make_answer(
                    query_request, 'disputed', None, None,
                    all_evidence, coverage_windows,
                    ['unresolved_conflict'], 'not_applicable',
                    conflict_details=conflict['details']
                )

        # AS-006: freshness evaluation for current queries
        if valid_time == 'current' and selected_assertion:
            freshness = self._evaluate_freshness(evidence_refs)
            if freshness['is_stale']:
                return self._make_answer(
                    query_request, 'stale', None, None,
                    evidence_refs, coverage_windows,
                    ['evidence_outside_freshness_window'], freshness['policy_ref'],
                    evidence_effective_at=freshness['evidence_effective_at']
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
                    query_request, 'verified', selected_assertion.get('value'), 'statement_occurrence',
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

    def _evaluate_coverage(self, valid_time, coverage_windows):
        if not coverage_windows:
            return {'status': 'unknown', 'reason_codes': ['no_coverage_window']}

        for cw in coverage_windows:
            coverage_start = cw['coverage_start']
            coverage_end = cw['coverage_end']
            continuity = cw['continuity']

            # Check if valid_time is within coverage window
            if coverage_start != 'unbounded' and valid_time < coverage_start:
                return {
                    'status': 'not_covered',
                    'reason_codes': ['outside_coverage_window'],
                    'gaps': [{'start': 'unbounded', 'end': coverage_start, 'reason': 'outside_window'}]
                }
            if coverage_end != 'unbounded' and valid_time > coverage_end:
                return {
                    'status': 'not_covered',
                    'reason_codes': ['outside_coverage_window'],
                    'gaps': [{'start': coverage_end, 'end': 'unbounded', 'reason': 'outside_window'}]
                }

            # Check continuity
            if continuity == 'unknown':
                return {
                    'status': 'not_covered',
                    'reason_codes': ['coverage_continuity_unknown'],
                    'gaps': [{'start': coverage_start, 'end': 'unbounded', 'reason': 'continuity_unknown'}]
                }

        # Coverage is sufficient
        return {'status': 'ok', 'reason_codes': []}

    def _evaluate_conflict(self, assertions, valid_time):
        # Check if assertions have conflicting values and overlapping valid_time
        if len(assertions) < 2:
            return {'is_conflict': False, 'details': []}

        # Check for overlapping valid_time
        def parse_time(t):
            if t == 'unbounded':
                return None
            from datetime import datetime
            return datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ')

        def overlap(a, b):
            a_start = parse_time(a['valid_time']['start'])
            a_end = parse_time(a['valid_time']['end'])
            b_start = parse_time(b['valid_time']['start'])
            b_end = parse_time(b['valid_time']['end'])

            if a_start and b_end and a_start >= b_end:
                return False
            if a_end and b_start and a_end <= b_start:
                return False
            return True

        # Check if any pair has conflicting values and overlapping time
        for i in range(len(assertions)):
            for j in range(i + 1, len(assertions)):
                if assertions[i].get('value') != assertions[j].get('value'):
                    if overlap(assertions[i], assertions[j]):
                        details = [
                            {
                                'assertion_id': a['assertion_id'],
                                'value': a.get('value'),
                                'perspective_ref': a.get('perspective_ref'),
                                'valid_time': a.get('valid_time'),
                            }
                            for a in assertions
                        ]
                        details.sort(key=lambda x: x['assertion_id'])
                        return {
                            'is_conflict': True,
                            'details': details
                        }

        return {'is_conflict': False, 'details': []}

    def _evaluate_freshness(self, evidence_refs):
        policies = self.initial.get('freshness_policies', [])
        if not policies:
            return {'is_stale': False, 'policy_ref': 'not_applicable', 'evidence_effective_at': None}

        policy = policies[0]
        max_age = policy.get('max_age_seconds', 0)
        evaluated_at = policy.get('evaluated_at', self.clock)
        policy_ref = policy.get('policy_id', 'not_applicable')

        # Find evidence effective time from source records
        evidence_effective_at = None
        for src in self.initial.get('source_records', []):
            evidence_effective_at = src.get('source_created_at')
            break

        if evidence_effective_at and evaluated_at:
            from datetime import datetime
            fmt = '%Y-%m-%dT%H:%M:%SZ'
            try:
                effective_dt = datetime.strptime(evidence_effective_at, fmt)
                evaluated_dt = datetime.strptime(evaluated_at, fmt)
                age_seconds = (evaluated_dt - effective_dt).total_seconds()
                is_stale = age_seconds > max_age
            except ValueError:
                is_stale = False
        else:
            is_stale = False

        return {
            'is_stale': is_stale,
            'policy_ref': policy_ref,
            'evidence_effective_at': evidence_effective_at,
        }

    def _coverage_gaps(self, coverage_windows, reason_codes):
        if 'outside_coverage_window' in reason_codes:
            for cw in coverage_windows:
                if cw['coverage_start'] != 'unbounded':
                    return [{'start': 'unbounded', 'end': cw['coverage_start'], 'reason': 'outside_window'}]
                elif cw['coverage_end'] != 'unbounded':
                    return [{'start': cw['coverage_end'], 'end': 'unbounded', 'reason': 'outside_window'}]
        if 'coverage_continuity_unknown' in reason_codes:
            for cw in coverage_windows:
                return [{'start': cw['coverage_start'], 'end': 'unbounded', 'reason': 'continuity_unknown'}]
        return []

    def _make_answer(self, query_request, status, value, scope, evidence_refs, coverage_windows, reason_codes, policy_ref, evidence_effective_at=None, conflict_details=None):
        result = {
            'answer_status': status,
            'answer_value': value,
            'verification_scope': scope,
            'valid_time': {
                'requested': query_request['valid_time'],
                'resolved': self.clock if query_request['valid_time'] == 'current' else query_request['valid_time'],
            },
            'recorded_as_of': 'current',
            'evaluated_at': self.clock,
            'evidence_refs': evidence_refs,
            'coverage': {
                'window_refs': [cw['coverage_window_id'] for cw in coverage_windows],
                'gaps': self._coverage_gaps(coverage_windows, reason_codes),
                'sufficient': len(coverage_windows) > 0 and 'outside_coverage_window' not in reason_codes and 'coverage_continuity_unknown' not in reason_codes,
            },
            'reason_codes': reason_codes,
            'data_revision': self.data_revision,
            'assessment_policy_ref': policy_ref,
        }
        if evidence_effective_at is not None:
            result['evidence_effective_at'] = evidence_effective_at
        if conflict_details is not None:
            result['conflict_details'] = conflict_details
        return result
