# CER-Analysis-Tool — 项目知识库

> 本文件是项目的完整上下文知识库，供 AI 助手（Cursor / Claude Code / 其他 LLM 工具）快速理解项目。
> 全局入口规则见 `.cursorrules`。

---

## 一、项目概览

| 项目 | 内容 |
|------|------|
| **项目名称** | CER-Analysis-Tool |
| **Python 包名** | `cer_tool` |
| **当前版本** | V2.0.0 |
| **定位** | 基于 Python 的桌面客户端工具，用于对比不同文本之间的字准确率（CER） |
| **核心依赖** | jieba（分词）、python-Levenshtein（编辑距离，推荐） |
| **已移除依赖** | jiwer（V2 移除，改用自研预处理流水线）、pandas（V2 移除，改用标准库 csv） |

---

## 二、目录结构

```
cer-analysis/                           # 项目根目录
├── .cursorrules                        # Cursor IDE 全局规则（瘦入口）
├── CLAUDE.md                           # 项目知识库（本文件）
├── pyproject.toml                      # 包定义 + 依赖分层 + 构建配置
├── Pipfile                             # pipenv 依赖管理
├── README.md / README_cn.md            # 项目说明（英文/中文）
├── LICENSE
│
├── src/                                # 正式源码目录
│   └── cer_tool/                       # Python 包
│       ├── __init__.py                 # 包元数据 (__version__, 兼容性包装)
│       ├── __main__.py                 # python -m cer_tool 入口
│       ├── metrics.py                  # 核心：CER 指标计算引擎
│       ├── cli.py                      # CLI 命令行接口
│       ├── gui.py                      # GUI 图形界面（tkinter）
│       ├── preprocessing.py            # 预处理流水线（可插拔步骤）
│       ├── file_utils.py              # 公共文件工具（多编码读取）
│       └── tokenizers/                 # 分词器模块
│           ├── __init__.py             # 模块导出
│           ├── base.py                 # 抽象基类 + 异常定义
│           ├── factory.py              # 工厂类（单例 + 缓存）
│           ├── jieba_tokenizer.py      # Jieba 实现
│           ├── thulac_tokenizer.py     # THULAC 实现
│           └── hanlp_tokenizer.py      # HanLP 实现
│
├── dev/                                # 开发辅助目录
│   ├── output/                         # 开发过程临时输出
│   └── v1.0-archive/                   # V1 源码完整封存（只读参考）
│
├── tests/                              # 测试目录（127 项 pytest 用例）
│   ├── pytest.ini                      # pytest 配置
│   ├── test_boundary.py                # 边界条件测试（20 用例）
│   ├── test_cli.py                     # CLI 工具测试（14 用例）
│   ├── test_preprocessing.py           # 预处理流水线测试（25 用例）
│   ├── test_core_metrics.py            # 核心指标计算测试（33 用例）
│   ├── test_tokenizers_unit.py         # 分词器单元测试（23 用例）
│   ├── test_with_pytest_marks.py       # V1 遗留集成测试（12 用例）
│   └── reports/                        # 测试报告与测试策略文档
│
├── docs/                               # 项目文档
│   ├── CER-Analysis-Tool-V2-改版建议书.md
│   ├── CER-Analysis-Tool-V2-架构变更说明.md
│   └── V1/                             # V1 文档归档
│
├── assets/                             # 静态资源（logo 等）
├── release/                            # 发布产物
└── ref/                                # 参考资料（只读，不允许修改）
```

---

## 三、开发环境

| 项目 | 规范 |
|------|------|
| **语言** | Python 3.12 |
| **包管理** | pipenv（主）/ pip + pyproject.toml |
| **安装方式** | `pip install -e .`（editable 模式） |
| **macOS 命令** | 使用 `python3` |
| **Windows 命令** | 使用 `python` |
| **代码风格** | 中文注释，类名驼峰，函数名下划线 |
| **原则** | 尽量使用官方标准库实现 |

---

## 四、关键入口命令

