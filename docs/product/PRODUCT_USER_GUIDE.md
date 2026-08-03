# 识海 Noetide 用户指南（大白话版）

## 这是什么东西

识海是一个装在你电脑上的“个人记忆整理软件”。它不像聊天软件，也不像网盘；它做的是把碎片资料变成可以搜索、可核对来源的结构化记忆。

你可以这样理解：

- “资料”是你的原始碎片，比如聊天记录、便签、会议纪要、文件夹里的文本。
- “识灵”是整理员，负责从资料里提出候选记忆。
- “候选”是整理员提出来、但还没写进正式记忆的东西。
- “记忆”是你确认后正式保存下来的人物、项目、承诺、事件、断言。

关键原则是：识灵只提候选，不自动覆盖你的正式记忆。你确认了才写进去。

## 安装和启动

Windows 下推荐用便携包：

1. 下载并解压 `Noetide-beta-v0.2.0-win64.zip`（或本轮构建的新包）。
2. 双击 `scripts/Noetide Setup.cmd`。
3. 第一次会问你数据文件夹放在哪，选一个你认识、能随时找到的文件夹。
4. 双击 `scripts/Noetide Start.cmd`。
5. 浏览器打开 `http://127.0.0.1:8765`。

如果你在源码目录里运行，也可以：

```powershell
python noetide_desktop.py --data-dir D:\sayhi-data
```

启动后窗口里会打印“识海已启动”和网页地址。不要把命令行关掉，服务才会一直开着。

## 每个页面是干什么的

- 总览：看当前有多少资料、多少已确认记忆、多少待确认候选。
- 导入：粘贴文本，或导入一个文件夹里的 `.md/.txt/.json/.csv`。
- 识灵分析：选择资料，让识灵生成候选记忆。
- 记忆：分三个标签看“资料”“记忆”“时间线”。
- 搜索：按人物、项目、关键词找资料和记忆。
- Agent 接入：看 Web 地址、MCP 地址、访问令牌，创建 Agent 授权。
- 导出备份：导出上下文包、创建加密备份、导入包、恢复备份。
- 设置：配置识灵用离线规则、本地模型还是云端模型，以及远程访问。

## 第一次使用，走一遍完整流程

下面用一段模拟聊天记录举例（不是真实个人信息）：

```text
今天和小王聊了“识海项目”。我答应下周给他一份完整方案。下周三是演示日。
```

操作步骤：

1. 打开“导入”，把上面这段文字粘贴到输入框，点“保存资料”。
2. 打开“识灵分析”，会看到刚才的资料。勾选它，点“运行识灵分析”。
3. 分析完成后，候选列表里会出现“小王”这类人物、“识海项目”这类项目，以及“我答应下周给他一份完整方案”这类承诺。
4. 对每一条候选，点“确认”就写进正式记忆，点“忽略”就不保存。
5. 打开“记忆”里的“时间线”，可以看到资料和已确认记忆。

## 怎么导入一大堆文件

1. 把文件整理到一个文件夹里。
2. 打开“导入”，在“导入文件夹”输入完整路径，例如 `D:\notes`。
3. 点“导入文件夹”。
4. 识海只处理 `.md`、`.txt`、`.json`、`.csv`，其他文件会跳过，并在结果里列出跳过原因。

重复内容会自动识别为“duplicate”，不会重复保存。

## 识灵分析：三种模式

识灵有两种能力来源：本地规则和大模型。

### 离线规则（默认）

不需要联网，不需要 API Key，也不调用任何大模型。它用本地规则从中文文本里提取人物、项目、承诺、事件、断言。适合先测试、先整理不敏感资料。

### 本地模型

如果你在本机装了支持 OpenAI 兼容接口的模型服务（例如 Ollama），可以这样配：

- 模式：本地模型
- 接口地址：`http://127.0.0.1:11434/v1/chat/completions`
- 模型名：你本地模型的名字
- API Key：一般可留空

识灵会把每份资料发给本地模型，要求它只返回结构化候选 JSON。

### 云端模型

如果要用云端 OpenAI 兼容接口：

- 模式：云端模型
- 接口地址：`https://.../v1/chat/completions`
- 模型名：模型名称
- API Key：服务商提供的 Key

云端模式会把资料发送到你填写的模型服务。资料会不会出电脑，由你的设置决定。默认离线模式不会外发。

## Agent 怎么接入

识海提供 REST API 和 MCP 两种接入方式。

### 1. 先在网页里拿到地址和令牌

打开“Agent 接入”页面：

- Web 地址：`http://127.0.0.1:8765`
- MCP 地址：`http://127.0.0.1:8765/mcp`
- 访问令牌：每次启动都会生成，也可以点“重新生成”

### 2. 创建默认授权

在“Agent 接入”页面点“创建默认 MCP 授权”。它会生成一个 `cap_product_default` 授权，允许读取现有资料、提出候选、追加资料。

如果 Agent 要写入一个新的 `src_...` 来源，可以先在“自定义授权”输入这个来源 ID，点“创建”。也可以用 API 创建：

```bash
curl -X POST http://127.0.0.1:8765/api/mcp/capability \
  -H "Content-Type: application/json" \
  -d '{"resource_ids":["src_agent_inbox_001"]}'
```

