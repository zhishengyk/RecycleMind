#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用户管理对话框
"""

import sys
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QLabel

def test_simple_dialog():
    """测试简单对话框"""
    app = QApplication(sys.argv)
    
    dialog = QDialog()
    dialog.setWindowTitle("测试对话框")
    dialog.resize(300, 200)
    
    layout = QVBoxLayout(dialog)
    layout.addWidget(QLabel("这是一个测试对话框"))
    
    btn = QPushButton("关闭")
    btn.clicked.connect(dialog.accept)
    layout.addWidget(btn)
    
    dialog.exec()
    print("测试对话框运行成功！")

def test_user_management_import():
    """测试用户管理模块导入"""
    try:
        from user_management import UserManager
        print("✓ UserManager 导入成功")
        
        user_manager = UserManager()
        print("✓ UserManager 创建成功")
        
        return True
    except Exception as e:
        print(f"✗ UserManager 导入失败: {e}")
        return False

def test_user_management_dialog():
    """测试用户管理对话框"""
    try:
        from user_management import UserManagementDialog
        print("✓ UserManagementDialog 导入成功")
        
        app = QApplication(sys.argv)
        dialog = UserManagementDialog(None)
        print("✓ UserManagementDialog 创建成功")
        
        return True
    except Exception as e:
        print(f"✗ UserManagementDialog 导入失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("用户管理对话框测试")
    print("=" * 50)
    
    # 测试基本对话框
    print("1. 测试基本对话框...")
    test_simple_dialog()
    
    # 测试用户管理模块导入
    print("\n2. 测试用户管理模块导入...")
    um_ok = test_user_management_import()
    
    # 测试用户管理对话框
    print("\n3. 测试用户管理对话框...")
    dialog_ok = test_user_management_dialog()
    
    print("\n" + "=" * 50)
    if um_ok and dialog_ok:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败")
    print("=" * 50)

if __name__ == "__main__":
    main() 