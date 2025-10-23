# 测试策略说明

## 概述

本项目采用分层测试策略，通过pytest标记系统将测试分为不同类别，支持灵活的测试执行方式。

## 测试标记分类

### 基础标记

| 标记 | 说明 | 依赖 | 执行时间 |
|------|------|------|----------|
| `basic` | 基础测试 | 仅jieba | 快速 |
| `optional` | 可选分词器测试 | thulac/hanlp | 中等 |
| `slow` | 慢速测试 | 无特殊 | 较慢 |
| `network` | 网络测试 | 网络连接 | 依赖网络 |
| `gui` | GUI测试 | 显示环境 | 中等 |
| `integration` | 集成测试 | 多组件 | 中等 |
| `unit` | 单元测试 | 单功能 | 快速 |

### 标记组合

可以组合多个标记，例如：
```python
@pytest.mark.optional
@pytest.mark.network
@pytest.mark.slow
def test_hanlp():
    pass
```

## 测试执行方式

### 1. 运行所有测试
```bash
pytest
```

### 2. 只运行基础测试（推荐用于CI）
```bash
pytest -m "basic"
```

### 3. 只运行可选分词器测试
```bash
pytest -m "optional"
```

### 4. 排除慢速测试
```bash
pytest -m "not slow"
```

### 5. 运行基础测试但排除慢速
```bash
pytest -m "basic and not slow"
```

### 6. 运行单元测试
```bash
pytest -m "unit"
```

### 7. 运行集成测试
```bash
pytest -m "integration"
```

### 8. 显示详细信息
```bash
pytest -v
```

### 9. 显示测试覆盖率
```bash
pytest --cov=../dev/src --cov-report=html
```

## 条件跳过

测试使用`skipif`装饰器来条件跳过不适用的测试：

```python
@pytest.mark.optional
@pytest.mark.skipif(not is_tokenizer_available('thulac'), reason="THULAC not installed")
def test_thulac_tokenizer():
    # 只有THULAC可用时才运行
    pass
```

## CI/CD集成

### GitHub Actions配置示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  basic-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r dev/src/requirements.txt
          pip install pytest pytest-cov
      
      - name: Run basic tests
        run: |
          cd tests
          pytest -m "basic" -v
  
  optional-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      
      - name: Install all dependencies
        run: |
          pip install -r dev/src/requirements.txt
          pip install thulac hanlp pytest pytest-cov
      
      - name: Run optional tests
        run: |
          cd tests
          pytest -m "optional and not network" -v
```

## 测试分层策略

### 第一层：基础测试（CI必须通过）
- 仅依赖jieba分词器
- 执行时间短（< 1分钟）
- 覆盖核心功能
- 总是在CI中运行

**包含测试**:
- 基本CER计算
- 编辑距离算法
- 文本标准化
- 核心API

### 第二层：可选测试（CI可选运行）
- 需要thulac或hanlp
- 执行时间中等（1-5分钟）
- 覆盖高级功能
- 在完整测试环境中运行

**包含测试**:
- THULAC分词器测试
- HanLP分词器测试（不含网络）
- 多分词器集成测试

### 第三层：完整测试（手动/定期运行）
- 包含网络依赖
- 执行时间较长（> 5分钟）
- 覆盖所有功能
- 定期完整验证

**包含测试**:
- HanLP模型下载测试
- 大文本性能测试
- 所有集成测试
- GUI测试

## 测试文件组织

```
tests/
├── pytest.ini                      # pytest配置
├── README_测试策略.md              # 本文档
├── test_with_pytest_marks.py       # 分层测试示例
├── test_system.py                  # 系统测试
├── test_tokenizers.py              # 分词器测试
├── performance_test.py             # 性能测试
└── ...
```

## 最佳实践

### 1. 测试命名
- 测试文件以`test_`开头
- 测试函数以`test_`开头
- 使用描述性名称

### 2. 标记使用
- 每个测试至少标记一个类别（unit/integration）
- 基础测试必须标记`basic`
- 可选依赖必须标记`optional`并使用`skipif`
- 慢速测试必须标记`slow`
- 需要网络的测试必须标记`network`

### 3. 断言使用
- 使用清晰的断言消息
- 每个测试只验证一个概念
- 使用`pytest.approx()`比较浮点数

### 4. fixture使用
- 共享的设置使用fixture
- 避免在测试间共享状态
- 使用适当的scope

## 示例

### 基础单元测试
```python
@pytest.mark.basic
@pytest.mark.unit
def test_cer_calculation():
    metrics = ASRMetrics(tokenizer_name='jieba')
    cer = metrics.calculate_cer("你好", "你好")
    assert cer == 0.0
```

### 可选分词器测试
```python
@pytest.mark.optional
@pytest.mark.skipif(not is_tokenizer_available('thulac'), 
                    reason="THULAC not installed")
def test_thulac():
    metrics = ASRMetrics(tokenizer_name='thulac')
    # 测试代码
```

### 集成测试
```python
@pytest.mark.integration
@pytest.mark.basic
def test_full_pipeline():
    # 测试完整流程
    pass
```

### 参数化测试
```python
@pytest.mark.basic
@pytest.mark.parametrize("input,expected", [
    ("test1", "result1"),
    ("test2", "result2"),
])
def test_multiple_cases(input, expected):
    assert process(input) == expected
```

## 持续改进

### 当前测试覆盖率
- 核心算法: ~80%
- 分词器适配: ~70%
- GUI功能: ~30%

### 改进计划
1. 增加GUI自动化测试
2. 增加边界条件测试
3. 增加异常处理测试
4. 建立性能基准测试

## 参考资料

- [pytest官方文档](https://docs.pytest.org/)
- [pytest标记文档](https://docs.pytest.org/en/stable/how-to/mark.html)
- [pytest参数化文档](https://docs.pytest.org/en/stable/how-to/parametrize.html)

---

**文档版本**: V1.0  
**最后更新**: 2025-10-23  
**维护人员**: 开发团队

