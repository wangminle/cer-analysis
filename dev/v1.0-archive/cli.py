#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASR字准确率计算工具 - 命令行接口
支持批处理、分词器选择、语气词过滤和CSV导出
"""

import argparse
import sys
import os
import csv
from pathlib import Path
from typing import List, Tuple

from asr_metrics_refactored import ASRMetrics
from text_tokenizers import get_available_tokenizers, get_tokenizer_info


def read_file_with_encodings(file_path: str) -> str:
    """
    使用多种编码方式读取文件内容
    
    Args:
        file_path (str): 文件路径
        
    Returns:
        str: 文件内容
    """
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read().strip()
        except UnicodeDecodeError:
            continue
    
    # 最后尝试系统默认编码
    try:
        with open(file_path, 'r') as f:
            return f.read().strip()
    except Exception as e:
        raise Exception(f"无法读取文件 {file_path}: {str(e)}")


def process_single_pair(asr_file: str, ref_file: str, 
                       tokenizer: str, filter_fillers: bool,
                       verbose: bool = False) -> dict:
    """
    处理单个文件对
    
    Args:
        asr_file: ASR文件路径
        ref_file: 标注文件路径
        tokenizer: 分词器名称
        filter_fillers: 是否过滤语气词
        verbose: 是否显示详细信息
        
    Returns:
        dict: 计算结果
    """
    try:
        # 读取文件
        asr_text = read_file_with_encodings(asr_file)
        ref_text = read_file_with_encodings(ref_file)
        
        # 创建ASRMetrics实例
        metrics = ASRMetrics(tokenizer_name=tokenizer)
        
        # 计算详细指标
        result = metrics.calculate_detailed_metrics(ref_text, asr_text, filter_fillers)
        
        # 添加文件信息
        result['asr_file'] = os.path.basename(asr_file)
        result['ref_file'] = os.path.basename(ref_file)
        result['filter_fillers'] = filter_fillers
        
        if verbose:
            print(f"\n处理: {result['asr_file']} <-> {result['ref_file']}")
            print(f"  CER: {result['cer']:.4f}")
            print(f"  准确率: {result['accuracy']:.4f}")
            print(f"  替换: {result['substitutions']}, 删除: {result['deletions']}, 插入: {result['insertions']}")
        
        return result
        
    except Exception as e:
        if verbose:
            print(f"\n错误: 处理文件对时出错")
            print(f"  ASR文件: {asr_file}")
            print(f"  标注文件: {ref_file}")
            print(f"  错误信息: {str(e)}")
        return None


def batch_process_directory(asr_dir: str, ref_dir: str,
                           tokenizer: str, filter_fillers: bool,
                           output_file: str = None,
                           verbose: bool = False) -> List[dict]:
    """
    批处理目录中的文件
    
    Args:
        asr_dir: ASR文件目录
        ref_dir: 标注文件目录
        tokenizer: 分词器名称
        filter_fillers: 是否过滤语气词
        output_file: 输出文件路径
        verbose: 是否显示详细信息
        
    Returns:
        List[dict]: 所有结果列表
    """
    asr_path = Path(asr_dir)
    ref_path = Path(ref_dir)
    
    # 获取所有txt文件
    asr_files = sorted(asr_path.glob('*.txt'))
    ref_files = sorted(ref_path.glob('*.txt'))
    
    if len(asr_files) != len(ref_files):
        print(f"警告: ASR文件数({len(asr_files)})和标注文件数({len(ref_files)})不匹配")
    
    results = []
    total = min(len(asr_files), len(ref_files))
    
    print(f"\n开始批处理，共{total}个文件对...")
    print(f"分词器: {tokenizer}")
    print(f"语气词过滤: {'启用' if filter_fillers else '禁用'}")
    print("-" * 60)
    
    for i, (asr_file, ref_file) in enumerate(zip(asr_files, ref_files), 1):
        if verbose:
            print(f"\n[{i}/{total}] ", end='')
        
        result = process_single_pair(
            str(asr_file), str(ref_file),
            tokenizer, filter_fillers, verbose
        )
        
        if result:
            results.append(result)
    
    # 统计总体结果
    if results:
        print("\n" + "=" * 60)
        print("批处理完成！")
        print("=" * 60)
        
        avg_cer = sum(r['cer'] for r in results) / len(results)
        avg_accuracy = sum(r['accuracy'] for r in results) / len(results)
        total_subs = sum(r['substitutions'] for r in results)
        total_dels = sum(r['deletions'] for r in results)
        total_ins = sum(r['insertions'] for r in results)
        
        print(f"成功处理: {len(results)}/{total}个文件对")
        print(f"平均CER: {avg_cer:.4f}")
        print(f"平均准确率: {avg_accuracy:.4f}")
        print(f"总错误: 替换={total_subs}, 删除={total_dels}, 插入={total_ins}")
        
        # 保存结果
        if output_file:
            save_results_to_csv(results, output_file)
            print(f"\n结果已保存到: {output_file}")
    
    return results


def save_results_to_csv(results: List[dict], output_file: str):
    """
    保存结果到CSV文件
    
    Args:
        results: 结果列表
        output_file: 输出文件路径
    """
    if not results:
        print("没有结果可以保存")
        return
    
    # 定义CSV列
    fieldnames = [
        'asr_file', 'ref_file', 'tokenizer',
        'cer', 'wer', 'accuracy',
        'substitutions', 'deletions', 'insertions',
        'ref_length', 'hyp_length',
        'filter_fillers'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            row = {field: result.get(field, '') for field in fieldnames}
            writer.writerow(row)


def save_results_to_txt(results: List[dict], output_file: str):
    """
    保存结果到TXT文件（制表符分隔）
    
    Args:
        results: 结果列表
        output_file: 输出文件路径
    """
    if not results:
        print("没有结果可以保存")
        return
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # 写入表头
        f.write("ASR文件\t标注文件\t分词器\tCER\t准确率\t替换\t删除\t插入\t过滤语气词\n")
        
        # 写入数据
        for result in results:
            f.write(f"{result['asr_file']}\t"
                   f"{result['ref_file']}\t"
                   f"{result['tokenizer']}\t"
                   f"{result['cer']:.4f}\t"
                   f"{result['accuracy']:.4f}\t"
                   f"{result['substitutions']}\t"
                   f"{result['deletions']}\t"
                   f"{result['insertions']}\t"
                   f"{'是' if result['filter_fillers'] else '否'}\n")


def list_tokenizers():
    """列出可用的分词器"""
    print("\n可用的分词器:")
    print("=" * 60)
    
    available = get_available_tokenizers()
    
    for name in available:
        info = get_tokenizer_info(name)
        status = "✓" if info.get('available') else "✗"
        version = info.get('version', 'unknown')
        desc = info.get('description', '')
        print(f"{status} {name:10s} (v{version:10s}) - {desc}")
    
    print("=" * 60)
    print(f"共 {len(available)} 个可用分词器")


def main():
    """主函数 - CLI入口"""
    parser = argparse.ArgumentParser(
        description='ASR字准确率计算工具 - 命令行版本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 单文件对比
  python cli.py --asr asr.txt --ref ref.txt
  
  # 指定分词器和过滤语气词
  python cli.py --asr asr.txt --ref ref.txt --tokenizer thulac --filter-fillers
  
  # 批量处理目录
  python cli.py --asr-dir ./asr_files --ref-dir ./ref_files --output results.csv
  
  # 列出可用分词器
  python cli.py --list-tokenizers
        """
    )
    
    # 基本选项
    parser.add_argument('--asr', type=str, help='ASR转写结果文件路径')
    parser.add_argument('--ref', type=str, help='标注文件路径')
    parser.add_argument('--asr-dir', type=str, help='ASR文件目录（批处理模式）')
    parser.add_argument('--ref-dir', type=str, help='标注文件目录（批处理模式）')
    
    # 分词器选项
    parser.add_argument('--tokenizer', type=str, default='jieba',
                       choices=['jieba', 'thulac', 'hanlp'],
                       help='选择分词器 (默认: jieba)')
    parser.add_argument('--list-tokenizers', action='store_true',
                       help='列出所有可用的分词器')
    
    # 处理选项
    parser.add_argument('--filter-fillers', action='store_true',
                       help='过滤语气词（如"嗯"、"啊"、"呢"等）')
    
    # 输出选项
    parser.add_argument('--output', '-o', type=str,
                       help='输出文件路径（支持.csv或.txt格式）')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='显示详细处理信息')
    
    args = parser.parse_args()
    
    # 列出分词器
    if args.list_tokenizers:
        list_tokenizers()
        return 0
    
    # 单文件模式
    if args.asr and args.ref:
        print("\n单文件对比模式")
        print("=" * 60)
        
        result = process_single_pair(
            args.asr, args.ref,
            args.tokenizer, args.filter_fillers,
            verbose=args.verbose
        )
        
        # 修复：处理失败时返回退出码 1
        if result is None:
            return 1
        
        if args.output:
            if args.output.endswith('.csv'):
                save_results_to_csv([result], args.output)
            else:
                save_results_to_txt([result], args.output)
            print(f"\n结果已保存到: {args.output}")
        
        return 0
    
    # 批处理模式
    elif args.asr_dir and args.ref_dir:
        results = batch_process_directory(
            args.asr_dir, args.ref_dir,
            args.tokenizer, args.filter_fillers,
            args.output, args.verbose
        )
        # 修复：存在任何失败时返回退出码 1
        if not results:
            return 1
        return 0
    
    # 没有提供足够的参数
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())

