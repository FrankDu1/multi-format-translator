"""
Ollama AI 总结服务
"""
import logging
import requests
from typing import Optional, Dict
from config import (
    OLLAMA_BASE_URL, 
    OLLAMA_MODEL, 
    OLLAMA_TIMEOUT,
    OLLAMA_TEMPERATURE,
    SUMMARY_MAX_WORDS
)

logger = logging.getLogger(__name__)


class OllamaService:
    """Ollama AI 总结服务"""
    
    def __init__(self):
        self.base_url = OLLAMA_BASE_URL
        self.model = OLLAMA_MODEL
        self.timeout = OLLAMA_TIMEOUT
        self.temperature = OLLAMA_TEMPERATURE
        self.max_words = SUMMARY_MAX_WORDS
    
    def _get_summary_prompt(self, text: str, language: str) -> str:
        """
        根据目标语言生成总结提示词
        
        Args:
            text: 要总结的文本
            language: 目标语言代码 (zh, en, de 等)
        
        Returns:
            提示词字符串
        """
        prompts = {
            "zh": f"""请用简洁的中文总结以下内容，字数控制在{self.max_words}字以内。
使用要点形式，突出核心信息：

{text}

总结：""",
            "en": f"""Please summarize the following content in concise English, within {self.max_words} words.
Use bullet points to highlight key information:

{text}

Summary:""",
            "de": f"""Bitte fassen Sie den folgenden Inhalt auf Deutsch zusammen, innerhalb von {self.max_words} Wörtern.
Verwenden Sie Aufzählungspunkte, um wichtige Informationen hervorzuheben:

{text}

Zusammenfassung:"""
        }
        
        # 如果语言不在字典中，默认使用中文
        return prompts.get(language, prompts["zh"])
    
    def check_health(self) -> bool:
        """
        检查 Ollama 服务是否可用
        
        Returns:
            True 如果服务可用，否则 False
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama 服务健康检查失败: {str(e)}")
            return False
    
    def generate_summary(self, text: str, target_language: str) -> Dict[str, any]:
        """
        生成文本总结
        
        Args:
            text: 要总结的文本
            target_language: 目标语言代码
        
        Returns:
            包含总结结果的字典:
            {
                "success": bool,
                "summary": str,  # 总结内容
                "error": str     # 错误信息(如果失败)
            }
        """
        # 检查输入
        if not text or not text.strip():
            return {
                "success": False,
                "summary": None,
                "error": "文本内容为空"
            }
        
        # 检查服务可用性
        if not self.check_health():
            return {
                "success": False,
                "summary": None,
                "error": "AI总结服务暂时不可用，请稍后再试 😊"
            }
        
        try:
            # 构建请求
            prompt = self._get_summary_prompt(text, target_language)
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_words * 2  # 预留空间
                }
            }
            
            logger.info(f"正在调用 Ollama 生成总结 (模型: {self.model}, 语言: {target_language})")
            
            # 调用 API
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 提取总结内容
            summary = result.get("response", "").strip()
            
            if not summary:
                return {
                    "success": False,
                    "summary": None,
                    "error": "AI未能生成有效的总结"
                }
            
            logger.info(f"总结生成成功，长度: {len(summary)} 字符")
            
            return {
                "success": True,
                "summary": summary,
                "error": None
            }
        
        except requests.Timeout:
            logger.error(f"Ollama 请求超时 (timeout={self.timeout}s)")
            return {
                "success": False,
                "summary": None,
                "error": "AI总结生成超时，请稍后重试 ⏱️"
            }
        
        except requests.RequestException as e:
            logger.error(f"Ollama 请求失败: {str(e)}")
            return {
                "success": False,
                "summary": None,
                "error": "AI总结服务连接失败，请检查网络 🔌"
            }
        
        except Exception as e:
            logger.error(f"生成总结时发生未知错误: {str(e)}")
            return {
                "success": False,
                "summary": None,
                "error": "生成总结时发生错误，请稍后重试 🔧"
            }


# 创建全局实例
ollama_service = OllamaService()