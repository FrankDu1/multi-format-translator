"""
图片翻译服务 - 完整版（Inpaint 包含文字绘制）
"""
import os
import sys
import subprocess
import logging
import requests
import base64
import json
from typing import List, Tuple, Dict
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# 创建 logger
logger = logging.getLogger(__name__)

# 如果还没有配置 logger，添加基本配置
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# 导入配置
try:
    from config import (
        OCR_SERVICE_URL,
        INPAINT_SERVICE_URL,
        USE_INPAINT
    )
except ImportError:
    OCR_SERVICE_URL = "http://47.97.97.198:29001/ocr"
    INPAINT_SERVICE_URL = "http://47.97.97.198:29002/inpaint"
    USE_INPAINT = True
    logger.warning("无法导入配置，使用默认值")

# 导入翻译器
try:
    from services.nllb_translator_pipeline import get_translator
except ImportError:
    logger.error("无法导入翻译器")
    get_translator = None


@dataclass
class OCRResult:
    """OCR 识别结果"""
    text: str
    box: list
    confidence: float = 0.0


# ============= 字体管理函数 =============

def install_fonts():
    """自动安装中文字体"""
    try:
        logger.info("检查并安装中文字体...")
        
        # 检查是否是 Linux 系统
        if not os.path.exists('/etc'):
            logger.warning("⚠️  非 Linux 系统，跳过自动安装")
            return False
        
        # 检查是否有 sudo 权限
        try:
            result = subprocess.run(['sudo', '-n', 'true'], 
                                  capture_output=True, 
                                  timeout=1)
            has_sudo = result.returncode == 0
        except:
            has_sudo = False
        
        if not has_sudo:
            logger.warning("⚠️  没有 sudo 权限，无法自动安装字体")
            return False
        
        # 检测操作系统
        if os.path.exists('/etc/debian_version'):
            logger.info("检测到 Debian/Ubuntu 系统")
            
            # 安装字体包
            fonts = ['fonts-wqy-zenhei', 'fonts-wqy-microhei', 'fonts-noto-cjk']
            
            for font in fonts:
                logger.info(f"  安装 {font}...")
                result = subprocess.run(
                    ['sudo', 'apt-get', 'install', '-y', '-qq', font],
                    capture_output=True,
                    timeout=120
                )
                if result.returncode == 0:
                    logger.info(f"  ✓ {font} 安装成功")
            
            # 刷新字体缓存
            subprocess.run(['sudo', 'fc-cache', '-fv'], 
                         capture_output=True,
                         timeout=30)
            
            logger.info("✓ 字体安装完成")
            return True
            
        elif os.path.exists('/etc/redhat-release'):
            logger.info("检测到 RHEL/CentOS 系统")
            
            fonts = ['wqy-zenhei-fonts', 'wqy-microhei-fonts']
            
            for font in fonts:
                logger.info(f"  安装 {font}...")
                subprocess.run(
                    ['sudo', 'yum', 'install', '-y', font],
                    capture_output=True,
                    timeout=120
                )
            
            subprocess.run(['sudo', 'fc-cache', '-fv'],
                         capture_output=True,
                         timeout=30)
            
            logger.info("✓ 字体安装完成")
            return True
        
        return False
            
    except Exception as e:
        logger.error(f"❌ 字体安装失败: {str(e)}")
        return False


def download_font_file(font_dir="fonts"):
    """下载字体文件到本地"""
    try:
        os.makedirs(font_dir, exist_ok=True)
        font_path = os.path.join(font_dir, "NotoSansSC-Regular.otf")
        
        if os.path.exists(font_path):
            logger.info(f"✓ 字体文件已存在: {font_path}")
            return font_path
        
        logger.info("下载字体文件...")
        
        import urllib.request
        url = "https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansSC-Regular.otf"
        
        logger.info(f"  从 {url} 下载...")
        urllib.request.urlretrieve(url, font_path)
        
        if os.path.exists(font_path):
            logger.info(f"✓ 字体下载成功: {font_path}")
            return font_path
        else:
            logger.error("❌ 字体下载失败")
            return None
            
    except Exception as e:
        logger.error(f"❌ 字体下载失败: {str(e)}")
        return None


