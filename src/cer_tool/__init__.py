"""
CER-Analysis-Tool - 中文 CER 字准确率分析工具
"""

__version__ = "2.0.0"
__project__ = "CER-Analysis-Tool"

import warnings


def __getattr__(name):
    """
    兼容性包装：旧类名 → 新类名（V2.0.x 过渡期保留，V2.1.0 移除）
    """
    _compat_map = {
        "ASRComparisonTool": ("cer_tool.gui", "CERAnalysisTool"),
    }
    if name in _compat_map:
        module_path, new_name = _compat_map[name]
        warnings.warn(
            f"{name} 已更名为 {new_name}，"
            f"请使用 from {module_path} import {new_name}。"
            f"旧名称将在 V2.1.0 中移除。",
            DeprecationWarning,
            stacklevel=2,
        )
        import importlib
        mod = importlib.import_module(module_path)
        return getattr(mod, new_name)
    raise AttributeError(f"module 'cer_tool' has no attribute {name}")
