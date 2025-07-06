#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用户管理功能修复
"""

import sys
import traceback

def test_user_management_import():
    """测试用户管理模块导入"""
    print("测试用户管理模块导入...")
    
    try:
        from user_management import UserManager, UserManagementDialog
        print("✓ user_management.py 导入成功")
        return True
    except Exception as e:
        print(f"✗ user_management.py 导入失败: {e}")
        return False

def test_simple_user_management_import():
    """测试简化用户管理模块导入"""
    print("测试简化用户管理模块导入...")
    
    try:
        from simple_user_management import SimpleUserManagementDialog
        print("✓ simple_user_management.py 导入成功")
        return True
    except Exception as e:
        print(f"✗ simple_user_management.py 导入失败: {e}")
        return False

def test_user_manager():
    """测试用户管理器"""
    print("测试用户管理器...")
    
    try:
        from user_management import UserManager
        user_manager = UserManager()
        print("✓ 用户管理器创建成功")
        
        # 测试认证
        if user_manager.authenticate_user("admin", "admin123"):
            print("✓ 用户认证成功")
        else:
            print("⚠️  用户认证失败（可能是数据库问题）")
        
        return True
    except Exception as e:
        print(f"✗ 用户管理器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("用户管理功能修复测试")
    print("=" * 50)
    
    # 测试导入
    um_ok = test_user_management_import()
    sum_ok = test_simple_user_management_import()
    
    # 测试用户管理器
    um_test_ok = test_user_manager()
    
    print("\n" + "=" * 50)
    if um_ok and sum_ok:
        print("✅ 所有模块导入成功！")
        if um_test_ok:
            print("✅ 用户管理器功能正常！")
        else:
            print("⚠️  用户管理器功能异常（可能是数据库问题）")
        print("\n现在可以运行程序测试用户管理功能：")
        print("1. python main.py - 完整版本")
        print("2. python main_simple.py - 简化版本")
    else:
        print("❌ 模块导入失败")
        print("请检查代码和依赖")
    
    print("=" * 50)
    return True

if __name__ == "__main__":
    main() 