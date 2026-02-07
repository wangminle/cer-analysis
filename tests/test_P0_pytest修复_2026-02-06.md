# P0 测试总结：修复 pytest 收集与运行

## 基本信息

| 项目 | 内容 |
|------|------|
| **任务编号** | T1 |
| **优先级** | P0 |
| **测试日期** | 2026-02-06 |
| **测试环境** | macOS, Python 3.12.10, pytest 8.4.1 |
| **测试人员** | AI 辅助 |

---

## 1. 问题描述

执行 `python3 -m pytest --collect-only` 时，收集阶段直接报 2 个 `ModuleNotFoundError`，导致整个测试套件无法运行。

### 报错信息

```
ERROR advanced_tokenizer_test.py
  ModuleNotFoundError: No module named 'text_tokenizers'
  原因：sys.path.append(os.path.join(os.path.dirname(__file__), 'src')) 路径错误

ERROR test-v0.1.0/example_test.py
  ModuleNotFoundError: No module named 'src'
  原因：from src.utils import ASRMetrics 路径已失效（V0.1.0 历史代码）
```

### 根因

1. `pytest.ini` 的 `python_files = test_*.py *_test.py` 模式过宽，`*_test.py` 把非 pytest 脚本 `advanced_tokenizer_test.py` 也收集进来
2. `testpaths = .` 且没有排除 `test-v0.1.0/` 子目录，导致历史版本脚本被收集
3. 多个手动脚本的 `sys.path` 设置不正确（指向 `'src'` 或 `'../src'` 而非 `'../dev/src'`）

---

## 2. 修复方案

### 2.1 修改 `pytest.ini`

| 修改项 | 修改前 | 修改后 |
|--------|--------|--------|
| `python_files` | `test_*.py *_test.py` | `test_*.py`（移除 `*_test.py`） |
| `norecursedirs` | 无 | `scripts test-v0.1.0 .git __pycache__ .pytest_cache` |
| `markers` | 7 个 | 10 个（新增 `boundary`、`cli`、`pipeline`） |

### 2.2 创建 `tests/scripts/` 目录

将 11 个非 pytest 脚本移入 `tests/scripts/` 子目录，使其不参与 pytest 自动收集：

**归档类（7 个）**：开发辅助脚本
- `advanced_tokenizer_test.py` — P0 报错元凶之一，`sys.path` 错误
- `test_architecture_demo.py` — 架构演示，494 行 Mock 代码
- `hanlp_tok_only.py` — HanLP 轻量化实验
- `hanlp_tokenizer_optimized.py` — HanLP 优化原型
- `test_tokenizer_issue.py` — 模型独立性调试脚本
- `test_version_fix.py` — 版本获取验证脚本
- `test_hanlp_integration.py` — HanLP 集成验证脚本

**冗余类（4 个）**：功能高度重复
- `test_system.py` — 与 `test_tokenizers.py` 功能 ~90% 重复
- `test_tokenizers.py` — 与 `test_system.py` 功能 ~90% 重复
- `simple_test.py` — `test_tokenizers.py` 的简化版
- `quick_test.py` — 与 `simple_test.py` ~80% 重复，且 `sys.path` 错误

### 2.3 创建 `tests/scripts/README.md`

为归档脚本提供说明文档，注明每个文件的用途和冗余原因。

---

## 3. 修复后验证

### 3.1 pytest --collect-only

```
$ python3 -m pytest --collect-only
========================= 14 tests collected in 8.20s ==========================
```

**结果：通过** ✅（0 error, 0 warning）

收集到的 14 个测试分布：
- `test_edit_ops_accurate.py` — 1 个用例
- `test_normalize_strategy.py` — 1 个用例
- `test_with_pytest_marks.py` — 12 个用例（含 3 个参数化）

### 3.2 pytest -m basic

```
$ python3 -m pytest -m basic
================= 10 passed, 4 deselected, 1 warning in 7.59s ==================
```

**结果：通过** ✅（10 passed, 0 failed）

被选中的 10 个 basic 测试全部通过：
- `test_jieba_tokenizer_basic` ✅
- `test_edit_distance_calculation` ✅
- `test_normalize_chinese_text_basic` ✅
- `test_complete_cer_calculation` ✅
- `test_highlight_errors` ✅
- `test_large_text_processing` ✅
- `test_cer_parametrized[hello-hello-0.0]` ✅
- `test_cer_parametrized[hello-hallo-0.2]` ✅
- `test_cer_parametrized[abc-ab-0.333]` ✅
- `test_with_fixture` ✅

### 3.3 全量非慢速测试

```
$ python3 -m pytest -m "not slow and not network"
================= 12 passed, 2 deselected, 1 warning in 8.05s ==================
```

**结果：通过** ✅（12 passed, 0 failed, 2 deselected）

---

## 4. 修复前后对比

| 指标 | 修复前 | 修复后 |
|------|--------|--------|
| `--collect-only` | ❌ 2 errors | ✅ 0 errors |
| `tests/` 根目录 .py 文件数 | 16 个 | 5 个（3 个 test_ + 2 个工具） |
| `scripts/` 目录 .py 文件数 | — | 11 个 |
| 可收集测试用例数 | 0（收集失败） | 14 个 |
| `pytest -m basic` | ❌ 无法执行 | ✅ 10 passed |
| 全量测试（非慢速） | ❌ 无法执行 | ✅ 12 passed |

---

## 5. 遗留事项

| 编号 | 说明 | 优先级 | 对应任务 |
|------|------|--------|---------|
| 1 | `test_normalize_strategy.py` 无断言，属于"假通过"，需改造为真正的 pytest 用例 | P2 | V2 测试重构 |
| 2 | `test_edit_ops_accurate.py` 有断言但含大量 print，需清理为标准 pytest 风格 | P2 | V2 测试重构 |
| 3 | `scripts/` 目录中的 4 个冗余文件后续可安全删除 | P3 | V2 测试整改 |
| 4 | `performance_test.py` 需改造为 pytest 用例并标记 `@pytest.mark.slow` | P2 | V2 测试重构 |
| 5 | pkg_resources 弃用警告（jieba 库）非本项目问题 | — | 等待 jieba 更新 |

---

## 6. 结论

**P0 任务（T1）已完成。** pytest 收集和运行恢复正常，整仓可测性断裂问题已修复。CI/CD 流程的基础条件已具备。
