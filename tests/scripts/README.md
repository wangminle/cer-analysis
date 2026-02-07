# tests/scripts/ - 非 pytest 脚本归档

本目录存放**不参与 pytest 自动收集**的脚本文件。这些脚本是开发过程中的手动验证工具、调试脚本和架构演示，需要手动运行（`python3 脚本名.py`）。

## 归档脚本（开发辅助工具）

| 文件 | 类型 | 说明 |
|------|------|------|
| `test_architecture_demo.py` | 架构演示 | 使用 Mock 类演示分词器架构设计（494 行），不依赖外部库 |
| `hanlp_tok_only.py` | HanLP 实验 | 独立的 HanLP 轻量化分词器实验代码 |
| `hanlp_tokenizer_optimized.py` | HanLP 实验 | 优化版 HanLP 分词器原型代码 |
| `test_tokenizer_issue.py` | 调试脚本 | 调试 thulac/hanlp 模型独立性问题 |
| `advanced_tokenizer_test.py` | 调试脚本 | 对比 thulac/hanlp 分词差异（P0 报错元凶之一） |
| `test_version_fix.py` | 验证脚本 | 验证分词器版本获取修复 |
| `test_hanlp_integration.py` | 验证脚本 | HanLP 集成验证 |

## 冗余脚本（V2 整改后可删除）

| 文件 | 说明 | 冗余原因 |
|------|------|---------|
| `test_system.py` | 系统功能验证 | 与 `test_tokenizers.py` 功能 ~90% 重复 |
| `test_tokenizers.py` | 分词器架构测试 | 与 `test_system.py` 功能 ~90% 重复 |
| `simple_test.py` | 简单分词器测试 | `test_tokenizers.py` 的简化版 |
| `quick_test.py` | 快速验证测试 | 与 `simple_test.py` 功能 ~80% 重复 |

## 注意事项

- 这些脚本的 `sys.path` 设置可能已过时，运行前请确认路径正确
- pytest 通过 `pytest.ini` 中的 `norecursedirs = scripts` 排除本目录
- V2 正式测试用例请放在 `tests/` 根目录中
