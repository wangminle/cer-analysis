"""
HanLP分词器实现
基于HanLP库的分词器，提供BERT等深度学习模型支持
"""

from typing import List, Tuple
from .base import BaseTokenizer, TokenizerInitError, TokenizerProcessError


class HanlpTokenizer(BaseTokenizer):
    """
    HanLP分词器实现
    基于HanLP 2.x版本，支持BERT等深度学习模型的中文分词
    """
    
    def __init__(self):
        super().__init__()
        self.name = "hanlp"
        self.hanlp = None
        self.tok_model = None
        self.pos_model = None
    
    def initialize(self) -> bool:
        """
        初始化HanLP分词器
        
        Returns:
            bool: 初始化是否成功
            
        Raises:
            TokenizerInitError: 初始化失败时抛出
        """
        try:
            # 检查HanLP是否可用
            try:
                import hanlp
                self.hanlp = hanlp
            except ImportError:
                raise TokenizerInitError("HanLP库未安装，请运行: pip install hanlp")
            
            # 初始化分词模型
            try:
                # 使用HanLP的中文分词模型
                # 优先使用BERT模型，如果不可用则使用默认模型
                try:
                    self.tok_model = hanlp.load(hanlp.pretrained.tok.SIGHAN2005_PKU_BERT_BASE_ZH)
                except:
                    try:
                        self.tok_model = hanlp.load(hanlp.pretrained.tok.CTB6_CONVSEG)
                    except:
                        # 如果预训练模型不可用，尝试使用最基础的模型
                        self.tok_model = hanlp.load('PKU_NAME_MERGED_SYS_OPEN')
                
                # 初始化词性标注模型
                try:
                    self.pos_model = hanlp.load(hanlp.pretrained.pos.CTB5_POS_RNN_FASTTEXT_ZH)
                except:
                    # 如果词性标注模型不可用，设为None，后续使用替代方案
                    self.pos_model = None
                
                # 测试分词器是否正常工作
                test_result = self.tok_model("测试")
                if not test_result:
                    raise TokenizerInitError("HanLP分词器测试失败")
                
                # 获取版本信息
                try:
                    # 🔧 优化: 使用多种方式获取版本信息
                    try:
                        from importlib.metadata import version
                        self.version = version('hanlp')
                    except ImportError:
                        # Python < 3.8 使用importlib_metadata
                        try:
                            from importlib_metadata import version
                            self.version = version('hanlp')
                        except ImportError:
                            # 备用方案：从模块属性获取
                            self.version = getattr(hanlp, '__version__', 'unknown')
                    except Exception as e:
                        print(f"获取HanLP版本失败: {str(e)}")
                        self.version = getattr(hanlp, '__version__', 'unknown')
                except Exception:
                    self.version = 'unknown'
                
                self.is_initialized = True
                return True
                
            except Exception as e:
                raise TokenizerInitError(f"HanLP模型加载失败: {str(e)}")
                
        except Exception as e:
            raise TokenizerInitError(f"HanLP分词器初始化失败: {str(e)}")
    
    def cut(self, text: str) -> List[str]:
        """
        基础分词功能
        
        Args:
            text (str): 待分词的文本
            
        Returns:
            List[str]: 分词结果列表
            
        Raises:
            TokenizerProcessError: 分词处理失败时抛出
        """
        try:
            if not self.is_initialized:
                raise TokenizerProcessError("HanLP分词器未初始化")
            
            cleaned_text = self.validate_text(text)
            if not cleaned_text:
                return []
            
            # 使用HanLP进行分词
            result = self.tok_model(cleaned_text)
            return result
            
        except Exception as e:
            raise TokenizerProcessError(f"HanLP分词失败: {str(e)}")
    
    def posseg(self, text: str) -> List[Tuple[str, str]]:
        """
        词性标注功能
        
        Args:
            text (str): 待标注的文本
            
        Returns:
            List[Tuple[str, str]]: (词语, 词性)的元组列表
            
        Raises:
            TokenizerProcessError: 词性标注失败时抛出
        """
        try:
            if not self.is_initialized:
                raise TokenizerProcessError("HanLP分词器未初始化")
            
            cleaned_text = self.validate_text(text)
            if not cleaned_text:
                return []
            
            # 先进行分词
            words = self.cut(cleaned_text)
            
            if self.pos_model:
                # 如果有词性标注模型，使用HanLP进行词性标注
                try:
                    pos_tags = self.pos_model(words)
                    result = list(zip(words, pos_tags))
                    return result
                except Exception as e:
                    # 如果词性标注失败，使用默认词性
                    result = [(word, 'unk') for word in words]
                    return result
            else:
                # 如果没有词性标注模型，使用默认词性
                result = [(word, 'unk') for word in words]
                return result
            
        except Exception as e:
            raise TokenizerProcessError(f"HanLP词性标注失败: {str(e)}")
    
    def tokenize(self, text: str) -> List[Tuple[str, int, int]]:
        """
        精确分词，返回词语及其在原文中的位置
        HanLP某些模型支持输出偏移量，如果不支持则手动计算
        
        Args:
            text (str): 待分词的文本
            
        Returns:
            List[Tuple[str, int, int]]: (词语, 开始位置, 结束位置)的元组列表
            
        Raises:
            TokenizerProcessError: 分词处理失败时抛出
        """
        try:
            if not self.is_initialized:
                raise TokenizerProcessError("HanLP分词器未初始化")
            
            cleaned_text = self.validate_text(text)
            if not cleaned_text:
                return []
            
            # 尝试使用HanLP的偏移量功能
            try:
                # 检查模型是否支持输出偏移量
                if hasattr(self.tok_model, 'config') and hasattr(self.tok_model.config, 'output_offsets'):
                    # 启用偏移量输出
                    self.tok_model.config.output_offsets = True
                    result_with_offsets = self.tok_model(cleaned_text)
                    
                    if isinstance(result_with_offsets, tuple) and len(result_with_offsets) == 2:
                        tokens, offsets = result_with_offsets
                        result = []
                        for token, (start, end) in zip(tokens, offsets):
                            result.append((token, start, end))
                        return result
            except:
                pass  # 如果不支持偏移量，继续使用手动计算
            
            # 手动计算位置信息
            words = self.cut(cleaned_text)
            result = []
            current_pos = 0
            text_chars = list(cleaned_text)
            
            for word in words:
                word_chars = list(word)
                word_len = len(word_chars)
                
                # 在剩余文本中查找当前词语
                start_pos = current_pos
                found = False
                
                # 向前搜索匹配位置
                while start_pos <= len(text_chars) - word_len:
                    # 检查是否匹配
                    match = True
                    for i, char in enumerate(word_chars):
                        if start_pos + i >= len(text_chars) or text_chars[start_pos + i] != char:
                            match = False
                            break
                    
                    if match:
                        end_pos = start_pos + word_len
                        result.append((word, start_pos, end_pos))
                        current_pos = end_pos
                        found = True
                        break
                    
                    start_pos += 1
                
                # 如果没有找到匹配，使用近似位置
                if not found:
                    end_pos = current_pos + word_len
                    if end_pos > len(text_chars):
                        end_pos = len(text_chars)
                    result.append((word, current_pos, end_pos))
                    current_pos = end_pos
            
            return result
            
        except Exception as e:
            raise TokenizerProcessError(f"HanLP精确分词失败: {str(e)}")
    
    def get_info(self) -> dict:
        """
        获取HanLP分词器信息
        
        Returns:
            dict: 包含分词器详细信息的字典
        """
        info = super().get_info()
        
        # 获取模型信息
        tok_model_name = 'unknown'
        pos_model_name = 'unknown'
        
        if self.tok_model:
            if hasattr(self.tok_model, 'model_name'):
                tok_model_name = self.tok_model.model_name
            elif hasattr(self.tok_model, '__class__'):
                tok_model_name = self.tok_model.__class__.__name__
        
        if self.pos_model:
            if hasattr(self.pos_model, 'model_name'):
                pos_model_name = self.pos_model.model_name
            elif hasattr(self.pos_model, '__class__'):
                pos_model_name = self.pos_model.__class__.__name__
        
        info.update({
            'description': '基于HanLP库的深度学习中文分词器',
            'features': ['分词', '词性标注', '精确位置分词', 'BERT支持'],
            'dependencies': ['hanlp'],
            'performance': '较慢（深度学习模型）',
            'accuracy': '最高精度',
            'tok_model': tok_model_name,
            'pos_model': pos_model_name,
            'note': '首次使用时需要下载模型文件'
        })
        return info