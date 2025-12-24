from flask import Flask, request, jsonify
from flask_cors import CORS
from paddleocr import PaddleOCR
import cv2
import numpy as np
import base64
import time
import logging
import os
import re
from datetime import datetime

# ========== GPU配置 - 限制显存使用 ==========
# 设置PaddlePaddle显存使用 (1GB = 12.5% on 8GB GPU)
os.environ['FLAGS_fraction_of_gpu_memory_to_use'] = '0.125'  # 限制1GB
os.environ['FLAGS_allocator_strategy'] = 'auto_growth'        # 按需增长
os.environ['CUDA_VISIBLE_DEVICES'] = '0'                      # 使用GPU 0

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 环境变量配置
OCR_HOST = os.getenv('OCR_HOST', '0.0.0.0')
OCR_PORT = int(os.getenv('OCR_PORT', '8899'))
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}})

# 初始化OCR引擎
logger.info("🚀 初始化PaddleOCR...")
try:
    ocr = PaddleOCR(
        use_doc_orientation_classify=False, 
        use_doc_unwarping=False, 
        use_textline_orientation=False,
        lang='ch',              # 支持中英文
        # 新版本PaddleOCR通过环境变量控制GPU和显存，不需要这些参数
    )
    logger.info("✅ PaddleOCR初始化完成 (GPU模式, 显存限制: 1GB)")
except Exception as e:
    logger.error(f"❌ PaddleOCR初始化失败: {e}")
    raise

def image_from_base64(base64_str):
    """从base64字符串解码图像，支持所有常见格式（PNG、JPG、GIF、WEBP等）"""
    try:
        # 处理 data URL 格式 (data:image/jpeg;base64,...)
        if base64_str.startswith('data:image'):
            logger.info("检测到data URI格式，移除前缀")
            if 'base64,' in base64_str:
                base64_str = base64_str.split('base64,')[1]
        
        # 移除可能的空白字符
        base64_str = base64_str.strip()
        
        # 解码base64
        image_bytes = base64.b64decode(base64_str)
        logger.info(f"Base64解码成功，字节长度: {len(image_bytes)}")
        
        # 方法1: 尝试使用OpenCV直接解码
        image_array = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if image is not None:
            logger.info(f"✓ OpenCV解码成功: {image.shape}")
            return image
        
        # 方法2: 使用PIL处理（支持GIF等更多格式）
        logger.info("OpenCV解码失败，尝试使用PIL...")
        try:
            from PIL import Image
            import io
            
            # 使用PIL打开图片
            pil_image = Image.open(io.BytesIO(image_bytes))
            logger.info(f"PIL成功打开: 模式={pil_image.mode}, 尺寸={pil_image.size}, 格式={pil_image.format}")
            
            # 转换为RGB模式（处理GIF、RGBA、P模式等）
            if pil_image.mode in ('RGBA', 'LA'):
                # 有透明通道，转换为白色背景
                logger.info(f"转换 {pil_image.mode} -> RGB (白色背景)")
                background = Image.new('RGB', pil_image.size, (255, 255, 255))
                background.paste(pil_image, mask=pil_image.split()[-1])
                pil_image = background
            elif pil_image.mode == 'P':
                # 调色板模式
                logger.info("转换 P -> RGB")
                pil_image = pil_image.convert('RGB')
            elif pil_image.mode != 'RGB':
                # 其他模式
                logger.info(f"转换 {pil_image.mode} -> RGB")
                pil_image = pil_image.convert('RGB')
            
            # 转换为OpenCV格式 (BGR)
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            logger.info(f"✓ PIL转换成功: {image.shape}")
            return image
            
        except Exception as pil_error:
            logger.error(f"PIL处理失败: {pil_error}")
            raise ValueError(f"图像解码失败: OpenCV和PIL都无法解码")
        
    except base64.binascii.Error as e:
        logger.error(f"Base64解码错误: {e}")
        raise ValueError(f"Base64格式错误: {str(e)}")
    except Exception as e:
        logger.error(f"图像处理错误: {e}", exc_info=True)
        raise ValueError(f"图像处理失败: {str(e)}")

