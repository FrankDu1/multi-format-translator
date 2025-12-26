"""
测试通义千问 API Key 是否有效
"""
import requests
from config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL

def test_qwen_api():
    """测试 Qwen API"""
    
    print("=" * 50)
    print("测试通义千问 API")
    print("=" * 50)
    print(f"API Key: {QWEN_API_KEY[:15]}..." if QWEN_API_KEY else "未设置")
    print(f"Base URL: {QWEN_BASE_URL}")
    print(f"Model: {QWEN_MODEL}")
    print("=" * 50)
    print()
    
    if not QWEN_API_KEY:
        print("❌ 错误: QWEN_API_KEY 未设置")
        return
    
    # 构建请求
    headers = {
        "Authorization": f"Bearer {QWEN_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": QWEN_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "你是一个测试助手"
            },
            {
                "role": "user",
                "content": "请回复：测试成功"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    print("📡 发送请求到 Qwen API...")
    print()
    
    try:
        response = requests.post(
            f"{QWEN_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            print("✅ API Key 有效！")
            print()
            print("返回内容:")
            print("-" * 50)
            print(content)
            print("-" * 50)
            print()
            print("完整响应:")
            print(response.json())
            
        elif response.status_code == 401:
            print("❌ 认证失败: API Key 无效或已过期")
            print()
            print("请检查:")
            print("1. API Key 是否正确")
            print("2. 是否在阿里云控制台启用了该 Key")
            print("3. 账户是否有余额")
            print()
            print("错误详情:")
            print(response.text)
            
        else:
            print(f"⚠️ 请求失败 (状态码: {response.status_code})")
            print()
            print("响应内容:")
            print(response.text)
            
    except requests.Timeout:
        print("❌ 请求超时")
        print("请检查网络连接")
        
    except requests.RequestException as e:
        print(f"❌ 请求失败: {str(e)}")
        
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")


if __name__ == "__main__":
    test_qwen_api()
