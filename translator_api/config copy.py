"""
配置文件
"""
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# 基础路径
BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', str(BASE_DIR / 'uploads'))
ARCHIVE_FOLDER = os.getenv('ARCHIVE_FOLDER', str(BASE_DIR / 'archives'))
LOG_FOLDER = os.getenv('LOG_FOLDER', str(BASE_DIR / 'logs'))

# 服务端口配置（本地默认值）
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '5002'))
OCR_HOST = os.getenv('OCR_HOST', 'localhost')
OCR_PORT = int(os.getenv('OCR_PORT', '8899'))
INPAINT_HOST = os.getenv('INPAINT_HOST', 'localhost')
INPAINT_PORT = int(os.getenv('INPAINT_PORT', '8900'))

# 服务 URL（自动组装）
OCR_SERVICE_URL = os.getenv('OCR_SERVICE_URL', f'http://{OCR_HOST}:{OCR_PORT}')
INPAINT_SERVICE_URL = os.getenv('INPAINT_SERVICE_URL', f'http://{INPAINT_HOST}:{INPAINT_PORT}')

# CORS 允许的源（本地 + 生产）
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5001,http://127.0.0.1:5001').split(',')
if os.getenv('PRODUCTION_URL'):
    ALLOWED_ORIGINS.append(os.getenv('PRODUCTION_URL'))

# 监控认证
MONITOR_USERNAME = os.getenv('MONITOR_USERNAME', 'admin')
MONITOR_PASSWORD_HASH = os.getenv('MONITOR_PASSWORD_HASH', 
    generate_password_hash('change_me_in_production'))  # 默认密码

# 文件大小限制
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 16 * 1024 * 1024))  # 16MB

# AI 配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')

# Flask 配置
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "29003"))  # 默认端口改为 29003
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

# 🔥 监控认证配置
MONITOR_USERNAME = os.getenv("MONITOR_USERNAME", "admin")
MONITOR_PASSWORD_HASH = os.getenv(
    "MONITOR_PASSWORD_HASH",
    # 🔥 如果 .env 中没有，使用这个默认值（对应密码 "Welcome123456"）
    "pbkdf2:sha256:600000$P5ujlDw2lCNwiGdO$96edb9ccc0125a9278998cf07049068c669bf245f6bcc403908ae411a1492d15"
)
# 文件上传配置
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 10MB

# 外部服务 URL
#OCR_SERVICE_URL = os.getenv("OCR_SERVICE_URL", "http://47.97.97.198:29001/ocr")
#INPAINT_SERVICE_URL = os.getenv("INPAINT_SERVICE_URL", "http://47.97.97.198:29002/inpaint")

OCR_SERVICE_URL = os.getenv("OCR_SERVICE_URL", "http://localhost:29001/ocr")
INPAINT_SERVICE_URL = os.getenv("INPAINT_SERVICE_URL", "http://localhost:29002/inpaint")

USE_INPAINT = os.getenv("USE_INPAINT", "True").lower() == "true"


# 🔥 新增: Ollama AI 总结配置
#OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "https://chat.offerupup.cn/omodels")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:8b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "30"))  # 超时时间(秒)
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.3"))  # 温度(0-1,越低越确定)

# AI 总结配置
SUMMARY_MAX_WORDS = int(os.getenv("SUMMARY_MAX_WORDS", "150"))  # 总结最大字数

# GPU 配置 - 针对共享 GPU 的优化
GPU_MEMORY_LIMIT_GB = float(os.getenv("GPU_MEMORY_LIMIT_GB", "5.0"))  # 提高到 5GB（留 6GB 给其他程序）
GPU_DEVICE_ID = int(os.getenv("GPU_DEVICE_ID", "0"))  # GPU 设备 ID
USE_GPU = os.getenv("USE_GPU", "True").lower() == "true"  # 是否使用 GPU
GPU_MEMORY_FRACTION = float(os.getenv("GPU_MEMORY_FRACTION", "0.7"))  # 降到 70%，避免和其他程序冲突

# NLLB 翻译器配置
NLLB_MODEL_NAME = os.getenv("NLLB_MODEL_NAME", "facebook/nllb-200-distilled-600M")
NLLB_BATCH_SIZE = int(os.getenv("NLLB_BATCH_SIZE", "16"))  # 【建议】从6改为16
NLLB_MAX_LENGTH = int(os.getenv("NLLB_MAX_LENGTH", "200"))
NLLB_NUM_BEAMS = int(os.getenv("NLLB_NUM_BEAMS", "4"))
NLLB_USE_FP16 = os.getenv("NLLB_USE_FP16", "True").lower() == "true"

# PyTorch CUDA 配置
PYTORCH_CUDA_ALLOC_CONF = os.getenv("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "app.log")
