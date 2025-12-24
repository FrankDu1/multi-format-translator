# Inpaint + Render 服务 - 客户端调用指南

## 📡 API 说明

**服务地址**: `http://your-server:29002`

**功能**: 一次请求完成「移除原文字」+「渲染翻译文字」

---

## 🔧 POST /inpaint

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | File | ✅ | 原始图片文件 |
| `boxes` | String (JSON) | ✅ | 文字区域坐标数组 |
| `texts` | String (JSON) | ❌ | 翻译后的文字信息（可选） |

### Boxes 格式

```json
[
  [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],
  [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
]
```

### Texts 格式

```json
[
  {
    "text": "Hello",
    "color": [0, 0, 0],        // RGB 颜色，可选，默认黑色
    "bg_color": [255, 255, 255], // 背景色，可选
    "align": "center"          // 对齐: left/center/right，可选
  },
  {
    "text": "World",
    "color": [255, 0, 0]
  }
]
```

**⚠️ 注意**: `texts` 数组顺序必须与 `boxes` 对应！

---

## 💻 Python 客户端示例

### 完整示例（Inpaint + Render）

```python
import requests
import json
from PIL import Image
from io import BytesIO

def translate_image(image_path, boxes, translations, service_url="http://localhost:29002"):
    """
    完整的图片翻译：移除原文 + 渲染翻译
    
    Args:
        image_path: 图片路径
        boxes: 文字区域坐标
        translations: 翻译文字列表
        service_url: 服务地址
    
    Returns:
        PIL.Image: 处理后的图片
    """
    # 1. 准备 texts 数据
    texts_data = [
        {
            'text': translation,
            'color': [0, 0, 0],  # 黑色文字
            'align': 'center'
        }
        for translation in translations
    ]
    
    # 2. 发送请求
    with open(image_path, 'rb') as f:
        response = requests.post(
            f"{service_url}/inpaint",
            files={'file': ('image.jpg', f, 'image/jpeg')},
            data={
                'boxes': json.dumps(boxes),
                'texts': json.dumps(texts_data)  # 可选参数
            },
            timeout=60
        )
    
    # 3. 处理响应
    if response.status_code == 200:
        result_image = Image.open(BytesIO(response.content))
        return result_image
    else:
        error_info = response.json() if 'application/json' in response.headers.get('content-type', '') else {}
        raise Exception(f"处理失败 ({response.status_code}): {error_info}")


# ============ 使用示例 ============

# 示例 1: 基本用法
boxes = [
    [[100, 50], [200, 50], [200, 80], [100, 80]],
    [[150, 120], [300, 120], [300, 150], [150, 150]]
]

translations = ["Hello", "World"]

result = translate_image('manga.jpg', boxes, translations)
result.save('translated.jpg', quality=95)
print("✓ 翻译完成")


# 示例 2: 自定义样式
boxes = [[[100, 50], [300, 50], [300, 100], [100, 100]]]

texts_data = [{
    'text': '你好世界',
    'color': [255, 0, 0],      # 红色文字
    'bg_color': [255, 255, 0], # 黄色背景
    'align': 'center'
}]

with open('test.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:29002/inpaint',
        files={'file': f},
        data={
            'boxes': json.dumps(boxes),
            'texts': json.dumps(texts_data)
        }
    )

Image.open(BytesIO(response.content)).save('result.jpg')


# 示例 3: 只移除文字（不渲染）
boxes = [[[100, 50], [200, 50], [200, 80], [100, 80]]]

with open('test.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:29002/inpaint',
        files={'file': f},
        data={'boxes': json.dumps(boxes)}
        # 不传 texts 参数，只移除文字
    )

Image.open(BytesIO(response.content)).save('inpainted.jpg')


# 示例 4: 从 OCR + 翻译结果构建请求
ocr_results = [
    {"box": [[10, 20], [100, 20], [100, 40], [10, 40]], "text": "こんにちは"},
    {"box": [[10, 50], [120, 50], [120, 70], [10, 70]], "text": "世界"}
]

# 模拟翻译（实际应调用翻译 API）
translations = ["你好", "世界"]

boxes = [item["box"] for item in ocr_results]
result = translate_image('manga.jpg', boxes, translations)
```

