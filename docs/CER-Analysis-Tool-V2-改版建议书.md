# CER-Analysis-Tool-V2-改版建议书

## 文档信息


| 项目         | 内容                         |
| ---------- | -------------------------- |
| **文档版本**   | V1.5                       |
| **最后更新时间** | 2026-02-06 20:20           |
| **文档性质**   | 综合评审 + 改版规划                |
| **输入来源**   | AI架构评审报告 + 资深工程师代码审计       |
| **适用范围**   | CER-Analysis-Tool 项目 V2 迭代 |


---

## 一、评审背景

本文档综合了两份独立评审的结论：

1. **AI 架构评审**：从项目价值、同类对比、依赖合理性、代码架构、易用性五个维度进行全面评估。
2. **资深工程师代码审计**：通过实际运行 pytest、CLI、指标引擎等组件，验证了可测性、边界行为、退出码契约等工程质量问题。

两份评审的核心结论高度一致，本文将其合并为统一的改版建议。

---

## 二、项目价值确认

在讨论问题之前，先确认项目的核心价值——这些是 V2 迭代不应丢失的基本面。

### 2.1 定位价值：独特且有效


| 维度       | 评估  | 说明                             |
| -------- | --- | ------------------------------ |
| **市场空白** | 高   | 中文 CER 评估 + GUI + 多分词器，市面无直接竞品 |
| **用户门槛** | 低   | 非技术人员 5 分钟即可上手                 |
| **数据安全** | 高   | 全部本地处理，适合企业敏感数据                |
| **中文特化** | 高   | 语气词过滤、多编码支持、分词集成均为中文场景刚需       |


### 2.2 同类工具定位矩阵

```
                    低门槛 ◄──────────────────────► 高门槛
                    │                                  │
  专业评测能力 高    │         sclite/SCTK              │
                    │              ESPnet/WeNet         │
                    │                                   │
                    │  ★ CER-Tool V2（目标位置）         │
                    │                                   │
                    │  ★ CER-Tool V1（当前位置）         │
                    │                                   │
  专业评测能力 低    │    jiwer/fastwer                  │
                    │         werpy                     │
```

**V2 的目标**：在保持低门槛优势的同时，向"专业评测能力"方向提升一个台阶。

---

## 三、现存问题汇总（按优先级）

### 3.1 P0 级：阻断性问题

> P0 定义：影响项目基本可用性，必须立即修复。

#### P0-1：整仓可测性断裂

**发现者**：资深工程师实测  
**现象**：执行 `python3 -m pytest -m "basic and not slow"` 后，收集阶段直接报 2 个 `ModuleNotFoundError`，无法进入任何测试。

**根因分析**：


| 问题点           | 文件                                    | 具体原因                                                                                |
| ------------- | ------------------------------------- | ----------------------------------------------------------------------------------- |
| pytest 收集范围过宽 | `tests/pytest.ini`                    | `*_test.py` 规则将非 pytest 脚本（如 `advanced_tokenizer_test.py`、`hanlp_tok_only.py`）也收集进来 |
| 导入路径错误        | `tests/advanced_tokenizer_test.py:8`  | `sys.path` 设置不正确，导致模块找不到                                                            |
| 历史版本脚本干扰      | `tests/test-v0.1.0/example_test.py:9` | 导入 `src.utils` 路径已失效，但仍被 pytest 收集                                                  |


**影响范围**：

- 整个 CI/CD 流程无法建立
- 团队协作时无法验证代码变更是否引入回归
- 项目管理文档中声称"测试覆盖率 100%"与实际矛盾

---

### 3.2 P1 级：功能/行为缺陷

> P1 定义：核心功能存在逻辑缺陷或行为不符合预期。

#### P1-1：指标引擎空参考文本边界条件异常

**发现者**：资深工程师实测  
**现象**：`calculate_detailed_metrics("", "abc")` 返回 `cer=3.0`、`accuracy=-2.0`。

**根因分析**：

`asr_metrics_refactored.py` 中 `calculate_detailed_metrics()` 方法（约第 504-537 行）的空文本处理逻辑：

```python
# 问题代码
ref_chars = [""]   # 空参考文本时设置为 [""]
hyp_chars = list(hyp_processed)  # 假设文本正常拆分

# _calculate_edit_ops 会计算出 S+D+I = len(hyp_processed) 的操作
# 但 ref_length = len(ref_chars) = 1（因为是 [""]）
# 导致 cer = total_errors / 1 = total_errors，可能远大于 1
```

**对比**：同一文件中 `calculate_cer()` 方法（约第 269-273 行）对空参考文本有正确处理：

```python
if len(ref_processed) > 0:
    cer = distance / len(ref_processed)
else:
    cer = 1.0 if len(hyp_processed) > 0 else 0.0  # ← 正确的处理
```

**影响范围**：

- GUI 批量计算中若混入空文件，会产生异常的准确率数值（如 -200%）
- CSV 导出的统计数据被污染
- 整体统计中的平均准确率被拉偏

#### P1-2：CLI 退出码契约违反

**发现者**：资深工程师实测  
**现象**：传入不存在的文件后，CLI 打印了错误信息但进程退出码仍为 0。

**根因分析**：

`cli.py` 中 `main()` 函数：

```python
# 单文件模式（约第 301 行）
result = process_single_pair(...)  # result 为 None 时表示失败
# 但无论 result 是否为 None，都 return 0

# 批处理模式（约第 314 行）
results = batch_process_directory(...)  # 即使全部失败
return 0  # 仍然返回 0
```

**影响范围**：

- 自动化脚本和 CI/CD 管道中，失败会被"吞掉"
- 违反 Unix/POSIX 命令行工具的基本契约
- 调用方无法通过 `$?` 判断执行是否成功

#### P1-3：测试运行器 `run_tests.py` 不可用

**发现者**：资深工程师实测  
**现象**：`python tests/run_tests.py all` 执行失败。

**根因分析**：


| 问题点      | 行号     | 具体原因                                             |
| -------- | ------ | ------------------------------------------------ |
| 解释器硬编码   | 第 54 行 | 使用 `python` 而非 `sys.executable`，当前环境该解释器无 pytest |
| 路径嵌套错误   | 第 75 行 | 在 `tests/` 目录内再传 `tests/` 作为参数                   |
| 覆盖率路径不一致 | 第 98 行 | `--cov=src` 与实际路径 `dev/src` 不一致                  |


#### P1-4：预处理流水线"已设计未集成"

**发现者**：AI 架构评审  
**现象**：`preprocessing_pipeline.py` 实现了完整的流水线模块（约 430 行），但 `asr_metrics_refactored.py` 中的 `preprocess_text()` 完全没有使用它，而是内联调用 jiwer + 自有 normalize 方法。

**影响范围**：

- 架构文档描述的"可插拔预处理"能力在运行时实际不存在
- 用户无法通过 GUI 或 CLI 切换预处理策略
- jiwer 依赖无法移除（因为仍在使用其预处理功能）

---

### 3.3 P2 级：工程质量与体验问题

> P2 定义：不影响核心功能，但影响工程规范性和用户体验。

#### P2-1：依赖策略存在冲突

**双方共同发现**


| 文件                 | 声明                      | 矛盾                    |
| ------------------ | ----------------------- | --------------------- |
| `requirements.txt` | thulac/hanlp 注释掉，标注为可选  | 正确意图                  |
| `Pipfile`          | thulac/hanlp/torch 列为必装 | 与 requirements.txt 矛盾 |
| `README.md`        | 声明"可选依赖"                | 与 Pipfile 矛盾          |


此外，依赖合理性问题（AI 评审发现）：