def serialize_ocr_result(result):
    """将OCR结果序列化为可JSON化的格式"""
    serialized_results = []
    
    try:
        for i, res in enumerate(result if result else []):
            try:
                # PaddleOCR结果通常是一个包含检测和识别信息的对象
                if hasattr(res, 'json'):
                    # 使用PaddleOCR提供的json属性
                    res_dict = res.json
                elif isinstance(res, dict):
                    # 已经是字典格式
                    res_dict = res
                else:
                    # 手动提取属性
                    res_dict = {}
                    
                    # 尝试获取常见属性
                    if hasattr(res, '__dict__'):
                        for key, value in res.__dict__.items():
                            try:
                                if hasattr(value, 'tolist'):  # numpy数组
                                    res_dict[key] = value.tolist()
                                elif isinstance(value, (list, tuple)):
                                    # 递归处理列表中的numpy数组
                                    res_dict[key] = [
                                        v.tolist() if hasattr(v, 'tolist') else v 
                                        for v in value
                                    ]
                                elif isinstance(value, (str, int, float, bool, type(None))):
                                    res_dict[key] = value
                                else:
                                    res_dict[key] = str(value)
                            except Exception as e:
                                logger.warning(f"序列化属性 {key} 失败: {e}")
                                res_dict[key] = str(value)
                
                serialized_results.append(res_dict)
                
            except Exception as e:
                logger.error(f"序列化第 {i} 个结果失败: {e}")
                # 添加错误信息但继续处理
                serialized_results.append({
                    'error': f'序列化失败: {str(e)}',
                    'index': i
                })
                
    except Exception as e:
        logger.error(f"序列化OCR结果整体失败: {e}")
        return [{
            'error': f'序列化失败: {str(e)}',
            'result_type': str(type(result)),
            'result_length': len(result) if result else 0
        }]
    
    return serialized_results

def detect_text_language(text):
    """
    检测文本语言（增强版）- 支持德语词汇检测
    """
    text_lower = text.lower().strip()
    
    if not text_lower:
        return 'unknown'
    
    # 中文字符范围
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    # 日文假名
    japanese_pattern = re.compile(r'[\u3040-\u309f\u30a0-\u30ff]')
    # 韩文
    korean_pattern = re.compile(r'[\uac00-\ud7af]')
    # 德语特殊字符
    german_special_pattern = re.compile(r'[äöüÄÖÜß]')
    # 英文字母
    english_pattern = re.compile(r'[a-zA-Z]')
    
    # 常见德语词汇（不含特殊字符）
    common_german_words = {
        'der', 'die', 'das', 'und', 'ist', 'du', 'ich', 'wir', 'sie', 
        'hallo', 'guten', 'tag', 'morgen', 'abend', 'nacht',
        'bitte', 'danke', 'ja', 'nein', 'nicht', 'oder', 'aber',
        'von', 'zu', 'mit', 'für', 'auf', 'aus', 'ein', 'eine',
        'bin', 'bist', 'sind', 'sein', 'haben', 'hat', 'hast',
        'was', 'wer', 'wie', 'wo', 'warum', 'wann'
    }
    
    # 字符统计
    chinese_count = len(chinese_pattern.findall(text))
    japanese_count = len(japanese_pattern.findall(text))
    korean_count = len(korean_pattern.findall(text))
    german_special_count = len(german_special_pattern.findall(text))
    english_count = len(english_pattern.findall(text))
    
    total_chars = len(text_lower)
    
    # 🔥 德语词汇检测
    german_word_count = 0
    words = re.findall(r'\b\w+\b', text_lower)
    for word in words:
        if word in common_german_words:
            german_word_count += 1
    
    german_word_ratio = german_word_count / len(words) if words else 0
    
    # 计算各语言占比
    chinese_ratio = chinese_count / total_chars
    japanese_ratio = japanese_count / total_chars
    korean_ratio = korean_count / total_chars
    english_ratio = english_count / total_chars
    
    # 判断逻辑
    if chinese_ratio >= 0.3:
        return 'zh'
    elif japanese_ratio >= 0.3:
        return 'ja'
    elif korean_ratio >= 0.3:
        return 'ko'
    elif german_special_count > 0:
        return 'de'
    elif german_word_ratio >= 0.3:  # 30%的词汇是德语常用词
        return 'de'
    elif english_ratio >= 0.5:  # 有英文字母且占比高
        return 'en'
    else:
        return 'unknown'
    

