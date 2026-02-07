"""
THULAC分词器实现
基于THULAC库的分词器，提供高精度中文分词
"""

from typing import List, Tuple
from .base import BaseTokenizer, TokenizerInitError, TokenizerProcessError


class ThulacTokenizer(BaseTokenizer):
    """
    THULAC分词器实现
    基于THULAC库，提供高精度中文分词和词性标注功能
    """
    
    def __init__(self):
        super().__init__()
        self.name = "thulac"
        self.thu = None
    
    def initialize(self) -> bool:
        """
        初始化THULAC分词器
        
        Returns:
            bool: 初始化是否成功
            
        Raises:
            TokenizerInitError: 初始化失败时抛出
        """
        try:
            # 检查THULAC是否可用
            try:
                import thulac
            except ImportError:
                raise TokenizerInitError("THULAC库未安装，请运行: pip install thulac")
            
            # 初始化THULAC实例
            try:
                self.thu = thulac.thulac(seg_only=False)  # seg_only=False表示同时进行分词和词性标注
                
                # 测试THULAC是否正常工作
                test_result = self.thu.cut("测试", text=True)
                if not test_result:
                    raise TokenizerInitError("THULAC分词器测试失败")
                
                # 获取版本信息
                try:
                    # 🔧 修复: 使用importlib.metadata获取版本信息（Python 3.8+推荐方式）
                    try:
                        from importlib.metadata import version
                        self.version = version('thulac')
                    except ImportError:
                        # Python < 3.8 使用importlib_metadata
                        try:
                            from importlib_metadata import version
                            self.version = version('thulac')
                        except ImportError:
                            # 备用方案：使用pkg_resources
                            try:
                                import pkg_resources
                                self.version = pkg_resources.get_distribution('thulac').version
                            except:
                                # 最后备用方案：尝试从模块属性获取
                                self.version = getattr(thulac, '__version__', '0.2.x')
                    except Exception as e:
                        print(f"获取THULAC版本失败: {str(e)}")
                        self.version = '0.2.x'  # 设置默认版本
                except Exception:
                    self.version = 'unknown'
                
                self.is_initialized = True
                return True
                
            except Exception as e:
                raise TokenizerInitError(f"THULAC初始化失败: {str(e)}")
                
        except Exception as e:
            raise TokenizerInitError(f"THULAC分词器初始化失败: {str(e)}")
    
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
                raise TokenizerProcessError("THULAC分词器未初始化")
            
            cleaned_text = self.validate_text(text)
            if not cleaned_text:
                return []
            
            # 使用THULAC进行分词，只返回词语
            result_text = self.thu.cut(cleaned_text, text=True)
            # 分割成词语列表
            words = result_text.split()
            
            # 提取词语部分（去掉词性标注）
            result = []
            for word in words:
                if '_' in word:
                    word_part = word.split('_')[0]
                    result.append(word_part)
                else:
                    result.append(word)
            
            return result
            
        except Exception as e:
            raise TokenizerProcessError(f"THULAC分词失败: {str(e)}")
    
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
                raise TokenizerProcessError("THULAC分词器未初始化")
            
            cleaned_text = self.validate_text(text)
            if not cleaned_text:
                return []
            
            # 使用THULAC进行词性标注
            result_text = self.thu.cut(cleaned_text, text=True)
            # 分割成词语列表
            words = result_text.split()
            
            # 解析词语和词性
            result = []
            for word_pos in words:
                if '_' in word_pos:
                    word, pos = word_pos.split('_', 1)
                    result.append((word, pos))
                else:
                    # 如果没有词性标注，使用默认值
                    result.append((word_pos, 'unk'))
            
            return result
            
        except Exception as e:
            raise TokenizerProcessError(f"THULAC词性标注失败: {str(e)}")
    
    def tokenize(self, text: str) -> List[Tuple[str, int, int]]:
        """
        精确分词，返回词语及其在原文中的位置
        由于THULAC不直接提供位置信息，需要手动计算
        
        Args:
            text (str): 待分词的文本
            
        Returns:
            List[Tuple[str, int, int]]: (词语, 开始位置, 结束位置)的元组列表
            
        Raises:
            TokenizerProcessError: 分词处理失败时抛出
        """
        try:
            if not self.is_initialized:
                raise TokenizerProcessError("THULAC分词器未初始化")
            
            cleaned_text = self.validate_text(text)
            if not cleaned_text:
                return []
            
            # 获取分词结果
            words = self.cut(cleaned_text)
            
            # 手动计算位置信息
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
                
                # 如果没有找到匹配（可能由于分词结果与原文不一致），使用近似位置
                if not found:
                    end_pos = current_pos + word_len
                    if end_pos > len(text_chars):
                        end_pos = len(text_chars)
                    result.append((word, current_pos, end_pos))
                    current_pos = end_pos
            
            return result
            
        except Exception as e:
            raise TokenizerProcessError(f"THULAC精确分词失败: {str(e)}")
    
    def get_info(self) -> dict:
        """
        获取THULAC分词器信息
        
        Returns:
            dict: 包含分词器详细信息的字典
        """
        info = super().get_info()
        info.update({
            'description': '基于THULAC库的中文分词器',
            'features': ['分词', '词性标注', '精确位置分词'],
            'dependencies': ['thulac'],
            'performance': '中等',
            'accuracy': '高精度',
            'note': 'tokenize方法使用手动位置计算，可能存在精度差异'
        })
        return info 