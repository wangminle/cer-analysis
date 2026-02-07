import jiwer
import difflib
import re
import jieba
import jieba.posseg
import jieba.analyse

class ASRMetrics:
    """
    提供计算ASR结果准确率的各种指标工具类
    """
    
    @staticmethod
    def preprocess_chinese_text(text):
        """
        使用jieba进行中文文本分词预处理
        
        Args:
            text (str): 输入中文文本
            
        Returns:
            str: 分词后重新组合的文本
        """
        # 使用jieba进行分词
        words = jieba.cut(text)
        # 重新组合文本，保持原始字符
        return "".join(words)
    
    @staticmethod
    def filter_filler_words(text):
        """
        过滤中文语气词，如"嗯"、"啊"、"呢"等
        
        Args:
            text (str): 输入中文文本
            
        Returns:
            str: 过滤掉语气词后的文本
        """
        # 定义常见的语气词列表
        filler_words = ["嗯", "啊", "呢", "吧", "哦", "呀", "啦", "喔", 
                    "诶", "唉", "噢", "喂", "呐", "呵", "咯", "咦", "嘿"]
        
        # 使用jieba词性标注
        words_pos = jieba.posseg.cut(text)
        
        # 过滤语气词
        filtered_words = []
        for word, flag in words_pos:
            # 检查是否为语气词
            if word in filler_words:
                continue
            # 检查词性是否为语气词（y）
            if flag == 'y':
                continue
            filtered_words.append(word)
        
        # 重新组合文本
        return "".join(filtered_words)
    
    @staticmethod
    def normalize_chinese_text(text):
        """
        针对中文特性的标准化处理
        
        Args:
            text (str): 输入中文文本
            
        Returns:
            str: 标准化后的文本
        """
        # 移除标点符号
        text = re.sub(r'[^\w\s]', '', text)
        
        # 统一全角/半角字符
        full_width = "".join(chr(0xff00 + ord(c) - 0x20) if ord(c) <= 0x7f else c for c in text)
        
        # 统一数字格式
        normalized_text = re.sub(r'[0-9０-９]+', '0', full_width)
        
        # 统一空格处理
        normalized_text = re.sub(r'\s+', '', normalized_text)
        
        return normalized_text
    
    @staticmethod
    def get_character_positions(text):
        """
        利用jieba的tokenize功能进行精确字符定位
        
        Args:
            text (str): 输入文本
            
        Returns:
            list: 包含(字符, 位置)元组的列表
        """
        positions = []
        for tk in jieba.tokenize(text):
            word, start, end = tk
            for i, char in enumerate(word):
                positions.append((char, start+i))
        return positions
    
    @staticmethod
    def preprocess_text(text, filter_fillers=False):
        """
        预处理文本：移除标点符号、转换为小写、移除多余空格等
        
        Args:
            text (str): 输入文本
            filter_fillers (bool): 是否过滤语气词
            
        Returns:
            str: 预处理后的文本
        """
        # 创建基本预处理转换
        transformation = jiwer.Compose([
            jiwer.RemoveMultipleSpaces(),
            jiwer.Strip(),
            jiwer.RemovePunctuation(),
            jiwer.ToLowerCase(),
        ])
        
        # 应用预处理
        processed_text = transformation(text)
        
        # 如果需要过滤语气词
        if filter_fillers:
            processed_text = ASRMetrics.filter_filler_words(processed_text)
        
        # 对于中文，先进行jieba分词预处理
        processed_text = ASRMetrics.preprocess_chinese_text(processed_text)
        
        # 应用中文标准化处理
        processed_text = ASRMetrics.normalize_chinese_text(processed_text)
        
        return processed_text
    
    @staticmethod
    def calculate_cer(reference, hypothesis, filter_fillers=False):
        """
        计算字符错误率 (Character Error Rate)
        
        Args:
            reference (str): 参考文本（标准文本）
            hypothesis (str): 假设文本（ASR生成文本）
            filter_fillers (bool): 是否过滤语气词
            
        Returns:
            float: 字符错误率
        """
        # 预处理文本
        ref_processed = ASRMetrics.preprocess_text(reference, filter_fillers)
        hyp_processed = ASRMetrics.preprocess_text(hypothesis, filter_fillers)
        
        # 获取字符位置信息
        ref_positions = ASRMetrics.get_character_positions(ref_processed)
        hyp_positions = ASRMetrics.get_character_positions(hyp_processed)
        
        # 提取字符列表
        ref_chars = [pos[0] for pos in ref_positions] if ref_positions else list(ref_processed)
        hyp_chars = [pos[0] for pos in hyp_positions] if hyp_positions else list(hyp_processed)
        
        # 确保两个字符串都不为空
        if len(ref_chars) == 0:
            ref_chars = [""]
        if len(hyp_chars) == 0:
            hyp_chars = [""]
            
        # 计算编辑距离
        import Levenshtein
        distance = Levenshtein.distance(ref_processed, hyp_processed)
        
        # 计算CER
        if len(ref_processed) > 0:
            cer = distance / len(ref_processed)
        else:
            cer = 1.0 if len(hyp_processed) > 0 else 0.0
        
        return cer
    
    @staticmethod
    def calculate_wer(reference, hypothesis, filter_fillers=False):
        """
        计算词错误率 (Word Error Rate)
        
        Args:
            reference (str): 参考文本（标准文本）
            hypothesis (str): 假设文本（ASR生成文本）
            filter_fillers (bool): 是否过滤语气词
            
        Returns:
            float: 词错误率
        """
        # 预处理文本
        ref_processed = ASRMetrics.preprocess_text(reference, filter_fillers)
        hyp_processed = ASRMetrics.preprocess_text(hypothesis, filter_fillers)
        
        # 对于中文文本，每个字符视为一个"词"
        # 先将字符串转为列表，确保每个元素都是单个字符
        ref_words = [char for char in ref_processed]
        hyp_words = [char for char in hyp_processed]
        
        # 确保列表不为空
        if not ref_words:
            ref_words = [""]
        if not hyp_words:
            hyp_words = [""]
        
        # 使用自定义的方式计算WER
        s, d, i = ASRMetrics._calculate_edit_ops(ref_words, hyp_words)
        if len(ref_words) > 0:
            wer = (s + d + i) / len(ref_words)
        else:
            wer = 1.0 if len(hyp_words) > 0 else 0.0
        
        return wer
    
    @staticmethod
    def _calculate_edit_ops(reference, hypothesis):
        """计算编辑操作（替换、删除、插入）的数量"""
        # 使用Levenshtein库计算编辑操作
        import Levenshtein
        
        # 将列表转为字符串，然后计算编辑距离
        ref_str = "".join(reference)
        hyp_str = "".join(hypothesis)
        
        # 计算编辑操作
        ops = Levenshtein.editops(ref_str, hyp_str)
        
        # 统计各类操作数量
        s = len([op for op in ops if op[0] == 'replace'])  # 替换
        d = len([op for op in ops if op[0] == 'delete'])   # 删除
        i = len([op for op in ops if op[0] == 'insert'])   # 插入
        
        return s, d, i
    
    @staticmethod
    def calculate_accuracy(reference, hypothesis, filter_fillers=False):
        """
        计算准确率 (1 - CER)
        
        Args:
            reference (str): 参考文本（标准文本）
            hypothesis (str): 假设文本（ASR生成文本）
            filter_fillers (bool): 是否过滤语气词
            
        Returns:
            float: 准确率
        """
        cer = ASRMetrics.calculate_cer(reference, hypothesis, filter_fillers)
        return 1.0 - cer
    
    @staticmethod
    def calculate_detailed_metrics(reference, hypothesis, filter_fillers=False):
        """
        计算详细的错误指标，包括插入、删除、替换错误
        
        Args:
            reference (str): 参考文本（标准文本）
            hypothesis (str): 假设文本（ASR生成文本）
            filter_fillers (bool): 是否过滤语气词
            
        Returns:
            dict: 包含各种错误指标的字典
        """
        # 预处理文本
        ref_processed = ASRMetrics.preprocess_text(reference, filter_fillers)
        hyp_processed = ASRMetrics.preprocess_text(hypothesis, filter_fillers)
        
        # 获取字符位置信息
        ref_positions = ASRMetrics.get_character_positions(ref_processed)
        hyp_positions = ASRMetrics.get_character_positions(hyp_processed)
        
        # 提取字符列表
        ref_chars = [pos[0] for pos in ref_positions] if ref_positions else list(ref_processed)
        hyp_chars = [pos[0] for pos in hyp_positions] if hyp_positions else list(hyp_processed)
        
        # 确保列表不为空
        if not ref_chars:
            ref_chars = [""]
        if not hyp_chars:
            hyp_chars = [""]
        
        # 使用自定义方式计算详细指标
        s, d, i = ASRMetrics._calculate_edit_ops(ref_chars, hyp_chars)
        
        # 计算总错误数和字符错误率
        total_errors = s + d + i
        ref_length = len(ref_chars)
        hyp_length = len(hyp_chars)
        
        if ref_length > 0:
            cer = total_errors / ref_length
        else:
            cer = 1.0 if hyp_length > 0 else 0.0
        
        # 返回详细指标
        return {
            'cer': cer,
            'wer': cer,  # 对于中文，CER和WER相同
            'mer': cer,  # 匹配错误率
            'wil': cer,  # 词信息丢失率
            'wip': 1.0 - cer,  # 词信息保留率
            'hits': ref_length - (s + d),  # 命中数
            'substitutions': s,  # 替换错误数
            'deletions': d,      # 删除错误数
            'insertions': i,     # 插入错误数
            'ref_length': ref_length,  # 参考文本长度
            'hyp_length': hyp_length,  # 假设文本长度
            'accuracy': 1.0 - cer  # 准确率
        }
    
    @staticmethod
    def show_differences(reference, hypothesis, filter_fillers=False):
        """
        显示两个文本之间的差异
        
        Args:
            reference (str): 参考文本（标准文本）
            hypothesis (str): 假设文本（ASR生成文本）
            filter_fillers (bool): 是否过滤语气词
            
        Returns:
            str: 格式化的差异信息
        """
        # 预处理文本
        ref_processed = ASRMetrics.preprocess_text(reference, filter_fillers)
        hyp_processed = ASRMetrics.preprocess_text(hypothesis, filter_fillers)
        
        # 使用difflib计算差异
        d = difflib.Differ()
        diff = list(d.compare(list(ref_processed), list(hyp_processed)))
        
        return ''.join(diff)
    
    @staticmethod
    def highlight_errors(reference, hypothesis, filter_fillers=False):
        """
        高亮显示错误部分
        
        Args:
            reference (str): 参考文本（标准文本）
            hypothesis (str): 假设文本（ASR生成文本）
            filter_fillers (bool): 是否过滤语气词
            
        Returns:
            tuple: (参考文本高亮版, 假设文本高亮版)
        """
        # 预处理文本
        ref_processed = ASRMetrics.preprocess_text(reference, filter_fillers)
        hyp_processed = ASRMetrics.preprocess_text(hypothesis, filter_fillers)
        
        # 使用difflib的SequenceMatcher找出匹配和不匹配的部分
        matcher = difflib.SequenceMatcher(None, ref_processed, hyp_processed)
        
        # 构建高亮标记的字符串
        ref_highlighted = []
        hyp_highlighted = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                ref_highlighted.append(ref_processed[i1:i2])
                hyp_highlighted.append(hyp_processed[j1:j2])
            elif tag == 'replace':
                ref_highlighted.append(f"[{ref_processed[i1:i2]}]")
                hyp_highlighted.append(f"[{hyp_processed[j1:j2]}]")
            elif tag == 'delete':
                ref_highlighted.append(f"[{ref_processed[i1:i2]}]")
            elif tag == 'insert':
                hyp_highlighted.append(f"[{hyp_processed[j1:j2]}]")
        
        return ''.join(ref_highlighted), ''.join(hyp_highlighted) 