def get_font(size=20, try_install=True):
    """获取可用的中文字体"""
    font_paths = [
        "fonts/NotoSansSC-Regular.otf",
        "fonts/SourceHanSansSC-Regular.otf",
        "fonts/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simsun.ttc",
        "/System/Library/Fonts/PingFang.ttc",
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, size=size)
                logger.info(f"✓ 使用字体: {font_path}")
                return font
            except Exception as e:
                logger.debug(f"字体加载失败 {font_path}: {e}")
                continue
    
    logger.warning("⚠️  系统中未找到中文字体")
    
    if try_install:
        logger.info("尝试下载字体文件...")
        downloaded_font = download_font_file()
        
        if downloaded_font and os.path.exists(downloaded_font):
            try:
                font = ImageFont.truetype(downloaded_font, size=size)
                logger.info(f"✓ 使用下载的字体: {downloaded_font}")
                return font
            except Exception as e:
                logger.error(f"下载的字体加载失败: {e}")
        
        logger.info("尝试自动安装系统字体...")
        if install_fonts():
            return get_font(size=size, try_install=False)
    
    logger.warning("⚠️  无法加载中文字体，使用默认字体（可能显示乱码）")
    return ImageFont.load_default()


def check_fonts_on_startup():
    """启动时检查字体可用性"""
    try:
        logger.info("=" * 60)
        logger.info("检查中文字体...")
        logger.info("=" * 60)
        
        font = get_font(size=16, try_install=True)
        
        test_img = Image.new('RGB', (200, 50), color='white')
        draw = ImageDraw.Draw(test_img)
        test_text = "中文测试 English Test"
        draw.text((10, 10), test_text, font=font, fill='black')
        
        logger.info("✓ 字体测试通过")
        logger.info("=" * 60)
        return True
    except Exception as e:
        logger.error(f"❌ 字体测试失败: {e}")
        logger.info("=" * 60)
        return False


# ============= OCR 函数 =============

