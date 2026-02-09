# CER-Evaluation Skill 可行性分析

> **文档类型**：技术探讨  
> **日期**：2026-02-09  
> **背景**：探讨是否可以将 CER-Analysis-Tool 封装为 Anthropic Skills，让 AI 助手自动完成 ASR 质量评估闭环。

---

## 一、核心问题

**能否将 CER-Analysis-Tool 封装为一个 Skill，使 AI 助手（Claude / Cursor Agent）在用户提供 ASR 转写文本和标准参考文本后，自动完成 CER 计算、结果解读、质量报告生成——形成 ASR 质量评估的完整闭环？**

---

## 二、Skill 是什么（Anthropic 规范摘要）

根据 Anthropic 的 Skill Creator 规范，Skill 是一种**模块化、自包含的能力扩展包**，核心特征：

| 维度 | 说明 |
|------|------|
| **本质** | 给 AI 助手的"岗前培训手册"——把通用助手变成领域专家 |
| **四大能力** | 专业工作流、工具集成、领域知识、可复用资源 |
| **触发机制** | 通过 `name` + `description` 元数据自动匹配用户意图 |
| **渐进加载** | 元数据(~100词) → SKILL.md(<5k词) → 脚本/参考文档(按需) |
| **核心原则** | 精简（只补 Claude 不知道的）、自由度分级（脆弱操作用脚本，灵活任务用指引） |

### 标准目录结构

```
skill-name/
├── SKILL.md                # 必需：元数据 + 工作流指引
├── scripts/                # 可选：可执行脚本（确定性、高复用）
├── references/             # 可选：参考文档（按需加载到上下文）
└── assets/                 # 可选：输出资源（模板、图片等）
```

---

## 三、项目现状 vs Skill 需求对照

### 3.1 CER-Analysis-Tool 已具备的能力

| 能力 | 现状 | Skill 可用性 |
|------|------|-------------|
| CER / WER / 准确率计算 | `metrics.py` — 基于 Levenshtein 距离 | ✅ 核心引擎，直接复用 |
| 多分词器支持 | jieba / THULAC / HanLP，工厂+单例模式 | ✅ 作为可配置参数 |
| 文本预处理流水线 | `preprocessing.py` — 标点、全半角、数字、语气词等 | ✅ 降低计算噪声 |
| CLI 命令行接口 | `cer-tool --asr X --ref Y --format json` | ✅ **最关键**：AI 助手可直接调用 |
| JSON 结构化输出 | 含 summary + 逐对 results | ✅ AI 助手可解析 |
| 批量处理 | `--asr-dir` + `--ref-dir` | ✅ 支持目录级批处理 |
| 多编码读取 | UTF-8 / GBK / GB2312 / GB18030 自动探测 | ✅ 对中文 ASR 场景很实用 |

### 3.2 做成 Skill 还缺什么

| 缺口 | 说明 | 解决难度 |
|------|------|----------|
| **CER 质量等级标准** | 业界没有统一标准，但 Skill 需要告诉 Claude "CER=0.08 是好是坏" | 低：在 references/ 中定义分级表即可 |
| **错误模式分析指引** | 替换/删除/插入的比例代表什么？常见原因是什么？ | 低：领域知识文档 |
| **报告模板** | 输出的质量报告需要结构化格式 | 低：Markdown 模板 |
| **环境依赖** | `cer_tool` 需要 `pip install -e .` 预装 | 中：需在 SKILL.md 中说明前置条件 |

### 3.3 结论：**完全适合做成 Skill**

理由：
1. **有明确的 CLI 工具**：Claude 可以通过 Shell 调用 `cer-tool`，获取 JSON 结构化输出，无需理解内部实现
2. **工作流确定性高**：输入文件 → 调用 CLI → 解析 JSON → 生成报告，步骤固定
3. **领域知识价值大**：CER 的解读、ASR 错误模式分析、改进建议——这些是 Claude 通用知识中较薄弱的部分
4. **高复用性**：每次 ASR 评测都是相同工作流，符合 Skill 的"重复性任务"定位

---

## 四、Skill 设计方案

### 4.1 命名与触发

```yaml
---
name: cer-evaluation
description: >
  ASR（自动语音识别）字准确率（CER）评估工具。使用 CER-Analysis-Tool 的 CLI
  自动计算字符错误率，分析错误模式，生成结构化质量报告。
  当用户需要以下操作时触发：
  (1) 评估 ASR 转写质量 (2) 计算 CER/WER/字准确率
  (3) 对比 ASR 输出与标准文本 (4) 批量评测多个 ASR 结果
  (5) 生成 ASR 质量报告
---
```

### 4.2 目录结构

```
cer-evaluation/
├── SKILL.md                            # 工作流指引（< 300 行）
├── scripts/
│   └── cer_report.py                   # 报告生成脚本（调用 CLI + 格式化输出）
└── references/
    ├── quality-thresholds.md           # CER 质量分级标准 + 行业基准
    └── error-patterns.md               # ASR 常见错误模式 + 改进建议
```

### 4.3 SKILL.md 核心工作流（草案）

