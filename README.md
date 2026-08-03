# Noetide 识海

本地优先的个人记忆管理软件。你把聊天记录、笔记、文件碎片放进识海，识海帮你整理成人物、项目、承诺、事件、断言等结构化记忆；所有记忆先出“候选”，你确认后才正式写入。它自带网页管理界面、REST API 和 MCP 接口，可以接本地或云端 AI 大模型。

这不是一个只能看演示的 MVP。这个版本已经能安装到 Windows、导入你自己的资料、用离线规则或大模型整理、让 Agent 通过 MCP/API 接入、导出上下文包、加密备份和远程访问。

## 它现在能做什么

- 本地安装：解压后运行安装脚本，双击启动，浏览器管理。
- 导入资料：粘贴文本，或把 `.md/.txt/.json/.csv` 文件夹一次性导入。
- 识灵分析：离线规则不需要大模型；也可以接本地模型或云端 OpenAI 兼容接口。
- 候选确认：识灵只生成候选，你在网页里确认或忽略，不会自动乱写。
- 记忆管理：人物、项目、承诺、事件、断言，带证据来源、搜索和时间线。
- Agent 接入：提供 `http://127.0.0.1:8765/mcp`，支持 `list_resources`、`read_resource`、`propose_changeset`、`record_source`。
- 导出与备份：导出上下文包，加密备份，恢复备份，导入上下文包。
- 远程访问：开启令牌后，手机、其他电脑或云端服务器可以通过 REST API 访问。

## 一分钟启动（Windows）

1. 下载并解压 `Noetide-beta-v0.3.0-win64.zip`（SHA-256 `55c26e39aca14ef3839978093d55856403ce19f6ca8e222e6543f0aecb3b80f2`）。
2. 双击 `scripts/Noetide Setup.cmd`，选一个你自己的数据文件夹。
3. 双击 `scripts/Noetide Start.cmd`。
4. 浏览器打开 `http://127.0.0.1:8765`。

从源码启动：

```powershell
python noetide_desktop.py --data-dir D:\sayhi-data
```

或安装 Python 包后：

```powershell
noetide-product --data-dir D:\sayhi-data
```

## 第一次使用

1. 打开“导入”，粘贴一段聊天记录或笔记，点“保存资料”；也可以填文件夹路径，点“导入文件夹”。
2. 打开“识灵分析”，勾选资料，点“运行识灵分析”。
3. 在候选列表里确认你认可的记忆，忽略不想要的。
4. 打开“记忆”查看资料、已确认记忆和时间线；打开“搜索”找内容。

更详细的大白话操作说明见 [用户指南](docs/product/PRODUCT_USER_GUIDE.md)。

## 识灵怎么分析

- 离线规则：默认模式，不联网、不需要大模型，用本地规则提取人物/项目/承诺/事件/断言。
- 本地模型：填本地 OpenAI 兼容地址，例如 `http://127.0.0.1:11434/v1/chat/completions`。
- 云端模型：填 `https://.../v1/chat/completions` 和 API Key。
- 模型只做“候选生成”，不会自动确认；确认动作始终由你或你授权的 Agent 发起。

## Agent / MCP 怎么接入

在网页“Agent 接入”页复制 MCP 地址和访问令牌，然后让 Agent 向 `/mcp` 发 JSON-RPC 格式请求。默认授权包含：

- `list_resources`：列出资料
- `read_resource`：读取资料
- `propose_changeset`：写入待确认候选
- `record_source`：追加资料

请求包外层格式示例（用户指南里有完整示例）：

```json
{"jsonrpc":"2.0","id":"1","method":"noetide.mcp","params":{"request":{...},"payload":{...}}}
```

## 远程访问

默认只监听 `127.0.0.1`，只有本机能用。要远程/手机访问：

1. 打开“设置”，把“远程访问”设为“开启令牌访问”。
2. 填 `0.0.0.0` 和端口，保存后重启服务。
3. 在“Agent 接入”复制令牌。
4. 手机或其他电脑请求 `/api/...` 或 `/mcp` 时带 `Authorization: Bearer <token>`。

## 数据与隐私

- 数据默认只存在你选择的数据文件夹；不开启远程访问时，服务只在本机监听。
- 可以导入你自己的真实资料；是否把资料发给云端模型由你设置决定。
- 导出上下文包、加密备份都从网页“导出备份”页操作。
- 卸载默认不删数据；删除数据前会先做校验备份。

## 测试状态

当前工作区已完成产品级验证：

- 产品定向测试：5/5 OK（空库初始化、导入、分析、确认、导出、备份、搜索、API、设置、MCP、自定义 Agent 授权）。
- 全量 configured-adapter 语义回归：485 OK、0 skipped（2026-08-03）。
- 端到端验证：启动空库、导入文本、识灵分析、API overview、桌面/移动 Web UI 截图均通过。

## 当前边界

- Windows 桌面优先；未代码签名，Windows SmartScreen 可能提示，这是预期现象。
- 无自动更新；升级包脚本会先备份数据。
- MCP 当前是完整产品所需的本地/远程 HTTP 接口，不含 A2A、多租户账户体系或连接器。
- 云端部署可以把本服务放到有公网地址的服务器并开启令牌，但多用户账户、HTTPS 网关、域名和运维由部署者负责。

## 更多文档

- 大白话用户指南：`docs/product/PRODUCT_USER_GUIDE.md`
- 项目状态：`docs/PROJECT_STATE.md`
- 当前交接：`docs/process/CURRENT_HANDOFF.md`
- License：`LICENSE`
