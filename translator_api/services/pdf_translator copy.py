import os
import fitz  # PyMuPDF
import re
from typing import List, Dict, Tuple
from logger_config import app_logger

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'uploads')

def translate_pdf_file(pdf_file_path, src_lang='auto', tgt_lang='zh', enable_summary=False):
    try:
        from services.nllb_translator_pipeline import get_translator
        translator = get_translator()
        summary_result = None

        app_logger.info(f"🚀 开始PDF翻译: {pdf_file_path}")
        
        # 打开PDF
        doc = fitz.open(pdf_file_path)
        
        # 【关键优化1】改进文本提取：按视觉行提取，避免碎片化
        all_texts = []
        text_positions = []
        
        app_logger.info("📝 提取PDF文本（按视觉行）...")
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # 获取页面所有单词
            words = page.get_text("words")
            if not words:
                continue
            
            # 按Y坐标分组形成视觉行
            from collections import defaultdict
            lines_dict = defaultdict(list)
            
            for word_info in words:
                x0, y0, x1, y1, text, _, _, _ = word_info
                if not text.strip():
                    continue
                
                # 使用精确的Y坐标分组（同一行的文本）
                y_key = round(y0, 1)  # 四舍五入到小数点后1位
                lines_dict[y_key].append({
                    'x0': x0,
                    'text': text,
                    'rect': fitz.Rect(x0, y0, x1, y1)
                })
            
            # 处理每一行
            for y_key in sorted(lines_dict.keys()):
                line_items = lines_dict[y_key]
                
                # 按X坐标排序（从左到右）
                line_items.sort(key=lambda item: item['x0'])
                
                # 组合行文本
                line_text = ' '.join(item['text'] for item in line_items)
                
                # 计算行的整体边界框
                line_rect = None
                for item in line_items:
                    if line_rect is None:
                        line_rect = item['rect']
                    else:
                        line_rect = line_rect.include_rect(item['rect'])
                
                if line_text.strip() and line_rect:
                    all_texts.append(line_text.strip())
                    text_positions.append({
                        'page_num': page_num,
                        'rect': line_rect,
                        'font_size': max(8, line_rect.height),
                        'original_text': line_text.strip()
                    })
        
        app_logger.info(f"✅ 提取完成: {len(all_texts)} 个文本行")
        
        # 显示前几行用于调试
        for i, text in enumerate(all_texts[:5]):
            pos = text_positions[i]
            app_logger.debug(f"  行{i+1}: '{text}' (页{pos['page_num']+1}, Y={pos['rect'].y0})")
        
        # 语言检测（保持不变）
        if src_lang == 'auto':
            sample = ' '.join(all_texts[:3])
            chinese_chars = sum(1 for c in sample if '\u4e00' <= c <= '\u9fff')
            english_chars = sum(1 for c in sample if 'a' <= c.lower() <= 'z')
            src_lang = 'zh' if chinese_chars > english_chars else 'en'
            app_logger.info(f"🔍 检测到源语言: {src_lang}")
        
        # 【关键优化2】批量翻译
        app_logger.info(f"🔤 批量翻译 ({src_lang} -> {tgt_lang})...")
        translated_texts = translator.translate_batch(
            all_texts, 
            src_lang=src_lang, 
            tgt_lang=tgt_lang,
            batch_size=6  # 适当减小批次大小
        )
        
        # 确保结果数量匹配
        if len(translated_texts) != len(all_texts):
            app_logger.warning(f"⚠️ 结果数量不匹配，进行调整")
            if len(translated_texts) < len(all_texts):
                translated_texts.extend([''] * (len(all_texts) - len(translated_texts)))
            else:
                translated_texts = translated_texts[:len(all_texts)]
        
        # 【关键优化3】改进的PDF写回逻辑
        app_logger.info("📄 生成翻译后的PDF...")
        
        # 创建新文档，而不是修改原文档
        new_doc = fitz.open()
        
        for page_num in range(len(doc)):
            original_page = doc[page_num]
            
            # 创建新页面（保持原尺寸）
            new_page = new_doc.new_page(
                width=original_page.rect.width,
                height=original_page.rect.height
            )
            
            # 收集这一页的所有翻译
            page_items = []
            for i, pos in enumerate(text_positions):
                if pos['page_num'] == page_num and i < len(translated_texts):
                    if translated_texts[i].strip():  # 只处理非空翻译
                        page_items.append((pos, translated_texts[i]))
            
            if not page_items:
                continue
            
            # 按Y坐标排序（从上到下）
            page_items.sort(key=lambda x: x[0]['rect'].y0)
            
            # 写入翻译文本
            for pos_info, translated in page_items:
                rect = pos_info['rect']
                font_size = pos_info['font_size']
                
                try:
                    new_page.insert_text(
                        (rect.x0, rect.y0 + font_size * 0.8),
                        translated,
                        fontsize=min(font_size, 14),  # 限制字体大小
                        color=(0, 0, 0),
                        fontname="china-s"
                    )
                except:
                    # 回退方案
                    try:
                        new_page.insert_text(
                            (rect.x0, rect.y0 + font_size * 0.8),
                            translated[:100],  # 截断长文本
                            fontsize=min(font_size, 14),
                            color=(0, 0, 0)
                        )
                    except Exception as e:
                        app_logger.warning(f"⚠️ 文本插入失败: {e}")
        
        # 保存文件
        out_filename = f"translated_{os.path.basename(pdf_file_path)}"
        out_path = os.path.join(UPLOAD_DIR, out_filename)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        
        new_doc.save(out_path)
        new_doc.close()
        doc.close()
        
        app_logger.info(f"✅ PDF保存成功: {out_path}")
        
        # AI总结（保持不变）
        if enable_summary:
            try:
                combined = '\n'.join(translated_texts[:20])
                if combined.strip():
                    app_logger.info("🧠 生成AI总结...")
                    from config import AI_PROVIDER
                    if AI_PROVIDER == 'qwen':
                        from services.qwen_service import qwen_service as ai_service
                    else:
                        from services.ollama_service import ollama_service as ai_service
                    
                    summary_result = ai_service.generate_summary(
                        text=combined,
                        target_language=tgt_lang
                    )
            except Exception as e:
                app_logger.error(f"❌ AI总结异常: {e}")
        
        app_logger.info(f"🎉 PDF翻译完成")
        return out_path, summary_result
        
    except Exception as e:
        app_logger.error(f"❌ PDF翻译失败: {e}")
        import traceback
        app_logger.error(traceback.format_exc())
        raise


