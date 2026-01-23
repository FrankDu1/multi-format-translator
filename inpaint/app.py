# main.py
"""
Inpaint 服务 - 智能移除图片中指定区域的文字并渲染翻译后的文字
支持 GPU 加速和 Docker 部署
"""
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
from io import BytesIO
import logging
import sys
from datetime import datetime
import os

# ==================== 日志配置 ====================
def setup_logger():
    """配置日志系统 - Windows UTF-8 支持"""
    import sys
    import io
    
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_format = '%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
    
    # 🔥 Windows 下强制使用 UTF-8 输出
    if sys.platform == 'win32':
        # 方案1: 包装 stdout 为 UTF-8
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer,
            encoding='utf-8',
            errors='replace'
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer,
            encoding='utf-8',
            errors='replace'
        )
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    return logging.getLogger(__name__)

logger = setup_logger()

# 环境变量配置
INPAINT_HOST = os.getenv('INPAINT_HOST', '0.0.0.0')
INPAINT_PORT = int(os.getenv('INPAINT_PORT', '8900'))
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*')

# ==================== 配置 ====================
class Config:
    """服务配置 - 支持环境变量"""
    # 服务配置 (使用统一的环境变量名称)
    HOST = os.getenv('INPAINT_HOST', '0.0.0.0')
    PORT = int(os.getenv('INPAINT_PORT', 8900))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # 图片处理配置
    MAX_IMAGE_SIZE = int(os.getenv('MAX_IMAGE_SIZE', 10 * 1024 * 1024))  # 10MB
    INPAINT_RADIUS = int(os.getenv('INPAINT_RADIUS', 7))
    OUTPUT_QUALITY = int(os.getenv('OUTPUT_QUALITY', 95))
    
    # Inpaint 方法: TELEA (快) 或 NS (质量好)
    INPAINT_METHOD_NAME = os.getenv('INPAINT_METHOD', 'TELEA')
    INPAINT_METHOD = cv2.INPAINT_TELEA if INPAINT_METHOD_NAME == 'TELEA' else cv2.INPAINT_NS
    
    # 🔥 Mask扩展边距（像素）- 确保完全覆盖文字
    MASK_PADDING = int(os.getenv('MASK_PADDING', 15))
    
    # 文字渲染配置
    DEFAULT_FONT_PATH = os.getenv('FONT_PATH', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    DEFAULT_TEXT_COLOR = tuple(map(int, os.getenv('TEXT_COLOR', '0,0,0').split(',')))  # 黑色
    DEFAULT_BG_COLOR = tuple(map(int, os.getenv('BG_COLOR', '255,255,255').split(',')))  # 白色
    MIN_FONT_SIZE = int(os.getenv('MIN_FONT_SIZE', 10))
    MAX_FONT_SIZE = int(os.getenv('MAX_FONT_SIZE', 200))
    
    # CORS 配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

config = Config()

# 创建 Flask 应用
app = Flask(__name__)
CORS(app, origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != '*' else config.CORS_ORIGINS)

# ==================== GPU 检测 ====================
def check_gpu_support():
    """检查 OpenCV CUDA 支持"""
    try:
        cuda_count = cv2.cuda.getCudaEnabledDeviceCount()
        if cuda_count > 0:
            logger.info(f"✓ GPU 加速可用 - CUDA 设备数: {cuda_count}")
            for i in range(cuda_count):
                logger.info(f"  GPU {i}: {cv2.cuda.printShortCudaDeviceInfo(i)}")
            return True
    except:
        pass
    
    logger.info("✗ GPU 不可用，使用 CPU 模式")
    return False

GPU_AVAILABLE = check_gpu_support()

# ==================== 字体管理 ====================
def get_font_path():
    """获取可用的中文字体路径"""
    font_paths = [
        # Linux 中文字体（优先级从高到低）
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttf',      # 文泉驿微米黑
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttf',        # 文泉驿正黑
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',  # Noto Sans CJK
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',  # Noto Sans CJK (另一个路径)
        '/usr/share/fonts/truetype/arphic/uming.ttc',          # AR PL UMing
        
        # macOS 中文字体
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Light.ttc',
        
        # Windows 中文字体
        'C:\\Windows\\Fonts\\simhei.ttf',        # 黑体
        'C:\\Windows\\Fonts\\msyh.ttc',          # 微软雅黑
        'C:\\Windows\\Fonts\\simsun.ttc',        # 宋体
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            logger.info(f"✓ 找到字体: {path}")
            
            # 更严格的中文支持测试
            try:
                test_font = ImageFont.truetype(path, 20)
                
                # 创建测试图片
                test_img = Image.new('RGB', (100, 30), color='white')
                test_draw = ImageDraw.Draw(test_img)
                
                # 渲染中文测试
                test_text = "测试中文"
                test_draw.text((5, 5), test_text, font=test_font, fill=(0, 0, 0))
                
                # 检查是否真的渲染了内容（不是空白或方块）
                # 获取像素数据，检查是否有变化
                pixels = list(test_img.getdata())
                non_white_pixels = sum(1 for p in pixels if p != (255, 255, 255))
                
                if non_white_pixels > 50:  # 有足够多的非白色像素，说明渲染成功
                    logger.info(f"  ✓ 字体支持中文 (渲染像素: {non_white_pixels})")
                    return path
                else:
                    logger.warning(f"  ✗ 字体不支持中文 (渲染像素: {non_white_pixels})")
                    
            except Exception as e:
                logger.warning(f"  ✗ 字体测试失败: {e}")
                continue
    
    logger.error("✗ 未找到支持中文的字体！")
    logger.error("  请安装中文字体:")
    logger.error("  sudo apt install fonts-wqy-microhei fonts-wqy-zenhei fonts-noto-cjk")
    return None


FONT_PATH = get_font_path()


def calculate_font_size(box, text, font_path, max_attempts=30):
    """
    自动计算合适的字体大小
    
    Args:
        box: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        text: 要绘制的文字
        font_path: 字体文件路径
        max_attempts: 最大尝试次数
        
    Returns:
        int: 合适的字体大小
    """
    if not text or not font_path:
        return config.MIN_FONT_SIZE
    
    # 计算 box 的宽高
    points = np.array(box)
    width = np.max(points[:, 0]) - np.min(points[:, 0])
    height = np.max(points[:, 1]) - np.min(points[:, 1])
    
    # 二分查找合适的字体大小
    min_size = config.MIN_FONT_SIZE
    max_size = config.MAX_FONT_SIZE
    best_size = min_size
    
    for _ in range(max_attempts):
        size = (min_size + max_size) // 2
        
        try:
            font = ImageFont.truetype(font_path, size)
        except:
            font = ImageFont.load_default()
            return config.MIN_FONT_SIZE
        
        # 获取文字边界
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 检查是否适合（留 10% 边距）
        if text_width <= width * 0.9 and text_height <= height * 0.9:
            best_size = size
            min_size = size + 1
        else:
            max_size = size - 1
        
        if min_size > max_size:
            break
    
    return max(best_size, config.MIN_FONT_SIZE)


def draw_text_on_image(image, texts_data, font_path):
    """
    在图片上绘制翻译后的文字
    
    Args:
        image: PIL.Image 对象
        texts_data: [
            {
                'box': [[x1,y1], [x2,y2], [x3,y3], [x4,y4]],
                'text': '翻译后的文字',
                'color': (R, G, B),  # 可选，默认黑色
                'bg_color': (R, G, B),  # 可选，背景色
                'align': 'center'  # 可选: left/center/right
            }
        ]
        font_path: 字体文件路径
        
    Returns:
        PIL.Image: 绘制后的图片
    """
    if not font_path:
        logger.warning("字体路径无效，跳过文字渲染")
        return image
    
    draw = ImageDraw.Draw(image)
    rendered_count = 0
    
    for i, item in enumerate(texts_data):
        try:
            box = item.get('box')
            text = item.get('text', '').strip()
            
            if not box or not text:
                logger.debug(f"文字 {i}: 跳过（box或text为空）")
                continue
            
            color = tuple(item.get('color', config.DEFAULT_TEXT_COLOR))
            # 🔥 默认使用白色背景，确保文字可读
            bg_color = item.get('bg_color', config.DEFAULT_BG_COLOR)
            align = item.get('align', 'center')
            
            # 计算 box 中心点和尺寸
            points = np.array(box)
            center_x = int(np.mean(points[:, 0]))
            center_y = int(np.mean(points[:, 1]))
            box_width = int(np.max(points[:, 0]) - np.min(points[:, 0]))
            box_height = int(np.max(points[:, 1]) - np.min(points[:, 1]))
            
            # 自动计算字体大小
            font_size = calculate_font_size(box, text, font_path)
            
            try:
                font = ImageFont.truetype(font_path, font_size)
            except Exception as e:
                logger.warning(f"加载字体失败: {e}, 使用默认字体")
                font = ImageFont.load_default()
            
            # 获取文字边界
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 根据对齐方式计算位置
            if align == 'center':
                x = center_x - text_width // 2
                y = center_y - text_height // 2
            elif align == 'left':
                x = int(np.min(points[:, 0]))
                y = center_y - text_height // 2
            else:  # right
                x = int(np.max(points[:, 0])) - text_width
                y = center_y - text_height // 2
            
            # 绘制背景（如果指定）
            if bg_color:
                bg_color = tuple(bg_color)
                padding = 5  # 🔥 增大背景边距
                draw.rectangle(
                    [(x - padding, y - padding),
                     (x + text_width + padding, y + text_height + padding)],
                    fill=bg_color
                )
            
            # 绘制文字
            draw.text((x, y), text, font=font, fill=color)
            
            rendered_count += 1
            logger.debug(
                f"文字 {i}: '{text}' at ({x},{y}), "
                f"size={font_size}, box={box_width}x{box_height}"
            )
            
        except Exception as e:
            logger.error(f"绘制文字 {i} 失败: {e}", exc_info=True)
            continue
    
    logger.info(f"✓ 渲染文字: {rendered_count}/{len(texts_data)} 段")
    return image


# ==================== 原有的辅助函数 ====================
def normalize_boxes(boxes, image_shape=None):
    """
    标准化 boxes 格式，支持两种输入格式：
    1. 嵌套列表: [[[x1,y1], [x2,y2], [x3,y3], [x4,y4]], ...]
    2. 扁平列表: [[x1,y1,x2,y2,x3,y3,x4,y4], ...]
    
    Args:
        boxes: 原始boxes列表
        image_shape: 图片形状 (height, width, channels)，用于裁剪坐标
    
    返回: numpy array 格式的坐标点列表
    """
    normalized_boxes = []
    
    # 获取图片尺寸（如果提供）
    max_x = None
    max_y = None
    if image_shape is not None:
        max_y, max_x = image_shape[:2]
    
    for i, box in enumerate(boxes):
        if not box:
            logger.debug(f"跳过空 box {i}")
            continue
        
        try:
            # 检查是嵌套列表还是扁平列表
            if isinstance(box[0], (list, tuple)):
                points = np.array(box, dtype=np.float32)
            else:
                if len(box) != 8:
                    logger.warning(f"Box {i} 格式错误: 长度 {len(box)}, 期望 8")
                    continue
                points = np.array(box, dtype=np.float32).reshape(-1, 2)
            
            if len(points) != 4:
                logger.warning(f"Box {i} 点数错误: {len(points)}, 期望 4")
                continue
            
            # 🔥 裁剪坐标到图片范围内
            if max_x is not None and max_y is not None:
                points[:, 0] = np.clip(points[:, 0], 0, max_x - 1)
                points[:, 1] = np.clip(points[:, 1], 0, max_y - 1)
            
            # 转换为整数
            points = points.astype(np.int32)
            
            normalized_boxes.append(points)
            logger.debug(f"Box {i}: {points.tolist()}")
            
        except Exception as e:
            logger.warning(f"Box {i} 解析失败: {e}")
            continue
    
    logger.info(f"标准化完成: {len(normalized_boxes)}/{len(boxes)} 个有效 boxes")
    return normalized_boxes


def create_mask_from_boxes(image_shape, boxes, padding=5):
    """
    根据 boxes 创建 mask
    
    Args:
        image_shape: 图片形状 (height, width, channels)
        boxes: 标准化后的 boxes 列表
        padding: 扩展边距（像素），用于确保完全覆盖文字
    
    Returns:
        mask: numpy array, 255 表示需要修复的区域
    """
    mask = np.zeros(image_shape[:2], dtype=np.uint8)
    height, width = image_shape[:2]
    
    for points in boxes:
        # 🔥 扩大box范围，确保完全覆盖文字
        expanded_points = points.copy()
        
        # 计算中心点
        center_x = np.mean(points[:, 0])
        center_y = np.mean(points[:, 1])
        
        # 向外扩展每个点
        for i in range(len(expanded_points)):
            dx = expanded_points[i][0] - center_x
            dy = expanded_points[i][1] - center_y
            
            # 计算扩展方向
            length = np.sqrt(dx*dx + dy*dy)
            if length > 0:
                dx = dx / length * padding
                dy = dy / length * padding
                
                # 应用扩展并限制在图片范围内
                expanded_points[i][0] = int(np.clip(expanded_points[i][0] + dx, 0, width - 1))
                expanded_points[i][1] = int(np.clip(expanded_points[i][1] + dy, 0, height - 1))
        
        # 在 mask 上绘制扩展后的区域
        cv2.fillPoly(mask, [expanded_points], 255)
    
    return mask


def validate_boxes(boxes, image_shape):
    """
    验证 boxes 坐标是否在图片范围内
    
    Args:
        boxes: 标准化后的 boxes 列表
        image_shape: 图片形状 (height, width, channels)
    
    Returns:
        bool: 是否有效
        str: 错误信息（如果无效）
    """
    height, width = image_shape[:2]
    
    for i, points in enumerate(boxes):
        for j, point in enumerate(points):
            x, y = point
            if x < 0 or x >= width or y < 0 or y >= height:
                msg = f"Box {i} 点 {j} 超出范围: ({x},{y}), 图片: {width}x{height}"
                logger.warning(msg)
                return False, msg
    
    logger.info(f"坐标验证通过: {len(boxes)} 个 boxes 在 {width}x{height} 图片范围内")
    return True, ""


# ==================== API 端点 ====================
@app.route('/inpaint', methods=['POST'])
def inpaint():
    """
    Inpaint + 文字渲染 API 端点
    
    接收图片、文字区域坐标和翻译文字，智能移除原文字并渲染翻译后的文字
    
    请求参数:
        file: 图片文件
        boxes: JSON 数组，文字区域坐标 [[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], ...]
        texts: JSON 数组（可选），翻译后的文字信息 [
            {
                'text': '翻译文字',
                'color': [R, G, B],  # 可选
                'bg_color': [R, G, B],  # 可选
                'align': 'center'  # 可选
            }
        ]
    """
    request_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    start_time = datetime.now()
    
    logger.info(f"[{request_id}] 收到 inpaint 请求")
    
    try:
        # 1. 验证文件上传
        if 'file' not in request.files:
            logger.warning(f"[{request_id}] 缺少文件")
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.warning(f"[{request_id}] 文件名为空")
            return jsonify({'error': 'Empty filename'}), 400
        
        # 2. 验证 boxes
        if 'boxes' not in request.form:
            logger.warning(f"[{request_id}] 缺少 boxes")
            return jsonify({'error': 'No boxes provided'}), 400
        
        # 3. 解析 boxes JSON
        try:
            boxes_str = request.form['boxes']
            boxes = json.loads(boxes_str)
            
            if not isinstance(boxes, list):
                return jsonify({'error': 'Boxes must be an array'}), 400
            
            logger.info(f"[{request_id}] 文件: {file.filename}, boxes: {len(boxes)}")
            
        except json.JSONDecodeError as e:
            logger.error(f"[{request_id}] JSON 解析失败: {e}")
            return jsonify({'error': 'Invalid JSON in boxes parameter', 'detail': str(e)}), 400
        
        # 4. 解析 texts JSON（可选）
        texts_data = None
        if 'texts' in request.form:
            try:
                texts_str = request.form['texts']
                texts_data = json.loads(texts_str)
                
                if not isinstance(texts_data, list):
                    return jsonify({'error': 'Texts must be an array'}), 400
                
                logger.info(f"[{request_id}] 翻译文字: {len(texts_data)} 段")
                
            except json.JSONDecodeError as e:
                logger.error(f"[{request_id}] texts JSON 解析失败: {e}")
                return jsonify({'error': 'Invalid JSON in texts parameter', 'detail': str(e)}), 400
        
        # 5. 读取图片
        try:
            image = Image.open(file.stream)
            logger.info(f"[{request_id}] 图片: {image.size} {image.mode}")
            
            # 转换为 RGB
            if image.mode != 'RGB':
                logger.debug(f"[{request_id}] 转换 {image.mode} -> RGB")
                image = image.convert('RGB')
            
        except Exception as e:
            logger.error(f"[{request_id}] 图片读取失败: {e}")
            return jsonify({'error': 'Unsupported image format', 'detail': str(e)}), 400
        
        # 6. 转换为 numpy 数组
        img_array = np.array(image)
        logger.debug(f"[{request_id}] 数组形状: {img_array.shape}")
        
        # 7. 处理 boxes（空则返回原图）
        if len(boxes) == 0:
            logger.info(f"[{request_id}] boxes 为空，返回原图")
            output = BytesIO()
            image.save(output, format='JPEG', quality=config.OUTPUT_QUALITY)
            output.seek(0)
            return send_file(output, mimetype='image/jpeg')
        
        # 8. 标准化 boxes
        try:
            normalized_boxes = normalize_boxes(boxes, img_array.shape)
            if not normalized_boxes:
                logger.warning(f"[{request_id}] 没有有效的 boxes")
                return jsonify({'error': 'No valid boxes'}), 400
        except Exception as e:
            logger.error(f"[{request_id}] Boxes 格式错误: {e}")
            return jsonify({'error': 'Invalid boxes format', 'detail': str(e)}), 400
        
        # 9. 验证坐标（这一步现在应该总是通过，因为已经裁剪过了）
        is_valid, error_msg = validate_boxes(normalized_boxes, img_array.shape)
        if not is_valid:
            logger.warning(f"[{request_id}] 坐标验证失败（不应该发生）: {error_msg}")
            # 不返回错误，继续处理
        
        # 10. 先用白色填充所有box区域，再inpaint
        pil_masked = Image.fromarray(img_array.copy())
        draw = ImageDraw.Draw(pil_masked)
        for points in normalized_boxes:
            draw.polygon([tuple(p) for p in points], fill=(255,255,255))
        img_array_masked = np.array(pil_masked)
        
        
        # 11. 创建 mask 并执行 inpainting
        mask = create_mask_from_boxes(img_array.shape, normalized_boxes, padding=config.MASK_PADDING)
        mask_pixels = np.count_nonzero(mask)
        logger.info(f"[{request_id}] Mask: {mask_pixels} 像素需要修复 (padding={config.MASK_PADDING})")
        try:
            img_bgr = cv2.cvtColor(img_array_masked, cv2.COLOR_RGB2BGR)
            
            logger.debug(f"[{request_id}] 开始 inpaint (方法: {config.INPAINT_METHOD_NAME}, 半径: {config.INPAINT_RADIUS})")
            result_bgr = cv2.inpaint(img_bgr, mask, config.INPAINT_RADIUS, config.INPAINT_METHOD)
            result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
            
            logger.info(f"[{request_id}] ✓ Inpainting 完成")
            
            # 转回 PIL Image
            result_image = Image.fromarray(result_rgb)
            result_image.save(os.path.join(debug_dir, f'{debug_base}_inpainted.jpg'))
            
        except Exception as e:
            logger.error(f"[{request_id}] Inpainting 失败: {e}", exc_info=True)
            return jsonify({'error': 'Inpainting failed', 'detail': str(e)}), 500
        
        # 12. 渲染翻译后的文字（如果提供了 texts）
        if texts_data:
            try:
                # 将 box 和 text 对应起来
                combined_texts = []
                for i, text_item in enumerate(texts_data):
                    # 🔥 优先使用 text_item 中的 box（如果有），否则从 boxes 参数中获取
                    box = text_item.get('box')
                    if not box and i < len(boxes):
                        box = boxes[i]
                    
                    if box:
                        combined_item = {
                            'box': box,
                            'text': text_item.get('text', ''),
                            'color': text_item.get('color', list(config.DEFAULT_TEXT_COLOR)),
                            'bg_color': text_item.get('bg_color'),
                            'align': text_item.get('align', 'center')
                        }
                        combined_texts.append(combined_item)
                    else:
                        logger.warning(f"[{request_id}] texts[{i}] 没有 box 信息，跳过")
                
                result_image = draw_text_on_image(result_image, combined_texts, FONT_PATH)
                
            except Exception as e:
                logger.error(f"[{request_id}] 文字渲染失败: {e}", exc_info=True)
                # 渲染失败不影响返回 inpaint 后的图片
                logger.warning(f"[{request_id}] 继续返回未渲染文字的图片")
        
        # 13. 返回结果
        output = BytesIO()
        result_image.save(output, format='JPEG', quality=config.OUTPUT_QUALITY)
        output.seek(0)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"[{request_id}] ✓ 完成: {processing_time:.3f}s, 输出: {len(output.getvalue())/1024:.1f}KB")
        
        return send_file(output, mimetype='image/jpeg', as_attachment=False, download_name='inpainted.jpg')
    
    except Exception as e:
        logger.error(f"[{request_id}] 未知错误: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error', 'detail': str(e)}), 500


@app.route('/', methods=['GET'])
def root():
    """服务根路径"""
    return jsonify({
        'service': 'Inpaint + Render Service',
        'version': '2.0.0',
        'description': '智能移除图片中指定区域的文字并渲染翻译后的文字',
        'endpoints': {
            '/inpaint': 'POST - 执行 inpaint 和文字渲染操作',
            '/health': 'GET - 健康检查'
        },
        'features': [
            'OpenCV Inpainting',
            'GPU 加速支持',
            '自动字体大小计算',
            '多种对齐方式',
            '背景色支持'
        ]
    })


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'inpaint-render',
        'font_available': FONT_PATH is not None,
        'gpu_available': GPU_AVAILABLE
    })


if __name__ == '__main__':
    logger.info("=" * 70)
    logger.info("Inpaint + Render 服务启动")
    logger.info("=" * 70)
    logger.info(f"服务地址: http://{INPAINT_HOST}:{INPAINT_PORT}")
    logger.info(f"日志级别: {os.getenv('LOG_LEVEL', 'INFO')}")
    logger.info(f"GPU 加速: {'启用' if GPU_AVAILABLE else '禁用 (CPU模式)'}")
    logger.info(f"Inpaint 方法: {config.INPAINT_METHOD_NAME}")
    logger.info(f"修复半径: {config.INPAINT_RADIUS}")
    logger.info(f"字体路径: {FONT_PATH or '未找到'}")
    logger.info(f"最大图片: {config.MAX_IMAGE_SIZE / (1024*1024):.0f}MB")
    logger.info(f"输出质量: {config.OUTPUT_QUALITY}")
    logger.info(f"OpenCV: {cv2.__version__}")
    logger.info(f"NumPy: {np.__version__}")
    logger.info("=" * 70)
    
    app.run(
        host=INPAINT_HOST,
        port=INPAINT_PORT,
        debug=config.DEBUG
    )