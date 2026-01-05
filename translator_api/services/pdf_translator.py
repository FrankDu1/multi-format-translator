import os
import fitz  # PyMuPDF
import tempfile
from typing import List, Dict, Optional
from logger_config import app_logger
from collections import defaultdict

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'uploads')
FONT_DIR = os.path.join(os.path.dirname(__file__), '..', 'fonts')


def translate_pdf_file(pdf_file_path, src_lang='auto', tgt_lang='zh', enable_summary=False):
    """
    PDF翻译主函数 - 按坐标提取文本，翻译后重建PDF
    
    核心策略：
    1. 按Y坐标分组提取文本行（保持位置信息）
    2. 逐条翻译（确保1:1对应）
    3. 删除原文（redaction）后用show_pdf_page保留图片
    4. 在相同位置插入翻译文本
    
    参数：
        pdf_file_path: PDF文件路径
        src_lang: 源语言（'auto'为自动检测）
        tgt_lang: 目标语言（'zh'/'en'/'de'等）
        enable_summary: 是否生成AI摘要
    
    返回：
        (翻译后的PDF路径, AI摘要结果)
    """
    try:
        from services.nllb_translator_pipeline import get_translator
        translator = get_translator()
        summary_result = None

        app_logger.info(f"🚀 开始翻译PDF: {pdf_file_path}")
        
        doc = fitz.open(pdf_file_path)
        
        # ============ 步骤1：提取文本和位置信息 ============
        all_texts, text_positions = _extract_text_with_positions(doc)
        
        app_logger.info(f"✅ 提取完成: {len(all_texts)} 个文本行")
        _log_text_preview(all_texts, text_positions, max_lines=10)
        
        # ============ 步骤2：语言检测 ============
        if src_lang == 'auto':
            src_lang = _detect_language(all_texts)
            app_logger.info(f"🔍 检测到源语言: {src_lang}")
        
        # ============ 步骤3：批量翻译 ============
        app_logger.info(f"🔤 批量翻译 ({src_lang} -> {tgt_lang})...")
        
        translated_texts = translator.translate_batch(
            all_texts, 
            src_lang=src_lang, 
            tgt_lang=tgt_lang,
            batch_size=8,
            force_individual=True  # PDF翻译使用逐条模式，确保位置对应
        )
        
        if len(translated_texts) != len(all_texts):
            app_logger.warning(f"⚠️ 翻译结果数量不匹配，使用原文补充")
            translated_texts = all_texts.copy()[:len(all_texts)]
        
        app_logger.info(f"✅ 翻译完成")
        _log_translation_preview(all_texts, translated_texts, text_positions, max_lines=5)
        
        # ============ 步骤4：重建PDF ============
        is_cjk_target = tgt_lang in ['zh', 'ja', 'ko', 'zh-CN', 'zh-TW', 'zh-Hans', 'zh-Hant']
        app_logger.info(f"📄 创建翻译PDF (目标语言: {tgt_lang}, CJK字体: {is_cjk_target})")
        
        # 查找中文字体（仅CJK语言需要）
        chinese_font_path = _find_chinese_font() if is_cjk_target else None
        
        # 创建新PDF并插入翻译
        out_path = _rebuild_pdf_with_translation(
            doc, text_positions, translated_texts, 
            is_cjk_target, chinese_font_path, pdf_file_path
        )
        
        doc.close()
        
        app_logger.info(f"✅ PDF翻译完成: {out_path}")
        
        # ============ 步骤5：生成AI摘要（可选）============
        if enable_summary:
            summary_result = _generate_ai_summary(translated_texts, tgt_lang)
        
        return out_path, summary_result
        
    except Exception as e:
        app_logger.error(f"❌ PDF翻译失败: {e}")
        import traceback
        app_logger.error(traceback.format_exc())
        raise


