#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预处理流水线测试模块

覆盖场景：
- 各个预处理步骤的独立功能
- 流水线的组装与执行
- 预设模板（basic / conservative / aggressive / cer_optimized / asr_evaluation）
- 流水线管理（添加、移除、启用/禁用步骤）
- 链式调用
- create_pipeline 便捷函数
- 边界条件（空字符串、仅空白、超长文本）
"""

import pytest
from cer_tool.preprocessing import (
    PreprocessingPipeline, PipelinePresets, create_pipeline,
    PreprocessingStep,
    RemovePunctuationStep, NormalizeWidthStep, NormalizeWhitespaceStep,
    NormalizeNumbersStep, LowercaseStep, FilterFillerWordsStep,
    ChineseTokenizeStep, CustomFunctionStep
)


# ════════════════════════════════════════════════════
# 第一组：单步骤功能测试
# ════════════════════════════════════════════════════

class TestIndividualSteps:
    """各预处理步骤独立功能测试"""

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_remove_punctuation(self):
        """移除标点符号：中英文标点均被移除"""
        step = RemovePunctuationStep()
        assert step.process("你好，世界！") == "你好世界"
        assert step.process("hello, world!") == "hello world"
        assert step.process("测试。、；：？") == "测试"

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_normalize_width(self):
        """全半角归一化：全角字母和数字转换为半角"""
        step = NormalizeWidthStep()
        assert step.process("Ｈｅｌｌｏ") == "Hello"
        assert step.process("１２３") == "123"
        # 中文不受影响
        assert step.process("你好") == "你好"

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_normalize_whitespace(self):
        """空白字符归一化：所有空白被移除"""
        step = NormalizeWhitespaceStep()
        assert step.process("你 好  世界") == "你好世界"
        assert step.process("a  b\tc\nd") == "abcd"
        assert step.process("   ") == ""

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_normalize_numbers(self):
        """数字归一化：所有数字序列替换为 0"""
        step = NormalizeNumbersStep()
        assert step.process("有123个苹果") == "有0个苹果"
        assert step.process("电话010和12345") == "电话0和0"
        # 全角数字也被替换
        assert step.process("数量５０") == "数量0"

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_lowercase(self):
        """转小写：英文字母统一为小写"""
        step = LowercaseStep()
        assert step.process("Hello WORLD") == "hello world"
        assert step.process("中文ABC") == "中文abc"

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_filter_filler_words_simple(self):
        """语气词过滤（无分词器）：简单字符串替换"""
        step = FilterFillerWordsStep(tokenizer=None)
        assert step.process("嗯好的啊") == "好的"
        assert step.process("嗯嗯嗯") == ""
        # 不在语气词列表中的字不受影响
        assert step.process("你好世界") == "你好世界"

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_step_disabled(self):
        """步骤禁用后不处理文本"""
        step = RemovePunctuationStep()
        step.set_enabled(False)
        assert step.process("你好，世界！") == "你好，世界！"

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_custom_function_step(self):
        """自定义函数步骤"""
        step = CustomFunctionStep("反转", lambda text: text[::-1])
        assert step.process("你好") == "好你"
        assert step.process("abc") == "cba"


# ════════════════════════════════════════════════════
# 第二组：流水线组装与执行
# ════════════════════════════════════════════════════

class TestPipelineAssembly:
    """流水线组装与执行测试"""

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_empty_pipeline(self):
        """空流水线不修改文本"""
        pipeline = PreprocessingPipeline()
        assert pipeline.process("你好，世界！") == "你好，世界！"

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_pipeline_chain_call(self):
        """链式调用添加步骤"""
        pipeline = PreprocessingPipeline()
        result = pipeline.add_step(RemovePunctuationStep()) \
                        .add_step(NormalizeWhitespaceStep()) \
                        .add_step(LowercaseStep())
        # 链式调用返回的是同一个 pipeline 实例
        assert result is pipeline
        assert len(pipeline.get_steps()) == 3

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_pipeline_step_order(self):
        """步骤按添加顺序执行"""
        # 先转小写，再移除标点
        pipeline1 = PreprocessingPipeline()
        pipeline1.add_step(LowercaseStep())
        pipeline1.add_step(RemovePunctuationStep())
        
        # 先移除标点，再转小写
        pipeline2 = PreprocessingPipeline()
        pipeline2.add_step(RemovePunctuationStep())
        pipeline2.add_step(LowercaseStep())
        
        text = "Hello, WORLD!"
        # 两种顺序在此输入下结果应一致
        result1 = pipeline1.process(text)
        result2 = pipeline2.process(text)
        assert result1 == result2 == "hello world"

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_pipeline_remove_step(self):
        """移除步骤后流水线行为变化"""
        pipeline = PreprocessingPipeline()
        pipeline.add_step(RemovePunctuationStep())
        pipeline.add_step(LowercaseStep())
        
        assert pipeline.process("Hello!") == "hello"
        
        pipeline.remove_step("转小写")
        assert pipeline.process("Hello!") == "Hello"

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_pipeline_enable_disable(self):
        """启用/禁用步骤"""
        pipeline = PreprocessingPipeline()
        pipeline.add_step(RemovePunctuationStep())
        pipeline.add_step(LowercaseStep())
        
        # 禁用小写转换
        pipeline.enable_step("转小写", False)
        assert pipeline.process("Hello!") == "Hello"
        
        # 重新启用
        pipeline.enable_step("转小写", True)
        assert pipeline.process("Hello!") == "hello"

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_pipeline_clear(self):
        """清空流水线"""
        pipeline = PreprocessingPipeline()
        pipeline.add_step(RemovePunctuationStep())
        pipeline.add_step(LowercaseStep())
        assert len(pipeline.get_steps()) == 2
        
        pipeline.clear()
        assert len(pipeline.get_steps()) == 0
        assert pipeline.process("Hello!") == "Hello!"

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_pipeline_insert_step(self):
        """在指定位置插入步骤"""
        pipeline = PreprocessingPipeline()
        pipeline.add_step(RemovePunctuationStep())
        pipeline.add_step(LowercaseStep())
        
        # 在位置 1 插入全半角归一
        pipeline.insert_step(1, NormalizeWidthStep())
        steps = pipeline.get_steps()
        assert len(steps) == 3
        assert steps[1].name == "统一全半角"


# ════════════════════════════════════════════════════
# 第三组：预设模板测试
# ════════════════════════════════════════════════════

class TestPresets:
    """预设模板测试"""

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_basic_preset(self):
        """basic 预设：标点移除 + 全半角归一 + 空白归一"""
        pipeline = PipelinePresets.basic()
        assert len(pipeline.get_steps()) == 3
        result = pipeline.process("你好，世界！ Hello１２３")
        # 标点移除、全角→半角、空白移除
        assert "，" not in result
        assert "！" not in result
        assert " " not in result
        assert "123" in result  # 全角 → 半角

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_conservative_preset(self):
        """conservative 预设：仅全半角 + 空白归一（保留标点和大小写）"""
        pipeline = PipelinePresets.conservative()
        assert len(pipeline.get_steps()) == 2
        result = pipeline.process("Hello, World！")
        # 标点被保留（半角逗号不变，全角感叹号转半角）
        assert "H" in result  # 大小写保留

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_aggressive_preset(self):
        """aggressive 预设：最大化标准化"""
        pipeline = PipelinePresets.aggressive()
        # 无分词器时 5 步：标点 + 全半角 + 数字归一 + 空白 + 小写（无语气词过滤）
        assert len(pipeline.get_steps()) == 5
        result = pipeline.process("Hello 123, 世界!")
        assert result == result.lower()  # 已转小写
        assert "0" in result  # 数字归一

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_cer_optimized_preset(self):
        """cer_optimized 预设：标点 + 全半角 + 空白"""
        pipeline = PipelinePresets.cer_optimized()
        assert len(pipeline.get_steps()) == 3
        result = pipeline.process("今天天气，非常好！")
        assert result == "今天天气非常好"

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_asr_evaluation_preset(self):
        """asr_evaluation 预设：标点 + 全半角 + 空白（无分词器时）"""
        pipeline = PipelinePresets.asr_evaluation()
        assert len(pipeline.get_steps()) == 3  # 无分词器时不加语气词过滤

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_create_pipeline_convenience(self):
        """create_pipeline 便捷函数"""
        pipeline = create_pipeline('basic')
        assert len(pipeline.get_steps()) == 3

    @pytest.mark.basic
    @pytest.mark.pipeline
    def test_create_pipeline_invalid_preset(self):
        """create_pipeline 传入无效预设名 → 抛出 ValueError"""
        with pytest.raises(ValueError, match="未知的预设名称"):
            create_pipeline('nonexistent')


# ════════════════════════════════════════════════════
# 第四组：边界条件
# ════════════════════════════════════════════════════

class TestPreprocessingBoundary:
    """预处理边界条件测试"""

    @pytest.mark.basic
    @pytest.mark.pipeline
    @pytest.mark.boundary
    def test_empty_string(self):
        """空字符串通过所有步骤不崩溃"""
        pipeline = PipelinePresets.aggressive()
        result = pipeline.process("")
        assert result == ""

    @pytest.mark.basic
    @pytest.mark.pipeline
    @pytest.mark.boundary
    def test_whitespace_only(self):
        """仅空白字符经过空白归一后变为空字符串"""
        pipeline = PipelinePresets.basic()
        result = pipeline.process("   \t\n  ")
        assert result == ""

    @pytest.mark.basic
    @pytest.mark.pipeline
    @pytest.mark.boundary
    def test_repr(self):
        """Pipeline 和 Step 的 __repr__ 不崩溃"""
        pipeline = PipelinePresets.basic()
        repr_str = repr(pipeline)
        assert "3" in repr_str
        
        step = RemovePunctuationStep()
        repr_str = repr(step)
        assert "启用" in repr_str