```bash
# GUI 模式
python3 -m cer_tool

# CLI 模式
python3 -m cer_tool.cli --asr asr.txt --ref ref.txt
cer-tool --asr asr.txt --ref ref.txt --format json

# 运行测试
python3 -m pytest -v                        # 全量测试
python3 -m pytest -m basic                  # 仅基础测试
python3 -m pytest -m "not slow"             # 排除慢速测试
python3 -m pytest --collect-only            # 检查收集
```

---

## 五、文档管理规范

1. 架构设计、需求规格说明书、UI设计说明、项目管理这四类重要文档，使用前缀 `CER-Analysis-Tool-V2-`。
2. 每次更新重要文档时：
   - 版本号 +0.1（格式 `V[x.x]`）
   - 更新时间格式 `YYYY-MM-DD HH:MM`
   - 附带更新说明
3. 所有文档放在 `/docs` 目录，使用 Markdown 格式。

---

## 六、任务管理规范

1. 以项目管理文档中的开发计划为依据，每次只专注一个任务。
2. 改动任务范围外的代码时，先向用户提出修改意见，等待批准。
3. 每完成一个任务后，执行自我测试并输出测试总结到 `/tests/reports`。
4. 开始新任务前，评估过去 3 天的开发是否已完成测试流程。
5. 每完成 2-3 个任务后，更新项目管理文档；如有变化，同步更新架构/需求/UI 文档。

---

## 七、测试标准

1. 每个任务完成后，必须编写 pytest 测试脚本放在 `/tests` 目录根层。
2. 测试必须包含：正常功能测试、边界条件测试、异常情况测试。
3. 测试脚本使用中文注释，使用 `@pytest.mark` 分类标记。
4. 编写完成后立即执行，根据结果调整后重新执行。
5. 测试完成后生成总结文档，命名格式：`test_[功能名称]_[日期].md`，放在 `/tests/reports` 目录。

### pytest 标记体系

| 标记 | 说明 |
|------|------|
| `basic` | 基础测试，仅依赖 jieba |
| `boundary` | 边界条件测试 |
| `cli` | CLI 工具测试 |
| `pipeline` | 预处理流水线测试 |
| `unit` | 单元测试 |
| `integration` | 集成测试 |
| `optional` | 可选分词器测试（需 thulac/hanlp） |
| `slow` | 慢速测试 |

---

## 八、公共资源获取

1. 需要当天日期时：使用 `date` 命令查询真实时间，不要凭记忆。
2. 需要文件路径时：使用 `pwd` 命令查询真实路径，不要猜测。

---

## 九、V2 改版进度

### 已完成

| 阶段 | 任务 | 状态 |
|------|------|------|
| 第一阶段A | T1 修复 pytest 收集 | ✅ |
| 第一阶段A | T2 修复指标边界条件 | ✅ |
| 第一阶段A | T3 修复 CLI 退出码 | ✅ |
| 第一阶段A | T4 修复 run_tests.py | ✅ |
| 第一阶段B | T5 集成预处理流水线 | ✅ |
| 第一阶段B | T5b 目录重组 + 包化 | ✅ |
| 第二阶段 | T6 移除 jiwer 依赖 | ✅ |
| 第二阶段 | T7 移除 pandas 依赖 | ✅ |
| 第二阶段 | T8 统一依赖分层 | ✅ |
| 第二阶段 | T9 提取公共模块 | ✅ |
| 第二阶段 | T10 CLI 增强 | ✅ |
| 第二阶段 | T11 修正架构文档 | ✅ |
| 补强 | N1 项目改名落地 | ✅ |
| 补强 | N2-N6 测试体系补强（127 用例） | ✅ |
| 补强 | N7 tests/ 目录整理（reports/scripts/test-v0.1.0 分层） | ✅ |

### 待开展（第三阶段）

| 编号 | 任务 | 优先级 |
|------|------|--------|
| T12 | 文件名自动配对 | P2 |
| T13 | 支持更多文件格式（.csv/.json/.srt） | P2 |
| T14 | 对齐可视化增强 | P2 |
| T15 | 批量统计分析增强 | P2 |
| T16 | GUI 视觉升级（customtkinter） | P3 |
| T17 | 打包与分发（PyInstaller） | P3 |
