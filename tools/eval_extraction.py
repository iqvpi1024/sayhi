"""识灵提取质量评测:用固定合成语料对提取管线做可重复的量化评测。

仅使用标准库。两种模式:
- offline:不调模型,走 product.py 的离线规则路径(NoetideApp._offline_items)做基线;
- cloud:用 EXTRACTION_SYSTEM_PROMPT + build_extraction_prompt 走 chat_completion 真实调用,
  再经 parse_extraction_output 解析与 _candidate_from_extraction 映射,与产品链路一致。

安全不变量:api_key 只从 --api-key 或环境变量 NOETIDE_EVAL_API_KEY 进入,
绝不写入报告/stdout;报告写出前对全文再做一次 api_key 替换脱敏。

用法:
  python tools/eval_extraction.py --mode offline \
      --output docs/testing/results/extraction-eval-offline-20260808.json
  python tools/eval_extraction.py --mode cloud --provider deepseek \
      --output docs/testing/results/extraction-eval-cloud-deepseek-20260808.json
  (cloud 模式未提供 api_key 时不执行,报告记 not_executed)
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from noetide_micro import llm_providers, product  # noqa: E402

CORPUS_DIR = ROOT / "tests/fixtures/extraction_eval_v1"
EXPECTED_PATH = CORPUS_DIR / "expected.json"
API_KEY_ENV = "NOETIDE_EVAL_API_KEY"
CORPUS_GLOB = ("*.md", "*.txt")

JsonObject = dict[str, Any]


def _collect_texts(value: Any) -> list[str]:
    """递归收集候选结构里的全部字符串,拼成该语料的提取文本 haystack。"""
    texts: list[str] = []
    if isinstance(value, str):
        texts.append(value)
    elif isinstance(value, dict):
        for item in value.values():
            texts.extend(_collect_texts(item))
    elif isinstance(value, (list, tuple)):
        for item in value:
            texts.extend(_collect_texts(item))
    return texts


def _git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT, capture_output=True, text=True, timeout=10,
        )
        commit = result.stdout.strip()
        if result.returncode == 0 and commit:
            return commit
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown"


def _load_expected() -> JsonObject:
    return json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))


def _corpus_files() -> list[Path]:
    files = [p for pattern in CORPUS_GLOB for p in CORPUS_DIR.glob(pattern)]
    return sorted({p.name: p for p in files}.values(), key=lambda p: p.name)


def _run_offline(source_text: str) -> tuple[list[JsonObject], JsonObject]:
    """离线规则基线:_offline_items 不触碰 self 状态,直接以未绑定方法调用(避免建库)。"""
    items = product.NoetideApp._offline_items(None, {"content": source_text})
    # 离线路径不经模型输出解析:parse 指标记 None,编造证据丢弃恒为 0(不产出 evidence_quote)
    stats: JsonObject = {
        "parsed": len(items),
        "dropped_invalid": None,
        "dropped_fabricated_evidence": 0,
        "error": None,
    }
    return items, stats


def _run_cloud(
    source_text: str, provider: str, endpoint: str, api_key: str, model: str,
    timeout: float, temperature: float | None, max_tokens: int,
) -> tuple[list[JsonObject], JsonObject, str | None]:
    messages = [
        {"role": "system", "content": llm_providers.EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": llm_providers.build_extraction_prompt(source_text)},
    ]
    try:
        raw = llm_providers.chat_completion(
            provider, endpoint, api_key, model, messages,
            timeout=timeout, temperature=temperature, max_tokens=max_tokens,
        )
    except Exception as exc:
        # 适配层已脱敏,这里再保险替换一次;调用失败按解析失败计
        message = str(exc).replace(api_key, "***") if api_key else str(exc)
        stats = {"parsed": 0, "dropped_invalid": 0, "dropped_fabricated_evidence": 0, "error": "call_failed"}
        return [], stats, message
    entries, stats = llm_providers.parse_extraction_output(raw, source_text)
    items = [product.NoetideApp._candidate_from_extraction(entry) for entry in entries]
    return items, stats, None


def _score(items: list[JsonObject], expectation: JsonObject) -> JsonObject:
    haystack = "\n".join(_collect_texts(items))
    facts = expectation.get("expected_facts") or []
    fragments = expectation.get("verbatim_fragments") or []
    missing_facts: list[str] = []
    for fact in facts:
        phrases = [str(p) for p in (fact.get("phrases") or [])]
        if not phrases or not all(phrase in haystack for phrase in phrases):
            missing_facts.append(str(fact.get("id") or "?"))
    missing_fragments = [frag for frag in fragments if str(frag) not in haystack]
    return {
        "expected_facts_total": len(facts),
        "facts_recalled": len(facts) - len(missing_facts),
        "fact_recall": round((len(facts) - len(missing_facts)) / len(facts), 4) if facts else None,
        "missing_facts": missing_facts,
        "verbatim_total": len(fragments),
        "verbatim_retained": len(fragments) - len(missing_fragments),
        "verbatim_retention": round((len(fragments) - len(missing_fragments)) / len(fragments), 4) if fragments else None,
        "missing_verbatim": missing_fragments,
    }


def _ratio(part: int, whole: int) -> float | None:
    return round(part / whole, 4) if whole else None


def run_eval(args: argparse.Namespace) -> JsonObject:
    expected = _load_expected()
    corpora = expected.get("corpora") or {}
    api_key = ""
    if args.mode == "cloud":
        api_key = (args.api_key or "").strip() or os.environ.get(API_KEY_ENV, "").strip()
        if not api_key:
            return {
                "schema_version": "noetide.extraction-eval-result.v1",
                "suite_id": "extraction_eval_v1",
                "run_result": "not_executed",
                "reason": f"api_key_missing:cloud 模式需 --api-key 或环境变量 {API_KEY_ENV}",
                "mode": "cloud",
                "provider": args.provider,
                "model": args.model or None,
                "api_key": "not_provided",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "git_commit": _git_commit(),
            }

    results: list[JsonObject] = []
    started = time.perf_counter()
    for path in _corpus_files():
        source_text = path.read_text(encoding="utf-8")
        expectation = corpora.get(path.name)
        if expectation is None:
            results.append({"file": path.name, "error": "expected.json 缺少该语料的期望定义"})
            continue
        t0 = time.perf_counter()
        call_error = None
        if args.mode == "offline":
            items, stats = _run_offline(source_text)
            parse_success = None  # 离线不经模型输出解析,该指标不适用
        else:
            items, stats, call_error = _run_cloud(
                source_text, args.provider, args.endpoint or "", api_key,
                args.model or "", args.timeout, args.temperature, args.max_tokens,
            )
            parse_success = 0 if (call_error or stats.get("error")) else 1
        duration_ms = round((time.perf_counter() - t0) * 1000, 1)
        entry: JsonObject = {
            "file": path.name,
            "char_count": len(source_text),
            "items_extracted": len(items),
            "parse_success": parse_success,
            "stats": stats,
            "duration_ms": duration_ms,
            **_score(items, expectation),
        }
        if call_error:
            entry["call_error"] = call_error
        results.append(entry)
    total_duration_ms = round((time.perf_counter() - started) * 1000, 1)

    scored = [r for r in results if "expected_facts_total" in r]
    facts_total = sum(r["expected_facts_total"] for r in scored)
    facts_hit = sum(r["facts_recalled"] for r in scored)
    verb_total = sum(r["verbatim_total"] for r in scored)
    verb_hit = sum(r["verbatim_retained"] for r in scored)
    parse_values = [r["parse_success"] for r in scored if r["parse_success"] is not None]
    report: JsonObject = {
        "schema_version": "noetide.extraction-eval-result.v1",
        "suite_id": "extraction_eval_v1",
        "run_result": "completed",
        "mode": args.mode,
        "provider": args.provider if args.mode == "cloud" else None,
        "model": (args.model or None) if args.mode == "cloud" else None,
        # api_key 永不落盘:只记录是否提供
        "api_key": "provided(masked)" if api_key else ("not_provided" if args.mode == "cloud" else None),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "dependencies": "stdlib_only",
        },
        # --api-key 的值(两种写法)不进入 command 记录
        "command": [
            "python", "tools/eval_extraction.py",
            *[
                ("--api-key=***" if a.startswith("--api-key=") else ("--api-key" if a == "--api-key" else a))
                for a in sys.argv[1:]
                if a != api_key
            ],
        ],
        "corpus_dir": "tests/fixtures/extraction_eval_v1",
        "corpus_count": len(results),
        "results": results,
        "aggregate": {
            "parse_success_rate": _ratio(sum(parse_values), len(parse_values)) if parse_values else None,
            "dropped_fabricated_evidence_total": sum(
                r["stats"]["dropped_fabricated_evidence"] or 0 for r in scored
            ),
            "dropped_invalid_total": sum(r["stats"]["dropped_invalid"] or 0 for r in scored),
            "fact_recall": _ratio(facts_hit, facts_total),
            "facts_recalled": f"{facts_hit}/{facts_total}",
            "verbatim_retention": _ratio(verb_hit, verb_total),
            "verbatim_retained": f"{verb_hit}/{verb_total}",
            "total_duration_ms": total_duration_ms,
        },
        "metric_definitions": {
            "parse_success": "模型输出被 parse_extraction_output 成功解析(stats.error 为空)记 1,否则 0;offline 不经解析记 null",
            "fact_recall": "期望事实的全部 phrases 出现在该语料全部提取文本(候选所有字符串字段拼接)中记为召回",
            "verbatim_retention": "期望实质片段(口诀/数字/日期)原样出现在提取文本中",
            "dropped_fabricated_evidence": "evidence_quote 未在原文逐字出现而被丢弃的候选数(offline 不产出证据,恒为 0)",
        },
        "notes": [],
    }
    if args.mode == "offline":
        report["cloud_eval"] = "not_executed"
        report["notes"].append("本次为 offline 基线;cloud 模式未执行(not_executed):未提供 api_key")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="识灵提取质量评测(固定合成语料,stdlib only)")
    parser.add_argument("--mode", choices=("offline", "cloud"), required=True)
    parser.add_argument("--provider", default="openai_compatible", help="cloud 模式的提供商预置 key 或 adapter 名")
    parser.add_argument("--endpoint", default="", help="覆盖预置 endpoint;空则用预置缺省")
    parser.add_argument("--model", default="", help="覆盖预置 model;空则用预置缺省")
    parser.add_argument("--api-key", default="", help=f"建议改用环境变量 {API_KEY_ENV},避免进 shell 历史")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--temperature", type=float, default=None, help="缺省不发送该字段(推理模型兼容)")
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument("--output", default="", help="报告 JSON 写出路径;空则只打印摘要")
    args = parser.parse_args(argv)

    report = run_eval(args)

    # 脱敏兜底:报告文本落盘/打印前,任何 api_key 出现一律替换
    api_key = (args.api_key or "").strip() or os.environ.get(API_KEY_ENV, "").strip()
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if api_key:
        text = text.replace(api_key, "***")

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8", newline="\n")
        print(f"WROTE: {output_path}")

    if report.get("run_result") == "not_executed":
        print(f"NOT_EXECUTED: {report.get('reason')}")
        return 0

    aggregate = report["aggregate"]
    for entry in report["results"]:
        if "expected_facts_total" not in entry:
            print(f"ERROR: {entry['file']}: {entry.get('error')}")
            continue
        parse_label = "n/a(offline)" if entry["parse_success"] is None else str(entry["parse_success"])
        print(
            f"RESULT: {entry['file']}: parse={parse_label} "
            f"recall={entry['facts_recalled']}/{entry['expected_facts_total']} "
            f"verbatim={entry['verbatim_retained']}/{entry['verbatim_total']} "
            f"fabricated_dropped={entry['stats']['dropped_fabricated_evidence']} "
            f"duration={entry['duration_ms']}ms"
        )
    print(
        f"SUMMARY: mode={report['mode']} corpora={report['corpus_count']} "
        f"fact_recall={aggregate['facts_recalled']} ({aggregate['fact_recall']}) "
        f"verbatim_retention={aggregate['verbatim_retained']} ({aggregate['verbatim_retention']}) "
        f"total_duration={aggregate['total_duration_ms']}ms"
    )
    if report.get("cloud_eval") == "not_executed":
        print("NOT_EXECUTED: cloud 模式(未提供 api_key,仅记录 offline 基线)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
