"""LLM 提供商适配层:统一 chat_completion 接口、提供商预置表与结构化提取解析。

仅使用标准库。安全不变量:
- api_key 永不进入异常信息(统一经 _scrub 脱敏),调用方保证不进日志/审计 payload;
- 本模块不做 scheme 门禁:cloud 强制 https、local 强制 loopback 由 product.py
  `_model_items` 在发送前完成,云端发送仍先过 `_cloud_authorize` 三门。
"""

from __future__ import annotations

import json
import re
import urllib.request
from typing import Any, Mapping

JsonObject = dict[str, Any]

ADAPTER_KINDS = ("openai_compatible", "anthropic", "gemini")

# 提供商预置表:webui 下拉与 product.py 缺省 endpoint/model 的唯一来源。
# adapter 取值限 ADAPTER_KINDS;gemini endpoint 中的 {model} 在发送前替换为实际模型名。
PROVIDER_PRESETS: dict[str, JsonObject] = {
    "openai": {
        "label": "OpenAI",
        "adapter": "openai_compatible",
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "model": "gpt-4o-mini",
    },
    "anthropic": {
        "label": "Anthropic",
        "adapter": "anthropic",
        "endpoint": "https://api.anthropic.com/v1/messages",
        "model": "claude-3-5-sonnet-20241022",
    },
    "gemini": {
        "label": "Gemini",
        "adapter": "gemini",
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        "model": "gemini-2.0-flash",
    },
    "deepseek": {
        "label": "DeepSeek",
        "adapter": "openai_compatible",
        "endpoint": "https://api.deepseek.com/v1/chat/completions",
        "model": "deepseek-chat",
    },
    "moonshot": {
        "label": "Moonshot/Kimi",
        "adapter": "openai_compatible",
        "endpoint": "https://api.moonshot.cn/v1/chat/completions",
        "model": "moonshot-v1-8k",
    },
    "zhipu": {
        "label": "智谱",
        "adapter": "openai_compatible",
        "endpoint": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "model": "glm-4-flash",
    },
    "qwen": {
        "label": "通义",
        "adapter": "openai_compatible",
        "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "model": "qwen-turbo",
    },
    "ollama_remote": {
        "label": "Ollama 远程",
        "adapter": "openai_compatible",
        "endpoint": "http://127.0.0.1:11434/v1/chat/completions",
        "model": "qwen2.5:7b",
    },
    "custom": {
        "label": "自定义",
        "adapter": "openai_compatible",
        "endpoint": "",
        "model": "",
    },
}


class ProviderCallError(RuntimeError):
    """提供商调用失败;message 保证不含 api_key。"""


def resolve_provider(provider: str | None) -> JsonObject:
    """把设置值(预置 key 或 adapter 名)归一为 {adapter, endpoint, model} 缺省表。"""
    key = str(provider or "").strip()
    preset = PROVIDER_PRESETS.get(key)
    if preset is not None:
        return dict(preset)
    if key in ADAPTER_KINDS:
        return {"label": key, "adapter": key, "endpoint": "", "model": ""}
    # 未知值 fail-closed 到 openai_compatible 且无默认端点,由调用方报 endpoint 缺失
    return {"label": "custom", "adapter": "openai_compatible", "endpoint": "", "model": ""}


def default_endpoint(provider: str | None) -> str:
    return str(resolve_provider(provider).get("endpoint") or "")


def default_model(provider: str | None) -> str:
    return str(resolve_provider(provider).get("model") or "")


def _scrub(message: str, api_key: str) -> str:
    """异常信息脱敏:任何情况下都不把 api_key 泄漏进错误文本。"""
    if api_key:
        message = message.replace(api_key, "***")
    return message


