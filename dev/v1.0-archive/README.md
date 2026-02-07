# V1.0 源码封存

本目录包含 CER-Analysis-Tool（原 Cer-MatchingTools）V1.0 版本的完整源码备份。

**封存日期**: 2026-02-06  
**封存原因**: V2 迭代重组目录结构，源码迁移至 `src/cer_tool/`

## 文件映射

| V1 文件 | V2 新路径 |
|---------|----------|
| `asr_metrics_refactored.py` | `src/cer_tool/metrics.py` |
| `main_with_tokenizers.py` | `src/cer_tool/gui.py` |
| `preprocessing_pipeline.py` | `src/cer_tool/preprocessing.py` |
| `cli.py` | `src/cer_tool/cli.py` |
| `text_tokenizers/` | `src/cer_tool/tokenizers/` |
| `requirements.txt` | `requirements.txt`（项目根目录） |

## 注意

- 本目录内容仅供历史参考，**请勿修改**
- 活跃开发请使用 `src/cer_tool/`
