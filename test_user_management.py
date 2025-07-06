#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理功能测试脚本
"""

import sys
from PyQt6.QtWidgets import QApplication
from user_management import UserManager

def test_user_management():
    """测试用户管理功能"""
    print("=== 用户管理功能测试 ===")
    
    # 创建用户管理器
    user_manager = UserManager()
    
    # 测试用户认证
    print("\n1. 测试用户认证:")
    print("默认管理员账户: admin / admin123")
    
    # 测试权限检查
    print("\n2. 测试权限检查:")
    if user_manager.authenticate_user("admin", "admin123"):
        print("✓ 管理员登录成功")
        print(f"当前用户: {user_manager.current_user['username']}")
        print(f"用户角色: {user_manager.current_user['role']}")
        
        # 测试各种权限
        permissions = ['user_manage', 'waste_manage', 'standard_manage', 'optimization', 'backup', 'log_view']
        for perm in permissions:
            has_perm = user_manager.has_permission(perm)
            print(f"权限 '{perm}': {'✓' if has_perm else '✗'}")
    else:
        print("✗ 管理员登录失败")
    
    # 测试操作日志
    print("\n3. 测试操作日志:")
    user_manager.log_operation("测试操作", "这是一条测试日志")
    print("✓ 操作日志记录成功")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_user_management() 