### 3. Agent 向 /mcp 发请求

外层是 JSON-RPC 2.0 格式，内层 `params.request` 是识海 MCP 请求：

```json
{
  "jsonrpc": "2.0",
  "id": "req-001",
  "method": "noetide.mcp",
  "params": {
    "request": {
      "contract_version": "y2s5-mcp-runtime-v1",
      "request_id": "req-001",
      "caller_ref": "local_user",
      "purpose": "personal_memory_read_and_propose",
      "capability_ref": "cap_product_default",
      "scope": {"resource_ids": ["src_p_abc"]},
      "requested_at": "2026-08-03T00:00:00+00:00",
      "action": "read_resource"
    },
    "payload": {
      "resource_id": "src_p_abc",
      "fields": ["metadata", "content"]
    }
  }
}
```

远程访问时加请求头：

```text
Authorization: Bearer <访问令牌>
```

支持的 MCP 动作：

- `list_resources`：列出授权范围内的资料。
- `read_resource`：读取资料内容或元数据。
- `propose_changeset`：把 Agent 整理的候选写入待确认队列。
- `record_source`：把 Agent 对话记录追加为新资料。

如果 Agent 只想简单地把一段对话保存进识海，也可以直接调用 REST 接口：

```bash
curl -X POST http://127.0.0.1:8765/api/ingest/text \
  -H "Content-Type: application/json" \
  -d '{"title":"Agent 对话","content":"这是模拟对话内容"}'
```

## 常用 REST 接口

- `GET /api/health`：服务是否活着
- `GET /api/overview`：总览数据
- `GET /api/sources`：资料列表
- `POST /api/ingest/text`：保存文本
- `POST /api/ingest/folder`：导入文件夹
- `POST /api/analyze`：运行识灵分析
- `GET /api/candidates`：候选列表
- `POST /api/candidates/<id>/confirm`：确认候选
- `POST /api/candidates/<id>/reject`：忽略候选
- `GET /api/objects`：正式记忆
- `GET /api/search?q=关键词`：搜索
- `GET /api/timeline`：时间线
- `POST /api/export`：导出上下文包
- `POST /api/backup`：创建加密备份
- `POST /api/import`：导入上下文包
- `POST /api/restore`：恢复备份

## 导出、备份、恢复

- 导出上下文包：把当前资料和记忆导出成可读 Markdown + JSON 包，方便迁移或查看。
- 创建本地备份：生成加密的 `.nobak` 备份文件。备份密钥会自动存在本地设置里。
- 恢复备份：在“导出备份”页填备份路径和密钥，恢复到新数据库文件。恢复不会覆盖当前数据库。
- 导入上下文包：把以前导出的包再导入到当前识海。

备份路径示例：

```text
D:\sayhi-data\backups\noetide_20260803_120000.nobak
```

## 远程访问：手机、其他电脑、云服务器

默认情况下识海只服务本机，这是安全设计。要远程访问：

1. 打开“设置”。
2. “远程访问”选“开启令牌访问”。
3. “监听地址”填 `0.0.0.0`，端口保持 `8765` 或改成你的端口。
4. 点“保存设置”，然后重启识海服务。
5. 在“Agent 接入”复制访问令牌。

之后手机或其他电脑请求：

```text
http://你的电脑IP:8765/api/overview
```

并带：

```text
Authorization: Bearer <访问令牌>
```

如果部署到云服务器，建议把服务放在 HTTPS 网关后面，并且只给可信 Agent 发令牌。

## 数据放在哪里

- 默认数据目录是 `%LOCALAPPDATA%\Noetide\data`。
- 如果你在源码里用 `--data-dir`，就放在你指定的目录。
- 数据文件主要是 `noetide.sqlite3`、`settings.json`，以及 `exports/`、`backups/` 目录。
- 卸载默认不删除数据；删除数据必须显式确认，并先创建校验备份。

## 常见问题

### 打开网页是空白或者连不上

确认启动窗口还开着，确认地址是 `http://127.0.0.1:8765`。如果端口被占用，用 `--port` 换一个端口。

### 识灵分析没有候选

离线规则只识别明确的中文表达，例如“我和小王聊了项目”“我答应下周给方案”。如果文本太短或表达不明确，可能没有候选。这时可以换本地模型或云端模型再试。

### 接本地模型失败

确认模型服务已启动，接口地址是 OpenAI 兼容的 `/v1/chat/completions` 地址，模型名正确。本地模式只允许 `http://` 地址。

### 接云端模型失败

云端模式只允许 `https://` 地址，并且要填正确 API Key。失败时分析结果会显示 `model_call_failed` 或类似原因。

### 手机连不上

先确认服务监听的是 `0.0.0.0`，保存设置后重启，再确认防火墙放行端口，并在请求里带正确令牌。

### 为什么有些文件没导入

文件夹导入目前只处理 `.md`、`.txt`、`.json`、`.csv`，并且要求文件是 UTF-8 文本。其他文件会被跳过。

## 一句话总结

安装识海 -> 导入碎片 -> 识灵提候选 -> 你确认记忆 -> Agent/手机通过 MCP/API 读写 -> 导出/备份兜底。
