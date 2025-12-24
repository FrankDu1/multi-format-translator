"""
NLLB (No Language Left Behind) 翻译服务
使用Meta的NLLB模型进行高质量多语言翻译
"""

import os
import logging
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# 【新增】导入配置
try:
    from config import (
        NLLB_MODEL_NAME,
        NLLB_BATCH_SIZE,
        NLLB_MAX_LENGTH,
        NLLB_NUM_BEAMS,
        NLLB_USE_FP16,
        USE_GPU,
        GPU_DEVICE_ID,
        GPU_MEMORY_FRACTION,
        PYTORCH_CUDA_ALLOC_CONF
    )
except ImportError:
    # 如果导入失败,使用默认值
    NLLB_MODEL_NAME = "facebook/nllb-200-distilled-600M"
    NLLB_BATCH_SIZE = 8
    NLLB_MAX_LENGTH = 200
    NLLB_NUM_BEAMS = 4
    NLLB_USE_FP16 = True
    USE_GPU = True
    GPU_DEVICE_ID = 0
    GPU_MEMORY_FRACTION = 0.7
    PYTORCH_CUDA_ALLOC_CONF = "expandable_segments:True"

logger = logging.getLogger(__name__)

class NLLBTranslator:
    """NLLB翻译器"""
    
    def __init__(self, model_name=None):  # 【修改】改为可选参数
        """
        初始化NLLB翻译器
        
        Args:
            model_name: 模型名称，如果为None则从配置文件读取
        """
        # 🔥 新增: 初始化 Ollama 服务
        try:
            from services.ollama_service import ollama_service
            self.ollama_service = ollama_service
            logger.info("✓ Ollama AI 总结服务已加载")
        except Exception as e:
            logger.warning(f"⚠️ Ollama AI 总结服务加载失败: {e}")
            self.ollama_service = None
    
        # 【修改】优先使用配置文件
        if model_name is None:
            model_name = NLLB_MODEL_NAME
        
        self.model_name = model_name
        
        # 【修改】设置PyTorch CUDA内存分配器
        if PYTORCH_CUDA_ALLOC_CONF:
            os.environ['PYTORCH_CUDA_ALLOC_CONF'] = PYTORCH_CUDA_ALLOC_CONF
            logger.info(f"✓ 设置 PYTORCH_CUDA_ALLOC_CONF: {PYTORCH_CUDA_ALLOC_CONF}")
        
        # 【修改】根据配置选择设备
        if USE_GPU and torch.cuda.is_available():
            self.device = f"cuda:{GPU_DEVICE_ID}"
            logger.info(f"✓ 使用 GPU: {torch.cuda.get_device_name(GPU_DEVICE_ID)}")
            logger.info(f"✓ GPU 显存限制: {GPU_MEMORY_FRACTION * 100}%")
        else:
            self.device = "cpu"
            logger.info("✓ 使用 CPU")
        
        self.tokenizer = None
        self.model = None
        
        # 【新增】存储配置参数
        self.batch_size = NLLB_BATCH_SIZE
        self.max_length = NLLB_MAX_LENGTH
        self.num_beams = NLLB_NUM_BEAMS
        self.use_fp16 = NLLB_USE_FP16
        
        # 语言代码映射 (NLLB使用特殊的语言代码)
        self.lang_map = {
            'zh': 'zho_Hans',
            'en': 'eng_Latn',
            'zh_cn': 'zho_Hans',
            'zh_tw': 'zho_Hant',
            'chinese': 'zho_Hans',
            'english': 'eng_Latn',
            'de': 'deu_Latn',
            'german': 'deu_Latn',
            'deutsch': 'deu_Latn',
            'fr': 'fra_Latn',
            'french': 'fra_Latn',
            'es': 'spa_Latn', 
            'spanish': 'spa_Latn',
            'ja': 'jpn_Jpan',
            'japanese': 'jpn_Jpan',
            'ko': 'kor_Hang',
            'korean': 'kor_Hang',
            'ru': 'rus_Cyrl',
            'russian': 'rus_Cyrl',
        }
        
        logger.info(f"✓ 初始化 NLLB 翻译器")
        logger.info(f"  模型: {self.model_name}")
        logger.info(f"  设备: {self.device}")
        logger.info(f"  批次大小: {self.batch_size}")
        logger.info(f"  最大长度: {self.max_length}")
        logger.info(f"  Beam搜索: {self.num_beams}")
        logger.info(f"  FP16: {self.use_fp16}")
    
    def load_model(self):
        """加载模型"""
        if self.model is not None:
            return
        
        logger.info(f"📦 加载模型: {self.model_name}...")
        
        try:
            # 加载tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # 【新增】预先获取lang_code_to_id的访问方法
            if hasattr(self.tokenizer, 'lang_code_to_id'):
                self._get_lang_token_id = lambda code: self.tokenizer.lang_code_to_id[code]
                logger.info("✓ 使用 lang_code_to_id 方法")
            else:
                self._get_lang_token_id = lambda code: self.tokenizer.convert_tokens_to_ids(code)
                logger.info("✓ 使用 convert_tokens_to_ids 方法")
            
            # 根据配置加载模型
            if self.use_fp16 and self.device.startswith("cuda"):
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16
                )
                logger.info("✓ 使用 FP16 精度")
            else:
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    self.model_name
                )
                logger.info("✓ 使用 FP32 精度")
            
            # 移动到设备
            self.model = self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"✅ 模型加载成功: {self.model_name}")
            
            # 显示显存使用情况
            if self.device.startswith("cuda"):
                allocated = torch.cuda.memory_allocated(GPU_DEVICE_ID) / 1024**3
                reserved = torch.cuda.memory_reserved(GPU_DEVICE_ID) / 1024**3
                logger.info(f"📊 GPU 显存: 已分配 {allocated:.2f}GB, 已预留 {reserved:.2f}GB")
            
        except Exception as e:
            logger.error(f"❌ 模型加载失败: {e}")
            raise
    
    def get_lang_code(self, lang):
        """获取NLLB语言代码"""
        lang_lower = lang.lower()
        return self.lang_map.get(lang_lower, lang)
    
    def translate(self, text, src_lang='zh', tgt_lang='en'):
        """翻译单个文本"""
        if not text or not text.strip():
            return ""
        
        self.load_model()
        
        src_code = self.get_lang_code(src_lang)
        tgt_code = self.get_lang_code(tgt_lang)
        
        # 设置源语言
        self.tokenizer.src_lang = src_code
        
        # 编码
        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            max_length=self.max_length,
            truncation=True
        ).to(self.device)
        
        # 翻译
        with torch.no_grad():
            translated_tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=self._get_lang_token_id(tgt_code),  # 【修复】使用统一方法
                max_length=self.max_length,
                num_beams=self.num_beams
            )
        
        # 解码
        result = self.tokenizer.batch_decode(
            translated_tokens, 
            skip_special_tokens=True
        )[0]
        
        return result
    
    def translate_batch(self, texts, src_lang='zh', tgt_lang='en', batch_size=None):
        """批量翻译"""
        if not texts:
            return []
        
        self.load_model()
        
        if batch_size is None:
            batch_size = self.batch_size
        
        src_code = self.get_lang_code(src_lang)
        tgt_code = self.get_lang_code(tgt_lang)
        
        # 设置源语言
        self.tokenizer.src_lang = src_code
        
        results = []
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        logger.info(f"📊 批量翻译: {len(texts)} 个文本, 分 {total_batches} 批")
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # 编码
            inputs = self.tokenizer(
                batch, 
                return_tensors="pt", 
                padding=True,
                max_length=self.max_length,
                truncation=True
            ).to(self.device)
            
            # 翻译
            with torch.no_grad():
                translated_tokens = self.model.generate(
                    **inputs,
                    forced_bos_token_id=self._get_lang_token_id(tgt_code),  # 【修复】使用统一方法
                    max_length=self.max_length,
                    num_beams=self.num_beams
                )
            
            # 解码
            batch_results = self.tokenizer.batch_decode(
                translated_tokens, 
                skip_special_tokens=True
            )
            
            results.extend(batch_results)
            
            # 【新增】显示进度
            if (i // batch_size + 1) % 10 == 0 or (i + batch_size) >= len(texts):
                logger.info(f"  进度: {len(results)}/{len(texts)}")
        
        return results
    
    def auto_translate(self, text):
        """自动检测语言并翻译（中->英 或 英->中）"""
        # 简单检测：包含中文字符则认为是中文
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
        
        if has_chinese:
            return self.translate(text, 'zh', 'en')
        else:
            return self.translate(text, 'en', 'zh')

    # 🔥 新增: 带AI总结的翻译方法
    def translate_with_summary(
        self,
        texts,
        src_lang='zh',
        tgt_lang='en',
        batch_size=None,
        enable_summary=False
    ):
        """
        批量翻译并可选生成AI总结
        
        Args:
            texts: 文本列表
            src_lang: 源语言
            tgt_lang: 目标语言
            batch_size: 批次大小
            enable_summary: 是否启用AI总结
        
        Returns:
            {
                'translations': List[str],  # 翻译结果
                'summary': Dict or None     # AI总结结果
            }
        """
        # 1. 执行翻译
        translations = self.translate_batch(texts, src_lang, tgt_lang, batch_size)
        
        result = {
            'translations': translations,
            'summary': None
        }
        
        # 2. 如果启用总结,生成AI总结
        if enable_summary and self.ollama_service:
            try:
                # 合并所有翻译结果
                combined_text = '\n'.join(translations)
                
                if combined_text.strip():
                    logger.info(f"🧠 开始生成AI总结...")
                    summary_result = self.ollama_service.generate_summary(
                        text=combined_text,
                        target_language=tgt_lang
                    )
                    
                    result['summary'] = summary_result
                    
                    if summary_result.get('success'):
                        logger.info(f"✓ AI总结生成成功")
                    else:
                        logger.warning(f"⚠️ AI总结生成失败: {summary_result.get('error')}")
                        
            except Exception as e:
                logger.error(f"❌ AI总结异常: {e}")
                result['summary'] = {
                    'success': False,
                    'summary': None,
                    'error': '生成总结时发生错误 🔧'
                }
        elif enable_summary and not self.ollama_service:
            logger.warning("⚠️ AI总结服务未加载")
            result['summary'] = {
                'success': False,
                'summary': None,
                'error': 'AI总结服务暂时不可用 😊'
            }
        
        return result

# 单例模式
_translator_instance = None

def get_translator(model_name=None):  # 【修改】添加可选参数
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


# 测试函数
def test_translator():
    """测试翻译器"""
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
    
    # 测试3: 批量翻译
    print("\n【测试 3】批量翻译")
    texts = ["你好", "世界", "测试"]
    results = translator.translate_batch(texts, 'zh', 'en')
    for orig, trans in zip(texts, results):
        print(f"  {orig} -> {trans}")
    
    print("\n" + "=" * 70)
    print("测试完成！")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_translator()