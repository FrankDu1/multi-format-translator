"""
本地翻译服务 - 使用 Hugging Face MarianMT 模型
支持离线翻译，无需外部API

注意：需要安装 torch 和 transformers
如果使用云翻译模式，此模块不会被使用
"""

import os
from typing import List, Optional
import logging

# 条件导入 torch 和 transformers
try:
    # Compatibility shim: ensure torch.utils._pytree has register_pytree_node if possible
    from services.torch_compat import *  # noqa: F401,F403
    from transformers import MarianMTModel, MarianTokenizer
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("⚠️ torch/transformers 不可用，本地翻译需要云翻译模式")

# 配置国内镜像源（适用于中国大陆）
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 配置日志 - 只显示关键信息
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # 简化格式，不显示模块名
)
logger = logging.getLogger(__name__)

# 抑制 transformers 的详细日志
logging.getLogger("transformers").setLevel(logging.WARNING)
logging.getLogger("transformers.modeling_utils").setLevel(logging.ERROR)


class LocalTranslator:
    """本地翻译器类"""
    
    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"✓ 翻译器初始化完成 (设备: {self.device.upper()})")
        
        # 预定义的模型映射
        self.model_map = {
            ("zh", "en"): "Helsinki-NLP/opus-mt-zh-en",
            ("en", "zh"): "Helsinki-NLP/opus-mt-en-zh",
            # 可以添加更多语言对
        }
    
    def load_model(self, source_lang: str, target_lang: str) -> bool:
        """
        加载指定语言对的翻译模型
        
        Args:
            source_lang: 源语言代码 (如 'zh', 'en')
            target_lang: 目标语言代码 (如 'zh', 'en')
            
        Returns:
            bool: 是否成功加载
        """
        lang_pair = (source_lang, target_lang)
        
        # 如果已经加载，直接返回
        if lang_pair in self.models:
            logger.info(f"模型已缓存，直接使用: {source_lang} -> {target_lang}")
            return True
        
        # 获取模型名称
        model_name = self.model_map.get(lang_pair)
        if not model_name:
            logger.error(f"不支持的语言对: {source_lang} -> {target_lang}")
            return False
        
        try:
            # 检查模型是否已下载
            from pathlib import Path
            cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
            model_cache = cache_dir / f"models--{model_name.replace('/', '--')}"
            
            if not model_cache.exists():
                print(f"\n⏳ 首次运行，正在下载模型...")
                print(f"📦 模型: {model_name}")
                print(f"📦 大小: 约300MB")
                print(f"💾 缓存: {model_cache}")
                print(f"⚠️  请勿中断下载...\n")
                is_cached = False
            else:
                print(f"✓ 模型已缓存，正在加载...")
                is_cached = True
            
            # 加载tokenizer和模型（抑制详细日志）
            print(f"  [1/3] 加载 Tokenizer...", end='', flush=True)
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                tokenizer = MarianTokenizer.from_pretrained(
                    model_name,
                    local_files_only=is_cached
                )
            print(" ✓")
            
            print(f"  [2/3] 加载翻译模型...", end='', flush=True)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = MarianMTModel.from_pretrained(
                    model_name,
                    local_files_only=is_cached
                )
            print(" ✓")
            
            print(f"  [3/3] 准备推理引擎...", end='', flush=True)
            model.to(self.device)
            model.eval()  # 设置为评估模式
            print(" ✓")
            
            # 缓存模型
            self.tokenizers[lang_pair] = tokenizer
            self.models[lang_pair] = model
            
            print(f"✅ 模型就绪！({source_lang} → {target_lang})\n")
            return True
            
        except Exception as e:
            print(f"\n❌ 模型加载失败: {e}\n")
            print(f"可能的原因:")
            print(f"  1. 网络连接问题（首次需要下载模型）")
            print(f"  2. 磁盘空间不足（需要至少1GB）")
            print(f"  3. 权限问题（无法写入缓存目录）\n")
            print(f"解决方案:")
            print(f"  • 检查网络连接")
            print(f"  • 清理磁盘空间")
            print(f"  • 确保已配置镜像: .\setup_china.ps1\n")
            return False
    
    def translate(
        self, 
        texts: List[str], 
        source_lang: str = "zh", 
        target_lang: str = "en",
        batch_size: int = 8
    ) -> List[str]:
        """
        翻译文本列表
        
        Args:
            texts: 要翻译的文本列表
            source_lang: 源语言代码
            target_lang: 目标语言代码
            batch_size: 批处理大小
            
        Returns:
            List[str]: 翻译后的文本列表
        """
        if not texts:
            return []
        
        # 加载模型
        lang_pair = (source_lang, target_lang)
        if not self.load_model(source_lang, target_lang):
            logger.error("模型加载失败")
            return texts  # 返回原文
        
        tokenizer = self.tokenizers[lang_pair]
        model = self.models[lang_pair]
        
        translated_texts = []
        
        try:
            # 分批处理
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Tokenize
                inputs = tokenizer(
                    batch, 
                    return_tensors="pt", 
                    padding=True, 
                    truncation=True,
                    max_length=512
                ).to(self.device)
                
                # 生成翻译
                with torch.no_grad():
                    translated = model.generate(**inputs)
                
                # Decode
                batch_translations = tokenizer.batch_decode(
                    translated, 
                    skip_special_tokens=True
                )
                
                translated_texts.extend(batch_translations)
                
                # 只在批量翻译时显示进度
                if len(texts) > 3:
                    print(f"  翻译进度: {len(translated_texts)}/{len(texts)}", end='\r', flush=True)
            
            # 清除进度行
            if len(texts) > 3:
                print(" " * 50, end='\r')
            
            return translated_texts
            
        except Exception as e:
            print(f"\n❌ 翻译失败: {e}")
            return texts  # 返回原文
    
    def translate_single(
        self, 
        text: str, 
        source_lang: str = "zh", 
        target_lang: str = "en"
    ) -> str:
        """
        翻译单个文本
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言代码
            target_lang: 目标语言代码
            
        Returns:
            str: 翻译后的文本
        """
        if not text or not text.strip():
            return text
        
        results = self.translate([text], source_lang, target_lang)
        return results[0] if results else text
    
    def detect_language(self, text: str) -> str:
        """
        简单的语言检测（基于字符判断）
        
        Args:
            text: 要检测的文本
            
        Returns:
            str: 语言代码 ('zh' 或 'en')
        """
        if not text:
            return "en"
        
        # 统计中文字符数量
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        total_chars = len(text.strip())
        
        if total_chars == 0:
            return "en"
        
        # 如果中文字符超过30%，判定为中文
        if chinese_chars / total_chars > 0.3:
            return "zh"
        else:
            return "en"
    
    def auto_translate(self, text: str, target_lang: str = None) -> dict:
        """
        自动检测语言并翻译
        
        Args:
            text: 要翻译的文本
            target_lang: 目标语言（可选，自动反向翻译）
            
        Returns:
            dict: 包含翻译结果和元信息
        """
        source_lang = self.detect_language(text)
        
        # 自动确定目标语言
        if target_lang is None:
            target_lang = "en" if source_lang == "zh" else "zh"
        
        # 翻译
        translated_text = self.translate_single(text, source_lang, target_lang)
        
        return {
            "original_text": text,
            "translated_text": translated_text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "detected_language": source_lang,
            "language_confidence": 0.95  # 简化版，固定置信度
        }