def filter_ocr_by_language_v2(ocr_results, target_lang='zh'):
    """
    过滤已序列化的 OCR 结果
    """
    if not ocr_results:
        logger.warning("⚠️  OCR结果为空")
        return []
    
    logger.info(f"📊 开始过滤，输入结果数量: {len(ocr_results)}")
    
    filtered_results = []
    total_count = 0
    filtered_count = 0
    lang_stats = {}
    
    try:
        for idx, res in enumerate(ocr_results):
            logger.debug(f"处理第 {idx+1} 个结果，类型: {type(res)}")
            
            if not isinstance(res, dict):
                logger.warning(f"⚠️  结果 {idx+1} 不是字典: {type(res)}")
                continue
            
            if 'res' not in res:
                logger.warning(f"⚠️  结果 {idx+1} 没有 'res' 键，键列表: {list(res.keys())}")
                continue
            
            rec_res = res['res']
            
            if 'rec_texts' not in rec_res:
                logger.warning(f"⚠️  结果 {idx+1} 的 'res' 没有 'rec_texts' 键，键列表: {list(rec_res.keys())}")
                continue
            
            rec_texts = rec_res['rec_texts']
            rec_scores = rec_res.get('rec_scores', [])
            
            # 🔥 尝试多个可能的 box 键
            boxes = (rec_res.get('dt_polys') or 
                    rec_res.get('rec_polys') or 
                    rec_res.get('rec_boxes') or [])
            
            logger.info(f"📝 结果 {idx+1}: 共 {len(rec_texts)} 个文本")
            
            filtered_texts = []
            filtered_scores = []
            filtered_boxes = []
            
            for i, text in enumerate(rec_texts):
                total_count += 1
                
                if not text or not text.strip():
                    logger.debug(f"  跳过空文本 {i+1}")
                    continue
                
                # 检测语言
                detected_lang = detect_text_language(text)
                
                logger.info(f"  [{i+1}] '{text}' -> {detected_lang}")
                
                # 统计
                if detected_lang not in lang_stats:
                    lang_stats[detected_lang] = {'count': 0, 'texts': []}
                lang_stats[detected_lang]['count'] += 1
                if len(lang_stats[detected_lang]['texts']) < 3:
                    lang_stats[detected_lang]['texts'].append(text)
                
                # 判断是否保留
                if detected_lang == target_lang:
                    filtered_texts.append(text)
                    filtered_scores.append(rec_scores[i] if i < len(rec_scores) else 0.0)
                    if i < len(boxes):
                        filtered_boxes.append(boxes[i])
                    filtered_count += 1
                    logger.info(f"      ✓ 保留")
                else:
                    logger.info(f"      ✗ 过滤 (需要 {target_lang})")
            
            # 如果有保留的文本，添加到结果
            if filtered_texts:
                logger.info(f"✓ 结果 {idx+1}: 保留 {len(filtered_texts)} 个文本")
                
                # 🔥 保持原始结构
                filtered_res = {
                    'res': {
                        'rec_texts': filtered_texts,
                        'rec_scores': filtered_scores
                    }
                }
                
                # 添加 boxes（如果有）
                if filtered_boxes:
                    if 'dt_polys' in rec_res:
                        filtered_res['res']['dt_polys'] = filtered_boxes
                    elif 'rec_polys' in rec_res:
                        filtered_res['res']['rec_polys'] = filtered_boxes
                    elif 'rec_boxes' in rec_res:
                        filtered_res['res']['rec_boxes'] = filtered_boxes
                
                # 🔥 保留其他重要字段
                for key in rec_res:
                    if key not in ['rec_texts', 'rec_scores', 'dt_polys', 'rec_polys', 'rec_boxes']:
                        filtered_res['res'][key] = rec_res[key]
                
                filtered_results.append(filtered_res)
            else:
                logger.info(f"✗ 结果 {idx+1}: 没有保留任何文本")
        
        # 打印统计
        logger.info(f"\n🔍 语言检测统计:")
        for lang, stats in sorted(lang_stats.items(), key=lambda x: -x[1]['count']):
            examples = ', '.join(f"'{t}'" for t in stats['texts'][:3])
            logger.info(f"   {lang.upper()}: {stats['count']} 个 (示例: {examples})")
        
        logger.info(f"\n🔍 过滤结果: {total_count} 个文本 → {filtered_count} 个 {target_lang.upper()} 文本")
        logger.info(f"📊 输出结果数量: {len(filtered_results)}")
        
    except Exception as e:
        logger.error(f"❌ 语言过滤失败: {e}", exc_info=True)
        return ocr_results  # 失败时返回原始结果
    
    return filtered_results


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'ocr_available': True,
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.2',
        'gpu_memory_limit': '1GB'
    })

