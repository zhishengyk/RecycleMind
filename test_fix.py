#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的程序
"""

import sys
import traceback

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        print("✓ PyQt6 导入成功")
    except Exception as e:
        print(f"✗ PyQt6 导入失败: {e}")
        return False
    
    try:
        from login import LoginDialog
        print("✓ login.py 导入成功")
    except Exception as e:
        print(f"✗ login.py 导入失败: {e}")
        return False
    
    try:
        from waste import WasteManager
        print("✓ waste.py 导入成功")
    except Exception as e:
        print(f"✗ waste.py 导入失败: {e}")
        return False
    
    try:
        from user_management import UserManager
        print("✓ user_management.py 导入成功")
    except Exception as e:
        print(f"✗ user_management.py 导入失败: {e}")
        return False
    
    return True

def test_database_connection():
    """测试数据库连接"""
    print("\n测试数据库连接...")
    
    try:
        from db import get_db_conn
        conn = get_db_conn()
        print("✓ 数据库连接成功")
        conn.close()
        return True
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        print("  这可能是正常的，如果数据库服务器未运行")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("废料管理系统 - 修复测试")
    print("=" * 50)
    
    # 测试导入
    if not test_imports():
        print("\n❌ 模块导入测试失败")
        return False
    
    # 测试数据库连接
    db_ok = test_database_connection()
    
    print("\n" + "=" * 50)
    if db_ok:
        print("✅ 所有测试通过！")
        print("建议运行: python main.py")
    else:
        print("⚠️  数据库连接失败，但程序仍可运行")
        print("建议运行: python main_simple.py")
    
    print("=" * 50)
    return True

if __name__ == "__main__":
    main() 