| 依赖       | 问题                                                                | 建议  |
| -------- | ----------------------------------------------------------------- | --- |
| `jiwer`  | 仅使用了 4 个预处理转换器，项目自己的 `preprocessing_pipeline.py` 已完全覆盖            | 可移除 |
| `pandas` | 仅在 `export_results()` 中调用一次 `DataFrame.to_csv()`，功能可用标准库 `csv` 替代 | 可移除 |


**如果成功移除 jiwer 和 pandas，核心依赖将从 4 个缩减为 2 个**：`jieba` + `python-Levenshtein`。

#### P2-2：重复代码未提取

**发现者**：AI 架构评审

- `main_with_tokenizers.py` 的 `read_file_with_multiple_encodings()` 与 `cli.py` 的 `read_file_with_encodings()` 逻辑几乎完全相同
- CLI 的 `process_single_pair()` 每次都新建 `ASRMetrics` 实例，未利用缓存

#### P2-3：GUI 易用性短板

**发现者**：AI 架构评审


| 问题               | 影响                               |
| ---------------- | -------------------------------- |
| Tkinter 界面视觉风格偏旧 | 用户第一印象不佳                         |
| 拖拽排序缺少视觉反馈       | 操作不直观                            |
| 仅支持 .txt 文件      | 不支持 .csv/.json/.srt 等常见 ASR 输出格式 |
| 无文件名自动配对         | 大批量文件手动配对效率低                     |
| 缺少文件内容预览         | 选错文件后不易发现                        |


#### P2-4：架构文档过度设计

**发现者**：AI 架构评审

架构文档中描述了 `MessageBus`、`DIContainer`、`PluginManager`、`InternalAPIRouter` 等组件，但代码中均未实现。文档中的设计大幅超出实际代码，可能给阅读者造成"代码比实际更复杂"的误解。

#### P2-5：缺少专业评测能力

**双方共同识别**

与行业标准工具（如 sclite/SCTK）相比，当前缺少：

- 字符级对齐可视化（alignment visualization）
- 句子级 CER 排序和分布分析
- 批次级加权统计
- 多参考文本支持
- JSON 可机读输出格式
- 置信区间等统计学指标

---

## 四、改版方案

### 4.1 改版原则

1. **先止血，再进化**：优先修复 P0/P1 级阻断性问题，再推进功能增强
2. **做减法再做加法**：先精简依赖和清理冗余代码，再添加新功能
3. **保持核心优势**：低门槛 + 中文特化 + 本地化，不为"专业化"牺牲易用性
4. **可验证的改进**：每项改动必须有对应的自动化测试验证

### 4.2 改版任务清单

#### 第一阶段A：稳定性修复（P0 + P1 行为问题，预计 2-3 天）

> **原则**：只修 bug，不搬目录。在现有 `dev/src/` 结构下就地修复，确保所有行为缺陷先得到验证和封闭。

| 编号  | 优先级 | 任务              | 详细说明                                                                                                                                                                                                               | 验证标准                                                                        |
| --- | --- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------- |
| T1  | P0  | 修复 pytest 收集与运行 | 1. 收敛 `pytest.ini` 中的收集模式，仅收集 `test_*.py` 2. 将非 pytest 的历史脚本（`advanced_tokenizer_test.py`、`hanlp_tok_only.py` 等）移入 `tests/scripts/` 子目录 3. 将 `tests/test-v0.1.0/` 加入 `norecursedirs` 4. 修复所有测试文件的导入路径 | `python3 -m pytest --collect-only` 无报错，且 `python3 -m pytest -m basic` 可成功执行 |
| T2  | P1  | 修复指标边界条件        | 1. 统一 `calculate_detailed_metrics()` 与 `calculate_cer()` 的空文本处理逻辑 2. 确保 CER 值域为 [0, +∞)，accuracy 值域为 (-∞, 1.0] 3. 空参考文本 + 非空假设 → CER=1.0（而非 N.0）                                                                   | 新增 4 组边界测试：(空,空)→CER=0、(空,非空)→CER=1.0、(非空,空)→CER=1.0、(仅标点归一后为空)             |
| T3  | P1  | 修复 CLI 退出码      | 1. 单文件模式：`process_single_pair` 返回 None 时 `main()` 返回 1 2. 批处理模式：存在任何失败时返回 1 3. `--verbose` 参数传递修正                                                                                                                  | 测试：传入不存在文件 → 退出码 1；正常执行 → 退出码 0                                             |
| T4  | P1  | 修复 run_tests.py | 1. 将 `python` 替换为 `sys.executable` 2. 修正测试路径逻辑 3. 修正 `--cov` 路径为 `dev/src`                                                                                                                                         | `python3 tests/run_tests.py all` 一键可执行                                      |

**第一阶段A 完成标志**：`python3 -m pytest -m "basic and not slow"` 全部通过，CLI 退出码行为正确，无任何导入报错。

#### 第一阶段B：结构重构 + 预处理集成（预计 3-4 天）

> **原则**：在 A 的稳定基线上执行目录大迁移和预处理集成。每一步都通过已修复的测试套件回归验证。

| 编号  | 优先级 | 任务              | 详细说明                                                                                                                                                                                                               | 验证标准                                                                        |
| --- | --- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------- |
| T5  | P1  | 集成预处理流水线        | 1. 让 `asr_metrics_refactored.py` 的 `preprocess_text()` 使用 `PreprocessingPipeline` 2. 移除对 jiwer 预处理功能的调用 3. 在 GUI/CLI 中暴露预处理配置选项（可选）                                                                                | 移除 jiwer 后，全部测试仍通过                                                          |
| T5b | P1  | 目录重组 + 包化       | 执行第九章方案：封存 `dev/src/` → `dev/v1.0-archive/`，新建 `src/cer_tool/` 包，创建 `pyproject.toml`，`pip install -e .` | 所有测试在新目录结构下全部通过 |


#### 第二阶段：依赖精简与工程质量提升（P2，预计 2-3 天）


| 编号  | 优先级 | 任务           | 详细说明                                                                                                                                                                  | 验证标准                      |
| --- | --- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------- |
| T6  | P2  | 移除 jiwer 依赖  | 基于 T5 完成后，从 `requirements.txt` 和 `Pipfile` 中移除 jiwer                                                                                                                  | 安装依赖后不含 jiwer，所有功能正常      |
| T7  | P2  | 移除 pandas 依赖 | 1. 将 `export_results()` 中的 `pd.DataFrame.to_csv()` 替换为标准库 `csv.writer` 2. 从 `requirements.txt` 和 `Pipfile` 中移除 pandas                                                 | 安装依赖后不含 pandas，CSV 导出功能正常 |
| T8  | P2  | 统一依赖分层       | 1. 修正 `Pipfile` 中 thulac/hanlp/torch 为可选依赖 2. 保持 `requirements.txt`、`Pipfile`、`README.md` 三处口径一致 3. 考虑引入 `pyproject.toml`，使用 extras 管理可选依赖（如 `pip install .[thulac]`） | 三个文件的依赖声明完全一致             |
| T9  | P2  | 提取公共模块       | 1. 创建 `src/cer_tool/file_utils.py`，抽取多编码文件读取逻辑 2. GUI 和 CLI 共用同一个 `read_file_with_multiple_encodings()`                                                                    | 无重复代码，文件读取行为一致            |
| T10 | P2  | CLI 增强       | 1. 增加 `--version` 参数 2. 增加 JSON 输出格式支持 3. 批处理增加 `--recursive` 选项 4. 批处理利用 ASRMetrics 实例缓存                                                                             | CLI 功能测试通过                |
| T11 | P2  | 修正架构文档       | 1. 移除代码中未实现的组件描述（MessageBus、DIContainer 等） 2. 保持文档与实际代码一致 3. 将未实现部分移至"未来规划"章节                                                                                         | 文档评审通过                    |