### 错误处理示例

```python
def safe_translate_image(image_path, boxes, translations):
    """带完整错误处理的翻译"""
    try:
        # 验证参数
        if len(boxes) != len(translations):
            raise ValueError(f"boxes 和 translations 数量不匹配: {len(boxes)} vs {len(translations)}")
        
        result = translate_image(image_path, boxes, translations)
        print(f"✓ 成功处理 {len(boxes)} 个文字区域")
        return result
        
    except requests.exceptions.ConnectionError:
        print("✗ 连接失败: 无法连接到服务")
    except requests.exceptions.Timeout:
        print("✗ 请求超时")
    except ValueError as e:
        print(f"✗ 参数错误: {e}")
    except Exception as e:
        print(f"✗ 处理失败: {e}")
    
    return None
```

---

## 🎨 高级功能

### 1. 多种对齐方式

```python
texts_data = [
    {'text': '左对齐', 'align': 'left'},
    {'text': '居中对齐', 'align': 'center'},
    {'text': '右对齐', 'align': 'right'}
]
```

### 2. 自定义颜色

```python
texts_data = [
    {'text': '红色', 'color': [255, 0, 0]},
    {'text': '绿色', 'color': [0, 255, 0]},
    {'text': '蓝色', 'color': [0, 0, 255]}
]
```

### 3. 带背景的文字

```python
texts_data = [{
    'text': '重要提示',
    'color': [255, 255, 255],    # 白色文字
    'bg_color': [255, 0, 0]      # 红色背景
}]
```

---

## ⚠️ 重要注意事项

### 1. 参数必须是 JSON 字符串

```python
# ✅ 正确
data = {
    'boxes': json.dumps(boxes),
    'texts': json.dumps(texts_data)
}

# ❌ 错误
data = {
    'boxes': boxes,  # 不会自动转换！
    'texts': texts_data
}
```

### 2. texts 数组顺序必须与 boxes 对应

```python
boxes = [box1, box2, box3]
texts = [
    {'text': 'translation1'},  # 对应 box1
    {'text': 'translation2'},  # 对应 box2
    {'text': 'translation3'}   # 对应 box3
]
```

### 3. 颜色值必须是 [R, G, B] 数组

```python
# ✅ 正确
'color': [255, 0, 0]

# ❌ 错误
'color': (255, 0, 0)  # 不要用元组
'color': '#FF0000'    # 不要用十六进制
```

### 4. 响应是二进制图片数据

```python
# ✅ 正确
image = Image.open(BytesIO(response.content))

# ❌ 错误
image = Image.open(response.text)  # 会导致错误！
```

---

## 🔍 调试技巧

### 查看服务健康状态

```bash
curl http://localhost:29002/health

# 响应示例:
# {
#   "status": "healthy",
#   "font_available": true,
#   "gpu_available": false
# }
```

### 查看服务日志

```bash
docker logs -f inpaint-service

# 关键日志：
# [20241020_123456] 收到 inpaint 请求
# [20241020_123456] 文件: test.jpg, boxes: 2
# [20241020_123456] 翻译文字: 2 段
# [20241020_123456] ✓ Inpainting 完成
# [20241020_123456] ✓ 渲染文字: 2/2 段
# [20241020_123456] ✓ 完成: 1.234s
```

---

## 📊 性能优化

1. **批量处理**: 使用 `requests.Session()` 复用连接
2. **合理超时**: 大图片需要更长时间，建议 timeout=60
3. **压缩图片**: 输入图片建议 < 5MB

```python
# 使用 Session 提升性能
session = requests.Session()
for image_path in image_list:
    response = session.post(url, files=..., data=...)
```

---

## 🆘 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 文字未渲染 | 未提供 `texts` 参数 | 检查是否传递 `texts` |
| 文字乱码 | 字体不支持中文 | 检查服务日志 `font_available` |
| 文字位置错误 | boxes 和 texts 顺序不对应 | 确保数组顺序一致 |
| 文字太小/太大 | 自动计算失败 | 可以调整 box 大小 |
| `font_available: false` | 容器缺少中文字体 | 重新构建镜像（已包含字体） |

---

**版本**: 2.0.0 | **更新**: 2025-10-20