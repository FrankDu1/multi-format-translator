#!/usr/bin/env python3
"""
生成监控密码哈希值
用于配置 MONITOR_PASSWORD_HASH 环境变量
"""
from werkzeug.security import generate_password_hash
import getpass
import sys

def main():
    print("=" * 60)
    print("监控密码哈希生成工具")
    print("=" * 60)
    print()
    
    try:
        # 获取密码输入
        password = getpass.getpass('请输入监控密码: ')
        
        if not password:
            print("❌ 密码不能为空")
            sys.exit(1)
        
        # 确认密码
        password_confirm = getpass.getpass('请再次输入密码: ')
        
        if password != password_confirm:
            print("❌ 两次输入的密码不一致")
            sys.exit(1)
        
        # 生成哈希
        hash_value = generate_password_hash(password)
        
        # 输出结果
        print()
        print("=" * 60)
        print("✅ 密码哈希生成成功！")
        print("=" * 60)
        print()
        print("请将以下内容添加到 .env 文件中：")
        print()
        print(f"MONITOR_PASSWORD_HASH={hash_value}")
        print()
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n❌ 操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
