#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CER-Analysis-Tool - 命令行接口 (V2)
支持批处理、分词器选择、语气词过滤、多格式输出
"""

import argparse
import json
import sys
import os
import csv
from pathlib import Path
from typing import List, Optional

from cer_tool import __version__
from cer_tool.metrics import ASRMetrics
from cer_tool.tokenizers import get_available_tokenizers, get_tokenizer_info
from cer_tool.file_utils import read_file_with_encodings


def process_single_pair(asr_file: str, ref_file: str, 
                       tokenizer: str, filter_fillers: bool,
                       verbose: bool = False) -> Optional[dict]:
    """
    处理单个文件对
    
    Args:
        asr_file: ASR文件路径
        ref_file: 标注文件路径
        tokenizer: 分词器名称
        filter_fillers: 是否过滤语气词
        verbose: 是否显示详细信息
        
    Returns:
        dict: 计算结果，失败返回 None
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
        # 无论 verbose 与否，错误都需要报告
        print(f"\n错误: 处理文件对时出错", file=sys.stderr)
        print(f"  ASR文件: {asr_file}", file=sys.stderr)
        print(f"  标注文件: {ref_file}", file=sys.stderr)
        print(f"  错误信息: {str(e)}", file=sys.stderr)
        return None


def batch_process_directory(asr_dir: str, ref_dir: str,
                           tokenizer: str, filter_fillers: bool,
                           output_file: str = None,
                           output_format: str = "text",
                           verbose: bool = False) -> List[dict]:
    """
    批处理目录中的文件
    
    Args:
        asr_dir: ASR文件目录
        ref_dir: 标注文件目录
        tokenizer: 分词器名称
        filter_fillers: 是否过滤语气词
        output_file: 输出文件路径
        output_format: 输出格式 (text/csv/json)
        verbose: 是否显示详细信息
        
    Returns:
        List[dict]: 所有结果列表
    """
    asr_path = Path(asr_dir)
    ref_path = Path(ref_dir)
    
    # 获取所有txt文件，建立 文件名(stem) → 完整路径 的映射
    asr_map = {f.stem: f for f in sorted(asr_path.glob('*.txt'))}
    ref_map = {f.stem: f for f in sorted(ref_path.glob('*.txt'))}
    
    # 按文件名取交集进行配对，保持排序
    common_names = sorted(set(asr_map.keys()) & set(ref_map.keys()))
    asr_only = sorted(set(asr_map.keys()) - set(ref_map.keys()))
    ref_only = sorted(set(ref_map.keys()) - set(asr_map.keys()))
    
    # 报告未配对的文件
    if asr_only:
        print(f"警告: {len(asr_only)} 个ASR文件在标注目录中没有同名文件，将被跳过: "
              f"{', '.join(asr_only[:5])}{'...' if len(asr_only) > 5 else ''}",
              file=sys.stderr)
    if ref_only:
        print(f"警告: {len(ref_only)} 个标注文件在ASR目录中没有同名文件，将被跳过: "
              f"{', '.join(ref_only[:5])}{'...' if len(ref_only) > 5 else ''}",
              file=sys.stderr)
    
    if not common_names:
        print("错误: ASR目录与标注目录之间没有同名文件可配对", file=sys.stderr)
        return []
    
    results = []
    failed_count = 0
    total = len(common_names)
    
    if output_format != "json":
        print(f"\n开始批处理，共{total}个文件对（按文件名配对）...")
        print(f"分词器: {tokenizer}")
        print(f"语气词过滤: {'启用' if filter_fillers else '禁用'}")
        print("-" * 60)
    
    for i, name in enumerate(common_names, 1):
        asr_file = asr_map[name]
        ref_file = ref_map[name]
        if verbose:
            print(f"\n[{i}/{total}] ", end='')
        
        result = process_single_pair(
            str(asr_file), str(ref_file),
            tokenizer, filter_fillers, verbose
        )
        
        if result:
            results.append(result)
        else:
            failed_count += 1
    
    # 统计总体结果（非 JSON 模式打印人类可读摘要）
    if results and output_format != "json":
        print("\n" + "=" * 60)
        print("批处理完成！")
        print("=" * 60)
        
        avg_cer = sum(r['cer'] for r in results) / len(results)
        avg_accuracy = sum(r['accuracy'] for r in results) / len(results)
        total_subs = sum(r['substitutions'] for r in results)
        total_dels = sum(r['deletions'] for r in results)
        total_ins = sum(r['insertions'] for r in results)
        
        print(f"成功处理: {len(results)}/{total}个文件对")
        if failed_count > 0:
            print(f"失败: {failed_count}个文件对")
        print(f"平均CER: {avg_cer:.4f}")
        print(f"平均准确率: {avg_accuracy:.4f}")
        print(f"总错误: 替换={total_subs}, 删除={total_dels}, 插入={total_ins}")
    
    # 保存结果到文件（所有格式统一处理，修复 JSON 模式不写文件的 bug）
    if results and output_file:
        save_results(results, output_file, output_format)
        if output_format != "json":
            print(f"\n结果已保存到: {output_file}")
    
    return results