def _extract_text_with_positions(doc):
    """
    从PDF中提取文本和位置信息
    
    策略：按Y坐标分组（识别文本行），按X坐标排序（保持阅读顺序）
    
    返回：
        (文本列表, 位置信息列表)
    """
    all_texts = []
    text_positions = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        words = page.get_text("words")
        if not words:
            continue
        
        # 按Y坐标分组（同一行）
        lines_dict = defaultdict(list)
        for word_info in words:
            x0, y0, x1, y1, text, _, _, _ = word_info
            if not text.strip():
                continue
            
            y_key = round(y0, 1)
            lines_dict[y_key].append({
                'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1,
                'text': text, 'rect': fitz.Rect(x0, y0, x1, y1)
            })
        
        # 处理每一行
        for y_key in sorted(lines_dict.keys()):
            line_items = lines_dict[y_key]
            line_items.sort(key=lambda item: item['x0'])  # 按X坐标排序
            
            line_text = ' '.join(item['text'] for item in line_items)
            
            # 计算行的整体边界框
            line_rect = line_items[0]['rect']
            for item in line_items[1:]:
                line_rect = line_rect.include_rect(item['rect'])
            
            if line_text.strip():
                all_texts.append(line_text.strip())
                text_positions.append({
                    'page_num': page_num,
                    'rect': line_rect,
                    'font_size': line_rect.height if line_rect.height > 0 else 12,
                    'y_position': y_key,
                    'original_text': line_text.strip()
                })
    
    return all_texts, text_positions


def _detect_language(texts):
    """自动检测源语言（基于中英文字符比例）"""
    sample_text = ' '.join(texts[:10]) if texts else ""
    chinese_chars = sum(1 for char in sample_text if '\u4e00' <= char <= '\u9fff')
    english_chars = sum(1 for char in sample_text if 'a' <= char.lower() <= 'z')
    return 'zh' if chinese_chars > english_chars else 'en'


def _find_chinese_font():
    """查找可用的中文字体"""
    font_candidates = [
        os.path.join(FONT_DIR, 'NotoSansSC-Regular.ttf'),
        os.path.join(FONT_DIR, 'SourceHanSansSC-Regular.otf'),
        os.path.join(FONT_DIR, 'simhei.ttf'),
        os.path.join(FONT_DIR, 'msyh.ttc'),
        'C:\\Windows\\Fonts\\msyh.ttc',
        'C:\\Windows\\Fonts\\simhei.ttf',
        'C:\\Windows\\Fonts\\simsun.ttc',
    ]
    
    for font_path in font_candidates:
        if os.path.exists(font_path):
            app_logger.info(f"✓ 找到中文字体: {os.path.basename(font_path)}")
            return font_path
    
    app_logger.warning("⚠️ 未找到外部中文字体，将使用内置字体")
    return None


def _log_text_preview(texts, positions, max_lines=10):
    """输出前几行文本预览（用于调试）"""
    for i, text in enumerate(texts[:max_lines]):
        pos = positions[i]
        rect = pos['rect']
        app_logger.info(
            f"  行{i+1} (页{pos['page_num']+1}, Y={pos['y_position']:.1f}, "
            f"X:{rect.x0:.1f}-{rect.x1:.1f}): '{text}'"
        )


def _log_translation_preview(orig_texts, trans_texts, positions, max_lines=5):
    """输出前几行翻译对比（用于调试）"""
    app_logger.info("📋 翻译结果预览:")
    for i, (orig, trans) in enumerate(zip(orig_texts[:max_lines], trans_texts[:max_lines])):
        app_logger.info(f"  {i+1}. 原文: {orig}")
        app_logger.info(f"     译文: {trans}")
    
    app_logger.info("📍 翻译文本与坐标对应:")
    for i, (pos, trans) in enumerate(zip(positions[:max_lines], trans_texts[:max_lines]), 1):
        rect = pos['rect']
        app_logger.info(
            f"  {i}. Y={pos['y_position']:.1f} X:({rect.x0:.1f}-{rect.x1:.1f}) "
            f"'{trans[:50]}'"
        )