```markdown
# CER Evaluation Skill

## 前置条件
- CER-Analysis-Tool 已安装（`pip install -e /path/to/cer-analysis`）
- 验证：`cer-tool --version` 应返回版本号

## 工作流

### 步骤 1：确认输入
- 确认用户提供了 ASR 文件和参考文件（单对或目录）
- 确认文件为 .txt 格式，编码为 UTF-8 或 GBK 系列

### 步骤 2：执行评估
单文件：
  cer-tool --asr <asr_file> --ref <ref_file> --format json --filter-fillers

批量：
  cer-tool --asr-dir <asr_dir> --ref-dir <ref_dir> --format json \
           --output results.json --filter-fillers

### 步骤 3：解析结果
解析 JSON 输出，提取关键指标：
- cer（字符错误率）、accuracy（准确率）
- substitutions / deletions / insertions（错误分布）

### 步骤 4：质量评级
参考 references/quality-thresholds.md 对 CER 进行分级评定。

### 步骤 5：生成报告
运行 scripts/cer_report.py 或手动组织以下结构：
- 总体评级 + 平均 CER
- 逐文件明细
- 错误模式分析（参考 references/error-patterns.md）
- 改进建议
```

### 4.4 references/quality-thresholds.md（草案）

| CER 范围 | 质量等级 | 说明 | 典型场景 |
|-----------|----------|------|----------|
| 0% ~ 3% | 🟢 优秀 | 接近人工转写水平 | 安静环境、标准普通话 |
| 3% ~ 8% | 🟡 良好 | 可用于大多数业务场景 | 一般办公/会议环境 |
| 8% ~ 15% | 🟠 一般 | 需人工校对后使用 | 嘈杂环境、带口音 |
| 15% ~ 30% | 🔴 较差 | 仅供参考，不建议直接使用 | 远场、多人重叠 |
| > 30% | ⚫ 不可用 | ASR 引擎可能不适合该场景 | 极端噪声、非目标语言 |

### 4.5 references/error-patterns.md（草案要点）

| 错误类型 | 典型表现 | 常见原因 | 改进方向 |
|----------|----------|----------|----------|
| 替换为主 | S >> D + I | 同音字混淆、声学模型不足 | 语言模型优化、热词定制 |
| 删除为主 | D >> S + I | 语速过快、吞字 | 调整 VAD 参数、降速处理 |
| 插入为主 | I >> S + D | 噪声误识别、语气词误转 | 启用 `--filter-fillers`、降噪预处理 |
| 均匀分布 | S ≈ D ≈ I | 整体模型适配不足 | 考虑更换 ASR 引擎或领域微调 |

---

## 五、自由度分级分析

按照 Anthropic 的"自由度"原则：

| 环节 | 自由度 | 理由 |
|------|--------|------|
| CLI 调用 | **低**（固定脚本） | 参数组合固定，错一个 flag 就废；用脚本封装最安全 |
| JSON 解析 | **低**（固定结构） | 输出格式确定，解析逻辑不需要变化 |
| 质量评级 | **中**（参考文档） | 有标准分级表，但可根据用户业务场景调整阈值 |
| 报告撰写 | **高**（文本指引） | 报告的语言、格式、详略程度应由 Claude 根据上下文灵活决定 |
| 改进建议 | **高**（文本指引） | 需要结合具体错误模式、业务场景，由 Claude 发挥领域知识 |

---

## 六、实施路线图

| 阶段 | 任务 | 产出 | 预估工作量 |
|------|------|------|-----------|
| **Phase 1** | 编写 SKILL.md + quality-thresholds.md + error-patterns.md | 可用的基础 Skill | 半天 |
| **Phase 2** | 编写 `scripts/cer_report.py` 报告生成脚本 | 一键出报告 | 半天 |
| **Phase 3** | 实际测试 Skill（用真实 ASR 数据走一遍完整闭环） | 验证 + 迭代 | 1 天 |
| **Phase 4** | 打包分发（`package_skill.py`） | `.skill` 发布包 | 0.5 天 |

**总计约 2.5 天**，且 Phase 1 即可获得最小可用版本。

---

## 七、风险与限制

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| `cer_tool` 未预装 | Skill 无法运行 | SKILL.md 中明确前置条件 + 自动检测脚本 |
| 大文件批处理慢 | Claude 等待超时 | CLI 本身支持进度显示；建议分批处理 |
| CER 质量标准因领域而异 | 医疗/法律的阈值可能更严格 | references/ 中提供可调参数，Claude 可根据用户需求调整 |
| 仅支持中文 | 非中文 ASR 不适用 | 在 description 中明确标注"中文 ASR" |

---

## 八、结论

**CER-Analysis-Tool 完全适合封装为 Anthropic Skill。**

核心优势：
1. **CLI 即接口**——已有的 `cer-tool` 命令行工具是天然的 Skill 调用入口
2. **JSON 即协议**——结构化输出让 AI 助手可以精确解析
3. **领域知识有增值**——CER 解读、错误模式分析、改进建议是 Claude 通用知识中的盲区
4. **工作流高度标准化**——输入 → 计算 → 解读 → 报告，完美匹配 Skill 的"重复性任务"定位

建议优先实施 Phase 1，以最小成本验证闭环可行性。
