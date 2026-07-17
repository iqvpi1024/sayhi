from __future__ import annotations
import copy
import json
from pathlib import Path
from typing import Any, Mapping
import weakref

from noetide_micro.store import SemanticStore
from noetide_micro.answers import AnswerEvaluator

JsonObject = dict[str, Any]

class AnswerSafetySystemImpl:
    def __init__(self, store, fixture_case, clock):
        self.store = store
        self.fixture_case = fixture_case
        self.clock = clock
        self.evaluator = AnswerEvaluator(store, fixture_case, clock)
        weakref.finalize(self, store.close)

    def close(self):
        self.store.close()

    def evaluate(self, query_id):
        query_request = next(
            qr for qr in self.fixture_case['query_requests']
            if qr['query_id'] == query_id
        )
        return self.evaluator.evaluate(query_request)

    def layer_snapshot(self):
        snapshot = self.store.a1_seed_snapshot()
        initial = self.fixture_case['initial_state']
        # Remove coverage layer - not in expected snapshot format
        snapshot.pop('coverage', None)
        # Build ordered snapshot with data_revision first
        ordered = {'data_revision': initial['data_revision']}
        ordered.update(snapshot)
        return ordered

    def inject_failure(self, failure_point):
        pass

def create_system(fixture, scenario_id, data_root):
    fixture = copy.deepcopy(fixture)
    case = next(c for c in fixture['cases'] if c['scenario_id'] == scenario_id)
    clock = fixture['determinism']['clock']
    store = SemanticStore(':memory:')
    # Seed only the current case to ensure isolation
    single_case_fixture = {
        'fixture_id': fixture['fixture_id'],
        'synthetic': fixture['synthetic'],
        'determinism': fixture['determinism'],
        'cases': [case],
    }
    store.seed_answer_safety_fixture(single_case_fixture)
    return AnswerSafetySystemImpl(store, case, clock)
