"""
测试云翻译模式（不需要 torch）
"""
import os
os.environ['USE_CLOUD_TRANSLATE'] = 'true'

print("=" * 50)
print("测试云翻译模式（无 torch 依赖）")
print("=" * 50)

try:
    print("\n1. 测试导入 nllb_translator_pipeline...")
    from services.nllb_translator_pipeline import get_translator
    print("   ✓ 导入成功")
    
    print("\n2. 测试获取翻译器实例...")
    translator = get_translator()
    print("   ✓ 翻译器初始化成功")
    
    print("\n3. 测试简单翻译...")
    result = translator.translate("Hello World", src_lang='en', tgt_lang='zh')
    print(f"   原文: Hello World")
    print(f"   译文: {result}")
    
    print("\n✅ 所有测试通过！云翻译模式工作正常。")
    
except ImportError as e:
    print(f"\n❌ 导入错误: {e}")
    print("这是预期的错误，说明需要重新构建 Docker 镜像")
except Exception as e:
    print(f"\n❌ 运行时错误: {e}")
    import traceback
    traceback.print_exc()
