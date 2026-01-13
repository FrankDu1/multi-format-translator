"""
Image Translator API - 纯后端服务
提供图片翻译 REST API
"""
import os
import sys

# 🔥 确保能找到 config.py
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import threading
import time
from pathlib import Path
import uuid
import json
from datetime import timedelta
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
import base64
from services.ali_translate_client import AliTranslateClient



# 导入日志配置
from logger_config import app_logger, api_logger, log_exception

# use remote translate service or local
USE_CLOUD_TRANSLATE = os.getenv('USE_CLOUD_TRANSLATE', 'false').lower() == 'true'
app_logger.info(f"[启动] USE_CLOUD_TRANSLATE 环境变量: {os.getenv('USE_CLOUD_TRANSLATE')}")
app_logger.info(f"[启动] USE_CLOUD_TRANSLATE 解析结果: {USE_CLOUD_TRANSLATE}")

# 导入配置
try:
    from config import (
        API_HOST, API_PORT, UPLOAD_FOLDER, ARCHIVE_FOLDER, LOG_FOLDER,
        OCR_SERVICE_URL, INPAINT_SERVICE_URL, USE_INPAINT, ALLOWED_ORIGINS,
        MONITOR_USERNAME, MONITOR_PASSWORD_HASH, MAX_FILE_SIZE
    )
    # 🔥 修复：确保 UPLOAD_FOLDER 是绝对路径
    if not os.path.isabs(UPLOAD_FOLDER):
        UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), UPLOAD_FOLDER)
except Exception as e:
    app_logger.warning(f"Failed to load config: {e}, using defaults")
    API_HOST = "0.0.0.0"
    API_PORT = 5002
    # 🔥 修复：使用相对于当前文件的路径
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
    ARCHIVE_FOLDER = os.path.join(os.path.dirname(__file__), "archives")
    LOG_FOLDER = os.path.join(os.path.dirname(__file__), "logs")
    MAX_FILE_SIZE = 10 * 1024 * 1024
    OCR_SERVICE_URL = "http://localhost:8899/ocr"
    INPAINT_SERVICE_URL = "http://localhost:8900/inpaint"
    USE_INPAINT = True
    ALLOWED_ORIGINS = ["http://localhost:5001", "http://127.0.0.1:5001"]
    MONITOR_USERNAME = "admin"
    from werkzeug.security import generate_password_hash
    MONITOR_PASSWORD_HASH = generate_password_hash("change_me_in_production")

app = Flask(__name__)

# CORS 配置（使用配置文件）
# 如果 ALLOWED_ORIGINS 是 ['*']，则允许所有来源
if ALLOWED_ORIGINS == ['*']:
    CORS(app, 
         resources={r"/*": {
             "origins": "*",
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "expose_headers": ["Content-Type"],
             "max_age": 3600
         }}, 
         supports_credentials=False)
    app_logger.info("✓ CORS 已启用（允许所有来源）")
else:
    CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)
    app_logger.info(f"✓ CORS 已启用（允许来源: {ALLOWED_ORIGINS}）")

# 🔥 新增：使用日志目录配置
USAGE_LOG_FOLDER = os.path.join(LOG_FOLDER, "usage")
os.makedirs(USAGE_LOG_FOLDER, exist_ok=True)

# 🔥 确保归档目录存在
os.makedirs(ARCHIVE_FOLDER, exist_ok=True)

# 创建必要的目录
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("fonts", exist_ok=True)
os.makedirs("static", exist_ok=True)


# ============= 监控仪表盘认证 =============

# 🔥 配置监控密码（建议放到环境变量或 config.py）

def check_monitor_auth():
    """检查监控仪表盘的认证"""
    auth = request.authorization
    
    if not auth:
        return False
    
    # 验证用户名和密码
    if auth.username == MONITOR_USERNAME and check_password_hash(MONITOR_PASSWORD_HASH, auth.password):
        return True
    
    return False