def extract_pdf_debug_info(pdf_file_path):
    """
    调试函数：提取PDF结构信息
    """
    try:
        doc = fitz.open(pdf_file_path)
        app_logger.info("🔍 PDF调试信息:")
        
        for page_num in range(min(2, len(doc))):  # 只分析前2页
            page = doc[page_num]
            app_logger.info(f"\n📄 页面 {page_num + 1}:")
            
            # 原始文本
            raw_text = page.get_text()
            app_logger.info(f"  原始文本长度: {len(raw_text)}字符")
            if raw_text:
                app_logger.info(f"  前200字符: {raw_text[:200]}")
            
            # 按单词提取
            words = page.get_text("words")
            app_logger.info(f"  单词数量: {len(words)}")
            
            # 按字典提取
            blocks = page.get_text("dict")["blocks"]
            text_blocks = [b for b in blocks if b["type"] == 0]
            app_logger.info(f"  文本块数量: {len(text_blocks)}")
            
            # 显示前3个文本块的详细结构
            for i, block in enumerate(text_blocks[:3]):
                app_logger.info(f"\n  文本块 {i+1}:")
                for j, line in enumerate(block["lines"][:3]):  # 只显示前3行
                    line_text = ""
                    for span in line["spans"]:
                        line_text += span["text"] + " "
                    app_logger.info(f"    行{j+1}: '{line_text.strip()}'")
        
        doc.close()
        
    except Exception as e:
        app_logger.error(f"❌ PDF调试失败: {e}")

