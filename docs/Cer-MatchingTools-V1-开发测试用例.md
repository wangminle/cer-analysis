# 三种分词工具切换功能测试用例

## 测试目标
验证三种分词工具（Jieba、THULAC、HanLP）的切换功能，确保：
1. 分词器抽象层的正确性
2. GUI和命令行界面的集成
3. 不同分词器结果的一致性和准确性
4. 系统的稳定性和性能

## 1. 单元测试用例

### 1.1 分词器抽象层测试

#### TestBaseTokenizer
```python
def test_validate_text_valid_input():
    """测试有效文本输入验证"""
    # 输入: "我来到北京清华大学", "Hello World", "123中文"
    # 预期: 返回清理后的文本字符串

def test_validate_text_invalid_input():
    """测试无效文本输入验证"""
    # 输入: None, 123, [], ""
    # 预期: 抛出TokenizerProcessError或返回空字符串

def test_get_info():
    """测试分词器信息获取"""
    # 预期: 返回包含name, initialized, version的字典
```

#### TestJiebaTokenizer
```python
def test_initialize_success():
    """测试Jieba分词器初始化"""
    # 预期: initialize()返回True, is_initialized为True

def test_cut_basic():
    """测试基础分词功能"""
    # 输入: "我来到北京清华大学"
    # 预期: ["我", "来到", "北京", "清华大学"]

def test_posseg_functionality():
    """测试词性标注功能"""
    # 输入: "我爱北京天安门"
    # 预期: [("我", "r"), ("爱", "v"), ...]

def test_tokenize_positions():
    """测试精确分词位置信息"""
    # 输入: "永和服装饰品有限公司"
    # 预期: [("永和", 0, 2), ("服装", 2, 4), ...]
```

#### TestThulacTokenizer
```python
def test_availability_check():
    """测试THULAC可用性检查"""
    # 如果未安装: 抛出TokenizerInitError
    # 如果已安装: 正常初始化

def test_tokenize_position_calculation():
    """测试位置计算准确性"""
    # 验证手动计算的位置与原文一致
    # 重构文本应等于原文本
```

#### TestHanlpTokenizer
```python
def test_model_loading():
    """测试HanLP模型加载"""
    # 验证BERT模型能正确加载
    # 验证POS模型能正确加载

def test_tokenize_offset_support():
    """测试偏移量支持"""
    # 验证output_offsets=True是否工作
    # 验证偏移量的准确性
```

### 1.2 分词器工厂测试

#### TestTokenizerFactory
```python
def test_get_available_tokenizers():
    """测试获取可用分词器列表"""
    # 预期: 返回list, 至少包含'jieba'

def test_singleton_pattern():
    """测试单例模式"""
    # 同一分词器的多次获取应返回同一实例

def test_create_invalid_tokenizer():
    """测试创建无效分词器"""
    # 输入: 'invalid_tokenizer'
    # 预期: 抛出ValueError
```

### 1.3 ASRMetrics重构测试

#### TestASRMetricsRefactored
```python
def test_initialization_with_invalid_tokenizer():
    """测试无效分词器初始化"""
    # 输入: tokenizer_name='invalid'
    # 预期: 自动回退到'jieba'

def test_calculate_cer_consistency():
    """测试CER计算一致性"""
    # 使用相同文本对，不同分词器
    # 预期: 结果在合理范围内(0-1)

def test_filter_filler_words():
    """测试语气词过滤"""
    # 输入: "嗯，今天天气真不错啊。"
    # 预期: 结果不包含"嗯"和"啊"
```

## 2. 集成测试用例

### 2.1 GUI集成测试

#### TestGUITokenizerIntegration
```python
def test_tokenizer_combo_initialization():
    """测试GUI分词器下拉框初始化"""
    # 验证: 下拉框包含所有可用分词器
    # 验证: 默认选择为'jieba'

def test_tokenizer_selection_change():
    """测试分词器选择变化"""
    # 操作: 用户选择不同分词器
    # 验证: 状态正确更新，错误提示正确显示

def test_calculate_with_different_tokenizers():
    """测试使用不同分词器计算"""
    # 准备: 创建测试文件
    # 操作: 切换分词器并计算
    # 验证: 计算完成，结果合理
```

### 2.2 命令行集成测试

#### TestCLITokenizerIntegration
```python
def test_tokenizer_parameter():
    """测试--tokenizer参数"""
    # 命令: check_accuracy.py --tokenizer thulac
    # 验证: 使用指定分词器，输出包含分词器信息

def test_invalid_tokenizer_parameter():
    """测试无效分词器参数"""
    # 命令: check_accuracy.py --tokenizer invalid
    # 预期: 命令返回错误，错误信息清晰
```

### 2.3 端到端测试