#### 第三阶段：功能增强与体验升级（P2+，预计 5-7 天）


| 编号  | 优先级 | 任务       | 详细说明                                                                                 | 验证标准                                       |
| --- | --- | -------- | ------------------------------------------------------------------------------------ | ------------------------------------------ |
| T12 | P2  | 文件名自动配对  | 1. 实现按文件名相似度自动匹配 2. 支持前缀/后缀/编号匹配规则 3. GUI 中提供"自动配对"按钮                                | 文件名为 `001_asr.txt` 和 `001_ref.txt` 时自动配对成功 |
| T13 | P2  | 支持更多文件格式 | 1. 支持 .csv（每行一句）格式 2. 支持 .json 格式 3. 支持 .srt 字幕格式                                    | 各格式文件的导入和计算正常                              |
| T14 | P2  | 增加对齐可视化  | 1. 在差异高亮 Tab 中增加字符级对齐视图 2. 用红/绿/黄颜色标注替换/插入/删除                                        | 对齐视图正确显示错误类型                               |
| T15 | P2  | 批量统计分析增强 | 1. 句子级 CER 排序（定位最差句子） 2. 批次级加权统计（总字符数为权重） 3. CER 分布区间统计                              | 统计结果在整体统计 Tab 中展示                          |
| T16 | P3  | GUI 视觉升级 | 1. 评估迁移到 `customtkinter`（迁移成本最低） 2. 或评估 PySide6 方案 3. 提升整体视觉风格                       | 界面现代化，功能不退化                                |
| T17 | P3  | 打包与分发    | 1. 创建 `pyproject.toml` 2. 配置 PyInstaller 或 cx_Freeze 多平台打包 3. 生成 macOS/Windows 可执行文件 | 双平台可执行文件可正常运行                              |


### 4.3 任务依赖关系

```
【第一阶段A：稳定性修复】          【第一阶段B：结构重构】
T1（pytest 修复）──┐
T2（边界修复）  ──┤
T3（CLI 退出码）──┤── A 完成 ─── T5（预处理集成）──┐
T4（run_tests）──┘               T5b（目录重组）──┤── B 完成
                                                  │
【第二阶段：依赖精简 + 工程质量】                         │
                         T6（移除 jiwer，依赖 T5）◄──┘
                         T7（移除 pandas）
                         T8（统一依赖分层，pyproject.toml 已在 B 中引入）
                         T9（提取公共模块）
                         T10（CLI 增强）
                         T11（修正文档）
                                  │
【第三阶段：功能增强】                 │
                         T12（自动配对）
                         T13（多格式）
                         T14（对齐可视化）
                         T15（统计增强）
                         T16（GUI 升级，可并行）
                         T17（打包分发，可并行）
```

**关键路径**：T1 → T5 → T5b → T6 → 第二阶段

> **风险控制**：第一阶段拆为 A/B 两部分后，A 阶段完成即可获得一个"可测试的稳定基线"。若 B 阶段的目录迁移遇到预期外的问题（如深层依赖的路径耦合），不会影响已修复的行为缺陷。

---

## 五、改版后依赖对比

### 5.1 当前依赖（V1）

```
核心依赖（4个）：
  jieba >= 0.42.1
  jiwer >= 2.5.0        ← 仅用了预处理，可移除
  pandas >= 1.3.0       ← 仅用了CSV导出，可移除
  python-Levenshtein >= 0.12.2

可选依赖（3个，但 Pipfile 当必装）：
  thulac >= 0.2.0
  hanlp >= 2.1.0
  torch（隐式依赖）
```

### 5.2 目标依赖（V2）

```
核心依赖（2个）：
  jieba >= 0.42.1
  python-Levenshtein >= 0.12.2

可选依赖（通过 extras 管理）：
  pip install cer-matchingtools[thulac]   → thulac >= 0.2.0
  pip install cer-matchingtools[hanlp]    → hanlp >= 2.1.0, torch
  pip install cer-matchingtools[all]      → 以上全部
```

**安装体积变化（待实测）**：

以下为静态预估值，正式开发时需按下表实测后回填实际数据：

| 安装方式 | 平台 | V1 体积（预估） | V2 体积（预估） | V2 体积（实测） | 安装耗时（实测） |
|---------|------|--------------|--------------|--------------|-------------|
| core（核心） | macOS | ~150 MB | ~10 MB | *TODO* | *TODO* |
| core（核心） | Linux (x86_64) | ~150 MB | ~10 MB | *TODO* | *TODO* |
| core（核心） | Windows 10/11 | ~150 MB | ~10 MB | *TODO* | *TODO* |
| `.[hanlp]` | macOS | ~2.5 GB | ~2.5 GB | *TODO* | *TODO* |
| `.[hanlp]` | Linux (x86_64) | ~2.5 GB | ~2.5 GB | *TODO* | *TODO* |
| `.[all]` | macOS | ~2.6 GB | ~2.6 GB | *TODO* | *TODO* |

> **注意**：预估值基于 `pip download --no-deps` 的包大小累加，实际安装可能因间接依赖变动。建议在 T6/T7 完成后，使用干净虚拟环境（`python -m venv --clear`）分别实测三种安装方式并回填此表。

---

## 六、改版后质量验证标准

### 6.1 自动化测试门禁


| 检查项         | 命令                                 | 通过标准               |
| ----------- | ---------------------------------- | ------------------ |
| pytest 收集   | `python3 -m pytest --collect-only` | 0 error, 0 warning |
| 基础测试        | `python3 -m pytest -m basic`       | 全部通过               |
| 边界测试        | `python3 -m pytest -m boundary`    | 全部通过（含新增 4 组）      |
| CLI 测试      | `python3 -m pytest -m cli`         | 退出码行为正确            |
| 无 jiwer 验证  | `pip show jiwer`                   | 返回"not found"      |
| 无 pandas 验证 | `pip show pandas`                  | 返回"not found"      |
| 一键测试        | `python3 tests/run_tests.py all`   | 全部通过               |
| **代码风格检查** | `ruff check src/cer_tool/`         | 0 error（可配置忽略规则）   |
| **类型检查**   | `mypy src/cer_tool/ --ignore-missing-imports` | 核心模块（`metrics.py`、`preprocessing.py`、`cli.py`）0 error |

> **说明**：`ruff` 集成了 flake8、isort、pyupgrade 等多种检查，单工具即可覆盖代码风格和导入排序。`mypy` 初期仅强制要求核心计算模块通过，GUI 模块（tkinter 类型支持较弱）可后续逐步推进。两项工具已包含在 `pyproject.toml` 的 `[project.optional-dependencies] dev` 中。


### 6.2 手动验收清单


| 场景        | 验收动作                                                      | 预期结果                        |
| --------- | --------------------------------------------------------- | --------------------------- |
| 空文件处理     | GUI 导入一个空 .txt 文件并计算                                      | 显示 CER=1.0（或 0.0 取决于配对），无崩溃 |
| CLI 失败退出码 | `python3 cli.py --asr /nonexist --ref /nonexist; echo $?` | 输出 1                        |
| CSV 导出    | GUI 计算后导出 CSV                                             | 文件可被 Excel/Numbers 正常打开     |
| 分词器切换     | GUI 中切换 jieba → thulac → hanlp                            | 状态正确显示，计算结果合理               |
| 预处理配置     | CLI 使用不同预处理配置                                             | 结果符合预期差异                    |


---

## 七、改版后文档更新清单

改版完成后，以下文档需同步更新：


