from __future__ import annotations
import argparse,hashlib,json,platform,socket,sqlite3,subprocess,sys,unittest,uuid
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[2]
REQUIRED=[f"C1-{i:03d}" for i in range(1,8)]
def blocked(*args:Any,**kwargs:Any)->Any:raise RuntimeError("external network is disabled by the C1 runner")
def sid(test):return getattr(getattr(test,test._testMethodName),"_noetide_scenario_id","unknown")
class Result(unittest.TestResult):
 def __init__(self):super().__init__();self.rows={}
 def _r(self,t,s,d=""):self.rows[sid(t)]={"individual_test_result":s,"detail":d[:1000]}
 def addSuccess(self,t):super().addSuccess(t);self._r(t,"passed")
 def addFailure(self,t,e):super().addFailure(t,e);self._r(t,"failed",self._exc_info_to_string(e,t))
 def addError(self,t,e):super().addError(t,e);self._r(t,"errored",self._exc_info_to_string(e,t))
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",required=True,type=Path);a=p.parse_args();out=a.output.resolve()
 if ROOT not in out.parents or out.exists():raise SystemExit("output must be new and inside repository")
 old,connect=socket.socket,socket.create_connection;socket.socket=blocked;socket.create_connection=blocked
 try:
  suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromName("tests.semantic.test_c1_boundaries"),unittest.defaultTestLoader.loadTestsFromName("tests.semantic.test_c1_changesets")]);r=Result();suite.run(r)
 finally:socket.socket,socket.create_connection=old,connect
 rows=[{"test_id":x,**r.rows.get(x,{"individual_test_result":"errored","detail":"missing"})} for x in REQUIRED];ok=all(x["individual_test_result"]=="passed" for x in rows)
 manifest=ROOT/"tests/c1_suite_manifest.json"
 artifact={"schema_version":"noetide.c1-run-result.v1","run_id":f"c1-{uuid.uuid4().hex}","suite_id":"c1_decision_outcome_v1","manifest_sha256":hashlib.sha256(manifest.read_bytes()).hexdigest(),"git_commit":subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip(),"environment":{"platform":platform.platform(),"python":platform.python_version(),"sqlite":sqlite3.sqlite_version,"network":"blocked","dependencies":"stdlib_only"},"command":["python","-m","tests.runner.run_c1_suite",*sys.argv[1:]],"exit_code":0 if ok else 1,"run_result":"passed" if ok else "failed","required_results":rows}
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(artifact,indent=2)+"\n",encoding="utf-8")
 print(f"{'passed' if ok else 'failed'}: {len(rows)} C1 scenarios");return 0 if ok else 1
if __name__=="__main__":raise SystemExit(main())