#### TestEndToEndWorkflow
```python
def test_complete_workflow():
    """测试完整工作流程"""
    # 测试用例:
    test_cases = [
        {
            'ref': "北京大学是中国最著名的高等学府之一。",
            'asr': "北京大学是中国最著名的高登学府之一。",
            'expected_errors': ['著->登']
        }
    ]
    # 验证: 每个分词器都能完成计算并返回合理结果

def test_performance_comparison():
    """测试性能对比"""
    # 使用大文本测试不同分词器
    # 验证: 所有分词器在30秒内完成
    # 记录: 性能数据用于对比
```

## 3. 性能和稳定性测试

### 3.1 性能测试

#### TestPerformance
```python
def test_large_file_processing():
    """测试大文件处理"""
    # 创建1000句重复文本
    # 验证: 30秒内完成处理
    # 验证: 内存使用在合理范围

def test_memory_usage():
    """测试内存使用"""
    # 创建10个不同分词器实例
    # 验证: 内存增长<500MB
```

### 3.2 稳定性测试

#### TestStability
```python
def test_error_recovery():
    """测试错误恢复"""
    # 输入异常数据: None, "", 数字, 列表等
    # 验证: 程序不崩溃，返回合理错误

def test_concurrent_usage():
    """测试并发使用"""
    # 多线程同时使用不同分词器
    # 验证: 无竞争条件，结果正确
```

## 4. 测试数据准备

### 4.1 标准测试文本
```python
# 简单文本
simple_texts = [
    "我来到北京清华大学",
    "今天天气真不错",
    "他来到了网易杭研大厦"
]

# 复杂文本  
complex_texts = [
    "北京大学是中国最著名的高等学府之一，创建于1898年。",
    "在第二届国际汉语分词测评中，共有四家单位提供测试语料。"
]

# 错误案例
error_cases = [
    {
        'ref': "今天天气真不错，阳光明媚。",
        'asr': "今天天气真不错阳光明美",
        'error_types': ['删除', '替换']
    }
]
```

### 4.2 测试文件创建
```python
def create_test_files():
    """创建测试文件"""
    import tempfile
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    
    # ASR文件
    asr_files = [
        "今天天气真不错阳光明美",
        "北京大学是中国最著名的高登学府",
        "他来到了网易杭研大夏"
    ]
    
    # 标注文件  
    ref_files = [
        "今天天气真不错，阳光明媚。",
        "北京大学是中国最著名的高等学府",
        "他来到了网易杭研大厦"
    ]
    
    return temp_dir, asr_files, ref_files
```

## 5. 测试环境配置

### 5.1 依赖检查
```python
def check_dependencies():
    """检查测试依赖"""
    required = ['jieba']
    optional = ['thulac', 'hanlp']
    
    available = []
    for dep in required + optional:
        try:
            __import__(dep)
            available.append(dep)
        except ImportError:
            if dep in required:
                raise Exception(f"Required dependency {dep} not found")
    
    return available
```

### 5.2 测试运行配置
```bash
# pytest配置文件 pytest.ini
[pytest]
markers =
    basic: marks tests as basic functionality (fast, essential)
    optional: marks tests for optional components (e.g., HanLP, THULAC)
    performance: marks tests for performance measurement (long running)
    gui: marks tests for GUI components (requires display)
    cli: marks tests for CLI functionality
    pipeline: marks tests for preprocessing pipeline
    regression: marks tests for regression testing
norecursedirs = v0.1.0 output

# 运行示例
# 运行基础测试（排除可选组件）
pytest -m "not optional and not performance and not gui"

# 运行所有测试
pytest

# 运行特定类型测试
pytest -m basic
pytest -m cli
pytest -m pipeline
```

## 6. 预期测试结果

### 6.1 成功标准
- 所有单元测试通过率 > 95%
- 集成测试通过率 > 90%
- 性能测试在规定时间内完成
- 稳定性测试无崩溃

### 6.2 性能基准
| 分词器 | 初始化时间 | 分词速度 | 内存使用 |
|--------|------------|----------|----------|
| Jieba  | < 1s       | > 1MB/s  | < 100MB  |
| THULAC | < 3s       | > 0.5MB/s| < 200MB  |
| HanLP  | < 10s      | > 0.2MB/s| < 500MB  |

### 6.3 准确性验证
- 相同文本CER=0（误差<0.01）
- 不同分词器结果差异<10%
- 错误类型识别准确率>90%

这个测试方案确保了系统的可靠性、性能和用户体验。

---

**文档版本**：V1.1  
**最后更新时间**：2025-10-23 14:58  
**更新说明**：[P2任务完成：更新测试运行配置，添加分层测试策略说明]  
**维护人员**：开发团队 