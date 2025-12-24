"""
日志配置模块
支持文件日志、控制台日志和旋转日志
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 日志目录（改为 translator_api/logs）
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# 日志级别配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# 日志格式
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def setup_logger(name: str, log_file: str = None, level: str = None) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_file: 日志文件名（可选，默认使用 name.log）
        level: 日志级别（可选，默认使用环境变量 LOG_LEVEL 或 INFO）
    
    Returns:
        配置好的 Logger 对象
    """
    logger = logging.getLogger(name)
    
    # 如果已经配置过，直接返回
    if logger.handlers:
        return logger
    
    # 设置日志级别
    log_level = getattr(logging, (level or LOG_LEVEL).upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（带日志旋转）
    if log_file is None:
        log_file = f"{name}.log"
    
    log_path = os.path.join(LOG_DIR, log_file)
    
    # 旋转日志：每个文件最大 10MB，保留 5 个备份
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # 防止日志传播到根日志记录器
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器（简化接口）
    
    Args:
        name: 日志记录器名称
    
    Returns:
        Logger 对象
    """
    return setup_logger(name)


# 预配置的日志记录器
app_logger = setup_logger('app', 'app.log')
ocr_logger = setup_logger('ocr', 'ocr.log')
translate_logger = setup_logger('translate', 'translate.log')
inpaint_logger = setup_logger('inpaint', 'inpaint.log')
api_logger = setup_logger('api', 'api.log')


def log_request(logger: logging.Logger, method: str, url: str, **kwargs):
    """记录 HTTP 请求"""
    logger.info(f"Request: {method} {url}")
    if kwargs:
        logger.debug(f"  Params: {kwargs}")


def log_response(logger: logging.Logger, status_code: int, response_time: float = None):
    """记录 HTTP 响应"""
    msg = f"Response: {status_code}"
    if response_time:
        msg += f" ({response_time:.2f}s)"
    
    if status_code >= 500:
        logger.error(msg)
    elif status_code >= 400:
        logger.warning(msg)
    else:
        logger.info(msg)


def log_exception(logger: logging.Logger, exc: Exception, context: str = None):
    """记录异常信息"""
    if context:
        logger.error(f"Exception in {context}: {exc}", exc_info=True)
    else:
        logger.error(f"Exception: {exc}", exc_info=True)


# 日志装饰器
def log_function_call(logger: logging.Logger = None):
    """
    函数调用日志装饰器
    
    Example:
        @log_function_call(logger)
        def my_function(arg1, arg2):
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)
            
            logger.debug(f"Calling {func.__name__}(args={args}, kwargs={kwargs})")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} completed successfully")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} failed: {e}", exc_info=True)
                raise
        return wrapper
    return decorator


if __name__ == "__main__":
    # 测试日志系统
    test_logger = setup_logger('test')
    
    test_logger.debug("这是一条调试信息")
    test_logger.info("这是一条信息")
    test_logger.warning("这是一条警告")
    test_logger.error("这是一条错误")
    
    print(f"\n日志文件保存在: {LOG_DIR}")
    print(f"日志级别: {LOG_LEVEL}")