def _post_json(url: str, headers: Mapping[str, str], body: JsonObject, timeout: float) -> JsonObject:
    request = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", **dict(headers)},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _openai_compatible_call(endpoint: str, api_key: str, model: str, messages: list[JsonObject], timeout: float) -> str:
    headers: JsonObject = {}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    body = {"model": model, "messages": messages, "temperature": 0, "max_tokens": 1024}
    payload = _post_json(endpoint, headers, body, timeout)
    try:
        return str(payload["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderCallError("unexpected_response_shape") from exc


def _anthropic_call(endpoint: str, api_key: str, model: str, messages: list[JsonObject], timeout: float) -> str:
    headers: JsonObject = {"anthropic-version": "2023-06-01"}
    if api_key:
        headers["x-api-key"] = api_key
    # Anthropic 协议:system 是顶层字段,messages 里不允许 system 角色
    system_text = "\n".join(str(m.get("content") or "") for m in messages if m.get("role") == "system")
    chat_messages = [
        {"role": str(m.get("role")), "content": str(m.get("content") or "")}
        for m in messages
        if m.get("role") in ("user", "assistant")
    ]
    body: JsonObject = {"model": model, "max_tokens": 1024, "messages": chat_messages}
    if system_text:
        body["system"] = system_text
    payload = _post_json(endpoint, headers, body, timeout)
    try:
        return str(payload["content"][0]["text"])
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderCallError("unexpected_response_shape") from exc


def _gemini_call(endpoint: str, api_key: str, model: str, messages: list[JsonObject], timeout: float) -> str:
    url = endpoint.replace("{model}", model) if "{model}" in endpoint else endpoint
    headers: JsonObject = {}
    if api_key:
        headers["x-goog-api-key"] = api_key
    system_text = "\n".join(str(m.get("content") or "") for m in messages if m.get("role") == "system")
    contents = [
        {"role": "model" if m.get("role") == "assistant" else "user", "parts": [{"text": str(m.get("content") or "")}]}
        for m in messages
        if m.get("role") in ("user", "assistant")
    ]
    body: JsonObject = {
        "contents": contents,
        "generationConfig": {"temperature": 0, "maxOutputTokens": 1024},
    }
    if system_text:
        body["system_instruction"] = {"parts": [{"text": system_text}]}
    payload = _post_json(url, headers, body, timeout)
    try:
        return str(payload["candidates"][0]["content"]["parts"][0]["text"])
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderCallError("unexpected_response_shape") from exc


def chat_completion(
    provider: str | None,
    endpoint: str | None,
    api_key: str | None,
    model: str | None,
    messages: list[JsonObject],
    timeout: float = 15.0,
) -> str:
    """统一入口:按 provider 分发到对应适配器,返回模型文本。

    endpoint/model 为空时回落到预置表缺省值;所有异常收敛为 ProviderCallError
    且 message 经 _scrub 脱敏(不含 api_key)。
    """
    preset = resolve_provider(provider)
    resolved_endpoint = str(endpoint or "").strip() or str(preset.get("endpoint") or "")
    if not resolved_endpoint:
        raise ProviderCallError("endpoint_missing")
    resolved_model = str(model or "").strip() or str(preset.get("model") or "") or "noetide-shiling"
    key = str(api_key or "").strip()
    adapter = str(preset.get("adapter") or "openai_compatible")
    try:
        if adapter == "anthropic":
            return _anthropic_call(resolved_endpoint, key, resolved_model, messages, timeout)
        if adapter == "gemini":
            return _gemini_call(resolved_endpoint, key, resolved_model, messages, timeout)
        return _openai_compatible_call(resolved_endpoint, key, resolved_model, messages, timeout)
    except ProviderCallError as exc:
        raise ProviderCallError(_scrub(str(exc), key)) from exc
    except Exception as exc:
        raise ProviderCallError(_scrub(str(exc), key)) from exc


# -- 结构化提取 prompt 与解析器 ------------------------------------------------

EXTRACTION_OBJECT_TYPES = ("entity", "project", "commitment", "event", "assertion")
MAX_EXTRACTION_ITEMS = 40

EXTRACTION_SYSTEM_PROMPT = (
    "你是识海识灵,一个保守的个人记忆整理助手。"
    "只输出 JSON,不要输出任何解释、问候或 Markdown 文字。"
    "不得编造原文没有的事实;每条候选必须带 evidence_quote,"
    "且 evidence_quote 必须是原文中逐字出现的片段。"
)


def build_extraction_prompt(source_text: str) -> str:
    """模型模式的用户提示:要求输出 JSON 数组候选,逐条带原文证据引用。"""
    return (
        "请从以下材料中提取少量可审核候选,只输出一个 JSON 数组。\n"
        '每个元素格式:{"object_type":"entity|project|commitment|event|assertion",'
        '"label":"人名/项目名/短语","summary":"一句话说明","evidence_quote":"原文逐字引用"}\n'
        "规则:object_type 只能是白名单值;evidence_quote 必须在原文中逐字出现;"
        "不得编造原文没有的事实;没有可提取内容时输出 []。\n"
        "材料:\n" + source_text
    )


def _json_candidates(text: str) -> list[str]:
    """容错候选:原文、首个 [ 到末个 ]、首个 { 到末个 },依次尝试。"""
    candidates = [text]
    left, right = text.find("["), text.rfind("]")
    if 0 <= left < right:
        candidates.append(text[left : right + 1])
    left, right = text.find("{"), text.rfind("}")
    if 0 <= left < right:
        candidates.append(text[left : right + 1])
    return candidates


def parse_extraction_output(raw: str, source_text: str) -> tuple[list[JsonObject], JsonObject]:
    """解析模型提取输出,fail-closed:任何解析失败都返回空列表 + 诚实 stats,不抛异常。

    容忍 ```json 围栏与前后杂文本;逐条校验 object_type 白名单,且
    evidence_quote 必须在 source_text 中真实出现(子串匹配)——编造证据的
    候选直接丢弃并计入 stats["dropped_fabricated_evidence"]。
    """
    stats: JsonObject = {"parsed": 0, "dropped_invalid": 0, "dropped_fabricated_evidence": 0, "error": None}
    text = str(raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```\s*$", "", text)
    parsed_obj: Any = None
    for candidate in _json_candidates(text):
        try:
            parsed_obj = json.loads(candidate)
            break
        except ValueError:
            continue
    if parsed_obj is None:
        stats["error"] = "invalid_json"
        return [], stats
    items = parsed_obj.get("candidates") if isinstance(parsed_obj, dict) else parsed_obj
    if not isinstance(items, list):
        stats["error"] = "invalid_shape"
        return [], stats
    entries: list[JsonObject] = []
    for item in items:
        if len(entries) >= MAX_EXTRACTION_ITEMS:
            break
        if not isinstance(item, dict):
            stats["dropped_invalid"] += 1
            continue
        object_type = item.get("object_type")
        label = str(item.get("label") or "").strip()
        summary = str(item.get("summary") or "").strip()
        quote = item.get("evidence_quote")
        if object_type not in EXTRACTION_OBJECT_TYPES or not (label or summary):
            stats["dropped_invalid"] += 1
            continue
        if not isinstance(quote, str) or not quote.strip():
            stats["dropped_invalid"] += 1
            continue
        if quote not in source_text:
            # 模型编造了原文中不存在的证据引用:该候选不可信,直接丢弃并计数
            stats["dropped_fabricated_evidence"] += 1
            continue
        entries.append({"object_type": object_type, "label": label, "summary": summary, "evidence_quote": quote})
    stats["parsed"] = len(entries)
    return entries, stats
