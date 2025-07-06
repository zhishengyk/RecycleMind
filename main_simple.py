#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版废料管理系统主程序
用于测试基本功能，不依赖数据库
"""

import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from waste import WasteManager

class SimpleLoginDialog(QDialog):
    """简化的登录对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("登录 - 废料管理系统")
        self.resize(350, 200)
        
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("废料管理系统")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 登录表单
        form_layout = QFormLayout()
        self.username_edit = QLineEdit(self)
        self.password_edit = QLineEdit(self)
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("用户名", self.username_edit)
        form_layout.addRow("密码", self.password_edit)
        layout.addLayout(form_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        self.btn_login = QPushButton("登录", self)
        self.btn_cancel = QPushButton("取消", self)
        btn_layout.addWidget(self.btn_login)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)
        
        self.btn_login.clicked.connect(self.try_login)
        self.btn_cancel.clicked.connect(self.reject)
        self.login_success = False
        
        # 设置默认值
        self.username_edit.setText("admin")
        self.password_edit.setText("admin123")

    def try_login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        
        if not username or not password:
            QMessageBox.warning(self, "登录失败", "用户名和密码不能为空")
            return
        
        # 简化的认证逻辑
        if username == "admin" and password == "admin123":
            self.login_success = True
            self.username_edit.clear()
            self.password_edit.clear()
            print(f"用户 {username} 登录成功")
            self.accept()
        else:
            QMessageBox.warning(self, "登录失败", "用户名或密码错误")

def main():
    """主函数"""
    try:
        app = QApplication(sys.argv)
        
        # 显示登录对话框
        login = SimpleLoginDialog()
        if login.exec() == QDialog.DialogCode.Accepted and login.login_success:
            # 创建主窗口（不传递用户管理器）
            window = WasteManager()
            window.show()
            print("主窗口已显示")
            sys.exit(app.exec())
        else:
            print("用户取消登录")
            sys.exit(0)
            
    except Exception as e:
        print(f"程序启动错误: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        
        # 显示错误对话框
        try:
            error_app = QApplication(sys.argv)
            QMessageBox.critical(None, "程序错误", 
                               f"程序启动时发生错误:\n{str(e)}\n\n请检查系统配置。")
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main() 