# 贡献指南

欢迎提交针对合成预览版的 bug 修复、测试、文档和可复现构建改进。

## 基本规则

- 不提交真实个人数据、凭据或工作区外资料。
- 不修改 `PRDv04.md`；产品语义变化必须发布新 PRD 或 Decision。
- 任何 Canonical 语义写入不得绕过 ChangeSet；Derived View 不能作为事实证据。
- 变更必须保留或新增相称的测试，并记录实际验证结果。

## 本地验证

在仓库根目录执行：

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m unittest discover -s tests\semantic
powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1
powershell -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1
```

对 Micro 或其他 manifest suite 的变更，还必须运行相应 validator 和新的 immutable runner result。不要覆盖已有 result 文件。
