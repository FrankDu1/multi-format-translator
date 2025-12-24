import requests
import base64
import os

class OCRResult:
    def __init__(self, text: str, box: list):
        self.text = text
        self.box = box

def call_remote_ocr(image_path: str, ocr_url: str = None) -> list:
    """
    调用远程OCR服务，返回识别结果列表，每项包含text和box
    
    OCR服务接受JSON格式:
    {
        "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."        "auto_rotate": false
    }
    """
    if ocr_url is None:
        ocr_url = os.getenv('OCR_SERVICE_URL', 'http://localhost:8899/ocr')    }
    或
    {
        "url": "https://example.com/image.jpg"
    }
    """
    # 读取图片并转换为base64
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    # 转换为base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # 确定图片格式
    image_format = 'jpeg'
    if image_path.lower().endswith('.png'):
        image_format = 'png'
    elif image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
        image_format = 'jpeg'
    elif image_path.lower().endswith('.webp'):
        image_format = 'webp'
    
    # 构建完整的base64字符串（包含data URI scheme）
    image_base64_full = f"data:image/{image_format};base64,{image_base64}"
    
    # 发送JSON请求
    headers = {'Content-Type': 'application/json'}
    payload = {'image_base64': image_base64_full}
    
    resp = requests.post(ocr_url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    
    data = resp.json()
    results = []
    
    # 解析返回数据
    # 响应格式: {"success": true, "result": [{"res": {"rec_texts": [...], "rec_polys": [...]}}]}
    if not data.get('success'):
        print(f"    ⚠️  OCR 服务返回失败")
        return results
    
    result_list = data.get('result', [])
    if not result_list:
        return results
    
    # 获取第一个结果（通常只有一个）
    res_data = result_list[0].get('res', {})
    
    # 获取识别的文字和坐标
    rec_texts = res_data.get('rec_texts', [])
    rec_polys = res_data.get('rec_polys', [])  # 多边形坐标 [[[x1,y1], [x2,y2], ...], ...]
    
    # 组合结果
    for text, poly in zip(rec_texts, rec_polys):
        results.append(OCRResult(text, poly))
    
    return results