| 文档                                | 更新内容                               |
| --------------------------------- | ---------------------------------- |
| `README.md`                       | 依赖说明（移除 jiwer/pandas）、安装方式更新、新功能说明 |
| `Cer-MatchingTools-V1-架构设计.md`    | 移除未实现组件、更新预处理流水线集成描述、版本号更新         |
| `Cer-MatchingTools-V1-需求规格说明书.md` | 增加新功能需求（自动配对、多格式等）                 |
| `Cer-MatchingTools-V1-项目管理.md`    | 更新开发计划、任务状态、代码统计                   |
| `tests/README_测试策略.md`            | 更新测试组织方式和标记说明                      |


---

## 八、总结

### 核心改版理念：三个关键词

1. **止血**（第一阶段）：修复测试、边界、退出码、流水线集成 —— 让项目回到"工程可信"状态
2. **瘦身**（第二阶段）：移除 jiwer + pandas，统一依赖分层 —— 大幅缩减核心安装体积（预估 >90%，待实测确认）
3. **进化**（第三阶段）：自动配对、多格式、对齐可视化 —— 向专业评测能力迈进一步

### 预期成果


| 指标         | V1 现状     | V2 目标                      |
| ---------- | --------- | -------------------------- |
| pytest 可运行 | 否（收集阶段报错） | 是（一键可执行）                   |
| 核心依赖数      | 4 个       | 2 个                        |
| 核心安装体积     | ~150 MB   | ~10 MB（预估，待实测）              |
| 空文本 CER    | 3.0（错误）   | 1.0（正确）                    |
| CLI 退出码    | 永远 0      | 失败返回 1                     |
| 预处理流水线     | 已设计未集成    | 已集成可配置                     |
| 文件格式支持     | 仅 .txt    | .txt / .csv / .json / .srt |
| 文件配对方式     | 仅手动       | 自动 + 手动                    |


---

## 九、项目目录结构整改方案

### 9.1 现状诊断

当前源码存放在 `dev/src/` 路径下，存在以下 5 个结构性问题：


| #   | 问题                           | 说明                                                                                                                                       |
| --- | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `**dev/src/` 嵌套层无工程价值**      | `dev/` 这一层既不是 Python 包，也不被任何工具链识别。所有测试文件都需要 `sys.path.insert(0, '../dev/src')` 来定位源码，路径深度无谓增加。Python 社区标准做法是 `项目根/src/包名/`。              |
| 2   | **源码文件散乱、无包结构**              | `asr_metrics_refactored.py`、`cli.py`、`main_with_tokenizers.py`、`preprocessing_pipeline.py` 平铺在 `src/` 根，缺少 `__init__.py`，无法被正常 `import`。 |
| 3   | **文件名暗示"临时性"**               | `asr_metrics_refactored.py`（带 `refactored`）、`main_with_tokenizers.py`（带 `with_tokenizers`）暴露了迭代痕迹，不适合作为正式代码命名。                           |
| 4   | `**v0.1.0/` 嵌在源码内**          | `dev/src/v0.1.0/` 包含旧版代码，放在当前源码目录下易被误引用，应与活跃源码分离。                                                                                        |
| 5   | `**requirements.txt` 位置不规范** | 依赖声明文件放在 `dev/src/` 内，而非项目根目录，不符合 Python 打包规范，也不便于 CI/CD 工具发现。                                                                           |


### 9.2 整改方案

#### 核心思路

1. 将现有 `dev/src/` 中的全部文件**封存**到 `dev/v1.0-archive/` 中，保留完整的 V1 历史
2. 在**项目根目录**新建 `src/cer_tool/` 作为正式的 Python 包
3. 将 `requirements.txt` 移至项目根目录
4. 同步更新 `.cursorrules`、`.gitignore`、测试文件中的路径引用

#### 9.2.1 V2 目标目录结构

```
cer-matchingtools/                          # 项目根
├── .cursorrules                            # [更新] 修正目录约定
├── .gitignore                              # [更新] 适配新路径
├── Pipfile                                 # [更新] 统一依赖声明
├── requirements.txt                        # [移至根目录] 核心依赖
├── requirements-dev.txt                    # [新增] 开发/测试依赖
├── README.md
├── README_cn.md
├── LICENSE
│
├── src/                                    # [新建] 正式源码目录
│   └── cer_tool/                           # [新建] Python 包
│       ├── __init__.py                     # 包入口，暴露版本号和公共接口
│       ├── __main__.py                     # 支持 python -m cer_tool 运行
│       ├── metrics.py                      # [改名自 asr_metrics_refactored.py]
│       ├── cli.py                          # CLI 命令行入口
│       ├── gui.py                          # [改名自 main_with_tokenizers.py]
│       ├── preprocessing.py                # [改名自 preprocessing_pipeline.py]
│       └── tokenizers/                     # [简化自 text_tokenizers/tokenizers/]
│           ├── __init__.py                 # 合并原 text_tokenizers/__init__.py
│           ├── base.py                     # 抽象基类和异常定义
│           ├── factory.py                  # 工厂类
│           ├── jieba_tokenizer.py          # Jieba 分词器
│           ├── thulac_tokenizer.py         # THULAC 分词器
│           └── hanlp_tokenizer.py          # HanLP 分词器
│
├── dev/                                    # 开发辅助目录
│   ├── output/                             # 开发过程临时输出
│   │   └── .gitkeep
│   └── v1.0-archive/                       # [新建] V1 源码完整封存
│       ├── README.md                       # 封存说明
│       ├── asr_metrics_refactored.py
│       ├── cli.py
│       ├── main_with_tokenizers.py
│       ├── preprocessing_pipeline.py
│       ├── requirements.txt
│       ├── text_tokenizers/...             # 原始分词器模块
│       └── v0.1.0/...                      # V0.1.0 历史代码
│
├── pyproject.toml                          # [新增] 包定义 + 依赖分层 + 构建配置
│
├── tests/                                  # 测试目录（详见第十章）
│   ├── conftest.py                         # 共享 fixture（无需 sys.path hack）
│   └── ...
│
├── docs/                                   # 项目文档
│   ├── V1/                                 # V1 文档归档
│   └── CER-Analysis-Tool-V2-改版建议书.md    # [已改名] 使用新项目前缀
│
├── release/                                # 发布产物
├── assets/                                 # 静态资源
└── ref/                                    # 参考资料（只读）
```

#### 9.2.2 文件改名映射


| V1 路径                               | V2 路径                           | 改名原因                                  |
| ----------------------------------- | ------------------------------- | ------------------------------------- |
| `dev/src/asr_metrics_refactored.py` | `src/cer_tool/metrics.py`       | 移除 `refactored` 后缀，名称简洁化              |
| `dev/src/main_with_tokenizers.py`   | `src/cer_tool/gui.py`           | 按职责命名，移除 `with_tokenizers` 后缀         |
| `dev/src/preprocessing_pipeline.py` | `src/cer_tool/preprocessing.py` | 名称简洁化，`pipeline` 概念在类名中体现             |
| `dev/src/cli.py`                    | `src/cer_tool/cli.py`           | 保持不变                                  |
| `dev/src/text_tokenizers/`          | `src/cer_tool/tokenizers/`      | 消除 `text_tokenizers/tokenizers/` 双层嵌套 |
| `dev/src/requirements.txt`          | `requirements.txt`（项目根）         | 符合 Python 项目规范                        |


#### 9.2.3 包内导入变化

**V1（跨模块导入靠 `sys.path` hack）**：

```python
# 测试文件中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../dev/src'))
from asr_metrics_refactored import ASRMetrics
from text_tokenizers import get_available_tokenizers
```

**V2（正式包导入，基于 `pip install -e .`）**：