def _rebuild_pdf_with_translation(doc, text_positions, translated_texts, 
                                  is_cjk_target, chinese_font_path, pdf_file_path):
    """
    重建PDF：删除原文，保留图片，插入翻译
    
    核心流程：
    1. 在原页面标记文本区域为redaction（白色填充）
    2. 应用redaction并保存到临时文件（确保show_pdf_page能看到删除效果）
    3. 从临时文件复制页面内容到新页面（此时只有图片，文本已删除）
    4. 在相同位置插入翻译文本（动态调整高度和字号，避免重叠）
    """
    new_doc = fitz.open()
    
    for page_num in range(len(doc)):
        original_page = doc[page_num]
        new_page = new_doc.new_page(
            width=original_page.rect.width,
            height=original_page.rect.height
        )
        
        app_logger.info(f"  处理第 {page_num + 1} 页...")
        
        # 步骤1：标记所有文本区域为redaction
        _redact_text_regions(original_page, text_positions, translated_texts, page_num)
        
        # 步骤2：通过临时文件复制redacted页面到新文档
        _copy_redacted_page(doc, new_page, page_num)
        
        # 步骤3：收集该页的翻译内容并按Y坐标排序
        page_items = _get_page_translations(text_positions, translated_texts, page_num)
        if not page_items:
            continue
        
        # 步骤4：插入翻译文本
        _insert_translations(new_page, page_items, is_cjk_target, chinese_font_path)
    
    # 保存并返回
    out_filename = f"translated_{os.path.basename(pdf_file_path)}"
    out_path = os.path.join(UPLOAD_DIR, out_filename)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    new_doc.save(out_path)
    
    new_doc.close()
    
    app_logger.info(f"✅ PDF保存成功: {out_path}")
    return out_path


def _redact_text_regions(page, text_positions, translated_texts, page_num):
    """在页面上标记所有文本区域为redaction"""
    redact_rects = []
    for i, pos in enumerate(text_positions):
        if pos['page_num'] == page_num and i < len(translated_texts):
            rect = pos['rect']
            # 扩展边界确保完全覆盖
            redact_rect = fitz.Rect(
                rect.x0 - 3, rect.y0 - 4,
                rect.x1 + 20, rect.y1 + 5
            )
            redact_rects.append(redact_rect)
    
    if redact_rects:
        for rect in redact_rects:
            page.add_redact_annot(rect, fill=(1, 1, 1))  # 白色填充
        page.apply_redactions()


