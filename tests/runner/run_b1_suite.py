from __future__ import annotations
import argparse, hashlib, json, platform, socket, sqlite3, subprocess, sys, unittest, uuid
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[2]; MANIFEST=ROOT/"tests/b1_suite_manifest.json"
def digest(path: Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def blocked(*args:Any,**kwargs:Any)->Any:raise RuntimeError("external network is disabled by the B1 runner")
def scenario_id(test:unittest.case.TestCase)->str:return getattr(getattr(test,test._testMethodName),"_noetide_scenario_id","unknown")
class Result(unittest.TestResult):
 def __init__(self):super().__init__();self.items={}
 def _record(self,test,status,detail=""):self.items[scenario_id(test)]={"individual_test_result":status,"detail":detail[:1000]}
 def addSuccess(self,test):super().addSuccess(test);self._record(test,"passed")
 def addFailure(self,test,err):super().addFailure(test,err);self._record(test,"failed",self._exc_info_to_string(err,test))
 def addError(self,test,err):super().addError(test,err);self._record(test,"errored",self._exc_info_to_string(err,test))
def main()->int:
 p=argparse.ArgumentParser();p.add_argument("--output",required=True,type=Path);args=p.parse_args();out=args.output.resolve()
 if ROOT not in out.parents or out.exists():raise SystemExit("output must be a new file inside the repository")
 manifest=json.loads(MANIFEST.read_text(encoding="utf-8"));bound=[]
 for item in manifest["artifacts"]:
  path=ROOT/item["path"]
  if not path.is_file() or digest(path)!=item["sha256"]:raise SystemExit(f"artifact hash mismatch: {item['path']}")
  bound.append({"role":item["role"],"path":item["path"],"sha256":item["sha256"]})
 old_socket,old_connect=socket.socket,socket.create_connection;socket.socket=blocked;socket.create_connection=blocked
 try:
  suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromName("tests.semantic.test_b1_budget"),unittest.defaultTestLoader.loadTestsFromName("tests.semantic.test_b1_persistence")]);result=Result();suite.run(result)
 finally:socket.socket,socket.create_connection=old_socket,old_connect
 required=[{"test_id":name,**result.items.get(name,{"individual_test_result":"errored","detail":"scenario result missing"})} for name in manifest["required_scenario_ids"]];passed=all(x["individual_test_result"]=="passed" for x in required)
 artifact={"schema_version":"noetide.b1-run-result.v1","run_id":f"b1-{uuid.uuid4().hex}","suite_id":manifest["suite_id"],"manifest_sha256":digest(MANIFEST),"git_commit":subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip(),"applicability":"current","environment":{"platform":platform.platform(),"python":platform.python_version(),"sqlite":sqlite3.sqlite_version,"network":"blocked","dependencies":"stdlib_only"},"exit_code":0 if passed else 1,"run_result":"passed" if passed else "failed","required_results":required,"bound_artifacts":bound}
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n");print(f"{artifact['run_result']}: {len(required)} required result IDs; artifact={out.relative_to(ROOT)}");return artifact["exit_code"]
if __name__=="__main__":raise SystemExit(main())
