import os
import fitz  # PyMuPDF
from logger_config import app_logger

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'uploads')

def translate_pdf_file(pdf_file_path, src_lang='auto', tgt_lang='zh', enable_summary=False):
    """使用 PyMuPDF 保留布局的PDF翻译 - 批量优化版"""
    try:
        from services.nllb_translator_pipeline import get_translator
        translator = get_translator()
        summary_result = None  # 🔥 初始化

        app_logger.info(f"🚀 开始翻译PDF: {pdf_file_path}")
        
        # 打开PDF
        doc = fitz.open(pdf_file_path)
        
        # 【步骤1】收集所有需要翻译的文本和位置信息
        all_texts = []  # 存储所有文本
        text_positions = []  # 存储对应的位置信息
        
        app_logger.info("📝 提取PDF文本...")
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_instances = page.get_text("dict")["blocks"]
            
            for block in text_instances:
                if block["type"] == 0:  # 文本块
                    for line in block["lines"]:
                        for span in line["spans"]:
                            original_text = span["text"].strip()
                            
                            if original_text:
                                all_texts.append(original_text)
                                
                                # 处理颜色值
                                color_value = span["color"]
                                if isinstance(color_value, int):
                                    r = ((color_value >> 16) & 0xFF) / 255.0
                                    g = ((color_value >> 8) & 0xFF) / 255.0
                                    b = (color_value & 0xFF) / 255.0
                                    color = (r, g, b)
                                elif isinstance(color_value, (list, tuple)):
                                    color = tuple(min(1.0, max(0.0, c)) for c in color_value[:3])
                                else:
                                    color = (0, 0, 0)
                                
                                text_positions.append({
                                    'page_num': page_num,
                                    'rect': fitz.Rect(span["bbox"]),
                                    'font_size': span["size"],
                                    'color': color,
                                    'original_text': original_text
                                })
        
        app_logger.info(f"✅ 提取完成: {len(all_texts)} 个文本块")
        
        # 【步骤2】批量翻译所有文本
        translated_texts = []
        if all_texts:
            # 处理自动检测
            if src_lang == 'auto':
                sample_text = all_texts[0] if all_texts else ""
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in sample_text)
                src_lang = 'zh' if has_chinese else 'en'
                app_logger.info(f"🔍 检测到源语言: {src_lang}")
            
            app_logger.info(f"🔤 批量翻译中 ({src_lang} -> {tgt_lang})...")
            
            # 🚀 关键改进：使用translate_batch
            translated_texts = translator.translate_batch(
                all_texts, 
                src_lang=src_lang, 
                tgt_lang=tgt_lang,
                batch_size=16  # 可以调整批次大小
            )
            all_translated_text = translated_texts
            app_logger.info(f"✅ 翻译完成: {len(translated_texts)} 个文本块")
        
        # 【步骤3】应用翻译结果到PDF
        app_logger.info("📄 生成翻译后的PDF...")
        for i, pos_info in enumerate(text_positions):
            if i >= len(translated_texts):
                break
                
            page = doc[pos_info['page_num']]
            translated_text = translated_texts[i]
            
            # 删除原文本(用白色矩形覆盖)
            page.draw_rect(pos_info['rect'], color=(1, 1, 1), fill=(1, 1, 1))
            
            # 插入翻译后的文本
            try:
                page.insert_text(
                    (pos_info['rect'].x0, pos_info['rect'].y0 + pos_info['font_size']),
                    translated_text,
                    fontsize=pos_info['font_size'],
                    color=pos_info['color'],
                    fontname="china-s"
                )
            except Exception as text_err:
                app_logger.warning(f"⚠️ 文本插入失败,使用默认颜色重试: {text_err}")
                try:
                    page.insert_text(
                        (pos_info['rect'].x0, pos_info['rect'].y0 + pos_info['font_size']),
                        translated_text,
                        fontsize=pos_info['font_size'],
                        color=(0, 0, 0),
                        fontname="china-s"
                    )
                except:
                    app_logger.error(f"❌ 无法插入文本: {translated_text[:30]}...")
        
        # 保存翻译后的PDF
        out_path = os.path.join(UPLOAD_DIR, 'translated_' + os.path.basename(pdf_file_path))
        doc.save(out_path)
        doc.close()
        
        # 🔥 新增: AI总结功能
        if enable_summary:
            try:
                from services.nllb_translator_pipeline import get_translator
                
                translator = get_translator()
                combined_text = '\n'.join(all_translated_text)
                
                if combined_text.strip():
                    app_logger.info(f"🧠 开始生成AI总结...")
                    
                    translation_result = translator.translate_with_summary(
                        texts=[combined_text],
                        src_lang=src_lang,
                        tgt_lang=tgt_lang,
                        enable_summary=True
                    )
                    
                    summary_result = translation_result.get('summary')
                    
                    if summary_result and summary_result.get('success'):
                        app_logger.info(f"✓ AI总结生成成功")
                    else:
                        app_logger.warning(f"⚠️ AI总结生成失败")
                        
            except Exception as e:
                app_logger.error(f"❌ AI总结异常: {e}")
                summary_result = {
                    'success': False,
                    'summary': None,
                    'error': '生成总结时发生错误 🔧'
                }

        app_logger.info(f"✅ PDF翻译完成: {out_path}")
        return out_path, summary_result
        
    except Exception as e:
        app_logger.error(f"❌ PDF翻译失败: {e}")
        import traceback
        app_logger.error(traceback.format_exc())
        raise