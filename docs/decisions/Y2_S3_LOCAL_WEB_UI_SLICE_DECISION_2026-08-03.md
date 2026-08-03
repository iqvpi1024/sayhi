# Y2-S3 本地 Web UI 切片产品决定

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-Y2-S3-001` |
| Date | 2026-08-03 |
| Product Baseline | `PRDv06.md` v0.6 Approved |
| Upstream Decision | `DEC-Y2-ENTRY-001` §2.4/§2.6（本地 Web UI，Y2-S3） |
| Current Slice | `SLICE-Y2-S3-LOCAL-WEB-UI-001` |

## 1. 决定内容

选择本地 Web UI 作为 Year 2 第三个切片。具体决定：

1. 实现一个 Python 标准库 HTTP 服务，仅绑定本机回环地址（`127.0.0.1`/`::1`），完全离线、无账户、无云服务、无第三方依赖、无前端构建链（vanilla HTML/JS/CSS）。
2. Web UI 是 A5 应用壳的呈现扩展：固定合成旅程覆盖记录、整理建议与影响预览、确认、视图、历史、撤销、导出与备份入口；CLI 继续维护。
3. 所有 Canonical 写操作继续经既有核心 ChangeSet 路径；记录只 append Source；Web 模块不得直接调用 store 写方法，不得提供绕过审查的写入路径。
4. 导出为请求时 Derived 的可读 Markdown 副本，只读 store，不落盘、不作证据；备份只写入服务器启动时配置的 `backup_dir`，请求不能指定任意路径。
5. 普通用户界面不得要求理解 ChangeSet、Projection 或 Revision；页面使用日常中文标签，内部技术字段只出现在机器 API。
6. 本切片只证明固定合成 Web 呈现链，不开放真实数据模式，不实现云端、账户、MCP、同步或任意文件上传。

## 2. 产品依据

- PRDv06 §18.8：本地 Web UI 完全离线、仅本机、无账户、覆盖记录/审查/确认/视图/撤销/历史/导出/备份入口；不产生新业务语义。
- PRDv06 §24.5：Y2-S3 关键约束为离线、仅本机、无账户。
- PRDv06 §6/§11/§17：所有 Canonical 写经 ChangeSet；模型/候选只能 propose；权限与本地单用户边界不得旁路。
- PRDv06 §21/§25：仓库与测试只使用显式合成数据；不得把 Derived 呈现反向当成事实证据。

## 3. 切片范围

- `src/noetide_micro/local_web.py`：stdlib HTTP 服务、回环绑定、路由、HTML 页面与只读/写 API。
- `src/noetide_micro/cli.py`：新增 `web` 命令入口，默认 `127.0.0.1`，可指定端口与备份目录。
- `src/noetide_micro/y2s3_testing_adapter.py`：临时目录 + 127.0.0.1 stub server + fixture clock 的 contract adapter。
- Suite：10 场景，覆盖 6 条不变量；全部使用固定合成 profile `y2s3_local_web_ui_v1`。

## 4. 非目标

- 云端后端（Y2-S4）、MCP runtime（Y2-S5）、账户体系、多设备同步、任意文件导入、生产级加密密钥管理。
- 改变 A5 或任何已 verified 切片的核心业务语义；不修改历史 fixture/oracle/result。
- 真实个人数据模式开放；不引入真实姓名、地址、组织、电话、邮箱、凭据或工作区外数据。

## 5. 不变量

- `Y2S3-INV-001`：local-only/offline——服务只绑定本机回环；无账户、无云、无外部网络调用。
- `Y2S3-INV-002`：no bypass——所有 Canonical 写经既有 ChangeSet，记录经 Source append；Web 模块无直接 store 写调用。
- `Y2S3-INV-003`：presentation derived——审查、视图、历史标签与导出 Markdown 是请求时 Derived，不持久化、不作证据。
- `Y2S3-INV-004`：confirm/undo——确认经 approve+publish，撤销经既有补偿路径；历史保留。
- `Y2S3-INV-005`：fail closed——未知路由、畸形请求、缺前置步骤、非回环 host 均拒绝且零业务写入。
- `Y2S3-INV-006`：deterministic/stdlib/synthetic——fixture clock、确定性响应、stdlib only、显式合成数据。

## 6. 授权与下一步

本决定授权 S1/S3/S4/S5/S6/S7/S9 SPEC applicability review，随后 slice contract、traceability、ADR、suite 物化、Implementation Plan。不授权业务编码。