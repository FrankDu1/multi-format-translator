"""
配置文件 - 支持环境变量配置，方便本地开发和生产部署
"""
import os
from pathlib import Path
from werkzeug.security import generate_password_hash

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv 不是必需的，可以直接使用系统环境变量

# 基础路径
BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', str(BASE_DIR / 'uploads'))
ARCHIVE_FOLDER = os.getenv('ARCHIVE_FOLDER', str(BASE_DIR / 'archives'))
LOG_FOLDER = os.getenv('LOG_FOLDER', str(BASE_DIR / 'logs'))

# 服务端口配置（本地默认值）
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '5002'))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
OCR_HOST = os.getenv('OCR_HOST', 'localhost')
OCR_PORT = int(os.getenv('OCR_PORT', '8899'))
INPAINT_HOST = os.getenv('INPAINT_HOST', 'localhost')
INPAINT_PORT = int(os.getenv('INPAINT_PORT', '8900'))

# 服务 URL（自动组装或直接指定）
OCR_SERVICE_URL = os.getenv('OCR_SERVICE_URL', f'http://{OCR_HOST}:{OCR_PORT}/ocr')
INPAINT_SERVICE_URL = os.getenv('INPAINT_SERVICE_URL', f'http://{INPAINT_HOST}:{INPAINT_PORT}/inpaint')
USE_INPAINT = os.getenv('USE_INPAINT', 'True').lower() == 'true'

# CORS 允许的源（本地 + 生产）
ALLOWED_ORIGINS_STR = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5001,http://127.0.0.1:5001')
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_STR.split(',')]
if os.getenv('PRODUCTION_URL'):
    ALLOWED_ORIGINS.append(os.getenv('PRODUCTION_URL'))

# 监控认证
MONITOR_USERNAME = os.getenv('MONITOR_USERNAME', 'admin')
MONITOR_PASSWORD_HASH = os.getenv('MONITOR_PASSWORD_HASH', 
    generate_password_hash('change_me_in_production'))  # 默认密码

# 文件大小限制
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 16 * 1024 * 1024))  # 16MB

# ========== AI 总结服务配置 ==========
# 选择 AI 提供商: 'ollama' (本地), 'qwen' (阿里云), 'openai' (OpenAI)
AI_PROVIDER = os.getenv('AI_PROVIDER', 'ollama')

# Ollama 配置（本地部署）
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5:7b')
OLLAMA_TIMEOUT = int(os.getenv('OLLAMA_TIMEOUT', '60'))
OLLAMA_TEMPERATURE = float(os.getenv('OLLAMA_TEMPERATURE', '0.7'))

# 通义千问配置（阿里云 DashScope）
QWEN_API_KEY = os.getenv('QWEN_API_KEY', '')
QWEN_BASE_URL = os.getenv('QWEN_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
QWEN_MODEL = os.getenv('QWEN_MODEL', 'qwen-plus')
QWEN_TIMEOUT = int(os.getenv('QWEN_TIMEOUT', '60'))
QWEN_TEMPERATURE = float(os.getenv('QWEN_TEMPERATURE', '0.7'))

# OpenAI 配置（未来扩展）
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
OPENAI_TIMEOUT = int(os.getenv('OPENAI_TIMEOUT', '60'))
OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))

# 通用配置
SUMMARY_MAX_WORDS = int(os.getenv('SUMMARY_MAX_WORDS', '200'))  # 总结最大字数
