# 识海 sayhi

**一个能为自己的记忆出庭作证的个人记忆系统。**
**A personal memory system that can testify for what it remembers.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Runtime deps: 0](https://img.shields.io/badge/runtime%20dependencies-0-brightgreen.svg)](pyproject.toml)
[![Tests: 530 passed / 0 skipped](https://img.shields.io/badge/tests-530%20passed%20%2F%200%20skipped-brightgreen.svg)](docs/PROJECT_STATE.md)
[![Suites: 26 hash-bound](https://img.shields.io/badge/verification%20suites-26%20hash--bound-brightgreen.svg)](docs/testing/README.md)
[![Platform: Win/mac/Linux](https://img.shields.io/badge/platform-Windows%20%C2%B7%20macOS%20%C2%B7%20Linux-lightgrey.svg)](dist/)

---

## 名字的故事

修仙小说里,主角的**识海**是意识之海:记忆、神识、感悟都沉在那片海里,外人不得而入,主角一念之间便可探取。那是他身上唯一绝对属于他、绝对受他掌控的东西。

每个人的记忆也该有这样一片海。

**sayhi**,谐音"识海"——也是对你的世界,说一声 hi。

## 为什么世界还需要一个"知识库"?

不需要。所以识海不是知识库。

- **Obsidian / Notion / Logseq** 是**仓库**:你写进去什么,它就存什么。它不关心真假。
- **"跟你的数据聊天"类 RAG 工具**是**黑箱**:它给你答案,但答案从哪来、是事实还是模型现编的,你无法追问。
- **各种 AI 笔记/第二大脑**是**速写员**:模型读完就替你"总结入库",幻觉和你的真话从此混为一谈,再也分不开。

识海做的是另一件事:**管理记忆的真实性**。

在识海里,每一条记忆都不是一句话,而是一份**带证据链的档案**。你导入的聊天记录原文(Source)、从中学到的事实(Fact)、你的观点(Opinion)、系统的推断(Inference)、对未来的预测(Prediction)、虚构创作(Fiction)——六种东西永远分开存放,永不混淆。任何一条记忆,你都能一层层追回去:**它是谁说的、出自哪份原始资料、什么时候进入系统、经过谁的确认。**

## 三条铁律

**1. AI 只提议,不写入。**
识灵(本地规则 / 本地大模型 / 云端模型,任选)读完你的资料后,只生成"候选记忆"。候选躺在待审区,你点头才入库,你忽略就消失。Agent 通过 MCP 接入时也一样——`propose_changeset` 是它唯一能碰写入口径的工具,直接写库的通道根本不存在。

**2. 当下不覆盖历史。**
识海是双时态的:今天的你会覆盖昨天的事实吗?不会——今天的认知只是新的一层。改口、矛盾、合并、拆分,全部留痕可查。Current State 永不覆盖 Historical State,Hypothesis 永不自动升级为 Fact。

**3. 推论永远成不了证据。**
系统计算出的任何"派生视图"(时间线、摘要、到期状态)都标注为 Derived,永远不能反过来充当事实的证据。投影过期了会明确告诉你"这是旧数据",绝不假装新鲜。

这三条不是产品文案,是写进存储层、被测试钉死的合同。

## 红线舱室:有些东西,永不出本机

健康、财务、亲密关系——这些 compartment 被标注为红线。识海的云端模型调用要连过三门才出得去:

1. **红线门**:红线舱室的内容直接拒绝,连授权记录都不留;
2. **授权门**:每一次外发都需要一个你显式签发的、有范围、有过期时间的 grant;
3. **预览门**:外发前先生成摘要留痕,发没发、发了什么,全量审计台账可查。

本地模式强制回环地址,连内网其他机器都指不过去。默认状态:零网络出口。

## 零依赖,真本地

- **纯 Python 标准库 + SQLite**。没有 pip install,没有 Docker,没有云服务,没有遥测。
- Windows portable 包自带运行时:解压 → 双击 → 浏览器打开 `127.0.0.1:8765`,完事;macOS/Linux 用源码启动包,两个脚本跑完同样的流程。
- 你的数据就是一个 SQLite 文件加几个导出包,在你自己的文件夹里。卸载默认不删数据。

## 它现在能做什么

- **导入**:粘贴文本,或整个文件夹的 `.md/.txt/.json/.csv/.docx` 一次导入(含文件夹监视)。
- **识灵分析**:离线规则(不联网)、本地模型(Ollama 等 OpenAI 兼容接口)、云端官方 API——内置 **OpenAI / Anthropic Claude / Google Gemini / DeepSeek / Moonshot(Kimi)/ 智谱 / 通义千问** 预置,任何 OpenAI 兼容服务选 `custom` 即可接入;云端调用全部经授权/红线/预览三门。多份资料并行提取,进度实时可见。
- **结构化提取**:模型输出必须是带原文证据引用的 JSON;**编造证据的候选会被自动丢弃并计数**,诚实透出在分析结果里。附[提取质量评测工具](tools/eval_extraction.py),可重复、可对比。
- **候选确认**:网页里逐条确认/忽略,相似候选自动合并成组、一键处理;模型永远没有自动入库的手。
- **问识海**:对着你的记忆提问。只根据已确认、带证据的记忆作答;没有证据就明确回答"我不知道"——不编造是它的设计,不是缺陷。召回可选**本地向量**(仅本地模型,记忆文本不出本机),回答前仍逐条过证据核对器。
- **记忆管理**:人物、项目、承诺、事件、断言——带证据来源、搜索、时间线,桌面和移动端自适应。
- **Agent 接入**:标准 MCP 协议(经官方 TypeScript/Python SDK 真实客户端验证)+ REST API,令牌鉴权;网页上一键签发限定范围的 Agent 授权。
- **导出与备份**:Context Pack 导出/导入(往返一致)、NOBAK2 加密备份(PBKDF2 + HMAC)、恢复前校验。
- **远程访问**:默认只听回环;显式开启令牌后才可远程,未配置令牌时服务拒绝绑定公网地址。

## 一分钟启动

**Windows**:

1. 到 [Releases](https://github.com/iqvpi1024/sayhi/releases) 下载最新版 `sayhi-beta-v0.3.5-win64.zip` 并解压(校验值见同页的 `SHA256SUMS`)。
2. 双击 `scripts/sayhi Setup.cmd`,选一个你自己的数据文件夹。
3. 双击 `scripts/sayhi Start.cmd`。
4. 浏览器打开 `http://127.0.0.1:8765`。

**macOS / Linux**(需要 Python 3.12+):

```bash
tar xzf sayhi-0.3.5-src.tar.gz && cd sayhi-0.3.5-src
scripts/portable/setup-noetide.sh    # 选数据目录并初始化
scripts/portable/start-noetide.sh    # 启动,浏览器打开 http://127.0.0.1:8765
```

从源码启动(任何平台,只需要 Python 3.12+,什么都不用装):

```bash
python noetide_desktop.py --data-dir ./my-data
```

更详细的大白话操作说明见 [用户指南](docs/product/PRODUCT_USER_GUIDE.md)。

## 把识海接进你的 Agent(Claude Code / Codex / 任何 MCP 客户端)

识海不抢你的主力工具——它站在后面,做**所有 Agent 共用的记忆中枢**。你换多少个 Agent,记忆都在你自己机器上,不锁死在任何一家厂商手里。

启动识海后,MCP 地址就是 `http://127.0.0.1:8765/mcp`(标准 MCP 协议,HTTP 传输)。以 Claude Code 为例:

```bash
claude mcp add --transport http sayhi http://127.0.0.1:8765/mcp
```

其他 Agent(Codex、Cursor 或任何支持 MCP 的客户端)同理:把 `/mcp` 地址配为 HTTP MCP server 即可。协议兼容性用官方 TypeScript SDK 与 Python SDK 真实客户端双向验证过,不是"理论上支持"。接好后你的 Agent 可以:

- `ask_memory` —— 用自然语言问你的记忆:"我最近在忙什么?""小米是哪年创立的?"只根据**你已确认的记忆**作答,逐条附原文证据;没有证据就诚实回答不知道,绝不编造。
- `propose_changeset` —— 对话中发现关于你的新事实时,提议一条记忆候选;**提议进你的网页候选队列,你点确认才生效**——Agent 永远没有自行入库的手。
- `read_resource` / `list_resources` / `record_source` —— 读授权范围内的原始资料、追加新资料。

安全边界照旧:每个 Agent 只拿得到你签发的**能力令牌**(网页 Agent 页勾选资料一键生成,Agent 端用 `X-Noetide-Capability` 请求头指定);红线舱室(病历、财务等)对 Agent 永远不可见;不可逆操作(确认、删除、导出)在 MCP 层硬性禁用。

## 凭什么相信它?——证据链工程

这是识海和"vibe coding"产物的根本区别。

识海的每一个功能切片,交付时都走完整条门禁链:**产品决策 → 合同 SPEC → 可执行测试(固定 fixture + oracle)→ 实现 → 官方 runner 出结果 → 门禁复审 → Git recovery tag**。测试结果文件与测试资产之间用 SHA-256 双向哈希绑定——改过任何一行测试,绑定立刻断裂,谁都能发现。

今天的状态,任何人都可以独立复核:

- **530 项语义回归,0 跳过**,全绿;
- **26 个验证套件**,每个的 fixture、oracle、结果文件哈希绑定可逐字节重算;
- **PRD 基线哈希链**:v04 → v05 → v06 三代产品需求文档逐字锚定,历史版本永久只读;
- **49 个 git tag**,每个 recovery tag 都指向一组可复现的验证记录;
- 零真实个人数据进入仓库(770 个跟踪文件 + 全部历史经扫描复核)。

我们不说"相信我"。我们说:**去查,证据都在。**

## 诚实的边界

- Windows 便携包未代码签名(SmartScreen 会提示,预期现象),暂无自动更新;macOS/Linux 目前是源码启动包(系统需 Python 3.12+),尚未在真实 mac/linux 机器上实测。
- 备份加密是 stdlib 约束下的自研构造(PBKDF2 20 万轮 + HMAC-SHA256),诚实声明:**非生产级密码学**,请用高强度密钥。
- 单用户设计:没有多租户、账户体系、A2A、托管云。远程访问 = 你自己的服务器 + 令牌,HTTPS 网关你自己负责。
- MCP 当前是只读 + 提议式写入的最小子集,不含 controlled mutate;不支持 SSE 独立流与会话(无会话实现)。
- 向量召回只在本地模型模式可用;云端模式下记忆文本永不离开本机,召回退化为字面匹配。

## sayhi in English

**sayhi (识海, "sea of consciousness")** is a **local-first, zero-dependency personal memory system** — pure Python stdlib + SQLite, with a local web UI, REST API, and a standard MCP endpoint. The name is a pun: *say hi* sounds like 识海 (shí hǎi), the "sea of consciousness" that protagonists in Chinese fantasy novels carry inside themselves — the one place that is absolutely theirs. Your memories deserve the same sovereignty.

**The memory layer for all your agents.** Claude Code, Codex, Cursor — any MCP-compatible agent plugs into sayhi and shares one memory base that lives on *your* machine. Switch agents as often as you like; your memory doesn't move. One line for Claude Code:

```bash
claude mcp add --transport http sayhi http://127.0.0.1:8765/mcp
```

**What makes it different from note apps and "chat with your data" tools is epistemic discipline:**

- **AI proposes, never writes.** Extraction (offline rules, local LLM via Ollama, or gated cloud APIs — OpenAI/Anthropic/Gemini/DeepSeek/Kimi and more) produces *candidates* with verbatim evidence quotes. Fabricated evidence is auto-dropped and counted. Nothing enters memory until you click confirm — not from the model, and not from any agent (irreversible MCP tools are hard-disabled).
- **It says "I don't know".** Ask it anything: answers are built only from confirmed memories, verified one by one against original sources. No evidence → an honest "no coverage", with reasons. Hallucination isn't discouraged; it's architecturally impossible.
- **Red-line compartments.** Health, finance, intimacy — marked content is invisible to agents and can never leave the machine. Every cloud call passes red-line + grant + preview gates with a full audit ledger.
- **History is never overwritten.** Bitemporal storage: corrections, contradictions and reversals are all preserved. Derived views can never become evidence.

**Evidence-chain engineering.** Every slice ships with hash-bound fixtures, oracles and runner outputs: 530 green regression tests (0 skipped), 26 verification suites, a hash-chained PRD lineage, 49 recovery tags. The MCP layer was verified against the official TypeScript and Python SDKs — not just "should work". Don't trust it — audit it.

**Honest limits:** single-user; unsigned Windows package (macOS/Linux via source tarball, Python 3.12+); backup crypto is a stdlib-only construction (PBKDF2 200k rounds + HMAC-SHA256), not production-grade; MCP is read + propose-only, no SSE sessions; vector recall is local-model only.

## 更多

- 大白话用户指南:[docs/product/PRODUCT_USER_GUIDE.md](docs/product/PRODUCT_USER_GUIDE.md)
- 项目状态与全部验证记录:[docs/PROJECT_STATE.md](docs/PROJECT_STATE.md)
- 独立安全审核报告:[项目全面审核报告-2026-08-07.md](项目全面审核报告-2026-08-07.md)
- License:[MIT](LICENSE)

如果"记忆应该带证据链"这件事说到了你心里,点个 Star——这是一个人用严格工程纪律打磨出来的作品,你的 Star 是它继续生长的证据。