```python
# 包内模块互相引用（相对导入或绝对导入均可）
from cer_tool.tokenizers import get_available_tokenizers
from cer_tool.metrics import ASRMetrics
from cer_tool.preprocessing import PreprocessingPipeline

# 测试文件中（通过 pip install -e . 安装包，无需 sys.path hack）
from cer_tool.metrics import ASRMetrics
```

#### 9.2.4 `.cursorrules` 同步更新要点

需将 `.cursorrules` 中以下约定修改：


| 原条目                                     | 修改为                                           |
| --------------------------------------- | --------------------------------------------- |
| "开发任务使用的目录是/dev目录，主要包括/src和/output两个目录" | "源码目录为 /src/cer_tool/，开发辅助输出目录为 /dev/output/" |
| "所有代码都放在/dev/src目录中"                    | "所有代码都放在 /src/cer_tool/ 目录中"                  |


#### 9.2.5 关联影响清单


| 受影响的文件/配置                    | 需要修改的内容                                                              |
| ---------------------------- | -------------------------------------------------------------------- |
| `.cursorrules`               | 更新目录约定（9.2.4 所述）                                                     |
| `.gitignore`                 | 更新 `/dev/output/*` 路径、添加 `/dev/v1.0-archive/` 相关规则                   |
| `Pipfile`                    | 无需移动，但需清理可选依赖为非必装                                                    |
| `tests/conftest.py`          | 仅放置共享 fixture，包路径由 `pip install -e .` 管理 |
| `tests/pytest.ini`           | `testpaths` 保持 `.`，无需改动                                              |
| `README.md` / `README_cn.md` | 更新项目结构说明和使用示例中的路径                                                    |


### 9.3 实施步骤（建议顺序）


| 步骤  | 操作                                                        | 风险              |
| --- | --------------------------------------------------------- | --------------- |
| 1   | 创建 `dev/v1.0-archive/` 目录，将 `dev/src/` 全部内容复制过去           | 低               |
| 2   | 创建 `src/cer_tool/` 包目录结构，新建 `__init__.py` 和 `__main__.py` | 低               |
| 3   | 将源码文件按映射表复制到新位置，同时执行改名                                    | 中（需检查内部 import） |
| 4   | 修改包内所有 `import` 语句，适配新的包结构                                | 中（核心步骤）         |
| 5   | 将 `requirements.txt` 移到项目根目录                              | 低               |
| 6   | 更新 `.cursorrules`、`.gitignore`、`README`                   | 低               |
| 7   | 创建 `pyproject.toml`，执行 `pip install -e .`，更新 `conftest.py`  | 低               |
| 8   | 验证：`pytest --collect-only` 和基础用例通过                        | 验证步骤            |
| 9   | 确认无误后，删除 `dev/src/` 目录                                    | 最后执行            |


### 9.4 变更前后对比


| 维度          | V1 (当前)                                  | V2 (目标)                                             |
| ----------- | ---------------------------------------- | --------------------------------------------------- |
| 源码路径        | `dev/src/*.py`（散文件）                      | `src/cer_tool/*.py`（正式包）                            |
| 路径深度（从根到源码） | 2 层（`dev/src/`）                          | 2 层（`src/cer_tool/`），但语义更清晰                         |
| Python 包结构  | 无（不可 import）                             | 完整包（支持 `from cer_tool import ...`）                  |
| 入口命令        | `python dev/src/main_with_tokenizers.py` | `python -m cer_tool` 或 `python src/cer_tool/gui.py` |
| 分词器模块路径     | `text_tokenizers/tokenizers/`（2 层嵌套）     | `tokenizers/`（1 层）                                  |
| 依赖文件        | `dev/src/requirements.txt`               | `requirements.txt`（根目录）                             |
| 测试导入        | `sys.path.insert(0, '../dev/src')`       | `pip install -e .`，直接 `import cer_tool`              |
| V1 历史代码     | 与活跃源码混在一起                                | 独立封存在 `dev/v1.0-archive/`                           |
| `v0.1.0` 代码 | 嵌在 `dev/src/v0.1.0/`                     | 封存在 `dev/v1.0-archive/v0.1.0/`                      |


### 9.5 兼容迁移策略

V2 涉及包路径变更（`dev/src/*.py` → `src/cer_tool/*.py`）、类名重命名（`ASRComparisonTool` → `CERAnalysisTool`）和 CLI 工具名调整，需要为已有脚本或上下游调用者提供过渡期。

#### 9.5.1 兼容窗口期

| 版本 | 期限 | 说明 |
|------|------|------|
| V2.0.x | 发布后 **1 个小版本**（约 2-4 周） | 保留旧入口的兼容包装，标记 `DeprecationWarning` |
| V2.1.0 | — | 移除全部兼容包装，旧入口调用直接报 `ImportError` |

#### 9.5.2 兼容包装实现

在 `src/cer_tool/__init__.py` 中添加旧名到新名的转发：

```python
# src/cer_tool/__init__.py
import warnings

# 旧类名 → 新类名（V2.0.x 兼容期内保留）
def __getattr__(name):
    _compat_map = {
        "ASRComparisonTool": "CERAnalysisTool",
        "ASRMetrics": "ASRMetrics",          # 类名未变，但路径变了
    }
    if name in _compat_map:
        warnings.warn(
            f"{name} 已更名为 {_compat_map[name]}，"
            f"请使用 from cer_tool.metrics import {_compat_map[name]}。"
            f"旧名称将在 V2.1.0 中移除。",
            DeprecationWarning,
            stacklevel=2,
        )
        # 实际导入并返回
        from cer_tool import metrics, gui
        return getattr(metrics, _compat_map[name], None) or getattr(gui, _compat_map[name], None)
    raise AttributeError(f"module 'cer_tool' has no attribute {name}")
```

#### 9.5.3 迁移映射表

| 旧路径 / 旧名称 | 新路径 / 新名称 | 移除版本 |
|----------------|----------------|---------|
| `from asr_metrics_refactored import ASRMetrics` | `from cer_tool.metrics import ASRMetrics` | V2.1.0 |
| `from main_with_tokenizers import ASRComparisonTool` | `from cer_tool.gui import CERAnalysisTool` | V2.1.0 |
| `python dev/src/main_with_tokenizers.py` | `python -m cer_tool` 或 `cer-tool` | V2.1.0 |
| `python dev/src/cli.py --asr ... --ref ...` | `python -m cer_tool.cli --asr ... --ref ...` | V2.1.0 |
| `from text_tokenizers import get_available_tokenizers` | `from cer_tool.tokenizers import get_available_tokenizers` | V2.1.0 |

> **建议**：在 `CHANGELOG.md` 或 `README.md` 的"升级指南"段落中列出此映射表，方便已有用户迁移。

---

## 十、测试体系整改方案

### 10.1 现状诊断

当前 `tests/` 目录下共有 **20 个测试相关文件**（含 `.py` 和 `.md`），以及 1 个子目录 `test-v0.1.0/`。经过逐文件审查，发现以下核心问题：

1. **pytest 无法运行**：`pytest.ini` 中 `python_files = test_*.py *_test.py` 的模式过宽，将非 pytest 脚本也收集进来，导致收集阶段报错。
2. **脚本类型混杂**：真正的 pytest 用例只有 1 个文件（`test_with_pytest_marks.py`），其余 `.py` 文件全部是"手动运行的验证脚本"（`if __name__ == "__main__"` 模式），不含 pytest 断言或标记。
3. **大量重复覆盖**：多个脚本测试几乎完全相同的功能（如分词器基本功能、ASRMetrics 基本计算），只是输出格式不同。
4. **导入路径不一致**：至少 3 种不同的 `sys.path` 设置方式，其中 2 种已失效。
5. **文档与实际脱节**：`test_cases.md` 和 `test_plan.md` 包含大量"计划中但未实现"的测试用例代码，但这些代码从未被写入实际可执行的 `.py` 文件中。

