# ADR-0022：Y2-S3 本地 Web UI 的 stdlib HTTP 服务形态

| 字段 | 值 |
|---|---|
| Status | `Accepted` |
| Slice | `SLICE-Y2-S3-LOCAL-WEB-UI-001` |
| Contract | `SPEC-Y2S3-LOCAL-WEB-UI-001` v0.1 |
| Decision | `DEC-Y2-S3-001` |

## 决定

Y2-S3 本地 Web UI 实现为 Python 标准库 `http.server.ThreadingHTTPServer` + `BaseHTTPRequestHandler`，只绑定 `127.0.0.1`/`::1`，内置 vanilla HTML/CSS/JS 页面，无前端构建链。服务持有单个 `LocalMicroRuntime`，API 路由按 `web_command` 委托给已验证核心能力：

```text
GET /                     -> home page（日常中文标签）
POST /api/record          -> runtime.intake（Source append + receipt）
POST /api/review          -> runtime.propose + app_shell 自然语言摘要与影响预览
POST /api/confirm         -> runtime.approve + runtime.publish
GET  /api/views           -> runtime.view（person_card/relationship_timeline）
GET  /api/history         -> store ledger 只读派生历史标签
POST /api/revert          -> runtime.revert
GET  /api/export          -> portability_snapshot + render_markdown（Derived，只读）
POST /api/backup          -> create_backup 写入服务配置的 backup_dir
```

- Web 模块不直接调用 store 写方法；写面只委托 runtime/已验证核心。
- 导出只读 store；备份路径来自服务构造参数，不接受请求指定路径。
- 普通页面不展示 ChangeSet/Projection/Revision 等内部术语；机器 API 保留稳定字段。

## 不采用的方案

- 仅扩展 CLI 不做 Web：不符合 PRDv06 §18.8 已激活的本地 Web 呈现入口。
- Flask/FastAPI/aiohttp：引入第三方依赖，违反 Y2-E-INV-005 与 DEC-Y2-ENTRY-001 §2.4。
- 前端框架/构建链（React/Vite 等）：增加离线安装与产物复杂度，不必要；固定合成 UI 用 vanilla JS 足够。
- 桌面 UI（tkinter/Electron/Tauri）：打包与跨平台验证成本高，DEC-Y2-ENTRY-001 已明确后置。
- 直接暴露 store/REST 全表接口：扩大写面与信息泄露面，违反 no-bypass 与最小呈现合同。

## 后果与验证

- 服务面仅回环，无账户/云/外部网络；测试用 127.0.0.1 stub server 与 loopback-only socket guard。
- 普通用户路径不暴露内部术语；由 HTML 可见文案断言与 API 响应形状共同验证。
- 所有写操作仍经已验证核心；Web 模块静态扫描证明无直接 store 写调用。
- 导出/备份复用已 verified 的 `portability`/`pack_backup` 能力，不重建格式或加密语义。
- 代价：HTTP 服务是长期运行的本地进程，需显式 close；备份目录必须由用户配置且只写该目录。