# 全局翻译器实例（单例模式）
_translator_instance = None


def get_translator() -> LocalTranslator:
    """
    获取翻译器实例（单例模式）
    
    Returns:
        LocalTranslator: 翻译器实例
    """
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = LocalTranslator()
    return _translator_instance


# 便捷函数
def translate_text(
    text: str, 
    source_lang: str = "zh", 
    target_lang: str = "en"
) -> str:
    """
    翻译单个文本的便捷函数
    
    Args:
        text: 要翻译的文本
        source_lang: 源语言代码
        target_lang: 目标语言代码
        
    Returns:
        str: 翻译后的文本
    """
    translator = get_translator()
    return translator.translate_single(text, source_lang, target_lang)


def translate_texts(
    texts: List[str], 
    source_lang: str = "zh", 
    target_lang: str = "en"
) -> List[str]:
    """
    翻译多个文本的便捷函数
    
    Args:
        texts: 要翻译的文本列表
        source_lang: 源语言代码
        target_lang: 目标语言代码
        
    Returns:
        List[str]: 翻译后的文本列表
    """
    translator = get_translator()
    return translator.translate(texts, source_lang, target_lang)


def auto_translate(text: str, target_lang: str = None) -> dict:
    """
    自动检测语言并翻译的便捷函数
    
    Args:
        text: 要翻译的文本
        target_lang: 目标语言（可选）
        
    Returns:
        dict: 翻译结果
    """
    translator = get_translator()
    return translator.auto_translate(text, target_lang)
