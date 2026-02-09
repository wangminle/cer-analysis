#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CER-Analysis-Tool 入口
支持 python -m cer_tool 运行
"""

import sys


def main():
    """主入口：默认启动 GUI，如果传入参数则走 CLI"""
    if len(sys.argv) > 1:
        # 有命令行参数，走 CLI 模式
        from cer_tool.cli import main as cli_main
        sys.exit(cli_main())
    else:
        # 无参数，启动 GUI
        import tkinter as tk
        from cer_tool.gui import CERAnalysisTool
        
        root = tk.Tk()
        app = CERAnalysisTool(root)
        root.mainloop()


if __name__ == "__main__":
    main()