def require_monitor_auth(f):
    """监控认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not check_monitor_auth():
            # 返回 401 要求认证
            return jsonify({'error': 'Authentication required'}), 401, {
                'WWW-Authenticate': 'Basic realm="Monitor Dashboard"'
            }
        return f(*args, **kwargs)
    return decorated



# ============= 用户行为监控 =============

def log_usage(request_data):
    """记录用户使用行为到 JSON 文件"""
    try:
        # 获取当前日期
        current_date = datetime.now()
        year = current_date.strftime('%Y')
        month = current_date.strftime('%m')
        day_folder = os.path.join(USAGE_LOG_FOLDER, year, month)
        os.makedirs(day_folder, exist_ok=True)
        
        # 日志文件名：usage_YYYYMMDD.json
        log_filename = f"usage_{current_date.strftime('%Y%m%d')}.json"
        log_filepath = os.path.join(day_folder, log_filename)
        
        # 读取现有记录
        if os.path.exists(log_filepath):
            with open(log_filepath, 'r', encoding='utf-8') as f:
                usage_data = json.load(f)
        else:
            usage_data = []
        
        # 添加新记录
        usage_data.append(request_data)
        
        # 写回文件
        with open(log_filepath, 'w', encoding='utf-8') as f:
            json.dump(usage_data, f, ensure_ascii=False, indent=2)
        
        app_logger.debug(f"📊 Usage logged: {request_data['translation_type']} ({request_data['status']})")
        
    except Exception as e:
        app_logger.error(f"❌ Failed to log usage: {e}")


def create_usage_record(request, translation_type, file_info=None, 
                       processing_time=0, status='success', error_message=None,
                       enable_summary=False):
    """创建使用记录"""
    return {
        'timestamp': datetime.now().isoformat(),
        'request_id': str(uuid.uuid4()),
        'client_ip': request.headers.get('X-Forwarded-For', request.remote_addr),
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'endpoint': request.path,
        'method': request.method,
        'translation_type': translation_type,
        'source_lang': file_info.get('source_lang') if file_info else None,
        'target_lang': file_info.get('target_lang') if file_info else None,
        'file_name': file_info.get('file_name') if file_info else None,
        'file_size_kb': file_info.get('file_size_kb') if file_info else None,
        'processing_time_seconds': round(processing_time, 2),
        'status': status,
        'error_message': error_message,
        'enable_summary': enable_summary
    }

# ============= 定时归档任务 =============

def archive_old_files(folder, max_age_hours=2, archive_folder=ARCHIVE_FOLDER):
    """归档超过指定时间的文件（不删除）"""
    try:
        now = time.time()
        max_age_seconds = max_age_hours * 3600
        archived_count = 0
        
        # 获取当前日期，用于创建归档目录
        current_date = datetime.now()
        year = current_date.strftime('%Y')
        month = current_date.strftime('%m')
        day = current_date.strftime('%d')
        
        # 创建归档目录：archives/YYYY/MM/DD/
        archive_path = os.path.join(archive_folder, year, month, day)
        os.makedirs(archive_path, exist_ok=True)
        
        for file_path in Path(folder).glob('*'):
            if file_path.is_file():
                file_age = now - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        # 移动文件到归档目录
                        dest_path = os.path.join(archive_path, file_path.name)
                        
                        # 如果目标文件已存在，添加时间戳后缀
                        if os.path.exists(dest_path):
                            name, ext = os.path.splitext(file_path.name)
                            timestamp = int(file_path.stat().st_mtime)
                            dest_path = os.path.join(archive_path, f"{name}_{timestamp}{ext}")
                        
                        # 移动文件
                        file_path.rename(dest_path)
                        archived_count += 1
                        
                        app_logger.info(
                            f"📦 归档文件: {file_path.name} → {year}/{month}/{day}/ "
                            f"(年龄: {file_age/3600:.1f}小时)"
                        )
                    except Exception as e:
                        app_logger.error(f"归档文件失败 {file_path}: {e}")
        
        if archived_count > 0:
            app_logger.info(f"✓ 归档完成，已归档 {archived_count} 个文件到 {year}/{month}/{day}/")
        else:
            app_logger.debug(f"ℹ️  无需归档的文件")
    
    except Exception as e:
        app_logger.error(f"归档任务失败: {e}")


def schedule_archive():
    """定时归档任务（每2小时）"""
    while True:
        time.sleep(2 * 3600)  # 2小时
        app_logger.info("🔄 开始定时归档...")
        archive_old_files(UPLOAD_FOLDER, max_age_hours=2)


# 🔥 修改：启动归档线程（替代清理线程）
archive_thread = threading.Thread(target=schedule_archive, daemon=True)
archive_thread.start()

# ============= 定时清理任务 =============

def cleanup_old_files(folder, max_age_hours=2):
    """清理超过指定时间的文件"""
    try:
        now = time.time()
        max_age_seconds = max_age_hours * 3600
        deleted_count = 0
        
        for file_path in Path(folder).glob('*'):
            if file_path.is_file():
                file_age = now - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        app_logger.info(f"🗑️  删除旧文件: {file_path.name} (年龄: {file_age/3600:.1f}小时)")
                    except Exception as e:
                        app_logger.error(f"删除文件失败 {file_path}: {e}")
        
        if deleted_count > 0:
            app_logger.info(f"✓ 清理完成，删除 {deleted_count} 个文件")
    
    except Exception as e:
        app_logger.error(f"清理任务失败: {e}")


def schedule_cleanup():
    """定时清理任务（每2小时）"""
    while True:
        time.sleep(2 * 3600)
        app_logger.info("🔄 开始定时清理...")
        cleanup_old_files(UPLOAD_FOLDER, max_age_hours=2)


# 启动清理线程
#cleanup_thread = threading.Thread(target=schedule_cleanup, daemon=True)
#cleanup_thread.start()


# ============= API 路由 =============

@app.route('/')
def index():
    """API 根路径"""
    return jsonify({
        'name': 'Image Translator API',
        'version': '2.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'translate': '/api/translate/image',
            'files': '/api/files/<filename>'
        }
    })


@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/translate/image', methods=['POST'])
def translate_image():
    """图片翻译接口"""
    start_time = time.time()
    usage_record = None  # 用于记录使用情况

    try:
        # 1. 检查文件
        if 'file' not in request.files:
            api_logger.warning("❌ No file in request")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            api_logger.warning("❌ Empty filename")
            return jsonify({'error': 'Empty filename'}), 400
        
        # 2. 获取参数
        src_lang = request.form.get('source_lang', 'en')
        tgt_lang = request.form.get('target_lang', 'zh')
        
        enable_summary = request.form.get('enable_summary', 'false').lower() == 'true'

        api_logger.info(f"Translation request: {src_lang} → {tgt_lang}")
        api_logger.info(f"Original filename: {file.filename}")
        api_logger.info(f"   AI Summary: {'✓' if enable_summary else '✗'}") 

        # 3. 保存上传的文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{timestamp}_{file.filename}"
        input_path = os.path.join(UPLOAD_FOLDER, safe_filename)
        
        file.save(input_path)
        file_size = os.path.getsize(input_path) / 1024
        api_logger.info(f"✓ File saved: {input_path} ({file_size:.1f}KB)")
        
        # 4. 执行翻译
        output_filename = f"{timestamp}_translated_{file.filename}"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        api_logger.info(f"Expected output: {output_path}")
        
        try:
            from services.image_translator import translate_image_with_ocr_and_nllb_detailed
            
            success, translations, error_message, summary_result = translate_image_with_ocr_and_nllb_detailed(
                image_path=input_path,
                output_path=output_path,
                src_lang=src_lang,
                tgt_lang=tgt_lang,
                ocr_url=OCR_SERVICE_URL,
                inpaint_url=INPAINT_SERVICE_URL,
                use_inpaint=USE_INPAINT,
                enable_summary=enable_summary
            )
            
            # 🔥 修复：区分不同的失败原因
            if not success:
                # 检查是否是"未检测到文本"的情况
                if '未检测到' in error_message or 'No text' in error_message or not translations:
                    api_logger.warning(f"⚠️  未检测到文本: {error_message}")
                    return jsonify({
                        'success': False,
                        'error': 'No text detected',
                        'message': error_message,
                        'code': 'NO_TEXT_DETECTED'
                    }), 400
                else:
                    # 其他失败原因（如翻译错误、文件错误等）
                    api_logger.error(f"❌ Translation failed: {error_message}")
                    return jsonify({
                        'success': False,
                        'error': 'Translation failed',
                        'message': error_message,
                        'code': 'TRANSLATION_ERROR'
                    }), 500
                
        except Exception as translation_error:
            api_logger.error(f"❌ Translation exception: {translation_error}")
            log_exception(api_logger, translation_error)
            # 🔥 记录异常
            usage_record = create_usage_record(
                request=request,
                translation_type='image',
                file_info={
                    'source_lang': src_lang,
                    'target_lang': tgt_lang,
                    'file_name': file.filename,
                    'file_size_kb': round(file_size, 2)
                },
                processing_time=elapsed,
                status='exception',
                error_message=str(translation_error),
                enable_summary=enable_summary
            )
            log_usage(usage_record)
            return jsonify({
                'error': 'Translation failed',
                'message': str(translation_error),
                'code': 'EXCEPTION'
            }), 500
        
        elapsed = time.time() - start_time
        
        # 🔥 成功的情况
        if success and os.path.exists(output_path):
            api_logger.info(f"✓ Translation completed ({elapsed:.2f}s)")
            # 🔥 记录成功
            usage_record = create_usage_record(
                request=request,
                translation_type='image',
                file_info={
                    'source_lang': src_lang,
                    'target_lang': tgt_lang,
                    'file_name': file.filename,
                    'file_size_kb': round(file_size, 2)
                },
                processing_time=elapsed,
                status='success',
                enable_summary=enable_summary
            )
            log_usage(usage_record)
            # 验证输出文件名
            actual_output_file = os.path.basename(output_path)
            api_logger.info(f"   Expected filename: {output_filename}")
            api_logger.info(f"   Actual filename: {actual_output_file}")
            api_logger.info(f"   Output exists: {os.path.exists(output_path)}")
            
            # 格式化翻译结果
            formatted_translations = []
            for trans in translations:
                formatted_translations.append({
                    'original_text': trans.get('original_text', ''),
                    'translated_text': trans.get('translated_text', ''),
                    'confidence': trans.get('confidence', 0.0)
                })
            
            # 📌 修复：构建正确的图片 URL
            scheme = request.headers.get('X-Forwarded-Proto', request.scheme)
            host = request.headers.get('X-Forwarded-Host', request.host)
            
            # 📌 关键修复：检查所有可能的代理标识
            # Nginx 会设置这些头部
            forwarded_host = request.headers.get('X-Forwarded-Host', '')
            original_uri = request.headers.get('X-Original-URI', '')
            request_url = request.url
            referer = request.headers.get('Referer', '')
            
            # 打印调试信息
            api_logger.info(f"   Request headers:")
            api_logger.info(f"   - Scheme: {scheme}")
            api_logger.info(f"   - Host: {host}")
            api_logger.info(f"   - X-Forwarded-Host: {forwarded_host}")
            api_logger.info(f"   - X-Original-URI: {original_uri}")
            api_logger.info(f"   - Request URL: {request_url}")
            api_logger.info(f"   - Referer: {referer}")
            
            # 📌 判断是否通过 Nginx 代理（检查域名）
            production_domain = os.getenv('PRODUCTION_DOMAIN', 'example.com')
            is_proxied = (
                production_domain in host or 
                production_domain in forwarded_host or
                'translator-api' in original_uri or
                'translator-api' in referer
            )
            
            if is_proxied:
                # 通过 Nginx 代理，需要加 /translator-api 前缀
                image_url = f"{scheme}://{host}/translator-api/api/files/{actual_output_file}"
            else:
                # 直接访问后端
                image_url = f"{scheme}://{host}/api/files/{actual_output_file}"
            
            api_logger.info(f"   Is proxied: {is_proxied}")
            api_logger.info(f"   Final image URL: {image_url}")
            
            return jsonify({
                'success': True,
                'message': 'Translation completed',
                'translated_image_url': image_url,
                'original_filename': file.filename,
                'translated_filename': actual_output_file,
                'processing_time': f"{elapsed:.2f}s",
                'translations': formatted_translations,
                **(
                    {
                        'summary': {
                            'success': summary_result['success'],
                            'content': summary_result.get('summary'),
                            'error': summary_result.get('error')
                        }
                    } if enable_summary and summary_result else {}
                )
            })
        # 🔥 如果失败（未检测到文本），返回友好错误
        if not success:
            api_logger.warning(f"⚠️  {error_message}")
            return jsonify({
                'success': False,
                'error': 'No text detected',
                'message': error_message,
                'code': 'NO_TEXT_DETECTED'
            }), 400
        else:
            api_logger.error(f"❌ Translation failed")
            api_logger.error(f"   Expected output: {output_path}")
            api_logger.error(f"   File exists: {os.path.exists(output_path)}")
            
            try:
                files = os.listdir(UPLOAD_FOLDER)
                translated_files = [f for f in files if 'translated' in f and timestamp in f]
                api_logger.error(f"   Files with timestamp {timestamp}: {translated_files}")
            except Exception as e:
                api_logger.error(f"   Cannot list files: {e}")
            
            return jsonify({'error': 'Translation failed'}), 500
    
    except Exception as e:
        api_logger.error(f"❌ API Error: {e}")
        try:
            usage_record = create_usage_record(
                request=request,
                translation_type='image',
                file_info=None,
                processing_time=elapsed,
                status='error',
                error_message=str(e)
            )
            log_usage(usage_record)
        except:
            pass  # 避免日志记录本身出错

        log_exception(api_logger, e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/translate/pdf', methods=['POST'])
def translate_pdf():
    """PDF翻译接口 - 模仿图片翻译的格式"""
    start_time = time.time()
    
    try:
        from services.pdf_translator import translate_pdf_file
        # 1. 检查文件
        if 'file' not in request.files:
            api_logger.warning("❌ No file provided")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            api_logger.warning("❌ No file selected")
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            api_logger.warning(f"❌ Invalid file type: {file.filename}")
            return jsonify({'error': 'Only PDF files are supported'}), 400
        
        # 2. 保存上传的文件
        upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        file.save(file_path)
        file_size = os.path.getsize(file_path) / 1024  # 转换为 KB

        # 3. 获取参数（与图片翻译保持一致）
        src_lang = request.form.get('source_lang', 'en')
        tgt_lang = request.form.get('target_lang', 'zh')

        # 新增: 获取AI总结开关
        enable_summary = request.form.get('enable_summary', 'false').lower() == 'true'
        
        api_logger.info(f"📄 PDF translation request:")
        api_logger.info(f"   File: {file.filename}")
        api_logger.info(f"   {src_lang} → {tgt_lang}")
        api_logger.info(f"   AI Summary: {'✓' if enable_summary else '✗'}")
        
        # 4. 调用PDF翻译
        try:
            # 🔥 修改: 传递 enable_summary 参数
            translated_pdf_path, summary_result = translate_pdf_file(
                file_path, 
                src_lang, 
                tgt_lang,
                enable_summary
            )
        except Exception as e:
            # 如果复杂版本失败，尝试简单版本
            elapsed = time.time() - start_time
            usage_record = create_usage_record(
                request=request,
                translation_type='pdf',  # 🔥 修正：应该是 'pdf' 而不是 'image'
                file_info={
                    'source_lang': src_lang,
                    'target_lang': tgt_lang,
                    'file_name': file.filename,
                    'file_size_kb': round(file_size, 2)
                },
                processing_time=elapsed,
                status='failed',
                error_message=str(e),
                enable_summary=enable_summary
            )
            log_usage(usage_record)
            api_logger.warning(f"⚠️ Advanced PDF translation failed: {e}")
            #translated_pdf_path = translate_pdf_simple(file_path, src_lang, tgt_lang)
            raise e
        
        elapsed = time.time() - start_time
        
        # 5. 返回结果（与图片翻译格式一致）
        download_filename = os.path.basename(translated_pdf_path)
        
        api_logger.info(f"✓ PDF translation completed ({elapsed:.2f}s)")
        api_logger.info(f"   Output: {download_filename}")
        # 🔥 记录成功
        usage_record = create_usage_record(
            request=request,
            translation_type='pdf',  # 🔥 修正：应该是 'pdf' 而不是 'image'
            file_info={
                'source_lang': src_lang,
                'target_lang': tgt_lang,
                'file_name': file.filename,
                'file_size_kb': round(file_size, 2)
            },
            processing_time=elapsed,
            status='success',
            enable_summary=enable_summary
        )
        log_usage(usage_record)
        # ✅ 修复：使用与图片翻译相同的 download_url 格式
        return jsonify({
            'success': True,
            'download_url': f'/api/files/{download_filename}',  # 修复：与图片一致
            'filename': download_filename,
            'source_lang': src_lang,
            'target_lang': tgt_lang,
            'processing_time': f"{elapsed:.2f}s",
            # 总结字段
            **(
                {
                    'summary': {
                        'success': summary_result['success'],
                        'content': summary_result.get('summary'),
                        'error': summary_result.get('error')
                    }
                } if enable_summary and summary_result else {}
            )
        })
        
    except Exception as e:
        elapsed = time.time() - start_time
        
        # 🔥 记录顶层异常
        try:
            usage_record = create_usage_record(
                request=request,
                translation_type='pdf',
                file_info={
                    'source_lang': request.form.get('source_lang', 'en'),
                    'target_lang': request.form.get('target_lang', 'zh'),
                    'file_name': request.files.get('file', type('', (), {'filename': 'unknown'})).filename if 'file' in request.files else 'unknown',
                    'file_size_kb': None
                },
                processing_time=elapsed,
                status='error',
                error_message=str(e),
                enable_summary=request.form.get('enable_summary', 'false').lower() == 'true'
            )
            log_usage(usage_record)
        except:
            pass  # 避免日志记录本身出错
        api_logger.error(f"❌ PDF translation API error: {e}")
        log_exception(api_logger, e)
        return jsonify({
            'error': 'PDF translation failed',
            'details': str(e)
        }), 500

@app.route('/api/translate/translate-text', methods=['POST'])
def translate_text():
    """文本翻译接口 - 使用统一的 NLLB 翻译器"""
    start_time = time.time()
    
    try:
        # 1. 获取 JSON 数据
        if not request.is_json:
            api_logger.warning("❌ Request is not JSON")
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        # 2. 验证必需参数
        text = data.get('text', '').strip()
        if not text:
            api_logger.warning("❌ Empty text")
            return jsonify({'error': 'Text is required'}), 400
        
        # ✅ 与图片翻译API保持一致的参数名

        src_lang = data.get('source_lang', 'en')
        tgt_lang = data.get('target_lang', 'zh')
        
        api_logger.info(f"📝 Text translation request:")
        api_logger.info(f"   Text: {text[:50]}{'...' if len(text) > 50 else ''}")
        api_logger.info(f"   {src_lang} → {tgt_lang}")  # ← 格式一致
        
        # 🔥 新增: 获取是否启用AI总结的参数
        enable_summary = data.get('enable_summary', False)
        
        api_logger.info(f"📝 Text translation request:")
        api_logger.info(f"   Text: {text[:50]}{'...' if len(text) > 50 else ''}")
        api_logger.info(f"   {src_lang} → {tgt_lang}")
        api_logger.info(f"   AI Summary: {'✓' if enable_summary else '✗'}")
       
        # 3. 调用统一的翻译器
        try:
            #USE_CLOUD_TRANSLATE=True
            if USE_CLOUD_TRANSLATE:
                # 云端翻译
                app_logger.info("[翻译] 使用阿里云远端翻译")
                client = AliTranslateClient()
                result = client.translate(text, source_lang=src_lang, target_lang=tgt_lang)

                if result.get('success'):
                    translated_text = result.get('translated_text', '')
                    if not translated_text:
                        raise Exception("Translation returned empty result")
                else:
                    raise Exception(result.get('error_message', 'Aliyun translation failed'))
            else:
                # 🔥 使用与图片翻译相同的翻译器
                from services.text_translator import split_text_into_chunks
                from services.nllb_translator_pipeline import get_translator

                # 分段处理
                chunks = split_text_into_chunks(text, max_length=400)
                api_logger.info(f"   分段数量: {len(chunks)}")

                translator = get_translator()
                translated_chunks = translator.translate_batch(chunks, src_lang, tgt_lang)
                translated_text = '\n'.join(translated_chunks)
                
                if not translated_text:
                    raise Exception("Translation returned empty result")
                
        except Exception as translation_error:
            api_logger.error(f"❌ Translation error: {translation_error}")
            log_exception(api_logger, translation_error)
            return jsonify({
                'error': 'Translation failed',
                'details': str(translation_error)
            }), 500
        
        # 🔥 新增: AI 总结功能
        summary_result = None
        if enable_summary:
            try:
                # 根据配置动态导入 AI 服务
                from config import AI_PROVIDER
                if AI_PROVIDER == 'qwen':
                    from services.qwen_service import qwen_service as ai_service
                else:
                    from services.ollama_service import ollama_service as ai_service
                
                api_logger.info(f"🧠 开始生成AI总结 (提供商: {AI_PROVIDER})...")
                summary_result = ai_service.generate_summary(
                    text=translated_text,
                    target_language=tgt_lang
                )
                
                if summary_result['success']:
                    api_logger.info(f"✓ AI总结生成成功")
                else:
                    api_logger.warning(f"⚠️ AI总结生成失败: {summary_result['error']}")
                    
            except Exception as summary_error:
                api_logger.error(f"❌ AI总结异常: {summary_error}")
                log_exception(api_logger, summary_error)
                # 🔥 总结失败不影响翻译结果
                summary_result = {
                    'success': False,
                    'summary': None,
                    'error': '生成总结时发生错误 🔧'
                }

        elapsed = time.time() - start_time
        
        api_logger.info(f"✓ Text translation completed ({elapsed:.2f}s)")
        api_logger.info(f"   Result: {translated_text[:50]}{'...' if len(translated_text) > 50 else ''}")
        
        return jsonify({
            'success': True,
            'original_text': text,
            'translated_text': translated_text,
            'source_lang': src_lang,
            'target_lang': tgt_lang,
            'processing_time': f"{elapsed:.2f}s",
            # 🔥 总结字段 (如果启用)
            **(
                {
                    'summary': {
                        'success': summary_result['success'],
                        'content': summary_result.get('summary'),
                        'error': summary_result.get('error')
                    }
                } if enable_summary and summary_result else {}
            )
        })
    
    except Exception as e:
        api_logger.error(f"❌ API Error: {e}")
        log_exception(api_logger, e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/translate/ppt', methods=['POST'])
def translate_ppt():
    """PPT 翻译接口 - 与图片/PDF 格式保持一致"""
    start_time = time.time()
    
    try:
        # 1. 检查文件
        if 'file' not in request.files:
            api_logger.warning("❌ No file in request")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            api_logger.warning("❌ Empty filename")
            return jsonify({'error': 'Empty filename'}), 400
        
        # 检查文件类型
        if not file.filename.lower().endswith(('.ppt', '.pptx')):
            api_logger.warning(f"❌ Invalid file type: {file.filename}")
            return jsonify({'error': 'Only PPT/PPTX files are supported'}), 400
        
        # 2. 获取参数（与图片翻译保持一致）
        src_lang = request.form.get('source_lang', 'auto')
        tgt_lang = request.form.get('target_lang', 'zh')
        enable_summary = request.form.get('enable_summary', 'false').lower() == 'true'

        simple_mode = request.form.get('simple', 'false').lower() == 'true'
        
        api_logger.info(f"📊 PPT translation request: {src_lang} → {tgt_lang}")
        api_logger.info(f"   Original filename: {file.filename}")
        api_logger.info(f"   Mode: {'Simple' if simple_mode else 'Full'}")
        api_logger.info(f"   AI Summary: {'✓' if enable_summary else '✗'}")
       
        # 3. 保存上传的文件（使用时间戳命名）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{timestamp}_{file.filename}"
        input_path = os.path.join(UPLOAD_FOLDER, safe_filename)
        
        file.save(input_path)
        file_size = os.path.getsize(input_path) / 1024
        api_logger.info(f"✓ File saved: {input_path} ({file_size:.1f}KB)")
        
        # 4. 执行翻译
        output_filename = f"{timestamp}_translated_{file.filename}"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        api_logger.info(f"   Expected output: {output_path}")
        
        try:
            from services.ppt_translator import translate_ppt_file, translate_ppt_simple
            
            # 根据模式选择翻译方法
            if simple_mode:
                actual_output_path = translate_ppt_simple(
                    input_path,
                    src_lang=src_lang,
                    tgt_lang=tgt_lang,
                    output_path=output_path,
                    enable_summary=enable_summary
                )
            else:
                actual_output_path, summary_result = translate_ppt_file(
                    input_path,
                    src_lang=src_lang,
                    tgt_lang=tgt_lang,
                    output_path=output_path,
                    enable_summary=enable_summary
                )
            
        except Exception as translation_error:
            elapsed = time.time() - start_time
            # 🔥 记录翻译失败
            usage_record = create_usage_record(
                request=request,
                translation_type='ppt',
                file_info={
                    'source_lang': src_lang,
                    'target_lang': tgt_lang,
                    'file_name': file.filename,
                    'file_size_kb': round(file_size, 2)
                },
                processing_time=elapsed,
                status='failed',
                error_message=str(translation_error),
                enable_summary=enable_summary
            )
            log_usage(usage_record)

            api_logger.error(f"❌ Translation error: {translation_error}")
            log_exception(api_logger, translation_error)
            return jsonify({
                'error': 'Translation failed',
                'details': str(translation_error)
            }), 500

        elapsed = time.time() - start_time

        # 5. 验证输出文件
        if os.path.exists(actual_output_path):
            actual_output_file = os.path.basename(actual_output_path)
            api_logger.info(f"✓ Translation completed ({elapsed:.2f}s)")
            api_logger.info(f"   Expected filename: {output_filename}")
            api_logger.info(f"   Actual filename: {actual_output_file}")
            
            # 🔥 记录成功
            usage_record = create_usage_record(
                request=request,
                translation_type='ppt',
                file_info={
                    'source_lang': src_lang,
                    'target_lang': tgt_lang,
                    'file_name': file.filename,
                    'file_size_kb': round(file_size, 2)
                },
                processing_time=elapsed,
                status='success',
                enable_summary=enable_summary
            )
            log_usage(usage_record)

            # 6. 构建下载 URL（与图片翻译逻辑一致）
            scheme = request.headers.get('X-Forwarded-Proto', request.scheme)
            host = request.headers.get('X-Forwarded-Host', request.host)
            forwarded_host = request.headers.get('X-Forwarded-Host', '')
            original_uri = request.headers.get('X-Original-URI', '')
            referer = request.headers.get('Referer', '')
            
            is_proxied = (
                'chat.offerupup.cn' in host or 
                'chat.offerupup.cn' in forwarded_host or
                'translator-api' in original_uri or
                'translator-api' in referer
            )
            
            if is_proxied:
                download_url = f"{scheme}://{host}/translator-api/api/files/{actual_output_file}"
            else:
                download_url = f"{scheme}://{host}/api/files/{actual_output_file}"
            
            api_logger.info(f"   Is proxied: {is_proxied}")
            api_logger.info(f"   Final download URL: {download_url}")
            
            # 7. 返回结果
            return jsonify({
                'success': True,
                'message': 'Translation completed',
                'translated_ppt_url': download_url,
                'original_filename': file.filename,
                'translated_filename': actual_output_file,
                'processing_time': f"{elapsed:.2f}s",
                'mode': 'simple' if simple_mode else 'full',
                # 🔥 总结字段 (如果启用)
                **(
                    {
                        'summary': {
                            'success': summary_result['success'],
                            'content': summary_result.get('summary'),
                            'error': summary_result.get('error')
                        }
                    } if enable_summary and summary_result else {}
                )
            })
        else:
            elapsed = time.time() - start_time
            # 🔥 记录输出文件不存在的失败
            usage_record = create_usage_record(
                request=request,
                translation_type='ppt',
                file_info={
                    'source_lang': src_lang,
                    'target_lang': tgt_lang,
                    'file_name': file.filename,
                    'file_size_kb': round(file_size, 2)
                },
                processing_time=elapsed,
                status='failed',
                error_message='Output file not found',
                enable_summary=enable_summary
            )
            log_usage(usage_record)

            api_logger.error(f"❌ Translation failed")
            api_logger.error(f"   Expected output: {output_path}")
            api_logger.error(f"   File exists: False")
            
            return jsonify({'error': 'Translation failed'}), 500
    
    except Exception as e:
        elapsed = time.time() - start_time
        
        # 🔥 记录顶层异常
        try:
            usage_record = create_usage_record(
                request=request,
                translation_type='ppt',
                file_info={
                    'source_lang': request.form.get('source_lang', 'auto'),
                    'target_lang': request.form.get('target_lang', 'zh'),
                    'file_name': request.files.get('file', type('', (), {'filename': 'unknown'})).filename if 'file' in request.files else 'unknown',
                    'file_size_kb': None
                },
                processing_time=elapsed,
                status='error',
                error_message=str(e),
                enable_summary=request.form.get('enable_summary', 'false').lower() == 'true'
            )
            log_usage(usage_record)
        except:
            pass  # 避免日志记录本身出错

        api_logger.error(f"❌ PPT translation API error: {e}")
        log_exception(api_logger, e)
        return jsonify({'error': str(e)}), 500



@app.route('/api/files/<path:filename>')
def serve_file(filename):
    """提供文件访问"""
    upload_dir = os.path.abspath(UPLOAD_FOLDER)
    file_path = os.path.join(upload_dir, filename)
    
    api_logger.info(f"📂 File request: {filename}")
    api_logger.info(f"   Path: {file_path}")
    api_logger.info(f"   Exists: {os.path.exists(file_path)}")
    
    # 安全检查
    if not file_path.startswith(upload_dir):
        api_logger.warning(f"⚠️  Invalid path: {filename}")
        return jsonify({'error': 'Invalid path'}), 403
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        api_logger.info(f"✓ Serving: {filename}")
        return send_file(
            file_path,
            mimetype='image/png',
            as_attachment=False
        )
    
    api_logger.error(f"❌ Not found: {filename}")
    
    # 调试：列出可用文件
    try:
        files = os.listdir(upload_dir)
        api_logger.info(f"   Available files: {files}")
    except Exception as e:
        api_logger.error(f"   Cannot list: {e}")
    
    return jsonify({'error': 'File not found'}), 404


@app.errorhandler(413)
def file_too_large(e):
    return jsonify({'error': 'File too large'}), 413


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    api_logger.error(f"Internal error: {e}")
    return jsonify({'error': 'Internal server error'}), 500


# ============= 监控仪表盘 API =============

@app.route('/api/monitor/dashboard')
@require_monitor_auth
def monitor_dashboard():
    """返回监控仪表盘的 HTML 页面"""
    return send_file('static/monitor.html')


@app.route('/api/monitor/stats')
@require_monitor_auth
def get_monitor_stats():
    """获取统计数据"""
    try:
        period = request.args.get('period', 'today')  # today, 7days, 30days, all
        
        # 读取使用日志
        usage_data = []
        current_date = datetime.now()
        
        if period == 'today':
            days_to_read = 1
        elif period == '7days':
            days_to_read = 7
        elif period == '30days':
            days_to_read = 30
        else:  # all
            days_to_read = 365  # 最多读取一年
        
        # 读取指定天数的日志
        for i in range(days_to_read):
            target_date = current_date - timedelta(days=i)
            year = target_date.strftime('%Y')
            month = target_date.strftime('%m')
            day_folder = os.path.join(USAGE_LOG_FOLDER, year, month)
            log_filename = f"usage_{target_date.strftime('%Y%m%d')}.json"
            log_filepath = os.path.join(day_folder, log_filename)
            
            if os.path.exists(log_filepath):
                try:
                    with open(log_filepath, 'r', encoding='utf-8') as f:
                        daily_data = json.load(f)
                        usage_data.extend(daily_data)
                except Exception as e:
                    app_logger.error(f"Failed to read log {log_filepath}: {e}")
        
        if not usage_data:
            return jsonify({
                'total_requests': 0,
                'success_rate': 0,
                'avg_processing_time': 0,
                'unique_ips': 0,
                'type_distribution': {},
                'daily_stats': [],
                'error_logs': []
            })
        
        # 计算统计数据
        total_requests = len(usage_data)
        success_count = len([r for r in usage_data if r['status'] == 'success'])
        success_rate = (success_count / total_requests * 100) if total_requests > 0 else 0
        
        # 平均处理时间
        processing_times = [r['processing_time_seconds'] for r in usage_data if r.get('processing_time_seconds')]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        # 唯一IP数
        unique_ips = len(set(r['client_ip'] for r in usage_data))
        
        # 翻译类型分布
        type_distribution = {}
        for record in usage_data:
            trans_type = record.get('translation_type', 'unknown')
            type_distribution[trans_type] = type_distribution.get(trans_type, 0) + 1
        
        # 每日统计（用于趋势图）
        daily_stats = {}
        for record in usage_data:
            date = record['timestamp'][:10]  # 提取日期部分 YYYY-MM-DD
            if date not in daily_stats:
                daily_stats[date] = {
                    'date': date,
                    'total': 0,
                    'success': 0,
                    'failed': 0,
                    'avg_time': []
                }
            
            daily_stats[date]['total'] += 1
            if record['status'] == 'success':
                daily_stats[date]['success'] += 1
            else:
                daily_stats[date]['failed'] += 1
            
            if record.get('processing_time_seconds'):
                daily_stats[date]['avg_time'].append(record['processing_time_seconds'])
        
        # 计算每日平均处理时间
        daily_stats_list = []
        for date, stats in sorted(daily_stats.items()):
            avg_time = sum(stats['avg_time']) / len(stats['avg_time']) if stats['avg_time'] else 0
            daily_stats_list.append({
                'date': date,
                'total': stats['total'],
                'success': stats['success'],
                'failed': stats['failed'],
                'avg_time': round(avg_time, 2),
                'success_rate': round(stats['success'] / stats['total'] * 100, 1) if stats['total'] > 0 else 0
            })
        
        # 错误日志（最近20条失败记录）
        error_logs = [
            {
                'timestamp': r['timestamp'],
                'client_ip': r['client_ip'],
                'translation_type': r['translation_type'],
                'error_message': r.get('error_message', 'Unknown error'),
                'file_name': r.get('file_name')
            }
            for r in usage_data if r['status'] in ['failed', 'error', 'exception']
        ]
        error_logs = sorted(error_logs, key=lambda x: x['timestamp'], reverse=True)[:20]
        
        return jsonify({
            'total_requests': total_requests,
            'success_rate': round(success_rate, 1),
            'avg_processing_time': round(avg_processing_time, 2),
            'unique_ips': unique_ips,
            'type_distribution': type_distribution,
            'daily_stats': daily_stats_list,
            'error_logs': error_logs
        })
        
    except Exception as e:
        app_logger.error(f"Failed to get monitor stats: {e}")
        log_exception(app_logger, e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitor/requests')
@require_monitor_auth
def get_monitor_requests():
    """获取请求列表（带分页和筛选）"""
    try:
        # 获取查询参数
        date = request.args.get('date', datetime.now().strftime('%Y%m%d'))
        limit = int(request.args.get('limit', 100))
        translation_type = request.args.get('type', None)  # 筛选翻译类型
        status = request.args.get('status', None)  # 筛选状态
        
        # 解析日期
        try:
            target_date = datetime.strptime(date, '%Y%m%d')
        except:
            target_date = datetime.now()
        
        year = target_date.strftime('%Y')
        month = target_date.strftime('%m')
        day_folder = os.path.join(USAGE_LOG_FOLDER, year, month)
        log_filename = f"usage_{date}.json"
        log_filepath = os.path.join(day_folder, log_filename)
        
        if not os.path.exists(log_filepath):
            return jsonify({
                'date': date,
                'total': 0,
                'records': []
            })
        
        # 读取日志
        with open(log_filepath, 'r', encoding='utf-8') as f:
            usage_data = json.load(f)
        
        # 应用筛选
        filtered_data = usage_data
        if translation_type:
            filtered_data = [r for r in filtered_data if r.get('translation_type') == translation_type]
        if status:
            filtered_data = [r for r in filtered_data if r.get('status') == status]
        
        # 排序（最新的在前）
        filtered_data = sorted(filtered_data, key=lambda x: x['timestamp'], reverse=True)
        
        # 限制数量
        filtered_data = filtered_data[:limit]
        
        return jsonify({
            'date': date,
            'total': len(usage_data),
            'filtered': len(filtered_data),
            'records': filtered_data
        })
        
    except Exception as e:
        app_logger.error(f"Failed to get monitor requests: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitor/system')
@require_monitor_auth
def get_system_status():
    """获取系统状态"""
    try:
        import psutil
        import shutil
        
        # CPU 和内存
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # 磁盘使用情况
        upload_disk = shutil.disk_usage(UPLOAD_FOLDER)
        archive_disk = shutil.disk_usage(ARCHIVE_FOLDER)
        
        # 文件统计
        upload_files = len(list(Path(UPLOAD_FOLDER).glob('*')))
        
        # 归档文件统计
        archive_count = 0
        archive_size = 0
        for root, dirs, files in os.walk(ARCHIVE_FOLDER):
            archive_count += len(files)
            for file in files:
                try:
                    archive_size += os.path.getsize(os.path.join(root, file))
                except:
                    pass
        
        # 检查服务状态
        services_status = {
            'api': True,  # 当前服务肯定在运行
            'ocr': check_service_health(OCR_SERVICE_URL),
            'inpaint': check_service_health(INPAINT_SERVICE_URL) if USE_INPAINT else None,
        }
        
        return jsonify({
            'cpu_percent': round(cpu_percent, 1),
            'memory_percent': round(memory.percent, 1),
            'memory_used_gb': round(memory.used / (1024**3), 2),
            'memory_total_gb': round(memory.total / (1024**3), 2),
            'upload_folder': {
                'path': UPLOAD_FOLDER,
                'files_count': upload_files,
                'total_gb': round(upload_disk.total / (1024**3), 2),
                'used_gb': round(upload_disk.used / (1024**3), 2),
                'free_gb': round(upload_disk.free / (1024**3), 2),
                'used_percent': round(upload_disk.used / upload_disk.total * 100, 1)
            },
            'archive_folder': {
                'path': ARCHIVE_FOLDER,
                'files_count': archive_count,
                'total_size_gb': round(archive_size / (1024**3), 2)
            },
            'services': services_status,
            'uptime': get_uptime()
        })
        
    except Exception as e:
        app_logger.error(f"Failed to get system status: {e}")
        return jsonify({'error': str(e)}), 500


def check_service_health(url):
    """检查服务健康状态"""
    try:
        import requests
        response = requests.get(url, timeout=2)
        return response.status_code == 200
    except:
        return False


# 启动时间（用于计算 uptime）
_start_time = time.time()

def get_uptime():
    """获取服务运行时间"""
    uptime_seconds = int(time.time() - _start_time)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    return f"{hours}h {minutes}m"




if __name__ == '__main__':
    app_logger.info("=" * 60)
    app_logger.info("🚀 启动图片翻译服务")
    app_logger.info("=" * 60)
    app_logger.info(f"📍 监听地址: {API_HOST}:{API_PORT}")
    app_logger.info(f" 上传目录: {UPLOAD_FOLDER}")
    app_logger.info(f"📦 归档目录: {ARCHIVE_FOLDER}")  # 🔥 新增
    app_logger.info(f"📊 使用日志: {USAGE_LOG_FOLDER}")  # 🔥 新增
    app_logger.info(f"🔍 OCR 服务: {OCR_SERVICE_URL}")
    app_logger.info(f"🎨 Inpaint 服务: {INPAINT_SERVICE_URL}")

    #app_logger.info(f"🗑️  自动清理: 每2小时")
    app_logger.info("=" * 60)
    
    # 检查字体
    try:
        from services.image_translator import check_fonts_on_startup
        check_fonts_on_startup()
    except Exception as e:
        app_logger.error(f"字体检查失败: {e}")
    
    # 启动服务
    try:
        app.run(
            host=API_HOST,
            port=API_PORT,
            debug=False,
            threaded=True
        )
    except KeyboardInterrupt:
        app_logger.info("\n👋 服务已停止")
    except Exception as e:
        app_logger.error(f"❌ 服务崩溃: {e}")
        log_exception(app_logger, e)
        raise
