#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本预处理流水线
支持可插拔的预处理节点和自定义预处理链
"""

import re
import unicodedata
from typing import List, Callable, Tuple, Any, Optional


class PreprocessingStep:
    """
    预处理步骤基类
    所有预处理节点都应该继承此类
    """
    
    def __init__(self, name: str):
        """
        初始化预处理步骤
        
        Args:
            name: 步骤名称
        """
        self.name = name
        self.enabled = True
    
    def process(self, text: str) -> str:
        """
        处理文本
        
        Args:
            text: 输入文本
            
        Returns:
            处理后的文本
        """
        raise NotImplementedError("子类必须实现process方法")
    
    def set_enabled(self, enabled: bool):
        """设置步骤是否启用"""
        self.enabled = enabled
    
    def __repr__(self):
        status = "启用" if self.enabled else "禁用"
        return f"{self.name} [{status}]"


class RemovePunctuationStep(PreprocessingStep):
    """移除标点符号步骤"""
    
    def __init__(self):
        super().__init__("移除标点符号")
    
    def process(self, text: str) -> str:
        if not self.enabled:
            return text
        return re.sub(r'[^\w\s]', '', text)


class NormalizeWidthStep(PreprocessingStep):
    """统一全/半角字符步骤"""
    
    def __init__(self):
        super().__init__("统一全半角")
    
    def process(self, text: str) -> str:
        if not self.enabled:
            return text
        return unicodedata.normalize('NFKC', text)


class NormalizeNumbersStep(PreprocessingStep):
    """数字归一步骤"""
    
    def __init__(self):
        super().__init__("数字归一")
    
    def process(self, text: str) -> str:
        if not self.enabled:
            return text
        return re.sub(r'[0-9０-９]+', '0', text)


class NormalizeWhitespaceStep(PreprocessingStep):
    """统一空格处理步骤"""
    
    def __init__(self):
        super().__init__("统一空格")
    
    def process(self, text: str) -> str:
        if not self.enabled:
            return text
        return re.sub(r'\s+', '', text)


class LowercaseStep(PreprocessingStep):
    """转换为小写步骤"""
    
    def __init__(self):
        super().__init__("转小写")
    
    def process(self, text: str) -> str:
        if not self.enabled:
            return text
        return text.lower()


class FilterFillerWordsStep(PreprocessingStep):
    """过滤语气词步骤"""
    
    def __init__(self, tokenizer=None):
        super().__init__("过滤语气词")
        self.tokenizer = tokenizer
        self.filler_words = ["嗯", "啊", "呢", "吧", "哦", "呀", "啦", "喔", 
                            "诶", "唉", "噢", "喂", "呐", "呵", "咯", "咦", "嘿"]
    
    def process(self, text: str) -> str:
        if not self.enabled:
            return text
        
        if not text.strip():
            return ""
        
        try:
            if self.tokenizer:
                # 使用分词器进行词性标注
                words_pos = self.tokenizer.posseg(text)
                filtered_words = []
                for word, flag in words_pos:
                    # 过滤语气词
                    if word in self.filler_words or flag == 'y':
                        continue
                    filtered_words.append(word)
                return "".join(filtered_words)
            else:
                # 简单的词表过滤
                result = text
                for filler in self.filler_words:
                    result = result.replace(filler, "")
                return result
        except Exception as e:
            print(f"警告: 语气词过滤失败: {str(e)}")
            return text


class ChineseTokenizeStep(PreprocessingStep):
    """中文分词步骤"""
    
    def __init__(self, tokenizer=None):
        super().__init__("中文分词")
        self.tokenizer = tokenizer
    
    def process(self, text: str) -> str:
        if not self.enabled or not self.tokenizer:
            return text
        
        if not text or len(text.strip()) <= 2:
            return text.strip()
        
        try:
            words = self.tokenizer.cut(text)
            return "".join(words)
        except Exception as e:
            print(f"警告: 分词失败: {str(e)}")
            return text


class CustomFunctionStep(PreprocessingStep):
    """自定义函数步骤"""
    
    def __init__(self, name: str, func: Callable[[str], str]):
        super().__init__(name)
        self.func = func
    
    def process(self, text: str) -> str:
        if not self.enabled:
            return text
        return self.func(text)


class PreprocessingPipeline:
    """
    文本预处理流水线
    支持添加、移除、排序预处理步骤
    """
    
    def __init__(self, tokenizer=None):
        """
        初始化预处理流水线
        
        Args:
            tokenizer: 分词器实例（可选）
        """
        self.tokenizer = tokenizer
        self.steps: List[PreprocessingStep] = []
    
    def add_step(self, step: PreprocessingStep) -> 'PreprocessingPipeline':
        """
        添加预处理步骤
        
        Args:
            step: 预处理步骤实例
            
        Returns:
            self: 支持链式调用
        """
        self.steps.append(step)
        return self
    
    def insert_step(self, index: int, step: PreprocessingStep) -> 'PreprocessingPipeline':
        """
        在指定位置插入预处理步骤
        
        Args:
            index: 插入位置
            step: 预处理步骤实例
            
        Returns:
            self: 支持链式调用
        """
        self.steps.insert(index, step)
        return self
    
    def remove_step(self, name: str) -> 'PreprocessingPipeline':
        """
        移除指定名称的预处理步骤
        
        Args:
            name: 步骤名称
            
        Returns:
            self: 支持链式调用
        """
        self.steps = [s for s in self.steps if s.name != name]
        return self
    
    def enable_step(self, name: str, enabled: bool = True) -> 'PreprocessingPipeline':
        """
        启用/禁用指定步骤
        
        Args:
            name: 步骤名称
            enabled: 是否启用
            
        Returns:
            self: 支持链式调用
        """
        for step in self.steps:
            if step.name == name:
                step.set_enabled(enabled)
                break
        return self
    
    def clear(self) -> 'PreprocessingPipeline':
        """清空所有步骤"""
        self.steps.clear()
        return self
    
    def process(self, text: str) -> str:
        """
        执行完整的预处理流水线
        
        Args:
            text: 输入文本
            
        Returns:
            处理后的文本
        """
        result = text
        for step in self.steps:
            if step.enabled:
                result = step.process(result)
        return result
    
    def get_steps(self) -> List[PreprocessingStep]:
        """获取所有步骤"""
        return self.steps.copy()
    
    def __repr__(self):
        enabled_count = sum(1 for s in self.steps if s.enabled)
        return f"PreprocessingPipeline(共{len(self.steps)}步，启用{enabled_count}步)"
    
    def print_steps(self):
        """打印所有步骤"""
        if not self.steps:
            print("流水线为空")
            return
        
        print(f"预处理流水线 (共{len(self.steps)}步):")
        for i, step in enumerate(self.steps, 1):
            status = "✓" if step.enabled else "✗"
            print(f"  {i}. {status} {step.name}")


# 预设的流水线配置模板
class PipelinePresets:
    """预设的流水线配置模板"""
    
    @staticmethod
    def basic(tokenizer=None) -> PreprocessingPipeline:
        """
        基础配置：仅做必要的标准化
        适用于大多数场景
        """
        pipeline = PreprocessingPipeline(tokenizer)
        pipeline.add_step(RemovePunctuationStep())
        pipeline.add_step(NormalizeWidthStep())
        pipeline.add_step(NormalizeWhitespaceStep())
        return pipeline
    
    @staticmethod
    def conservative(tokenizer=None) -> PreprocessingPipeline:
        """
        保守配置：保留数字和大小写
        适用于需要保留原始信息的场景
        """
        pipeline = PreprocessingPipeline(tokenizer)
        pipeline.add_step(NormalizeWidthStep())
        pipeline.add_step(NormalizeWhitespaceStep())
        return pipeline
    
    @staticmethod
    def aggressive(tokenizer=None) -> PreprocessingPipeline:
        """
        激进配置：最大化标准化
        适用于对准确率要求极高的场景
        """
        pipeline = PreprocessingPipeline(tokenizer)
        pipeline.add_step(RemovePunctuationStep())
        pipeline.add_step(NormalizeWidthStep())
        pipeline.add_step(NormalizeNumbersStep())
        pipeline.add_step(NormalizeWhitespaceStep())
        pipeline.add_step(LowercaseStep())
        if tokenizer:
            pipeline.add_step(FilterFillerWordsStep(tokenizer))
        return pipeline
    
    @staticmethod
    def cer_optimized(tokenizer=None) -> PreprocessingPipeline:
        """
        CER优化配置：专门为字准确率计算优化
        适用于纯字符级评估
        """
        pipeline = PreprocessingPipeline(tokenizer)
        pipeline.add_step(RemovePunctuationStep())
        pipeline.add_step(NormalizeWidthStep())
        pipeline.add_step(NormalizeWhitespaceStep())
        return pipeline
    
    @staticmethod
    def asr_evaluation(tokenizer=None) -> PreprocessingPipeline:
        """
        ASR评估配置：包含语气词过滤
        适用于ASR系统质量评估
        """
        pipeline = PreprocessingPipeline(tokenizer)
        pipeline.add_step(RemovePunctuationStep())
        pipeline.add_step(NormalizeWidthStep())
        pipeline.add_step(NormalizeWhitespaceStep())
        if tokenizer:
            pipeline.add_step(FilterFillerWordsStep(tokenizer))
        return pipeline


# 便捷函数
def create_pipeline(preset: str = "basic", tokenizer=None) -> PreprocessingPipeline:
    """
    创建预设的预处理流水线
    
    Args:
        preset: 预设名称 ('basic', 'conservative', 'aggressive', 'cer_optimized', 'asr_evaluation')
        tokenizer: 分词器实例（可选）
        
    Returns:
        PreprocessingPipeline: 配置好的流水线实例
    """
    presets = {
        'basic': PipelinePresets.basic,
        'conservative': PipelinePresets.conservative,
        'aggressive': PipelinePresets.aggressive,
        'cer_optimized': PipelinePresets.cer_optimized,
        'asr_evaluation': PipelinePresets.asr_evaluation,
    }
    
    if preset not in presets:
        raise ValueError(f"未知的预设名称: {preset}. 可选值: {list(presets.keys())}")
    
    return presets[preset](tokenizer)


if __name__ == "__main__":
    # 使用示例
    print("=" * 60)
    print("预处理流水线示例")
    print("=" * 60)
    
    # 示例1: 基础配置
    print("\n示例1: 基础配置")
    pipeline = create_pipeline('basic')
    pipeline.print_steps()
    
    test_text = "你好，世界！Hello１２３"
    result = pipeline.process(test_text)
    print(f"原文: {test_text}")
    print(f"结果: {result}")
    
    # 示例2: 自定义流水线
    print("\n示例2: 自定义流水线")
    custom_pipeline = PreprocessingPipeline()
    custom_pipeline.add_step(NormalizeWidthStep())
    custom_pipeline.add_step(NormalizeNumbersStep())
    custom_pipeline.print_steps()
    
    result2 = custom_pipeline.process(test_text)
    print(f"原文: {test_text}")
    print(f"结果: {result2}")
    
    # 示例3: 禁用某个步骤
    print("\n示例3: 禁用数字归一")
    custom_pipeline.enable_step("数字归一", False)
    custom_pipeline.print_steps()
    
    result3 = custom_pipeline.process(test_text)
    print(f"原文: {test_text}")
    print(f"结果: {result3}")
    
    print("\n" + "=" * 60)

