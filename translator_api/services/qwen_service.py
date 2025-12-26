"""
通义千问 (Qwen) AI 总结服务
支持阿里云 DashScope API（OpenAI 兼容格式）
"""
import logging
import requests
from typing import Dict
from config import (
    QWEN_API_KEY,
    QWEN_BASE_URL,
    QWEN_MODEL,
    QWEN_TIMEOUT,
    QWEN_TEMPERATURE,
    SUMMARY_MAX_WORDS
)

logger = logging.getLogger(__name__)


class QwenService:
    """通义千问 AI 总结服务（OpenAI 兼容格式）"""
    
    def __init__(self):
        self.api_key = QWEN_API_KEY
        self.base_url = QWEN_BASE_URL
        self.model = QWEN_MODEL
        self.timeout = QWEN_TIMEOUT
        self.temperature = QWEN_TEMPERATURE
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
        检查 API 服务是否可用
        
        Returns:
            True 如果服务可用，否则 False
        """
        # 检查必要的配置
        if not self.api_key or not self.base_url:
            logger.warning("Qwen API 配置不完整")
            return False
        
        try:
            # 简单的健康检查：发送一个最小请求
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 5
                },
                timeout=5
            )
            return response.status_code in [200, 400]  # 400也说明API可达
        except Exception as e:
            logger.warning(f"Qwen API 健康检查失败: {str(e)}")
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
        
        # 检查配置
        if not self.api_key:
            return {
                "success": False,
                "summary": None,
                "error": "AI总结服务未配置 API Key"
            }
        
        # 检查服务可用性（可选，避免每次都检查）
        # if not self.check_health():
        #     return {
        #         "success": False,
        #         "summary": None,
        #         "error": "AI总结服务暂时不可用，请稍后再试 😊"
        #     }
        
        try:
            # 构建 OpenAI 兼容格式的请求
            prompt = self._get_summary_prompt(text, target_language)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的文本总结助手，擅长提炼核心信息。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_words * 2  # 预留空间
            }
            
            logger.info(f"正在调用 Qwen API 生成总结 (模型: {self.model}, 语言: {target_language})")
            
            # 调用 API
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 提取总结内容（OpenAI 格式）
            summary = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            
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
            logger.error(f"Qwen API 请求超时 (timeout={self.timeout}s)")
            return {
                "success": False,
                "summary": None,
                "error": "AI总结生成超时，请稍后重试 ⏱️"
            }
        
        except requests.RequestException as e:
            logger.error(f"Qwen API 请求失败: {str(e)}")
            error_msg = str(e)
            if "401" in error_msg or "403" in error_msg:
                return {
                    "success": False,
                    "summary": None,
                    "error": "AI总结服务认证失败，请检查 API Key 🔑"
                }
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
qwen_service = QwenService()
