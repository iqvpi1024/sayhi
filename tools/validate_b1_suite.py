from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];MANIFEST=ROOT/"tests/b1_suite_manifest.json"
def digest(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->int:
 m=json.loads(MANIFEST.read_text(encoding="utf-8"));errors=[]
 if m.get("required_scenario_ids")!=["B1-001","B1-002","B1-003","B1-004","B1-005"]:errors.append("scenario set mismatch")
 if m.get("flags")!={"suite_defined":True,"suite_materialized":True,"suite_executed":False,"suite_passed":False}:errors.append("manifest must be materialized/not-executed")
 for item in m.get("artifacts",[]):
  path=ROOT/item["path"]
  if not path.is_file() or digest(path)!=item["sha256"]:errors.append("artifact hash mismatch: "+item["path"])
 if errors:print("FAILED: "+"; ".join(errors));return 1
 print("PASSED: B1 Candidate Review suite materialized with 5 scenarios");print("NOT_EXECUTED: B1 business runner");return 0
if __name__=="__main__":raise SystemExit(main())