@app.route('/ocr', methods=['POST'])
def ocr_api():
    """OCR识别接口 - 返回原始OCR结果"""
    start_time = time.time()
    request_id = f"req_{int(start_time * 1000)}"
    
    logger.info(f"[{request_id}] 收到OCR识别请求")
    
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': '请求Content-Type必须是application/json',
                'request_id': request_id
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空',
                'request_id': request_id
            }), 400
        
        # 🔥 从请求中读取参数
        source_lang = data.get('source_lang', None)
        filter_enabled = data.get('filter_by_language', False)
        
        logger.info(f"[{request_id}] 参数: source_lang={source_lang}, filter_enabled={filter_enabled}")
        
        # 获取图像
        image = None
        if 'url' in data and data['url']:
            import requests
            logger.info(f"[{request_id}] 从URL加载图像: {data['url']}")
            response = requests.get(data['url'], timeout=30)
            response.raise_for_status()
            image_array = np.frombuffer(response.content, np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("URL图像解码失败")
        else:
            image_data = None
            for key in ['image', 'image_base64', 'base64', 'img']:
                if key in data and data[key]:
                    image_data = data[key]
                    logger.info(f"[request_id] 使用参数: {key}")
                    break
            
            if not image_data:
                return jsonify({
                    'success': False,
                    'error': '请提供有效的image_base64或url参数',
                    'request_id': request_id,
                    'available_keys': list(data.keys())
                }), 400
            
            image = image_from_base64(image_data)
        
        logger.info(f"[{request_id}] 图像尺寸: {image.shape}")
        
        # OCR识别
        logger.info(f"[{request_id}] 开始OCR识别...")
        ocr_start_time = time.time()
        
        raw_ocr_result = ocr.predict(image)
        
        ocr_time = time.time() - ocr_start_time
        logger.info(f"[{request_id}] OCR识别完成，耗时: {ocr_time:.3f}秒")
        
        # 🔥 先序列化（转换为字典格式）
        serialized_result = serialize_ocr_result(raw_ocr_result)
        
        # 🔥 然后在序列化后的结果上过滤
        filtered = False
        if source_lang and filter_enabled:
            logger.info(f"[{request_id}] 🔍 开始语言过滤 (目标: {source_lang})...")
            filter_start_time = time.time()
            
            # 🔥 在序列化后的结果上过滤
            serialized_result = filter_ocr_by_language_v2(
                serialized_result,  # 传入序列化后的结果
                target_lang=source_lang
            )
            
            filter_time = time.time() - filter_start_time
            filtered = True
            logger.info(f"[{request_id}] ✓ 语言过滤完成，耗时: {filter_time:.3f}秒")
        else:
            logger.info(f"[{request_id}] ⊗ 跳过语言过滤")
        
        processing_time = time.time() - start_time
        
        # 统计信息
        total_texts = 0
        try:
            for res_dict in serialized_result:
                if isinstance(res_dict, dict) and 'res' in res_dict:
                    rec_texts = res_dict['res'].get('rec_texts', [])
                    total_texts += len(rec_texts)
        except:
            pass
        
        logger.info(f"[{request_id}] 处理完成，识别到 {total_texts} 个文本，总耗时: {processing_time:.3f}秒")
        
        # 返回结果
        return jsonify({
            'success': True,
            'result': serialized_result,
            'request_id': request_id,
            'processing_time': round(processing_time, 3),
            'ocr_time': round(ocr_time, 3),
            'total_texts': total_texts,
            'source_lang': source_lang,
            'filtered': filtered
        })
        
    except Exception as e:
        error_time = time.time() - start_time
        logger.error(f"[{request_id}] 处理失败: {str(e)}", exc_info=True)
        
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
            'request_id': request_id,
            'processing_time': round(error_time, 3)
        }), 500

@app.route('/ocr/parsed', methods=['POST'])
def ocr_parsed_api():
    """OCR识别接口 - 返回解析结果"""
    # 这个接口保持原样，不使用
    pass

if __name__ == '__main__':
    logger.info(f"✅ 服务启动完成，监听地址: {OCR_HOST}:{OCR_PORT}")
    logger.info("📋 可用接口:")
    logger.info("  - GET  /health     : 健康检查")
    logger.info("  - POST /ocr        : OCR识别（返回原始结果）")
    logger.info("  - POST /ocr/parsed : OCR识别（返回解析结果，兼容旧版本）")
    logger.info("💾 GPU显存限制: 1GB (通过环境变量控制)")
    app.run(host=OCR_HOST, port=OCR_PORT, debug=False, threaded=True)