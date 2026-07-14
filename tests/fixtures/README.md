# 合成 Fixture 规则

当前没有机器 fixture artifact。本目录未来只接收版本化合成数据。

每个 fixture set 必须：

- 标记 `synthetic=true`，使用虚构中性标识。
- 记录 schema version、固定时钟、时区、locale、seed 和 ID 规则。
- 对 Source 记录 UTF-8 byte length、locator 和 content hash。
- 将 initial state、input、expected state、forbidden state 和 receipt 分离。
- 不包含真实姓名、地址、公司、电话、邮箱、凭据、健康、债务或亲密关系资料。
- 不从工作区外文件、历史个人 Wiki 或在线账户生成。
- 修改后升 fixture version，并使旧 Verification Result applicability 可被判定。

Micro 的人类可读固定输入当前只定义在 `docs/testing/MICRO_MVP_ACCEPTANCE.md`；在 manifest 和机器 artifact 创建前，`suite_materialized` 保持 `false`。