def _copy_redacted_page(doc, new_page, page_num):
    """
    通过临时文件复制页面（确保redaction生效）
    
    原因：show_pdf_page需要从已保存的文件读取，
    否则会复制redaction前的内容
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tf:
        temp_path = tf.name
    
    try:
        doc.save(temp_path)
        with fitz.open(temp_path) as redacted_doc:
            new_page.show_pdf_page(new_page.rect, redacted_doc, page_num)
    finally:
        try:
            os.unlink(temp_path)
        except Exception:
            pass


def _get_page_translations(text_positions, translated_texts, page_num):
    """收集指定页面的翻译内容并按Y坐标排序"""
    page_items = []
    for i, pos in enumerate(text_positions):
        if pos['page_num'] == page_num and i < len(translated_texts):
            page_items.append((pos, translated_texts[i]))
    
    # 按Y坐标排序
    page_items.sort(key=lambda x: x[0]['y_position'])
    return page_items


def _calculate_safe_height(idx, current_y, sorted_items):
    """
    计算文本框安全高度（避免与下一行重叠）
    
    策略：根据行间距动态调整
    - 间距<15pt: 严格限制，留2pt间隙
    - 间距15-25pt: 中等限制，留3pt间隙  
    - 间距>25pt: 宽松限制，最大60pt
    """
    max_height = 60  # 默认值
    
    if idx + 1 < len(sorted_items):
        next_y = sorted_items[idx + 1][0]['y_position']
        gap = next_y - current_y
        
        if gap < 15:
            max_height = max(12, gap - 2)
        elif gap < 25:
            max_height = max(18, gap - 3)
        else:
            max_height = min(60, gap - 5)
    
    return max_height


def _insert_translations(new_page, sorted_items, is_cjk_target, chinese_font_path):
    """
    在新页面插入翻译文本
    
    策略：
    1. 计算动态高度（避免重叠）
    2. 优先使用内置字体（china-ss/helv等）
    3. 如果失败，渐进式缩小字号（80%→70%→60%→50%）
    4. CJK语言和西文语言使用不同字体集
    """
    for idx, (pos_info, translated_text) in enumerate(sorted_items):
        rect = pos_info['rect']
        font_size = max(7, min(18, pos_info.get('font_size', 12)))
        
        # 计算安全高度
        max_height = _calculate_safe_height(
            idx, pos_info['y_position'], sorted_items
        )
        
        clean_text = ' '.join(translated_text.split())
        
        app_logger.info(
            f"    插入: '{clean_text[:40]}...' "
            f"坐标:({rect.x0:.1f},{rect.y0:.1f})-({rect.x1:.1f},{rect.y1:.1f}) "
            f"最大高度:{max_height:.1f}"
        )
        
        # 构造文本框
        page_width = new_page.rect.width
        available_width = page_width - rect.x0 - 10
        text_width = min(available_width, page_width * 0.8, 500)
        
        text_rect = fitz.Rect(
            rect.x0, rect.y0,
            rect.x0 + text_width,
            rect.y0 + max_height
        )
        
        # 尝试插入（支持渐进式缩放）
        success = _try_insert_text(
            new_page, text_rect, clean_text, font_size,
            is_cjk_target, chinese_font_path
        )
        
        if not success:
            app_logger.warning(f"      ⚠️ 文本无法完全插入: {clean_text[:30]}...")


def _try_insert_text(page, text_rect, text, font_size, is_cjk_target, chinese_font_path):
    """
    尝试插入文本（支持多字体和渐进式缩放）
    
    返回：是否成功插入
    """
    # 步骤1：尝试原始字号
    font_list = _get_font_list(is_cjk_target)
    rc = _try_fonts(page, text_rect, text, font_size, font_list, 
                    chinese_font_path if is_cjk_target else None)
    
    if rc >= 0:
        return True
    
    # 步骤2：渐进式缩放
    app_logger.debug(f"  字号太大，开始缩放...")
    for scale in [0.8, 0.7, 0.6, 0.5]:
        smaller_size = font_size * scale
        rc = _try_fonts(page, text_rect, text, smaller_size, font_list, 
                       chinese_font_path if is_cjk_target else None)
        
        if rc >= 0:
            app_logger.info(f"      ✓ 缩小到{scale*100:.0f}%成功")
            return True
    
    return False


def _get_font_list(is_cjk_target):
    """获取字体列表（根据目标语言）"""
    if is_cjk_target:
        return ["china-ss", "china-s", "cjk"]  # 中日韩字体
    else:
        return ["helv", "times", "cour"]  # 西文字体（支持德语等）


def _try_fonts(page, text_rect, text, font_size, font_list, external_font_path):
    """
    尝试所有字体插入文本
    
    返回：insert_textbox的返回码（>=0表示成功）
    """
    # 尝试内置字体
    for fontname in font_list:
        try:
            rc = page.insert_textbox(
                text_rect, text,
                fontsize=font_size,
                fontname=fontname,
                color=(0, 0, 0),
                align=0
            )
            if rc >= 0:
                app_logger.info(f"      ✓ 成功 [字体:{fontname}] rc:{rc}")
                return rc
        except:
            continue
    
    # 尝试外部字体（仅CJK）
    if external_font_path:
        try:
            rc = page.insert_textbox(
                text_rect, text,
                fontsize=font_size,
                fontname="F1",
                fontfile=external_font_path,
                color=(0, 0, 0),
                align=0
            )
            if rc >= 0:
                app_logger.info(f"      ✓ 成功 [外部字体] rc:{rc}")
                return rc
        except:
            pass
    
    return -1


def _generate_ai_summary(translated_texts, tgt_lang):
    """生成AI摘要（可选功能）"""
    try:
        combined_text = '\n'.join(translated_texts[:20])
        if not combined_text.strip():
            return None
        
        app_logger.info("🧠 开始生成AI总结...")
        
        from config import AI_PROVIDER
        if AI_PROVIDER == 'qwen':
            from services.qwen_service import qwen_service as ai_service
        else:
            from services.ollama_service import ollama_service as ai_service
        
        summary_result = ai_service.generate_summary(
            text=combined_text,
            target_language=tgt_lang
        )
        
        if summary_result and summary_result.get('success'):
            app_logger.info("✓ AI总结生成成功")
            return summary_result
    except Exception as e:
        app_logger.error(f"❌ AI总结异常: {e}")
    
    return None


def translate_pdf_preserve_layout(pdf_file_path, src_lang='auto', tgt_lang='zh'):
    """
    备用方案：布局保留模式（已弃用，保留供参考）
    
    注意：主要使用translate_pdf_file()函数
    此函数创建简化的纯文本PDF，不保留图片和原始排版
    """
    try:
        from services.nllb_translator_pipeline import get_translator
        translator = get_translator()
        
        app_logger.info(f"🔄 使用布局保留模式翻译PDF: {pdf_file_path}")
        
        # 1. 提取文本和位置
        doc = fitz.open(pdf_file_path)
        
        # 收集所有文本块及其样式
        text_blocks = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if block["type"] != 0:
                    continue
                
                block_text = ""
                block_rect = None
                block_font_size = None
                
                for line in block["lines"]:
                    line_text = ""
                    for span in line["spans"]:
                        if span["text"].strip():
                            span_rect = fitz.Rect(span["bbox"])
                            if block_rect is None:
                                block_rect = span_rect
                            else:
                                block_rect = block_rect.include_rect(span_rect)
                            
                            if block_font_size is None:
                                block_font_size = span["size"]
                            
                            line_text += span["text"]
                    
                    if line_text:
                        block_text += line_text + "\n"
                
                if block_text.strip() and block_rect:
                    text_blocks.append({
                        'page_num': page_num,
                        'rect': block_rect,
                        'font_size': block_font_size or 12,
                        'text': block_text.strip()
                    })
        
        doc.close()
        
        if not text_blocks:
            return pdf_file_path
        
        # 2. 语言检测
        if src_lang == 'auto':
            sample_text = text_blocks[0]['text']
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in sample_text)
            src_lang = 'zh' if has_chinese else 'en'
        
        # 3. 翻译
        texts_to_translate = [block['text'] for block in text_blocks]
        translated_texts = translator.translate_batch(
            texts_to_translate,
            src_lang=src_lang,
            tgt_lang=tgt_lang,
            batch_size=4
        )
        
        # 4. 创建新PDF
        new_doc = fitz.open()
        
        # 按页面分组
        page_groups = {}
        for i, block in enumerate(text_blocks):
            page_num = block['page_num']
            if page_num not in page_groups:
                page_groups[page_num] = []
            
            if i < len(translated_texts):
                page_groups[page_num].append({
                    'rect': block['rect'],
                    'font_size': block['font_size'],
                    'text': translated_texts[i]
                })
        
        # 为每一页创建新页面
        for page_num, blocks in sorted(page_groups.items()):
            # 创建新页面（A4尺寸）
            page = new_doc.new_page(width=595, height=842)
            
            # 按Y坐标排序
            blocks.sort(key=lambda x: x['rect'].y0)
            
            # 写入翻译文本
            for block in blocks:
                rect = block['rect']
                font_size = block['font_size']
                text = block['text']
                
                # 调整位置到新页面（保持相对位置）
                new_y = rect.y0 if rect.y0 < 800 else 50
                
                try:
                    page.insert_text(
                        (50, new_y),
                        text,
                        fontsize=min(font_size, 14),
                        color=(0, 0, 0),
                        fontname="china-s"
                    )
                except:
                    page.insert_text(
                        (50, new_y),
                        text[:100],  # 截断长文本
                        fontsize=min(font_size, 14),
                        color=(0, 0, 0)
                    )
        
        # 5. 保存
        out_filename = f"layout_translated_{os.path.basename(pdf_file_path)}"
        out_path = os.path.join(UPLOAD_DIR, out_filename)
        new_doc.save(out_path)
        new_doc.close()
        
        app_logger.info(f"✅ 布局保留翻译完成: {out_path}")
        return out_path
        
    except Exception as e:
        app_logger.error(f"❌ 布局保留翻译失败: {e}")
        raise