### 10.2 逐文件评估

#### 10.2.1 可保留并改造的文件


| 文件                           | 当前类型      | 评估                                               | 处置建议                                     |
| ---------------------------- | --------- | ------------------------------------------------ | ---------------------------------------- |
| `test_with_pytest_marks.py`  | pytest 用例 | **唯一真正的 pytest 文件**，有 `@pytest.mark` 标记，有断言，结构良好 | **保留**，作为 V2 测试基础，扩充用例                   |
| `test_edit_ops_accurate.py`  | 手动脚本      | 含 8 个有价值的编辑距离测试场景，有 `assert` 断言                  | **改造**为 pytest 用例，合并到核心算法测试模块            |
| `test_normalize_strategy.py` | 手动脚本      | 含 5 个文本标准化测试场景，但只有 print 输出没有断言                  | **改造**为 pytest 用例，添加断言，合并到核心算法测试模块       |
| `performance_test.py`        | 手动脚本      | 性能基准测试，有实际价值                                     | **改造**为 pytest 用例，标记 `@pytest.mark.slow` |
| `pytest.ini`                 | 配置文件      | 需要修正收集规则                                         | **修改**：移除 `*_test.py` 模式，收紧 `testpaths`  |
| `run_tests.py`               | 运行脚本      | 概念有用但实现有 3 个 bug                                 | **修复**：`sys.executable`、路径修正、cov 路径      |


#### 10.2.2 高度重复、建议合并或删除的文件


| 文件                   | 当前类型 | 与谁重复                                                            | 处置建议                                       |
| -------------------- | ---- | --------------------------------------------------------------- | ------------------------------------------ |
| `test_system.py`     | 手动脚本 | 与 `test_tokenizers.py` 功能 ~90% 重复（都是遍历分词器做 cut/posseg/tokenize） | **删除**，测试内容合并到 `test_with_pytest_marks.py` |
| `test_tokenizers.py` | 手动脚本 | 与 `test_system.py` 功能 ~90% 重复                                   | **删除**，测试内容合并到 `test_with_pytest_marks.py` |
| `simple_test.py`     | 手动脚本 | 是 `test_tokenizers.py` 的简化版，零新增覆盖                               | **删除**                                     |
| `quick_test.py`      | 手动脚本 | 与 `simple_test.py` 功能 ~80% 重复，额外检查了文件存在性                        | **删除**，文件存在性检查无测试价值                        |


#### 10.2.3 特定用途、建议归档到 `tests/scripts/` 的文件


| 文件                             | 当前类型     | 说明                                                            | 处置建议                                         |
| ------------------------------ | -------- | ------------------------------------------------------------- | -------------------------------------------- |
| `test_architecture_demo.py`    | 架构演示     | 使用 Mock 类演示架构设计，**不是测试**，是教学/演示材料（494 行）                      | **移入** `tests/scripts/`，不参与 pytest 收集        |
| `hanlp_tok_only.py`            | HanLP 实验 | 独立的 HanLP 轻量化分词器实验代码，不依赖项目模块                                  | **移入** `tests/scripts/`                      |
| `hanlp_tokenizer_optimized.py` | HanLP 实验 | 独立的优化版 HanLP 分词器原型代码，不依赖项目模块                                  | **移入** `tests/scripts/`                      |
| `test_tokenizer_issue.py`      | 调试脚本     | 调试 thulac/hanlp 模型独立性问题的一次性脚本，`sys.path` 已错误                  | **移入** `tests/scripts/`                      |
| `advanced_tokenizer_test.py`   | 调试脚本     | 对比 thulac/hanlp 分词差异的调试脚本，`sys.path` 已错误（**P0 报错的元凶之一**）      | **移入** `tests/scripts/`                      |
| `test_version_fix.py`          | 验证脚本     | 验证分词器版本获取修复的一次性脚本，`sys.path` 已错误（指向 `../src` 而非 `../dev/src`） | **移入** `tests/scripts/`                      |
| `test_hanlp_integration.py`    | 验证脚本     | HanLP 集成验证，`sys.path` 已错误（指向 `../src`）                        | **移入** `tests/scripts/`，关键测试逻辑提取到 pytest 用例中 |


#### 10.2.4 历史版本文件


| 文件/目录                           | 说明                                                 | 处置建议                            |
| ------------------------------- | -------------------------------------------------- | ------------------------------- |
| `test-v0.1.0/example_test.py`   | v0.1.0 版本的测试脚本，导入 `src.utils` 已完全失效（**P0 报错元凶之二**） | **保持在原位**，在 `pytest.ini` 中排除该目录 |
| `test-v0.1.0/check_accuracy.py` | v0.1.0 版本的 CLI 工具，导入 `src.utils` 已失效               | 同上                              |
| `test-v0.1.0/example_ref.txt`   | 测试数据                                               | 同上                              |
| `test-v0.1.0/example_hyp.txt`   | 测试数据                                               | 同上                              |


#### 10.2.5 文档文件


| 文件                          | 说明                                   | 处置建议                                                          |
| --------------------------- | ------------------------------------ | ------------------------------------------------------------- |
| `test_cases.md`             | 包含大量"计划中但未实现"的测试用例伪代码（600+ 行）        | **删除**或标注为"历史参考"，V2 中实际测试用例应直接写在 `.py` 文件中                    |
| `test_plan.md`              | 与 `test_cases.md` 内容 ~70% 重复的测试计划伪代码 | **删除**，与 `test_cases.md` 合并价值也不大，V2 测试策略以 `README_测试策略.md` 为准 |
| `README_测试策略.md`            | 测试策略文档，内容合理                          | **保留并更新**，配合 V2 整改方案刷新内容                                      |
| `test_多分词器功能_2024-12-19.md` | 历史测试总结                               | **保留**作为历史记录                                                  |
| `requirements-test.txt`     | 测试依赖文件                               | **保留并更新**（当前为空文件）                                             |


### 10.3 V2 目标测试架构

#### 10.3.1 目录结构

```
tests/
├── conftest.py                         # [新增] pytest 全局 fixture 和 sys.path 配置
├── pytest.ini                          # [修改] 收紧收集规则
├── requirements-test.txt               # [更新] 填写测试依赖
├── run_tests.py                        # [修复] 解释器、路径、cov 修正
├── README_测试策略.md                   # [更新] 配合 V2 刷新
│
├── test_core_metrics.py                # [新增] 核心指标计算测试（合并多个文件的精华）
├── test_tokenizers_unit.py             # [新增] 分词器单元测试
├── test_preprocessing.py               # [新增] 预处理流水线测试
├── test_cli.py                         # [新增] CLI 工具测试
├── test_boundary.py                    # [新增] 边界条件测试（空文本、特殊字符等）
├── test_integration.py                 # [改造自 test_with_pytest_marks.py] 集成测试
├── test_performance.py                 # [改造自 performance_test.py] 性能测试
│
├── scripts/                            # [新增目录] 非 pytest 脚本归档
│   ├── README.md                       # 说明：这些是手动运行的脚本，不参与 pytest
│   ├── test_architecture_demo.py       # 架构演示
│   ├── hanlp_tok_only.py              # HanLP 实验
│   ├── hanlp_tokenizer_optimized.py   # HanLP 优化原型
│   ├── advanced_tokenizer_test.py     # 分词器对比调试
│   ├── test_tokenizer_issue.py        # 模型独立性调试
│   ├── test_version_fix.py            # 版本获取验证
│   └── test_hanlp_integration.py      # HanLP 集成验证
│
├── test-v0.1.0/                        # [保持原位] 历史版本测试，pytest 排除
│   ├── check_accuracy.py
│   ├── example_test.py
│   ├── example_ref.txt
│   └── example_hyp.txt
│
└── test_多分词器功能_2024-12-19.md     # [保留] 历史测试总结
```