def call_remote_ocr(
    image_path: str, 
    ocr_url: str = None, 
    src_lang: str = None,
    filter_by_lang: bool = True  # 🔥 默认启用过滤
) -> List[OCRResult]:
    """调用远程 OCR 服务"""
    if ocr_url is None:
        ocr_url = OCR_SERVICE_URL
    
    try:
        logger.info(f"调用 OCR 服务: {ocr_url}")
        if src_lang and filter_by_lang:
            logger.info(f"   源语言: {src_lang} (过滤: {filter_by_lang})")
        
        # 读取图片
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        logger.info(f"   图片大小: {len(image_data) / 1024:.1f} KB")
        
        # 构建请求
        payload = {
            "image_base64": image_base64
        }
        
        # 🔥 添加语言过滤参数
        if src_lang and filter_by_lang:
            payload["source_lang"] = src_lang
            payload["filter_by_language"] = True
            logger.info(f"   🔍 启用语言过滤: {src_lang}")
        
        # 发送请求
        resp = requests.post(ocr_url, json=payload, timeout=60)
        logger.info(f"OCR 响应状态: {resp.status_code}")
        
        if resp.status_code != 200:
            logger.error(f"OCR 服务返回错误: {resp.status_code}")
            logger.error(f"响应内容: {resp.text[:500]}")
            return []
        
        data = resp.json()
        
        if not data.get('success', False):
            logger.error(f"OCR 处理失败")
            return []
        
        if 'result' not in data:
            logger.error(f"OCR 响应格式错误，缺少 'result' 字段")
            return []
        
        result_list = data['result']
        if not result_list or len(result_list) == 0:
            logger.warning("OCR 未识别到任何文本")
            return []
        
        first_result = result_list[0]
        res = first_result.get('res', {})
        
        rec_texts = res.get('rec_texts', [])
        rec_scores = res.get('rec_scores', [])
        
        # 🔥 获取 boxes（优先使用 rec_polys）
        rec_polys = res.get('rec_polys', [])
        dt_polys = res.get('dt_polys', [])
        rec_boxes = res.get('rec_boxes', [])
        
        boxes = rec_polys or dt_polys or rec_boxes
        
        logger.info(f"   OCR 结果:")
        logger.info(f"      rec_texts: {len(rec_texts)} 个")
        logger.info(f"      boxes: {len(boxes)} 个")
        
        if not rec_texts:
            logger.warning("OCR 未识别到任何文本")
            return []
        
        # 构建结果
        ocr_results = []
        for i in range(len(rec_texts)):
            text = rec_texts[i] if i < len(rec_texts) else ""
            box = boxes[i] if i < len(boxes) else []
            score = rec_scores[i] if i < len(rec_scores) else 0.0
            
            if not text or not text.strip():
                continue
            
            if not box or len(box) == 0:
                logger.warning(f"      ⚠️  文本 '{text}' 没有 box")
            
            ocr_results.append(OCRResult(
                text=text.strip(),
                box=box,
                confidence=score
            ))
        
        # 显示结果
        filtered = data.get('filtered', False)
        if filtered:
            logger.info(f"   ✓ OCR 识别到 {len(ocr_results)} 段文字 (已过滤 {src_lang})")
        else:
            logger.info(f"   ✓ OCR 识别到 {len(ocr_results)} 段文字 (未过滤)")
        
        # 验证 boxes
        boxes_count = sum(1 for ocr in ocr_results if ocr.box and len(ocr.box) > 0)
        logger.info(f"      有效 boxes: {boxes_count}/{len(ocr_results)} 个")
        
        # 显示前几个结果
        for i, ocr in enumerate(ocr_results[:3], 1):
            has_box = "✓" if (ocr.box and len(ocr.box) > 0) else "✗"
            logger.info(f"      {i}. {ocr.text} (box: {has_box})")
        if len(ocr_results) > 3:
            logger.info(f"      ... 还有 {len(ocr_results)-3} 段")
        
        return ocr_results
        
    except Exception as e:
        logger.error(f"OCR 调用失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []


# ============= 翻译函数 =============

def translate_texts(texts: List[str], src_lang: str, tgt_lang: str) -> List[str]:
    """批量翻译文本"""
    if not texts:
        return []
    
    logger.info(f"翻译 {len(texts)} 段文本: {src_lang} → {tgt_lang}")
    
    try:
        if get_translator is None:
            logger.error("翻译器未初始化")
            return texts
        
        translator = get_translator()
        results = translator.translate_batch(texts, src_lang, tgt_lang)
        
        logger.info(f"✓ 翻译完成")
        return results
        
    except Exception as e:
        logger.error(f"翻译失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return texts


# ============= Inpaint 函数（包含文字绘制）=============

def call_inpaint_with_translation(
    image_path: str, 
    ocr_results: List[OCRResult], 
    translated_texts: List[str],
    inpaint_url: str = None
) -> str:
    """
    调用 Inpaint 服务：移除原文 + 绘制翻译文字
    
    Args:
        image_path: 原始图片路径
        ocr_results: OCR 识别结果（包含文字框位置）
        translated_texts: 翻译后的文字列表
        inpaint_url: Inpaint 服务 URL
    
    Returns:
        处理后的图片路径，失败返回 None
    """
    if inpaint_url is None:
        inpaint_url = INPAINT_SERVICE_URL
    
    try:
        logger.info(f"🎨 调用 Inpaint 服务（含文字绘制）: {inpaint_url}")
        logger.info(f"   处理 {len(ocr_results)} 个文字区域")
        
        # 准备 boxes 列表（用于移除原文）
        boxes = []
        # 准备 texts 列表（用于绘制翻译文字）
        texts = []
        
        for ocr, trans_text in zip(ocr_results, translated_texts):
            if not ocr.box:
                continue
            
            # 格式化 box - 确保是嵌套列表格式 [[x1,y1], [x2,y2], ...]
            if isinstance(ocr.box[0], (list, tuple)):
                formatted_box = ocr.box
            else:
                formatted_box = []
                for i in range(0, len(ocr.box), 2):
                    if i + 1 < len(ocr.box):
                        formatted_box.append([ocr.box[i], ocr.box[i+1]])
            
            boxes.append(formatted_box)
            
            # 构建 texts 数据（按照服务器要求的格式）
            texts.append({
                'text': trans_text,  # 翻译后的文字
                'color': [0, 0, 0],  # 黑色文字
                'align': 'center'    # 居中对齐
            })
        
        logger.info(f"   boxes 数量: {len(boxes)}")
        logger.info(f"   texts 数量: {len(texts)}")
        
        # 显示前几条翻译数据
        for i, (ocr, text_obj) in enumerate(zip(ocr_results[:3], texts[:3]), 1):
            logger.info(f"   {i}. {ocr.text} → {text_obj['text']}")
        
        # 使用文件上传方式（与 curl 示例一致）
        with open(image_path, 'rb') as f:
            files = {
                'file': ('image.png', f, 'image/png')
            }
            
            # 📌 关键修改：使用 'boxes' 和 'texts' 参数（JSON 字符串）
            data = {
                'boxes': json.dumps(boxes),  # 用于移除原文的区域
                'texts': json.dumps(texts)   # 用于绘制的翻译文字（带格式）
            }
            
            logger.info(f"   发送请求...")
            logger.info(f"   boxes 示例: {boxes[0] if boxes else 'None'}")
            logger.info(f"   texts 示例: {texts[0] if texts else 'None'}")
            
            resp = requests.post(
                inpaint_url, 
                files=files,
                data=data,
                timeout=120
            )
        
        logger.info(f"   响应状态: {resp.status_code}")
        
        if resp.status_code != 200:
            logger.warning(f"⚠️  Inpaint 服务返回错误: {resp.status_code}")
            logger.warning(f"   响应: {resp.text[:300]}")
            return None
        
        # 保存处理后的图片
        output_path = image_path.replace('.', '_translated.')
        
        content_type = resp.headers.get('Content-Type', '')
        logger.info(f"   响应类型: {content_type}")
        
        if 'image' in content_type:
            # 直接返回图片
            with open(output_path, 'wb') as f:
                f.write(resp.content)
            logger.info(f"✓ 图片已保存（直接格式）")
        
        elif 'json' in content_type:
            # JSON 格式
            json_data = resp.json()
            
            if 'image' in json_data or 'image_base64' in json_data:
                # Base64 编码的图片
                img_b64 = json_data.get('image') or json_data.get('image_base64')
                img_data = base64.b64decode(img_b64)
                with open(output_path, 'wb') as f:
                    f.write(img_data)
                logger.info(f"✓ 图片已保存（Base64 格式）")
            
            elif 'image_url' in json_data:
                # 返回图片 URL
                img_url = json_data['image_url']
                img_resp = requests.get(img_url, timeout=30)
                with open(output_path, 'wb') as f:
                    f.write(img_resp.content)
                logger.info(f"✓ 图片已保存（URL 格式）")
            
            elif 'output_path' in json_data:
                # 返回服务器端路径
                output_path = json_data['output_path']
                logger.info(f"✓ 使用服务器端路径: {output_path}")
            
            else:
                logger.error(f"❌ JSON 响应中没有图片数据: {json_data}")
                return None
        
        else:
            # 尝试直接保存
            with open(output_path, 'wb') as f:
                f.write(resp.content)
            logger.info(f"✓ 图片已保存（未知格式）")
        
        # 验证文件
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            logger.info(f"✓ Inpaint 完成: {output_path}")
            logger.info(f"   文件大小: {os.path.getsize(output_path) / 1024:.1f} KB")
            return output_path
        else:
            logger.error(f"❌ 图片保存失败")
            return None
    
    except requests.exceptions.Timeout:
        logger.error("❌ Inpaint 服务超时")
        return None
    except Exception as e:
        logger.error(f"❌ Inpaint 调用失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


# ============= 本地备用方案 =============

def simple_inpaint(image: Image.Image, boxes: list) -> Image.Image:
    """简单的图片修复：用白色矩形覆盖文字区域（备用）"""
    draw = ImageDraw.Draw(image)
    
    for box in boxes:
        if box and len(box) >= 4:
            if isinstance(box[0], (list, tuple)):
                draw.polygon([tuple(p) for p in box], fill='white')
            else:
                points = [(box[i], box[i+1]) for i in range(0, len(box), 2)]
                draw.polygon(points, fill='white')
    
    return image


def draw_translated_text_local(image: Image.Image, ocr_results: list, translated_texts: list, font_size: int = 20) -> Image.Image:
    """本地绘制翻译文字（备用）"""
    draw = ImageDraw.Draw(image)
    font = get_font(size=font_size)
    
    for ocr, trans in zip(ocr_results, translated_texts):
        if not trans or not trans.strip():
            continue
        
        if ocr.box and len(ocr.box) >= 4:
            if isinstance(ocr.box[0], (list, tuple)):
                xs = [p[0] for p in ocr.box]
                ys = [p[1] for p in ocr.box]
            else:
                xs = [ocr.box[i] for i in range(0, len(ocr.box), 2)]
                ys = [ocr.box[i+1] for i in range(0, len(ocr.box), 2)]
            
            x = int(min(xs))
            y = int(min(ys))
        else:
            x, y = 10, 10
        
        draw.text((x, y), trans, fill='black', font=font)
    
    return image


# ============= 主翻译函数 =============

def translate_image_with_ocr_and_nllb_detailed(
    image_path: str, 
    output_path: str, 
    src_lang: str = "zh", 
    tgt_lang: str = "en",
    ocr_url: str = None,
    inpaint_url: str = None,
    use_inpaint: bool = None,
    enable_summary: bool = False
) -> Tuple[bool, List[Dict], str, Dict]:
    """图片翻译完整流程（返回详细信息）"""
    try:
        if use_inpaint is None:
            use_inpaint = USE_INPAINT
        error_msg = None
        summary_result = None

        logger.info("=" * 60)
        logger.info("开始图片翻译流程（详细版）")
        logger.info(f"语言: {src_lang} → {tgt_lang}")
        logger.info("=" * 60)
        
        # 🔥 步骤1: OCR识别（确保传递参数）
        logger.info("[1/3] 🖼️  OCR 识别中...")
        ocr_results = call_remote_ocr(
            image_path, 
            ocr_url,
            src_lang=src_lang,      # 🔥 传递源语言
            filter_by_lang=True     # 🔥 启用过滤（默认值是 True，这里明确传递）
        )
        
        # 🔥 简化处理：如果OCR结果为空，直接返回原图
        if not ocr_results or len(ocr_results) == 0:
            logger.warning(f"⚠️  未检测到任何文本，返回原图")
            
            # 直接复制原图到输出路径
            import shutil
            shutil.copy(image_path, output_path)
            
            error_msg = f"图片中未检测到 {src_lang} 语言的文本"
            logger.info(f"✓ 已返回原图: {output_path}")
            return False, [], error_msg, None  # 🔥 返回失败和错误信息
        
        texts = [r.text for r in ocr_results]
        logger.info(f"✓ 识别到 {len(texts)} 段文字")
        
        # 步骤2: 翻译
        logger.info(f"\n[2/3] 🌐 翻译中 ({src_lang} → {tgt_lang})...")
        if enable_summary:
            from services.nllb_translator_pipeline import get_translator
            translator = get_translator()
            
            translation_result = translator.translate_with_summary(
                texts=texts,
                src_lang=src_lang,
                tgt_lang=tgt_lang,
                enable_summary=True
            )
            
            translated_texts = translation_result['translations']
            summary_result = translation_result.get('summary')
        else:
            # 原有逻辑
            translated_texts = translate_texts(texts, src_lang, tgt_lang)
        
        # 构建翻译记录
        translations = []
        for ocr, trans in zip(ocr_results, translated_texts):
            translations.append({
                'original_text': ocr.text,
                'translated_text': trans,
                'confidence': ocr.confidence,
                'box': ocr.box
            })
        
        logger.info(f"✓ 翻译完成")
        for i, t in enumerate(translations[:3], 1):
            logger.info(f"   {i}. {t['original_text']} → {t['translated_text']}")
        logger.info(f"✓ 构建了 {len(translations)} 条翻译记录")
        
        # 步骤3: Inpaint
        logger.info(f"\n[3/3] 🎨 Inpaint 处理中...")
        
        if use_inpaint and inpaint_url:
            result_path = call_inpaint_with_translation(
                image_path, 
                ocr_results, 
                translated_texts,
                inpaint_url
            )
            
            if result_path and os.path.exists(result_path):
                import shutil
                shutil.copy(result_path, output_path)
                logger.info(f"✓ 使用 Inpaint 服务完成")
            else:
                logger.warning(f"⚠️  Inpaint 失败，使用本地备用方案")
                image = Image.open(image_path)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                boxes = [r.box for r in ocr_results if r.box]
                image = simple_inpaint(image, boxes)
                image = draw_translated_text_local(image, ocr_results, translated_texts)
                image.save(output_path, quality=95)
        else:
            logger.info(f"   使用本地处理...")
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            boxes = [r.box for r in ocr_results if r.box]
            image = simple_inpaint(image, boxes)
            image = draw_translated_text_local(image, ocr_results, translated_texts)
            image.save(output_path, quality=95)
        
        if os.path.exists(output_path):
            logger.info("=" * 60)
            logger.info(f"✅ 图片翻译完成")
            logger.info(f"   输出: {output_path}")
            logger.info(f"   翻译数: {len(translations)}")
            logger.info("=" * 60)
            return True, translations, error_msg, summary_result
        else:
            logger.error("❌ 输出文件不存在")
            return False, [], error_msg, None

    except Exception as e:
        logger.error(f"❌ 图片翻译失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False, [], error_msg, None
