# Verification Results

本目录保存实际业务 suite 的不可改写运行结果。当前没有业务 Verification Result，因为 Micro suite 尚未物化、实现不存在、业务测试未执行。

规则：

- 文件名建议为 `<YYYYMMDDTHHMMSSZ>_<slice_id>_<run_id>.md`。
- 每次运行创建新文件；失败、partial 和 superseded 结果均保留。
- 结果必须绑定 commit、manifest、fixture、implementation 和环境。
- 只有同一次 current run 的全部 required tests passed 才能记录 `passed`。
- 静态合同校验继续记录在 `docs/testing/LATEST_STATIC_VALIDATION.md`，不得放入本目录冒充业务结果。

模板：`docs/testing/VERIFICATION_RESULT_TEMPLATE.md`。