#### 10.3.2 关键配置变更

**pytest.ini 修改方案**：

```ini
[pytest]
# 只收集 test_*.py 格式的文件（移除 *_test.py 避免误收非 pytest 脚本）
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# 测试根目录
testpaths = .

# 排除不应递归进入的子目录（替代无效的 collect_ignore_glob）
norecursedirs = scripts test-v0.1.0 .git __pycache__

# 也可在 addopts 中用 --ignore 精确排除单个文件（如有需要）
# addopts = --ignore=scripts/ --ignore=test-v0.1.0/

# 标记定义
markers =
    basic: 基础测试 - 仅依赖 jieba
    optional: 可选分词器测试 - 需要 thulac 或 hanlp
    slow: 慢速测试
    boundary: 边界条件测试
    cli: CLI 工具测试
    pipeline: 预处理流水线测试
    unit: 单元测试
    integration: 集成测试
```

**包安装方案（推荐，替代 `sys.path` hack）**：

在项目根目录新增 `pyproject.toml`，使测试环境通过 `pip install -e .` 安装包，直接验证真实包安装链路：

```toml
# pyproject.toml（项目根目录）
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "cer-tool"
version = "2.0.0"
requires-python = ">=3.12"
dependencies = [
    "jieba>=0.42.1",
    "python-Levenshtein>=0.12.2",
]

[project.optional-dependencies]
thulac = ["thulac>=0.2.0"]
hanlp = ["hanlp>=2.1.0", "torch"]
all = ["cer-tool[thulac]", "cer-tool[hanlp]"]
dev = ["pytest>=6.0", "pytest-cov", "ruff", "mypy"]

[tool.setuptools.packages.find]
where = ["src"]
```

开发环境初始化命令：

```bash
# 以 editable 模式安装，测试环境直接使用真实包路径
pip install -e ".[dev]"
```

此方案下 `conftest.py` 仅需要放置共享 fixture，无需任何 `sys.path` 操作：

```python
# tests/conftest.py
import pytest

@pytest.fixture
def jieba_metrics():
    """共享的 jieba ASRMetrics 实例"""
    from cer_tool.metrics import ASRMetrics
    return ASRMetrics(tokenizer_name='jieba')
```

> **注意**：`pyproject.toml` 同时解决了 T8（统一依赖分层）和 T17（打包分发）的部分需求，可提前在第一阶段引入。

#### 10.3.3 新增测试文件内容规划


| 文件                        | 来源                                                                         | 用例数（预估） | 标记                                |
| ------------------------- | -------------------------------------------------------------------------- | ------- | --------------------------------- |
| `test_core_metrics.py`    | 合并 `test_edit_ops_accurate.py` + `test_normalize_strategy.py` 的精华 + 新增边界用例 | 15-20   | `basic`, `unit`                   |
| `test_tokenizers_unit.py` | 从 `test_system.py`/`test_tokenizers.py` 提取有效断言                             | 10-15   | `basic`/`optional`, `unit`        |
| `test_preprocessing.py`   | 新写，覆盖 `cer_tool/preprocessing.py`                                          | 8-12    | `basic`, `pipeline`               |
| `test_cli.py`             | 新写，覆盖 `cer_tool/cli.py` 的参数解析、退出码、输出格式                                     | 8-10    | `basic`, `cli`                    |
| `test_boundary.py`        | 新写，覆盖空文本、仅标点、超长文本、特殊编码等边界                                                  | 10-15   | `basic`, `boundary`               |
| `test_integration.py`     | 改造自 `test_with_pytest_marks.py`，扩充端到端场景                                    | 10-12   | `basic`/`optional`, `integration` |
| `test_performance.py`     | 改造自 `performance_test.py`，添加断言和基准线                                         | 5-8     | `slow`                            |


**预计总用例数**：66-92 个（当前仅 ~12 个真正的 pytest 用例）

### 10.4 可删除文件清单

以下文件在整改完成后可安全删除：


| 文件                   | 删除理由                                               |
| -------------------- | -------------------------------------------------- |
| `test_system.py`     | 内容与 `test_tokenizers.py` 高度重复，价值已合并到新文件            |
| `test_tokenizers.py` | 内容与 `test_system.py` 高度重复，价值已合并到新文件                |
| `simple_test.py`     | `test_tokenizers.py` 的简化版，零新增覆盖                    |
| `quick_test.py`      | 与 `simple_test.py` 高度重复                            |
| `test_cases.md`      | 600+ 行未实现的伪代码，V2 用例直接写在 `.py` 中                    |
| `test_plan.md`       | 与 `test_cases.md` ~70% 重复，V2 以 `README_测试策略.md` 为准 |


### 10.5 整改前后对比


| 维度                      | 整改前（V1）        | 整改后（V2）                  |
| ----------------------- | -------------- | ------------------------ |
| `.py` 文件数               | 16 个           | 7 个正式用例 + 7 个归档脚本        |
| 真正的 pytest 用例数          | ~12 个（仅 1 个文件） | 66-92 个（7 个文件）           |
| `pytest --collect-only` | 报错，无法收集        | 正常收集所有用例                 |
| 边界条件覆盖                  | 无              | 10-15 个专项用例              |
| CLI 测试覆盖                | 无              | 8-10 个专项用例               |
| 预处理流水线覆盖                | 无              | 8-12 个专项用例               |
| `sys.path` 配置方式         | 至少 3 种，2 种已失效  | 统一 1 种（通过 `conftest.py`） |
| 导入路径一致性                 | 不一致            | 全部统一                     |


### 10.6 整改实施优先级

此测试整改与第四章中的改版任务关联如下：


| 改版任务                | 对应测试整改步骤                                                     | 优先级    |
| ------------------- | ------------------------------------------------------------ | ------ |
| T1（修复 pytest 收集）    | 10.3.2 修改 `pytest.ini` + 新增 `conftest.py` + 移动脚本到 `scripts/` | **P0** |
| T2（修复指标边界）          | 新增 `test_boundary.py`                                        | **P1** |
| T3（修复 CLI 退出码）      | 新增 `test_cli.py`                                             | **P1** |
| T4（修复 run_tests.py） | 修复 `run_tests.py`                                            | **P1** |
| T5（集成预处理流水线）        | 新增 `test_preprocessing.py`                                   | **P1** |
| T6-T7（移除依赖）         | 更新 `requirements-test.txt`，确保测试不依赖 jiwer/pandas              | **P2** |


---

## 十一、项目改名方案

### 11.1 改名概述

| 项目 | 内容 |
|------|------|
| **旧名称** | Cer-MatchingTools / CER-MatchingTools |
| **新名称** | CER-Analysis-Tool |
| **Python 包名** | `cer_tool`（保持不变，第九章已确定） |
| **改名原因** | "MatchingTools"含义模糊（像是"配对工具"），"Analysis-Tool"更准确地表达了"CER 分析工具"的定位 |

### 11.2 名称体系统一规范

为避免改名后又出现多种变体混用的问题，预先确定各场景的标准写法：

| 场景 | 标准写法 | 示例 |
|------|----------|------|
| 项目正式名称 | `CER-Analysis-Tool` | 文档标题、README |
| Git 仓库名 / 目录名 | `cer-analysis-tool` | 全小写 + 连字符 |
| Python 包名 | `cer_tool` | 下划线，简洁 |
| GUI 窗口标题 | `CER Analysis Tool` | 无连字符，空格分隔 |
| CLI 工具名 | `cer-tool` | 全小写 + 连字符 |
| 文档前缀（V2） | `CER-Analysis-Tool-V2-` | 替代原 `Cer-MatchingTools-V1-` |
| 代码中的类名 | `CERAnalysisTool`（替代 `ASRComparisonTool`） | 驼峰命名 |
| 代码注释/作者标注 | `CER-Analysis-Tool 项目组` | 替代 `CER-MatchingTools项目组` |

