# MVP-B Multilingual 原文与翻译对照切片产品决定

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-MVP-B-MULTILINGUAL-001` |
| Date | 2026-07-25 |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Previous Slice | `SLICE-MVP-B-RECONCILIATION-001`（已 verified，recovery tag `b4-reconciliation-rp-20260725`） |
| Current Slice | `SLICE-MVP-B-MULTILINGUAL-001` |

## 1. 决定内容

选择 MVP-B 的 B5 Multilingual 原文与翻译对照作为下一条窄切片，在一个固定合成 profile 上验证多语言 Source 的原文/翻译分离存储与对照读取：

1. 原文与翻译分离存储（FR-108、PRD §21.5）：原文进入 Source Vault 并携带 content hash；翻译作为独立的派生对照记录单独存储，通过 source_ref 关联。
2. 对照读取（FR-108）：同一 Source 的原文与翻译可以并排读取；翻译显式标记为非证据文本。
3. 证据完整性（PRD §21.5）：Evidence Ref 永远解析到原文；任何用翻译覆盖原文的写入被拒绝；翻译修订保留历史且不触碰原文。

## 2. 产品依据

- PRD §20.2 FR-108：多语言原文与翻译对照（P1）。
- PRD §21.5（962 行）：原文和翻译分离，翻译不能覆盖证据原文。
- PRD §8/§21.4：Source Vault 为唯一原始材料边界；软件停止后原始材料仍可独立读取。

## 3. 切片范围

- 单一固定合成 profile `b5_multilingual_v1`：合成原文（合成语言 A）+ 合成翻译（合成语言 B），均为显式合成文本。
- 原文经既有 Source Vault 追加路径存储（append receipt + content hash）；翻译作为独立对照记录存储，不进入 Evidence Ref 解析链。
- 对照读取为 Derived 只读：返回原文 + 翻译的并排视图；缺失翻译显式报告 `translation_unavailable`，不得把原文冒充翻译。
- 翻译修订产生新的翻译 revision 并保留全部历史；原文与 content hash 不变。
- 拒绝任何以翻译覆盖原文的写入尝试（fail closed）。

## 4. 非目标

- 真实翻译引擎、机器翻译、语言检测、LLM。
- 全语言覆盖、多翻译并存策略、翻译质量评分。
- 真实个人数据、连接器、多设备同步。
- 翻译的导出格式扩展（复用既有 Context Pack，本切片不扩展导出合同）。

## 5. 不变量

- 原文与 content hash 不因任何翻译操作改变。
- Evidence Ref 永远解析到原文；翻译不得成为 Evidence Ref、Assertion input 或 ChangeSet trigger。
- 翻译对照视图是 Derived；不反向成为事实证据。
- 翻译修订保留全部历史；Current 不覆盖 Historical。
- 固定 synthetic profile 外输入 fail closed 且无写入。

## 6. 授权与下一步

本决定只授权 S1/S2/S6/S7 的 B5 applicability review、追踪和测试合同设计。完成这些开发前产物前不得编写 B5 业务代码。
