"""
NLLB (No Language Left Behind) 翻译服务
使用Meta的NLLB模型进行高质量多语言翻译
"""

import os
# Compatibility shim: ensure torch.utils._pytree has register_pytree_node if possible
from services.torch_compat import *  # noqa: F401,F403
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class NLLBTranslator:
    """NLLB翻译器"""
    
    def __init__(self, model_name="facebook/nllb-200-distilled-600M"):
        """
        初始化NLLB翻译器
        
        Args:
            model_name: 模型名称，可选：
                - facebook/nllb-200-distilled-600M (600MB, 推荐)
                - facebook/nllb-200-distilled-1.3B (1.3GB, 更好效果)
                - facebook/nllb-200-1.3B (1.3GB, 完整版)
                - facebook/nllb-200-3.3B (3.3GB, 最佳效果，需要更多内存)
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.model = None
        
        # 语言代码映射 (NLLB使用特殊的语言代码)
        self.lang_map = {
            'zh': 'zho_Hans',  # 简体中文
            'en': 'eng_Latn',  # 英语
            'zh_cn': 'zho_Hans',
            'zh_tw': 'zho_Hant',  # 繁体中文
            'chinese': 'zho_Hans',
            'english': 'eng_Latn'
        }
        
        print(f"✓ 初始化 NLLB 翻译器 (模型: {model_name}, 设备: {self.device})")
    
    def load_model(self):
        """加载模型"""
        if self.model is not None:
            return
        
        print(f"正在加载 NLLB 模型: {self.model_name}")
        print("首次加载需要下载模型文件，请耐心等待...")
        
        # 配置中国镜像
        os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
        
        try:
            # 加载tokenizer
            print("  [1/2] 加载 Tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            print("  ✓ Tokenizer 加载完成")
            
            # 加载模型
            print("  [2/2] 加载模型...")
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            self.model.to(self.device)
            self.model.eval()
            print("  ✓ 模型加载完成")
            
            print(f"✓ NLLB 模型加载成功 (设备: {self.device})")
            
        except Exception as e:
            print(f"✗ 模型加载失败: {e}")
            raise
    
    def get_lang_code(self, lang):
        """获取NLLB语言代码"""
        lang = lang.lower().strip()
        return self.lang_map.get(lang, lang)
    
    def translate(self, text, src_lang='zh', tgt_lang='en'):
        """
        翻译文本
        
        Args:
            text: 要翻译的文本
            src_lang: 源语言 ('zh', 'en')
            tgt_lang: 目标语言 ('zh', 'en')
        
        Returns:
            翻译后的文本
        """
        if not text or not text.strip():
            return ""
        
        # 确保模型已加载
        if self.model is None:
            self.load_model()
        
        # 转换语言代码
        src_code = self.get_lang_code(src_lang)
        tgt_code = self.get_lang_code(tgt_lang)
        
        try:
            # 设置源语言
            self.tokenizer.src_lang = src_code
            
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.device)
            
            # 获取目标语言的token ID
            # NLLB tokenizer的正确方法
            try:
                # 尝试获取特殊token的ID
                # NLLB在词汇表中使用 __tgt_lang__ 格式
                tgt_token = f"__{tgt_code}__"
                if tgt_token in self.tokenizer.get_vocab():
                    tgt_lang_id = self.tokenizer.get_vocab()[tgt_token]
                else:
                    # 直接使用语言代码
                    tgt_lang_id = self.tokenizer.convert_tokens_to_ids(tgt_code)
            except:
                # 备用方法
                tgt_lang_id = self.tokenizer.convert_tokens_to_ids(tgt_code)
            
            # 生成翻译
            with torch.no_grad():
                generated_tokens = self.model.generate(
                    **inputs,
                    forced_bos_token_id=tgt_lang_id,
                    max_length=512,
                    num_beams=5,
                    early_stopping=True
                )
            
            # 解码
            translated = self.tokenizer.batch_decode(
                generated_tokens,
                skip_special_tokens=True
            )[0]
            
            return translated.strip()
            
        except Exception as e:
            print(f"翻译失败: {e}")
            import traceback
            traceback.print_exc()
            return f"[翻译错误: {str(e)}]"
    
    def translate_batch(self, texts, src_lang='zh', tgt_lang='en', batch_size=8):
        """
        批量翻译
        
        Args:
            texts: 文本列表
            src_lang: 源语言
            tgt_lang: 目标语言
            batch_size: 批次大小
        
        Returns:
            翻译结果列表
        """
        if not texts:
            return []
        
        # 确保模型已加载
        if self.model is None:
            self.load_model()
        
        results = []
        
        # 分批处理
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # 过滤空文本
            non_empty = [(idx, text) for idx, text in enumerate(batch) if text and text.strip()]
            
            if not non_empty:
                results.extend([''] * len(batch))
                continue
            
            indices, batch_texts = zip(*non_empty)
            
            # 翻译批次
            batch_results = []
            for text in batch_texts:
                translated = self.translate(text, src_lang, tgt_lang)
                batch_results.append(translated)
            
            # 重建结果（包括空文本）
            result_dict = dict(zip(indices, batch_results))
            for idx in range(len(batch)):
                results.append(result_dict.get(idx, ''))
        
        return results
    
    def auto_translate(self, text):
        """
        自动检测语言并翻译
        中文->英文, 英文->中文
        """
        if not text or not text.strip():
            return ""
        
        # 简单的语言检测
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
        
        if has_chinese:
            return self.translate(text, src_lang='zh', tgt_lang='en')
        else:
            return self.translate(text, src_lang='en', tgt_lang='zh')


# 单例模式
_translator_instance = None

def get_translator(model_name="facebook/nllb-200-distilled-600M"):
    """获取翻译器单例"""
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = NLLBTranslator(model_name)
    return _translator_instance


def translate_text(text, src_lang='zh', tgt_lang='en'):
    """便捷函数：翻译单个文本"""
    translator = get_translator()
    return translator.translate(text, src_lang, tgt_lang)


def translate_texts(texts, src_lang='zh', tgt_lang='en'):
    """便捷函数：批量翻译"""
    translator = get_translator()
    return translator.translate_batch(texts, src_lang, tgt_lang)


if __name__ == "__main__":
    # 测试
    print("=" * 70)
    print("NLLB 翻译器测试")
    print("=" * 70)
    
    translator = get_translator()
    
    # 测试1: 中文->英文
    print("\n【测试 1】中文 -> 英文")
    text_zh = "你好，世界！这是一个测试。"
    result = translator.translate(text_zh, 'zh', 'en')
    print(f"原文: {text_zh}")
    print(f"译文: {result}")
    
    # 测试2: 英文->中文
    print("\n【测试 2】英文 -> 中文")
    text_en = "Hello, world! This is a test."
    result = translator.translate(text_en, 'en', 'zh')
    print(f"原文: {text_en}")
    print(f"译文: {result}")
    
    # 测试3: 自动检测
    print("\n【测试 3】自动检测")
    result1 = translator.auto_translate("机器学习是人工智能的一个分支")
    print(f"中文: 机器学习是人工智能的一个分支")
    print(f"译文: {result1}")
    
    result2 = translator.auto_translate("Machine learning is a branch of artificial intelligence")
    print(f"英文: Machine learning is a branch of artificial intelligence")
    print(f"译文: {result2}")
    
    print("\n" + "=" * 70)
    print("测试完成！")