### 11.3 涉及改动的文件清单

经过全仓扫描，涉及改动的文件按类型分为 4 类：

#### 11.3.1 V2 活跃代码（必须改）

这些文件在 V2 目录重组后将成为活跃源码，**必须**更新名称。

| 文件（V1 路径 → V2 路径） | 引用位置 | 改动内容 |
|---------------------------|---------|----------|
| `dev/src/main_with_tokenizers.py` → `src/cer_tool/gui.py` | 第 14 行：`作者：CER-MatchingTools项目组` | 改为 `CER-Analysis-Tool 项目组` |
| 同上 | 第 53 行：`self.root.title("ASR字准确率对比工具 - 多分词器版本")` | 改为 `CER Analysis Tool - 多分词器版本` |
| 同上 | 第 32 行：`class ASRComparisonTool:` | 改为 `class CERAnalysisTool:` |
| 同上 | 第 1166 行：`app = ASRComparisonTool(root)` | 改为 `app = CERAnalysisTool(root)` |
| `dev/src/asr_metrics_refactored.py` → `src/cer_tool/metrics.py` | 第 18 行：`ASR字准确率计算类` | 改为 `CER 字准确率计算引擎` |
| `dev/src/cli.py` → `src/cer_tool/cli.py` | 第 4 行：`ASR字准确率计算工具 - 命令行接口` | 改为 `CER Analysis Tool - 命令行接口` |
| 同上 | 第 248 行：`description='ASR字准确率计算工具 - 命令行版本'` | 改为 `CER Analysis Tool - 命令行版本` |

**总计**：3 个源码文件，约 7 处改动

#### 11.3.2 项目配置与文档（必须改）

| 文件 | 引用位置 / 数量 | 改动内容 |
|------|-----------------|----------|
| `.cursorrules` | 第 17 行（1 处） | `"Cer-MatchingTools-V1-"` → V2 前缀 `"CER-Analysis-Tool-V2-"` |
| `README.md` | 第 158 行（1 处） | 目录名 `cer-matchingtools/` → `cer-analysis-tool/`（或保持实际目录名） |
| `README_cn.md` | 第 158 行（1 处） | 同上 |
| `Pipfile` | 无直接引用 | 不需要改名，但建议在注释中标注新项目名 |
| `docs/CER-Analysis-Tool-V2-改版建议书.md` | 9 处 | `Cer-MatchingTools` → `CER-Analysis-Tool`（本文档自身） |

**总计**：4 个配置/文档文件，约 12 处改动

#### 11.3.3 V1 归档文档（不改，加注释）

以下文件属于 V1 历史文档，已归档到 `docs/V1/` 目录。**建议不修改文件内容**（保持历史完整性），但文件名中的 `Cer-MatchingTools-V1-` 前缀保持不变。

| 文件 | 引用数 | 处置 |
|------|--------|------|
| `docs/V1/Cer-MatchingTools-V1-架构设计.md` | 1 处 | 不改，保持 V1 历史 |
| `docs/V1/Cer-MatchingTools-V1-需求规格说明书.md` | 1 处 | 不改，保持 V1 历史 |
| `docs/V1/Cer-MatchingTools-V1-项目管理.md` | 7 处 | 不改，保持 V1 历史 |
| `docs/V1/Cer-MatchingTools-V1-UI设计说明.md` | 0 处（文件名含旧名） | 不改，文件名保持 |
| `docs/V1/专家评审报告-评估与实施方案-20251023.md` | 2 处 | 不改，保持 V1 历史 |
| `docs/V1/新旧版本ASR字准统计工具性能分析对比报告.md` | 标题含旧名 | 不改 |

**总计**：6 个文件，**全部不改**

#### 11.3.4 V1 封存代码和历史测试（不改）

以下文件将封存到 `dev/v1.0-archive/` 或已在 `tests/` 中待归档，**不修改**。

| 文件 | 引用数 | 处置 |
|------|--------|------|
| `dev/src/v0.1.0/main.py` | 1 处 | 不改，封存到 `dev/v1.0-archive/` |
| `tests/test_system.py` | 1 处 | 不改，按第十章方案归档或删除 |
| `tests/quick_test.py` | 1 处 | 不改，按第十章方案删除 |
| `tests/test_多分词器功能_2024-12-19.md` | 5 处 | 不改，历史测试总结 |
| `tests/test-v0.1.0/check_accuracy.py` | 1 处 | 不改，历史版本 |
| `tests/test-v0.1.0/example_test.py` | 0 处 | 不改 |
| `release/cer-matchingtool-v0.1.0.exe` | 文件名含旧名 | 不改，V0.1.0 历史发布 |
| `assets/logo/cer-logo.png` | 文件名含旧名缩写 | 可保留，V2 如需新 logo 另行创建 |

**总计**：8 个文件，**全部不改**

### 11.4 特殊注意：Git 仓库名

当前 Git 仓库的本地目录名为 `cer-matchingtools`。如果需要一并修改：

| 操作 | 说明 | 风险 |
|------|------|------|
| 本地目录重命名 | 将 `cer-matchingtools/` 重命名为 `cer-analysis-tool/` | 低，但需更新 IDE 配置和终端路径 |
| 远程仓库重命名 | 如有 GitHub/GitLab 远程仓库，需在平台上 rename | 中，所有协作者需更新 remote URL |
| `.cursorrules` 中的路径 | 无硬编码的绝对路径，不受影响 | 无 |

**建议**：本地目录和远程仓库的改名可以在 V2 代码开发完成后再统一执行，避免开发期间频繁调整路径。

### 11.5 改名实施清单

按优先级排序：

| 步骤 | 操作 | 时机 | 优先级 |
|------|------|------|--------|
| 1 | 更新 `.cursorrules` 中的文档前缀 | 目录重组时（第九章） | P0 |
| 2 | V2 源码文件中的类名、窗口标题、注释 | 代码迁移时（第九章步骤 3-4） | P0 |
| 3 | CLI 的 `description` 字符串 | 代码迁移时 | P0 |
| 4 | `README.md` / `README_cn.md` 中的项目名和目录名 | V2 功能基本完成后统一更新 | P1 |
| 5 | 改版建议书自身的旧名引用 | 本轮编辑即可完成 | P1 |
| 6 | Git 本地目录 / 远程仓库改名 | V2 发布前 | P2 |
| 7 | 新 logo 制作（如需要） | V2 发布前 | P2 |

### 11.6 改动量总结

| 分类 | 文件数 | 改动处数 | 是否修改 |
|------|--------|---------|---------|
| V2 活跃源码 | 3 | ~7 | **是** |
| 项目配置与文档 | 4 | ~12 | **是** |
| V1 归档文档 | 6 | — | 否（保持历史） |
| V1 封存代码 + 历史测试 | 8 | — | 否（保持历史） |
| **合计需改动** | **7 个文件** | **~19 处** | — |

> **结论**：改名的实际代码改动量很小（7 个文件、约 19 处文本替换），且大部分改动会在第九章目录重组时自然完成——因为源码要从 `dev/src/` 复制到 `src/cer_tool/` 并重新整理 import，在复制过程中顺手替换名称即可，无需额外开发工时。

---

**本文档将作为 V2 迭代的指导文件，建议在正式开发前由项目组评审确认优先级和排期。**