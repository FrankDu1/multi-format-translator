"""
测试真实 OCR 服务的完整流程
"""
import requests
import base64
import json
from pathlib import Path

def create_test_image():
    """创建一个测试图片（包含中英文）"""
    from PIL import Image, ImageDraw, ImageFont
    
    # 创建测试图片
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("msyh.ttc", 40)  # 微软雅黑
    except:
        font = ImageFont.load_default()
    
    # 绘制中文
    draw.text((10, 10), "这是中文测试", fill='black', font=font)
    # 绘制英文
    draw.text((10, 80), "Hello World", fill='black', font=font)
    # 再绘制中文
    draw.text((10, 150), "图片翻译", fill='black', font=font)
    
    # 保存
    test_dir = Path(__file__).parent / 'test_images'
    test_dir.mkdir(exist_ok=True)
    
    image_path = test_dir / 'test_cn_en.png'
    img.save(image_path)
    
    print(f"✅ 测试图片已创建: {image_path}")
    return str(image_path)


def test_ocr_without_filter():
    """测试1: 不使用语言过滤"""
    print("\n" + "=" * 60)
    print("测试1: OCR 不过滤（原始结果）")
    print("=" * 60)
    
    # 创建测试图片
    image_path = create_test_image()
    
    # 读取图片
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # 发送请求（不过滤）
    payload = {
        'image_base64': image_data,
        'filter_by_language': False  # 🔥 不过滤
    }
    
    print("\n发送请求到 OCR 服务...")
    print(f"  URL: http://localhost:29001/ocr")
    print(f"  过滤: {payload['filter_by_language']}")
    
    try:
        response = requests.post(
            'http://localhost:29001/ocr',
            json=payload,
            timeout=30
        )
        
        print(f"\n响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print(f"✅ OCR 成功")
                print(f"   总文本数: {result.get('total_texts', 0)}")
                print(f"   处理时间: {result.get('processing_time', 0):.3f}秒")
                
                # 显示识别的文本
                ocr_result = result.get('result', [])
                if ocr_result and len(ocr_result) > 0:
                    rec_texts = ocr_result[0].get('res', {}).get('rec_texts', [])
                    print(f"\n识别到的文本:")
                    for i, text in enumerate(rec_texts, 1):
                        print(f"   {i}. '{text}'")
                    
                    return rec_texts
                else:
                    print("⚠️  没有识别到文本")
            else:
                print(f"❌ OCR 失败: {result.get('error')}")
        else:
            print(f"❌ HTTP 错误: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败！")
        print("💡 请确保 OCR 服务已启动:")
        print("   cd c:\\trans_web_app\\ocr")
        print("   python app.py")
        return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


def test_ocr_with_filter():
    """测试2: 使用语言过滤"""
    print("\n" + "=" * 60)
    print("测试2: OCR 过滤中文 (source_lang='zh')")
    print("=" * 60)
    
    # 使用已创建的测试图片
    test_dir = Path(__file__).parent / 'test_images'
    image_path = test_dir / 'test_cn_en.png'
    
    if not image_path.exists():
        print("❌ 测试图片不存在，先运行测试1")
        return
    
    # 读取图片
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # 发送请求（过滤中文）
    payload = {
        'image_base64': image_data,
        'source_lang': 'zh',            # 🔥 指定中文
        'filter_by_language': True      # 🔥 启用过滤
    }
    
    print("\n发送请求到 OCR 服务...")
    print(f"  URL: http://localhost:29001/ocr")
    print(f"  源语言: {payload['source_lang']}")
    print(f"  过滤: {payload['filter_by_language']}")
    
    try:
        response = requests.post(
            'http://localhost:29001/ocr',
            json=payload,
            timeout=30
        )
        
        print(f"\n响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print(f"✅ OCR 成功")
                print(f"   总文本数: {result.get('total_texts', 0)}")
                print(f"   是否过滤: {result.get('filtered', False)}")
                print(f"   处理时间: {result.get('processing_time', 0):.3f}秒")
                
                # 显示过滤后的文本
                ocr_result = result.get('result', [])
                if ocr_result and len(ocr_result) > 0:
                    rec_texts = ocr_result[0].get('res', {}).get('rec_texts', [])
                    print(f"\n过滤后的文本 (只有中文):")
                    if rec_texts:
                        for i, text in enumerate(rec_texts, 1):
                            print(f"   {i}. '{text}'")
                    else:
                        print("   ⚠️  没有保留任何文本！")
                        print("   💡 这就是问题所在！")
                    
                    return rec_texts
                else:
                    print("⚠️  OCR 结果为空")
            else:
                print(f"❌ OCR 失败: {result.get('error')}")
        else:
            print(f"❌ HTTP 错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


def test_ocr_response_structure():
    """测试3: 检查 OCR 响应数据结构"""
    print("\n" + "=" * 60)
    print("测试3: 检查 OCR 响应数据结构")
    print("=" * 60)
    
    # 使用测试图片
    test_dir = Path(__file__).parent / 'test_images'
    image_path = test_dir / 'test_cn_en.png'
    
    if not image_path.exists():
        print("❌ 测试图片不存在")
        return
    
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    payload = {
        'image_base64': image_data,
        'filter_by_language': False
    }
    
    try:
        response = requests.post(
            'http://localhost:29001/ocr',
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n完整响应结构:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            print("\n数据结构分析:")
            print(f"  success: {result.get('success')}")
            print(f"  result 类型: {type(result.get('result'))}")
            
            ocr_result = result.get('result', [])
            if ocr_result:
                print(f"  result 长度: {len(ocr_result)}")
                print(f"  result[0] 类型: {type(ocr_result[0])}")
                print(f"  result[0] 键: {list(ocr_result[0].keys())}")
                
                if 'res' in ocr_result[0]:
                    res = ocr_result[0]['res']
                    print(f"  res 类型: {type(res)}")
                    print(f"  res 键: {list(res.keys())}")
                    
                    if 'rec_texts' in res:
                        print(f"  rec_texts 类型: {type(res['rec_texts'])}")
                        print(f"  rec_texts 长度: {len(res['rec_texts'])}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == '__main__':
    print("=" * 60)
    print("  OCR 服务集成测试")
    print("=" * 60)
    
    # 运行测试
    texts_without_filter = test_ocr_without_filter()
    texts_with_filter = test_ocr_with_filter()
    test_ocr_response_structure()
    
    # 对比结果
    if texts_without_filter and texts_with_filter is not None:
        print("\n" + "=" * 60)
        print("对比结果:")
        print("=" * 60)
        print(f"不过滤: {len(texts_without_filter)} 个文本")
        print(f"过滤后: {len(texts_with_filter)} 个文本")
        
        if len(texts_with_filter) == 0:
            print("\n❌ 问题确认: 语言过滤把所有文本都过滤掉了！")
            print("💡 需要检查 app.py 中的 filter_ocr_by_language_v2 函数")
        elif len(texts_with_filter) < len(texts_without_filter):
            print(f"\n✅ 过滤正常: 过滤掉 {len(texts_without_filter) - len(texts_with_filter)} 个非中文文本")
        else:
            print("\n⚠️  异常: 过滤后文本数量没有减少")
    
    print("\n" + "=" * 60)
    print("  测试完成")
    print("=" * 60)