def save_results(results: List[dict], output_file: str, output_format: str = "text"):
    """
    保存结果到文件，支持多种格式
    
    Args:
        results: 结果列表
        output_file: 输出文件路径
        output_format: 输出格式 (text/csv/json)
    """
    if not results:
        print("没有结果可以保存")
        return
    
    if output_format == "json" or output_file.endswith('.json'):
        save_results_to_json(results, output_file)
    elif output_format == "csv" or output_file.endswith('.csv'):
        save_results_to_csv(results, output_file)
    else:
        save_results_to_txt(results, output_file)


def save_results_to_json(results: List[dict], output_file: str):
    """
    保存结果到JSON文件（V2新增）
    
    Args:
        results: 结果列表
        output_file: 输出文件路径
    """
    # 构建可序列化的输出
    output = {
        "tool": "CER-Analysis-Tool",
        "version": __version__,
        "summary": {
            "total_pairs": len(results),
            "avg_cer": sum(r['cer'] for r in results) / len(results),
            "avg_accuracy": sum(r['accuracy'] for r in results) / len(results),
            "total_substitutions": sum(r['substitutions'] for r in results),
            "total_deletions": sum(r['deletions'] for r in results),
            "total_insertions": sum(r['insertions'] for r in results),
        },
        "results": results,
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


def save_results_to_csv(results: List[dict], output_file: str):
    """
    保存结果到CSV文件
    
    Args:
        results: 结果列表
        output_file: 输出文件路径
    """
    fieldnames = [
        'asr_file', 'ref_file', 'tokenizer',
        'cer', 'wer', 'accuracy',
        'substitutions', 'deletions', 'insertions',
        'ref_length', 'hyp_length',
        'filter_fillers'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        
        for result in results:
            writer.writerow(result)


def save_results_to_txt(results: List[dict], output_file: str):
    """
    保存结果到TXT文件（制表符分隔）
    
    Args:
        results: 结果列表
        output_file: 输出文件路径
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("ASR文件\t标注文件\t分词器\tCER\t准确率\t替换\t删除\t插入\t过滤语气词\n")
        
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
        prog='cer-tool',
        description='CER-Analysis-Tool - 中文字准确率分析工具（命令行版本）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 单文件对比
  cer-tool --asr asr.txt --ref ref.txt
  
  # 指定分词器和过滤语气词
  cer-tool --asr asr.txt --ref ref.txt --tokenizer thulac --filter-fillers
  
  # 批量处理目录
  cer-tool --asr-dir ./asr_files --ref-dir ./ref_files --output results.csv
  
  # 批量处理并输出JSON
  cer-tool --asr-dir ./asr_files --ref-dir ./ref_files --output results.json --format json
  
  # 列出可用分词器
  cer-tool --list-tokenizers
        """
    )
    
    # 版本信息（V2 新增）
    parser.add_argument('--version', action='version', 
                       version=f'CER-Analysis-Tool {__version__}')
    
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
                       help='输出文件路径（支持 .csv/.txt/.json 格式）')
    parser.add_argument('--format', '-f', type=str, default='text',
                       choices=['text', 'csv', 'json'],
                       help='输出格式 (默认: text)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='显示详细处理信息')
    
    args = parser.parse_args()
    
    # 列出分词器
    if args.list_tokenizers:
        list_tokenizers()
        return 0
    
    # 单文件模式
    if args.asr and args.ref:
        if args.format != "json":
            print("\n单文件对比模式")
            print("=" * 60)
        
        result = process_single_pair(
            args.asr, args.ref,
            args.tokenizer, args.filter_fillers,
            verbose=args.verbose
        )
        
        if result is None:
            return 1
        
        # 输出结果
        if args.output:
            # 有输出文件：写入文件
            save_results([result], args.output, args.format)
            if args.format != "json":
                print(f"\n结果已保存到: {args.output}")
        
        if args.format == "json" and not args.output:
            # JSON 无文件：打印到 stdout
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.format != "json":
            # 默认 text 模式：始终打印结果到终端
            print(f"\n处理: {result['asr_file']} <-> {result['ref_file']}")
            print(f"  分词器:  {result.get('tokenizer', 'jieba')}")
            print(f"  CER:     {result['cer']:.4f}")
            print(f"  准确率:  {result['accuracy']:.4f}")
            print(f"  替换: {result['substitutions']}, "
                  f"删除: {result['deletions']}, "
                  f"插入: {result['insertions']}")
            print(f"  参考长度: {result['ref_length']}, "
                  f"假设长度: {result['hyp_length']}")
        
        return 0
    
    # 批处理模式
    elif args.asr_dir and args.ref_dir:
        results = batch_process_directory(
            args.asr_dir, args.ref_dir,
            args.tokenizer, args.filter_fillers,
            args.output, args.format, args.verbose
        )
        
        # JSON 无文件输出时打印到 stdout
        if args.format == "json" and not args.output and results:
            output = {
                "tool": "CER-Analysis-Tool",
                "version": __version__,
                "results": results,
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
        
        if not results:
            return 1
        return 0
    
    # 没有提供足够的参数
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
