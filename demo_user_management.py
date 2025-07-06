#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理功能演示脚本
"""

def demo_user_management():
    """演示用户管理功能"""
    print("=" * 50)
    print("废料管理系统 - 用户管理功能演示")
    print("=" * 50)
    
    print("\n📋 功能概述:")
    print("1. 用户权限管理 - 多角色权限系统")
    print("2. 操作日志记录 - 完整的操作审计")
    print("3. 数据备份恢复 - 数据安全保障")
    
    print("\n👥 用户角色:")
    print("• 管理员 (admin) - 拥有所有权限")
    print("  - 用户管理、废料管理、标准管理")
    print("  - 优化计算、数据备份、日志查看")
    print("• 操作员 (operator) - 业务操作权限")
    print("  - 废料管理、标准管理、优化计算")
    print("• 查看者 (viewer) - 只读权限")
    print("  - 废料查看、标准查看、优化查看")
    
    print("\n🔐 默认账户:")
    print("用户名: admin")
    print("密码: admin123")
    print("角色: 管理员")
    
    print("\n📊 主要功能:")
    print("1. 用户管理")
    print("   - 添加、编辑、删除用户")
    print("   - 设置用户角色和权限")
    print("   - 重置用户密码")
    print("   - 启用/禁用用户账户")
    
    print("\n2. 操作日志")
    print("   - 记录所有用户操作")
    print("   - 支持按用户、操作类型筛选")
    print("   - 详细的操作信息记录")
    print("   - 便于审计和问题追踪")
    
    print("\n3. 数据备份")
    print("   - 手动创建数据备份")
    print("   - 自动备份设置")
    print("   - 备份历史管理")
    print("   - 数据恢复功能")
    
    print("\n🚀 使用方法:")
    print("1. 运行主程序: python main.py")
    print("2. 使用管理员账户登录")
    print("3. 点击菜单栏'系统' → '用户管理'")
    print("4. 在用户管理对话框中管理用户和查看日志")
    print("5. 点击菜单栏'系统' → '数据备份'进行数据备份")
    
    print("\n" + "=" * 50)
    print("演示完成！")
    print("=" * 50)

if __name__ == "__main__":
    demo_user_management() 