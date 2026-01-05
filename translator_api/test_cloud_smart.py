"""
测试云端智能分组翻译功能
"""
import os
import sys

# 添加路径
sys.path.insert(0, os.path.dirname(__file__))

from services.nllb_translator_pipeline import get_translator
from logger_config import app_logger

def test_cloud_smart_translation():
    """测试云端智能翻译"""
    
    print("=" * 80)
    print("测试云端智能分组翻译")
    print("=" * 80)
    
    # 确保启用云端翻译
    os.environ['USE_CLOUD_TRANSLATE'] = 'true'
    
    translator = get_translator()
    
    # 测试数据：混合短文本和长文本
    test_texts = [
        # 短文本（<30字符）- 应该单独翻译
        "Name",
        "Age", 
        "City",
        "• Item 1",
        "• Item 2",
        
        # 长文本（>=30字符）- 应该智能合并
        "This is a longer paragraph that contains more than thirty characters.",
        "Another long sentence that should be grouped together for efficient translation.",
        "Machine translation has made significant progress in recent years.",
        
        # 再来几个短文本
        "Total",
        "Summary",
        
        # 再来一个长文本
        "The quick brown fox jumps over the lazy dog. This is a classic pangram used for testing."
    ]
    
    print(f"\n测试文本数量: {len(test_texts)}")
    print("\n原文:")
    for i, text in enumerate(test_texts, 1):
        print(f"  {i}. [{len(text)}字符] {text}")
    
    print("\n开始翻译...")
    print("-" * 80)
    
    # 执行翻译
    translated = translator.translate_batch(
        test_texts,
        src_lang='en',
        tgt_lang='zh',
        batch_size=4
    )
    
    print("-" * 80)
    print("\n翻译结果:")
    for i, (orig, trans) in enumerate(zip(test_texts, translated), 1):
        print(f"  {i}. {orig}")
        print(f"     → {trans}")
        print()
    
    # 验证结果
    print("=" * 80)
    print("验证:")
    success_count = sum(1 for t in translated if t and t.strip())
    print(f"  成功翻译: {success_count}/{len(test_texts)}")
    print(f"  成功率: {success_count/len(test_texts)*100:.1f}%")
    
    # 检查位置对应
    all_matched = len(translated) == len(test_texts)
    print(f"  位置对应: {'✅ 正确' if all_matched else '❌ 错误'}")
    
    print("=" * 80)


if __name__ == "__main__":
    test_cloud_smart_translation()
