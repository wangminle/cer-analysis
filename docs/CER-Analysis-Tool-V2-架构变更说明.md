# CER-Analysis-Tool V2 架构变更说明

> **版本**: V1.0  
> **最后更新**: 2026-02-06 20:20  
> **基线文档**: `docs/V1/Cer-MatchingTools-V1-架构设计.md`

---

## 1. 概述

本文档记录 CER-Analysis-Tool V2 迭代中所有架构层面的变更，作为 V1 架构设计文档的增量补充。V1 架构文档保持原样归档。

## 2. 项目更名

| 维度 | V1 | V2 |
|------|-----|-----|
| 项目名 | Cer-MatchingTools | CER-Analysis-Tool |
| Python 包名 | 无（脚本直接运行） | `cer_tool` |
| CLI 命令 | `python cli.py` | `cer-tool` / `python -m cer_tool` |

## 3. 目录结构变更

### V1 结构（已封存于 `dev/v1.0-archive/`）
```
dev/src/
├── asr_metrics_refactored.py    # 指标计算引擎
├── main_with_tokenizers.py      # GUI 主程序
├── cli.py                       # CLI 接口
├── preprocessing_pipeline.py    # 预处理流水线
├── text_tokenizers/             # 分词器包（双层嵌套）
│   ├── __init__.py
│   └── tokenizers/
│       ├── base.py / factory.py / jieba_tokenizer.py / ...
└── requirements.txt
```

### V2 结构（当前活跃）
```
src/cer_tool/                    # Python 标准 src-layout
├── __init__.py                  # 包元数据 (__version__)
├── __main__.py                  # python -m cer_tool 入口
├── metrics.py                   # 指标计算引擎（原 asr_metrics_refactored.py）
├── gui.py                       # GUI 主程序（原 main_with_tokenizers.py）
├── cli.py                       # CLI 接口（增强版）
├── preprocessing.py             # 预处理流水线（原 preprocessing_pipeline.py）
├── file_utils.py                # 公共文件工具（新建，从 CLI/GUI 提取）
└── tokenizers/                  # 分词器包（扁平化，消除双层嵌套）
    ├── __init__.py
    ├── base.py / factory.py / jieba_tokenizer.py / ...
```

## 4. 依赖变更

### 移除的依赖

| 依赖 | V1 用途 | V2 替代方案 |
|------|---------|-----------|
| `jiwer` | `preprocess_text()` 中的 `jiwer.Compose` 预处理 | 自研 `PreprocessingPipeline` |
| `pandas` | GUI 导出 CSV (`pd.DataFrame.to_csv()`) | 标准库 `csv.DictWriter` |

### 核心依赖（V2）

| 依赖 | 必需 | 用途 |
|------|------|------|
| `jieba` | 是 | 默认分词器 |
| `python-Levenshtein` | 推荐 | 高效编辑距离（内置纯 Python 备选） |

### 可选依赖（extras）

| extras 名称 | 包含 | 用途 |
|-------------|------|------|
| `thulac` | thulac>=0.2.0 | THULAC 分词器 |
| `hanlp` | hanlp>=2.1.0, torch | HanLP 分词器 |
| `all` | 全部可选 | 一键安装所有分词器 |
| `dev` | pytest, ruff, mypy | 开发/测试工具 |

## 5. 预处理架构变更

### V1：jiwer 硬依赖

```python
# V1 的 preprocess_text()
transformation = jiwer.Compose([
    jiwer.RemoveMultipleSpaces(),
    jiwer.Strip(),
    jiwer.RemovePunctuation(),
    jiwer.ToLowerCase(),
])
processed_text = transformation(text)
```

### V2：自研 PreprocessingPipeline

```python
# V2 的 preprocess_text() 通过 _build_pipeline() 构建
pipeline = PipelinePresets.cer_optimized(self.tokenizer)
pipeline.add_step(LowercaseStep())
processed_text = pipeline.process(text)
```

**优势**:
- 可插拔步骤，支持运行时动态配置
- 消除 jiwer 依赖（安装体积 >90% 缩减）
- 5 种预设模板（basic / conservative / aggressive / cer_optimized / asr_evaluation）

## 6. 指标引擎边界语义修正

### V1 行为（BUG）

| 输入 | V1 CER | V1 accuracy |
|------|--------|-------------|
| `("", "abc")` | 3.0 | -2.0 |
| `("", "")` | 不确定 | 不确定 |

### V2 行为（修正后）

| 输入 | V2 CER | V2 accuracy | 语义 |
|------|--------|-------------|------|
| `("", "")` | 0.0 | 1.0 | 两个都为空 → 完全匹配 |
| `("", "abc")` | 1.0 | 0.0 | 空参考 → 最差分数 |
| `("abc", "")` | 1.0 | 0.0 | 空假设 → 最差分数 |
| `("，。！", "abc")` | 1.0 | 0.0 | 标点归一后为空 → 同上 |

## 7. CLI 增强

| 功能 | V1 | V2 |
|------|-----|-----|
| `--version` | 无 | `CER-Analysis-Tool 2.0.0` |
| JSON 输出 | 无 | `--format json` / `--output result.json` |
| 退出码契约 | 失败返回 0 | 失败返回 1 |
| verbose 控制 | 硬编码 True | 遵循 `--verbose` 参数 |
| 错误输出 | stdout | stderr |

## 8. V1 架构文档中未实现组件的澄清

以下组件在 V1 架构文档中有描述，但在实际代码中并未完整实现：

| 组件 | 架构文档描述 | 实际状态（V2） |
|------|------------|--------------|
| 策略模式 (Strategy) | 算法管理层 | 未落地为独立 Strategy 接口，分词器切换通过 Factory 模式实现 |
| 缓存机制 | 数据访问层 - 存储管理层 | 分词器层有缓存（Singleton），但文件层无缓存 |
| 数据清洗 | 数据处理层 | 已通过 PreprocessingPipeline 实现（V2 新增） |
| 临时文件 | 存储管理层 | 未实现，当前无临时文件需求 |

---

*本文档随 V2 迭代持续更新。*
