"""
NLLB (No Language Left Behind) 翻译服务
使用Meta的NLLB模型进行高质量多语言翻译
"""

import os
import logging
import re
from dotenv import load_dotenv
load_dotenv()
from services.ali_translate_client import AliTranslateClient
from logger_config import app_logger, api_logger, log_exception
import concurrent.futures

USE_CLOUD_TRANSLATE = os.getenv('USE_CLOUD_TRANSLATE', 'false').lower() == 'true'
app_logger.info(f"[启动] USE_CLOUD_TRANSLATE 环境变量: {os.getenv('USE_CLOUD_TRANSLATE')}")
app_logger.info(f"[启动] USE_CLOUD_TRANSLATE 解析结果: {USE_CLOUD_TRANSLATE}")

# 🔥 条件导入：只在需要本地模型时才导入 torch
if not USE_CLOUD_TRANSLATE:
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        app_logger.info("✓ 本地模型依赖已加载 (torch, transformers)")
    except ImportError as e:
        app_logger.error(f"❌ 本地模型依赖缺失: {e}")
        app_logger.error("请安装: pip install torch transformers sentencepiece")
else:
    app_logger.info("ℹ️ 使用云翻译模式，跳过本地模型依赖")

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
        # 🔥 动态导入 AI 服务
        try:
            from config import AI_PROVIDER
            if AI_PROVIDER == 'qwen':
                from services.qwen_service import qwen_service
                self.ollama_service = qwen_service
            else:
                from services.ollama_service import ollama_service
                self.ollama_service = ollama_service
            logger.info(f"✓ AI总结服务已加载 (提供商: {AI_PROVIDER})")
        except Exception as e:
            logger.warning(f"⚠️ AI总结服务加载失败: {e}")
            self.ollama_service = None
    
        # 【修改】优先使用配置文件
        if model_name is None:
            model_name = NLLB_MODEL_NAME
        
        self.model_name = model_name
        
        # 【修改】设置PyTorch CUDA内存分配器
        if not USE_CLOUD_TRANSLATE and PYTORCH_CUDA_ALLOC_CONF:
            os.environ['PYTORCH_CUDA_ALLOC_CONF'] = PYTORCH_CUDA_ALLOC_CONF
            logger.info(f"✓ 设置 PYTORCH_CUDA_ALLOC_CONF: {PYTORCH_CUDA_ALLOC_CONF}")
        
        # 【修改】根据配置选择设备（仅本地模式）
        if not USE_CLOUD_TRANSLATE:
            import torch  # 仅在本地模式导入
            if USE_GPU and torch.cuda.is_available():
                self.device = f"cuda:{GPU_DEVICE_ID}"
                logger.info(f"✓ 使用 GPU: {torch.cuda.get_device_name(GPU_DEVICE_ID)}")
                logger.info(f"✓ GPU 显存限制: {GPU_MEMORY_FRACTION * 100}%")
            else:
                self.device = "cpu"
                logger.info("✓ 使用 CPU")
        else:
            self.device = None  # 云翻译模式不需要设备
        
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
    
    def _translate_batch_cloud_smart(self, texts, src_lang='zh', tgt_lang='en'):
        """
        云端翻译 - 智能分组策略
        
        策略：
        1. 短文本（<30字符）：单独翻译（表格单元格、列表标记）
        2. 长文本（>=30字符）：智能合并翻译（最多5个一组，总长度<900字符）
        """
        from concurrent.futures import ThreadPoolExecutor
        import time
        
        client = AliTranslateClient()
        
        logger.info(f"📊 [云端智能] 开始翻译 {len(texts)} 个文本片段...")
        
        # 步骤1：分析文本，分为短文本和长文本
        short_texts = []  # [(index, text)]
        long_texts = []   # [(index, text)]
        
        for idx, text in enumerate(texts):
            if not text or not str(text).strip():
                continue
            
            cleaned = str(text).strip()
            text_len = len(cleaned)
            
            if text_len < 30:
                short_texts.append((idx, cleaned))
            else:
                long_texts.append((idx, cleaned))
        
        logger.info(f"  - 短文本: {len(short_texts)} 个 (单独翻译)")
        logger.info(f"  - 长文本: {len(long_texts)} 个 (智能合并)")
        
        # 初始化结果数组
        results = [''] * len(texts)
        
        # 步骤2：并发翻译短文本
        def translate_single(item):
            idx, text = item
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    result = client.translate(text, source_lang=src_lang, target_lang=tgt_lang)
                    if result.get('success'):
                        return idx, result.get('translated_text', text)
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(0.5)
                    else:
                        logger.warning(f"⚠️ 翻译失败: {text[:20]}...")
            
            return idx, text  # 失败返回原文
        
        if short_texts:
            logger.info(f"🔄 并发翻译 {len(short_texts)} 个短文本...")
            with ThreadPoolExecutor(max_workers=10) as executor:
                for idx, translated in executor.map(translate_single, short_texts):
                    results[idx] = translated
            logger.info(f"✅ 短文本翻译完成")
        
        # 步骤3：智能合并翻译长文本
        if long_texts:
            logger.info(f"🔄 智能合并翻译 {len(long_texts)} 个长文本...")
            
            # 分组：每组最多5个文本，总长度<900字符
            groups = []
            current_group = []
            current_length = 0
            max_group_size = 5
            max_group_length = 900
            
            for idx, text in long_texts:
                text_len = len(text)
                
                # 判断是否需要新建组
                if (current_group and 
                    (len(current_group) >= max_group_size or 
                     current_length + text_len > max_group_length)):
                    groups.append(current_group)
                    current_group = []
                    current_length = 0
                
                current_group.append((idx, text))
                current_length += text_len
            
            if current_group:
                groups.append(current_group)
            
            logger.info(f"  分为 {len(groups)} 个合并组")
            
            # 翻译每个组
            for group_idx, group in enumerate(groups):
                if (group_idx + 1) % 5 == 0 or group_idx == len(groups) - 1:
                    logger.info(f"  进度: {group_idx + 1}/{len(groups)}")
                
                # 使用换行作为分隔符（更自然）
                separator = "\n\n"
                combined_text = separator.join([text for _, text in group])
                
                # 翻译
                max_retries = 3
                translated = None
                
                for attempt in range(max_retries):
                    try:
                        result = client.translate(
                            combined_text, 
                            source_lang=src_lang, 
                            target_lang=tgt_lang
                        )
                        
                        if result.get('success'):
                            translated = result.get('translated_text', '').strip()
                            break
                    except Exception as e:
                        logger.warning(f"⚠️ 请求异常 (尝试{attempt+1}/{max_retries}): {e}")
                    
                    if attempt < max_retries - 1:
                        time.sleep(1 * (attempt + 1))
                
                if not translated:
                    # 翻译失败，使用原文
                    logger.error(f"❌ 组{group_idx+1}翻译失败，使用原文")
                    for idx, text in group:
                        results[idx] = text
                    continue
                
                # 智能分割翻译结果
                translated_parts = translated.split('\n\n')
                
                # 如果分割数量不匹配
                if len(translated_parts) != len(group):
                    # 尝试按单个换行符分割
                    translated_parts = translated.split('\n')
                    translated_parts = [p.strip() for p in translated_parts if p.strip()]
                
                # 如果还是不匹配，按比例分割
                if len(translated_parts) != len(group):
                    translated_parts = self._split_by_ratio(translated, len(group))
                
                # 分配结果
                for i, (idx, original_text) in enumerate(group):
                    if i < len(translated_parts):
                        results[idx] = translated_parts[i].strip() or original_text
                    else:
                        results[idx] = original_text
            
            logger.info(f"✅ 长文本翻译完成")
        
        logger.info(f"✅ [云端智能] 翻译完成")
        return results
    
    def _translate_batch_cloud_individual(self, texts, src_lang='zh', tgt_lang='en'):
        """
        云端翻译 - 逐条翻译模式（用于需要精确位置对应的场景，如PDF）
        
        确保每个输入文本都有一个对应的输出文本，不会因为分组合并导致数量不匹配
        """
        from concurrent.futures import ThreadPoolExecutor
        import time
        
        client = AliTranslateClient()
        
        logger.info(f"📊 [云端逐条] 开始翻译 {len(texts)} 个文本片段...")
        
        results = [''] * len(texts)
        
        def translate_single(item):
            idx, text = item
            
            if not text or not str(text).strip():
                return idx, ''
            
            cleaned = str(text).strip()
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    result = client.translate(cleaned, source_lang=src_lang, target_lang=tgt_lang)
                    if result.get('success'):
                        return idx, result.get('translated_text', cleaned)
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(0.5)
                    else:
                        logger.warning(f"⚠️ 翻译失败: {cleaned[:20]}...")
            
            return idx, cleaned  # 失败返回原文
        
        # 并发翻译所有文本
        logger.info(f"🔄 并发翻译中（10线程）...")
        with ThreadPoolExecutor(max_workers=10) as executor:
            for idx, translated in executor.map(translate_single, enumerate(texts)):
                results[idx] = translated
                
                # 显示进度
                if (idx + 1) % 20 == 0 or (idx + 1) == len(texts):
                    logger.info(f"  进度: {idx + 1}/{len(texts)}")
        
        logger.info(f"✅ [云端逐条] 翻译完成")
        return results
    
    def _split_by_ratio(self, text, num_parts):
        """按比例分割文本（备用方案）"""
        if num_parts <= 1:
            return [text]
        
        # 尝试按标点符号分割
        sentences = re.split(r'[。.!?！？\n]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) >= num_parts:
            # 平均分配句子
            result = []
            sentences_per_part = len(sentences) // num_parts
            
            for i in range(num_parts):
                start = i * sentences_per_part
                end = start + sentences_per_part if i < num_parts - 1 else len(sentences)
                part = ' '.join(sentences[start:end])
                result.append(part)
            
            return result
        
        # 如果句子数不够，按长度分割
        part_length = len(text) // num_parts
        parts = []
        
        for i in range(num_parts):
            start = i * part_length
            end = start + part_length if i < num_parts - 1 else len(text)
            parts.append(text[start:end].strip())
        
        return parts

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
        
        if USE_CLOUD_TRANSLATE:
            client = AliTranslateClient()
            result = client.translate(text, source_lang=src_lang, target_lang=tgt_lang)
            if result.get('success'):
                return result.get('translated_text', '')
            else:
                return text 

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
    
    def translate_batch(self, texts, src_lang='zh', tgt_lang='en', batch_size=None, force_individual=False):
        """批量翻译 - 优化云端翻译版
        
        Args:
            texts: 要翻译的文本列表
            src_lang: 源语言
            tgt_lang: 目标语言
            batch_size: 批次大小
            force_individual: 强制逐条翻译（用于PDF等需要精确位置对应的场景）
        """
        if not texts:
            return []

        self.load_model()

        if batch_size is None:
            batch_size = self.batch_size

        src_code = self.get_lang_code(src_lang)
        tgt_code = self.get_lang_code(tgt_lang)

        # 云端翻译
        if USE_CLOUD_TRANSLATE:
            # 🔥 如果强制逐条翻译，使用简单模式
            if force_individual:
                return self._translate_batch_cloud_individual(texts, src_lang, tgt_lang)
            else:
                return self._translate_batch_cloud_smart(texts, src_lang, tgt_lang)

        # 本地翻译，设置源语言
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

            # 显示进度
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