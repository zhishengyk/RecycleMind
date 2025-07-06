#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的用户管理对话框
用于测试基本功能，不依赖数据库
"""

import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, 
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem, 
    QMessageBox, QLabel, QTextEdit, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt

class SimpleUserManagementDialog(QDialog):
    """简化的用户管理对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("用户管理 - 简化版")
        self.setMinimumSize(600, 400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 创建标签页
        tabs = QTabWidget()
        
        # 用户管理标签页
        user_tab = QWidget()
        user_layout = QVBoxLayout(user_tab)
        
        # 用户列表
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels([
            "ID", "用户名", "角色", "邮箱"
        ])
        user_layout.addWidget(self.user_table)
        
        # 用户操作按钮
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("添加用户")
        self.btn_edit = QPushButton("编辑用户")
        self.btn_delete = QPushButton("删除用户")
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        
        user_layout.addLayout(btn_layout)
        
        # 连接信号
        self.btn_add.clicked.connect(self.add_user)
        self.btn_edit.clicked.connect(self.edit_user)
        self.btn_delete.clicked.connect(self.delete_user)
        
        tabs.addTab(user_tab, "用户管理")
        
        # 操作日志标签页
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        
        # 日志说明
        info_label = QLabel("操作日志功能需要数据库支持")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        log_layout.addWidget(info_label)
        
        tabs.addTab(log_tab, "操作日志")
        
        # 数据备份标签页
        backup_tab = QWidget()
        backup_layout = QVBoxLayout(backup_tab)
        
        # 备份说明
        backup_info_label = QLabel("数据备份功能需要数据库支持")
        backup_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        backup_layout.addWidget(backup_info_label)
        
        tabs.addTab(backup_tab, "数据备份")
        
        layout.addWidget(tabs)
        
        # 加载默认用户数据
        self.load_default_users()
    
    def load_default_users(self):
        """加载默认用户数据"""
        # 模拟用户数据
        users = [
            (1, "admin", "管理员", "admin@recyclemind.com"),
            (2, "operator", "操作员", "operator@recyclemind.com"),
            (3, "viewer", "查看者", "viewer@recyclemind.com")
        ]
        
        self.user_table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.user_table.setItem(row, 0, QTableWidgetItem(str(user[0])))
            self.user_table.setItem(row, 1, QTableWidgetItem(user[1]))
            self.user_table.setItem(row, 2, QTableWidgetItem(user[2]))
            self.user_table.setItem(row, 3, QTableWidgetItem(user[3]))
    
    def add_user(self):
        """添加用户"""
        QMessageBox.information(self, "提示", "添加用户功能需要数据库支持")
    
    def edit_user(self):
        """编辑用户"""
        current_row = self.user_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要编辑的用户！")
            return
        
        username = self.user_table.item(current_row, 1).text()
        QMessageBox.information(self, "提示", f"编辑用户 {username} 功能需要数据库支持")
    
    def delete_user(self):
        """删除用户"""
        current_row = self.user_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要删除的用户！")
            return
        
        username = self.user_table.item(current_row, 1).text()
        if username == 'admin':
            QMessageBox.warning(self, "警告", "不能删除管理员账户！")
            return
        
        QMessageBox.information(self, "提示", f"删除用户 {username} 功能需要数据库支持")

def main():
    """测试函数"""
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = SimpleUserManagementDialog()
    dialog.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 