# Y2-S3 本地 Web UI 切片合同

## 0. 文档信息

| 字段 | 值 |
|---|---|
| Contract ID | `SPEC-Y2S3-LOCAL-WEB-UI-001` |
| 版本 | `0.1` |
| 状态 | `Approved for Y2-S3 slice` |
| 产品基线 | `PRDv06.md` v0.6 |
| 产品决定 | `DEC-Y2-S3-001` |
| 上游 | S1 v0.7、S2 v0.6、S3 v0.5、S4 v0.5、S5 v0.5、S6 v0.6、S7 v0.4、S9 v0.5 |
| 适用范围 | `SLICE-Y2-S3-LOCAL-WEB-UI-001`，仅固定合成数据 |

## 1. 目标与非目标

目标：证明固定合成用户可以通过本机 Web UI 完成记录、整理建议与影响预览、确认、视图、历史、撤销、导出与备份入口，全程不要求理解 ChangeSet、Projection 或 Revision；Web UI 不产生新业务语义。

非目标：云端后端（Y2-S4）、MCP runtime（Y2-S5）、账户、多设备、同步、真实数据、任意文件上传、前端构建链、第三方 HTTP 服务。

## 2. 对象与字段

```yaml
local_web_server:
  host: 127.0.0.1 | ::1
  account: absent
  cloud: absent
  external_network: absent
  dependencies: stdlib_only

web_command:
  record | review | confirm | views | history | revert | export | backup

http_request:
  method: GET | POST
  path: / | /api/<command>
  body: JSON（仅 POST 且仅必要字段）

web_response:
  status: ok | rejected
  payload: per-command 固定字段

home_page:
  title: 识海本地整理
  visible_copy: 日常中文标签，不含 ChangeSet/Projection/Revision 等内部术语
  client: vanilla HTML/CSS/JS，无外部资源

review_presentation:
  summary_text: 固定合成自然语言摘要
  evidence_citations: [source refs]
  presentation_revision: a5_shell_v1
  impact_preview: {will_create, will_modify, views_affected, impact_text}

portable_export:
  data_revision: <current>
  files: {markdown/sources.md, markdown/canonical.md, markdown/ledger.md}
  read_only: true

backup_receipt:
  backup_id: web_backup_001.nobak
  backup_file_exists: true
  source_db_sha256_matches: true
  created_at: fixture clock
```

## 3. 判定规则

1. HTTP 服务只能绑定回环地址；构造时非回环 host 拒绝；服务不发起任何外部网络调用。
2. 固定旅程：`record -> review -> confirm -> views -> history -> revert -> export -> backup`；`review` 返回自然语言摘要与影响预览。
3. 所有 Canonical 写操作经既有核心 ChangeSet 路径；`record` 只 append Source；Web 模块不得直接调用 store 写方法。
4. 普通用户页面只展示日常中文标签；机器 API 可携带稳定技术字段，但页面不得要求用户理解内部结构。
5. 导出为请求时 Derived Markdown 副本，只读 store、不落盘、不作证据。
6. 备份只写入服务器启动时配置的 `backup_dir`；请求不能指定任意路径；备份使用固定合成密钥标签。

## 4. 时间、证据与权限

- 全部时间来自 fixture clock；Web UI 不读 wall-clock。
- 审查、视图、历史标签与导出是 Derived；不持久化、不作证据、不反向修改 Canonical。
- 本切片为本地单用户无账户路径；不实现权限旁路。
- 备份加密沿用 `stdlib_deterministic_v1`，明确不是生产级加密选型。

## 5. 系统不变量

| ID | 不变量 |
|---|---|
| `Y2S3-INV-001` | local-only/offline——服务只绑定本机回环；无账户、无云、无外部网络调用。 |
| `Y2S3-INV-002` | no bypass——所有 Canonical 写经既有 ChangeSet，记录经 Source append；Web 模块无直接 store 写调用。 |
| `Y2S3-INV-003` | presentation derived——审查、视图、历史标签与导出 Markdown 是请求时 Derived，不持久化、不作证据。 |
| `Y2S3-INV-004` | confirm/undo——确认经 approve+publish，撤销经既有补偿路径；历史保留。 |
| `Y2S3-INV-005` | fail closed——未知路由、畸形请求、缺前置步骤、非回环 host 均拒绝且零业务写入。 |
| `Y2S3-INV-006` | deterministic/stdlib/synthetic——fixture clock、确定性响应、stdlib only、显式合成数据。 |

## 6. 失败、撤销与审计

- 未知路由/未知 action：HTTP 404 + `status=rejected`，零写入。
- 畸形 JSON 或错误 Content-Type：HTTP 400 + `status=rejected`，零写入。
- 缺前置步骤（未记录即审查、未审查即确认、未发布即撤销）：HTTP 409 + `status=rejected`，零写入。
- 发布/撤销失败：复用核心失败语义；Web 只报告拒绝状态，不部分写入。
- 审计：复用 Source append receipt、ChangeSet receipt、audit_event；Web UI 不新增审计对象。

## 7. 可执行验收

| ID | Given / When | Then |
|---|---|---|
| `Y2S3-001` | 启动 local Web 服务 / `GET /` | 返回 HTML 首页；可见文案为日常中文且不含内部术语；host 仅回环；无外部网络 |
| `Y2S3-002` | 已初始化合成库 / `POST /api/record` | Source append 回执返回；Canonical digest 与 revision 不变 |
| `Y2S3-003` | 已记录 / `POST /api/review` | 返回自然语言摘要、证据引用与影响预览；呈现不含 ChangeSet JSON 内部字段 |
| `Y2S3-004` | 已审查 / `POST /api/confirm` | approve+publish 原子完成；revision 前进；receipt 生成 |
| `Y2S3-005` | 已确认 / `GET /api/views` | person_card 与 relationship_timeline 反映新状态；读请求零写入 |
| `Y2S3-006` | 已确认 / `GET /api/history` | 返回 record/confirm 的日常事件标签；历史来自 Ledger |
| `Y2S3-007` | 已确认 / `POST /api/revert` + 再读视图与历史 | 补偿 revision 生成；视图恢复一致；历史保留撤销事件 |
| `Y2S3-008` | 全旅程 / `GET /api/export` + `POST /api/backup` | 导出只读且含三层 Markdown；备份文件只出现在配置目录且回执存在；请求不能指定路径 |
| `Y2S3-009` | 注入未知路由、畸形 JSON、缺前置步骤 / 对应请求 | 全部 `rejected`；Canonical、revision、Ledger 无业务写入 |
| `Y2S3-010` | 横切 / 两个独立系统 | 同输入响应字节一致；Web 模块静态扫描无 store 写调用；仅回环网络；stdlib only；fixture 显式合成 |

## 8. 完成定义

只有 fixture、oracle、manifest、offline runner、implementation plan 和同一次 immutable `Y2S3-001..010` passed result 存在，且所有 `Y2S3-INV-*` 有正/反证明时，Y2-S3 才能标记 `verified`。未执行时必须保持 `not_executed`。