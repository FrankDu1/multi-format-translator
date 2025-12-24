"""
文本翻译服务
使用 NLLB 模型进行纯文本翻译
"""

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from logger_config import app_logger
import re

# 全局模型缓存
_model = None
_tokenizer = None



def load_translation_model():
    """加载翻译模型（懒加载）"""
    global _model, _tokenizer
    
    if _model is None or _tokenizer is None:
        try:
            app_logger.info("🔄 加载 NLLB 翻译模型...")
            
            model_name = "facebook/nllb-200-distilled-600M"
            
            _tokenizer = AutoTokenizer.from_pretrained(model_name)
            _model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            
            # 如果有 GPU，使用 GPU
            if torch.cuda.is_available():
                _model = _model.to('cuda')
                app_logger.info("✓ 模型已加载到 GPU")
            else:
                app_logger.info("✓ 模型已加载到 CPU")
            
        except Exception as e:
            app_logger.error(f"❌ 模型加载失败: {e}")
            raise
    
    return _model, _tokenizer


def split_text_into_chunks(text, max_length=400):
    """
    按最大长度分割文本，避免模型截断
    
    Args:
        text: 原始文本
        max_length: 每块最大字符数
    
    Returns:
        list: 文本块列表
    """
    import re
    sentences = re.split(r'([。！？.!?])', text)
    chunks = []
    chunk = ''
    for i in range(0, len(sentences), 2):
        part = sentences[i]
        sep = sentences[i+1] if i+1 < len(sentences) else ''
        if len(chunk) + len(part) + len(sep) > max_length and chunk:
            chunks.append(chunk)
            chunk = ''
        chunk += part + sep
    if chunk:
        chunks.append(chunk)
    return [c.strip() for c in chunks if c.strip()]


def translate_chunk(text, model, tokenizer, src_lang, tgt_lang):
    """
    翻译单个文本块
    
    Args:
        text: 文本块
        model: 翻译模型
        tokenizer: 分词器
        src_lang: 源语言代码
        tgt_lang: 目标语言代码
    
    Returns:
        str: 翻译后的文本
    """
    try:
        # 设置源语言
        tokenizer.src_lang = src_lang
        
        # 编码
        inputs = tokenizer(
            text, 
            return_tensors="pt", 
            padding=True, 
            truncation=True, 
            max_length=400
        )
        
        # 如果模型在 GPU 上，输入也要在 GPU 上
        if torch.cuda.is_available():
            inputs = {k: v.to('cuda') for k, v in inputs.items()}
        
        # 设置目标语言
        model.config.forced_bos_token_id = tokenizer.convert_tokens_to_ids(f"<2{tgt_lang}>")
        
        # 生成翻译
        translated_tokens = model.generate(
            **inputs,
            max_length=600,
            num_beams=5,
            early_stopping=True
        )
        
        # 解码
        translated_text = tokenizer.batch_decode(
            translated_tokens, 
            skip_special_tokens=True
        )[0]
        
        return translated_text
    
    except Exception as e:
        app_logger.error(f"❌ 文本块翻译失败: {e}")
        return text  # 返回原文


def translate_text_with_nllb(text, src_lang='en', tgt_lang='zh'):
    """
    使用 NLLB 模型翻译文本（支持长文本分段翻译）
    
    Args:
        text: 要翻译的文本
        src_lang: 源语言代码 (en/zh/auto)
        tgt_lang: 目标语言代码 (en/zh)
    
    Returns:
        str: 翻译后的文本
    """
    try:
        # 加载模型
        model, tokenizer = load_translation_model()
        
        # 转换语言代码, NLLB 语言代码映射
        
        app_logger.info(f"🌐 翻译: {src_lang} → {tgt_lang}")
        app_logger.info(f"📝 原文长度: {len(text)} 字符")
        
        # ✅ 如果文本较短，直接翻译
        word_count = len(text.split())
        if word_count < 150:
            app_logger.info("📄 文本较短，直接翻译")
            return translate_chunk(text, model, tokenizer, src_lang, tgt_lang)
        
        # ✅ 长文本分段翻译
        app_logger.info("📚 文本较长，分段翻译")
        chunks = split_text_into_chunks(text, max_length=400)
        app_logger.info(f"📦 分为 {len(chunks)} 段")
        
        translated_chunks = []
        for i, chunk in enumerate(chunks, 1):
            app_logger.info(f"🔄 翻译第 {i}/{len(chunks)} 段...")
            translated = translate_chunk(
                chunk, 
                model, 
                tokenizer, 
                src_lang, 
                tgt_lang
            )
            translated_chunks.append(translated)
        
        # 合并翻译结果
        final_translation = ' '.join(translated_chunks)
        app_logger.info(f"✅ 翻译完成，译文长度: {len(final_translation)} 字符")
        
        return final_translation
    
    except Exception as e:
        app_logger.error(f"❌ 文本翻译失败: {e}")
        raise


def batch_translate_texts(texts, src_lang='en', tgt_lang='zh'):
    """
    批量翻译多个文本
    
    Args:
        texts: 文本列表
        src_lang: 源语言代码
        tgt_lang: 目标语言代码
    
    Returns:
        list: 翻译后的文本列表
    """
    try:
        results = []
        
        for text in texts:
            if text.strip():
                translated = translate_text_with_nllb(text, src_lang, tgt_lang)
                results.append(translated)
            else:
                results.append('')
        
        return results
    
    except Exception as e:
        app_logger.error(f"❌ 批量翻译失败: {e}")
        raise