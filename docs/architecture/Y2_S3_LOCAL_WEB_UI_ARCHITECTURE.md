# Y2-S3 本地 Web UI 架构视图

## 元信息

- Architecture ID: `ARCH-Y2S3-LOCAL-WEB-UI-001`
- Date: 2026-08-03
- Slice: `SLICE-Y2-S3-LOCAL-WEB-UI-001`
- ADR: `ADR-0022`
- Contract: `SPEC-Y2S3-LOCAL-WEB-UI-001` v0.1

## 1. 组件

```text
Browser (vanilla HTML/CSS/JS)
  -> local_web.py (ThreadingHTTPServer, 127.0.0.1/::1)
       GET /                 -> home page
       POST /api/record      -> LocalMicroRuntime.intake
       POST /api/review      -> runtime.propose + app_shell.render_review/render_impact_preview
       POST /api/confirm     -> runtime.approve + runtime.publish
       GET  /api/views       -> runtime.view
       GET  /api/history     -> store ledger 只读派生
       POST /api/revert      -> runtime.revert
       GET  /api/export      -> store.portability_snapshot + pack_backup.render_markdown
       POST /api/backup      -> pack_backup.create_backup（仅 server.backup_dir）
  -> LocalMicroRuntime / SemanticStore（已验证核心）
```

- Web 模块只有读面与委托写面；不直接调用 store 写方法。
- 页面呈现为请求时 Derived；导出 Markdown 不作证据。
- 备份写文件在服务器构造时给定的 `backup_dir` 内，请求不携带路径。

## 2. 边界

- 写面：Source append 经 intake；Canonical 写经 ChangeSet approve/publish/revert；备份文件仅写配置目录。
- 读面：`runtime.source/changeset/view/revision`、`store.portability_snapshot`、`store.ledger_records_of_type`。
- 失败面：非回环 host 构造拒绝；未知路由/畸形 JSON/缺前置步骤 reject 零业务写入。
- 时间面：全部使用 fixture clock，无 wall-clock。
- 网络面：服务只绑定回环；official runner 使用 loopback-only socket guard。

## 3. 数据流

固定合成旅程：`record -> review -> confirm -> views -> history -> revert -> export -> backup`。每一步只调用已验证核心；Web 返回日常标签或稳定 API 字段，不新增业务状态机。

## 4. 测试面

`y2s3_testing_adapter.py` 在临时目录启动 127.0.0.1 stub server，按 case 使用 HTTP 请求执行旅程；contract 10 场景覆盖 6 条不变量；导出/备份断言只读 store 与配置目录约束；Web 模块静态扫描无 store 写调用。