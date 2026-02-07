#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件工具模块 - 公共文件读写函数
从 CLI 和 GUI 中提取的重复逻辑
"""

from typing import List


def read_file_with_encodings(file_path: str, 
                              encodings: List[str] = None) -> str:
    """
    使用多种编码方式读取文件内容
    支持常见的中文编码格式，自动检测最适合的编码
    
    Args:
        file_path (str): 文件路径
        encodings (List[str]): 尝试的编码列表，默认 UTF-8 → GBK → GB2312 → GB18030
        
    Returns:
        str: 文件内容（已去除首尾空白）
        
    Raises:
        Exception: 如果所有编码方式都失败则抛出异常
    """
    if encodings is None:
        encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
    
    errors = []
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read().strip()
        except UnicodeDecodeError as e:
            errors.append(f"{encoding}: {e}")
            continue
    
    # 最后尝试系统默认编码
    try:
        with open(file_path, 'r') as f:
            return f.read().strip()
    except Exception as e:
        raise Exception(
            f"无法读取文件 {file_path}，尝试的编码: {', '.join(encodings)}。"
            f"最后错误: {str(e)}"
        )
