#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import zipfile
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QTabWidget, QVBoxLayout, QHBoxLayout, 
                             QTableWidget, QTableWidgetItem, QPushButton, 
                             QMessageBox, QFileDialog, QFormLayout, QLineEdit, 
                             QComboBox, QLabel, QTextEdit, QHeaderView, QWidget)
from PyQt6.QtCore import Qt, QTimer
from db import get_db_conn

class UserManager:
    """用户管理器"""
    
    def __init__(self):
        self.current_user = None
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        try:
            conn = get_db_conn()
            with conn.cursor() as cursor:
                # 创建用户表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(100) NOT NULL,
                        role ENUM('admin', 'operator', 'viewer') DEFAULT 'viewer',
                        email VARCHAR(100),
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建操作日志表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS operation_logs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        operation VARCHAR(100) NOT NULL,
                        details TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """)
                
                # 创建备份日志表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS backup_logs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        backup_name VARCHAR(100) NOT NULL,
                        backup_path VARCHAR(500) NOT NULL,
                        backup_size BIGINT,
                        created_by INT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (created_by) REFERENCES users(id)
                    )
                """)
                
                # 检查是否有管理员账户
                cursor.execute("SELECT 1 FROM users WHERE username = 'admin'")
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO users (username, password, role, email)
                        VALUES ('admin', 'admin123', 'admin', 'admin@example.com')
                    """)
                
                conn.commit()
            conn.close()
        except Exception as e:
            print(f"数据库初始化错误: {e}")
    
    def authenticate_user(self, username, password):
        """用户认证"""
        try:
            conn = get_db_conn()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, username, role, email 
                    FROM users 
                    WHERE username = %s AND password = %s AND is_active = TRUE
                """, (username, password))
                user_data = cursor.fetchone()
            conn.close()
            
            if user_data:
                self.current_user = {
                    'id': user_data[0],
                    'username': user_data[1],
                    'role': user_data[2],
                    'email': user_data[3]
                }
                return True
            return False
        except Exception as e:
            print(f"用户认证错误: {e}")
            return False
    
    def has_permission(self, permission):
        """检查用户权限"""
        if not self.current_user:
            return False
        
        role = self.current_user['role']
        if role == 'admin':
            return True
        elif role == 'operator':
            return permission in ['view', 'edit', 'add', 'delete']
        elif role == 'viewer':
            return permission == 'view'
        return False
    
    def log_operation(self, operation, details=""):
        """记录操作日志"""
        try:
            if self.current_user:
                conn = get_db_conn()
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO operation_logs (user_id, operation, details)
                        VALUES (%s, %s, %s)
                    """, (self.current_user['id'], operation, details))
                    conn.commit()
                conn.close()
        except Exception as e:
            print(f"记录操作日志错误: {e}")

class UserManagementDialog(QDialog):
    """用户管理对话框"""
    
    def __init__(self, user_manager=None, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.setWindowTitle("用户管理")
        self.resize(800, 600)
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 用户管理标签页
        self.user_tab = QWidget()
        self.tab_widget.addTab(self.user_tab, "用户管理")
        self.setup_user_tab()
        
        # 操作日志标签页
        self.log_tab = QWidget()
        self.tab_widget.addTab(self.log_tab, "操作日志")
        self.setup_log_tab()
        
        # 数据备份标签页
        self.backup_tab = QWidget()
        self.tab_widget.addTab(self.backup_tab, "数据备份")
        self.setup_backup_tab()
        
        # 加载数据
        self.load_users()
        self.load_logs()
    
    def setup_user_tab(self):
        """设置用户管理标签页"""
        layout = QVBoxLayout(self.user_tab)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("添加用户")
        self.btn_edit = QPushButton("编辑用户")
        self.btn_delete = QPushButton("删除用户")
        self.btn_reset = QPushButton("重置密码")
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 用户表格
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(5)
        self.user_table.setHorizontalHeaderLabels(["ID", "用户名", "角色", "邮箱", "状态"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.user_table)
        
        # 连接信号
        self.btn_add.clicked.connect(self.add_user)
        self.btn_edit.clicked.connect(self.edit_user)
        self.btn_delete.clicked.connect(self.delete_user)
        self.btn_reset.clicked.connect(self.reset_password)
    
    def setup_log_tab(self):
        """设置操作日志标签页"""
        layout = QVBoxLayout(self.log_tab)
        
        # 日志表格
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels(["时间", "用户", "操作", "详情", "ID"])
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.log_table)
    
    def setup_backup_tab(self):
        """设置数据备份标签页"""
        layout = QVBoxLayout(self.backup_tab)
        
        # 备份按钮
        btn_layout = QHBoxLayout()
        self.btn_create_backup = QPushButton("创建备份")
        self.btn_restore_backup = QPushButton("恢复备份")
        self.btn_auto_backup = QPushButton("设置自动备份")
        
        btn_layout.addWidget(self.btn_create_backup)
        btn_layout.addWidget(self.btn_restore_backup)
        btn_layout.addWidget(self.btn_auto_backup)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 备份日志表格
        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(5)
        self.backup_table.setHorizontalHeaderLabels(["备份名称", "路径", "大小", "创建者", "时间"])
        self.backup_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.backup_table)
        
        # 连接信号
        self.btn_create_backup.clicked.connect(self.create_backup)
        self.btn_restore_backup.clicked.connect(self.restore_backup)
        self.btn_auto_backup.clicked.connect(self.setup_auto_backup)
    
    def load_users(self):
        """加载用户列表"""
        try:
            conn = get_db_conn()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, username, role, email, is_active 
                    FROM users 
                    ORDER BY id
                """)
                users = cursor.fetchall()
            conn.close()
            
            self.user_table.setRowCount(len(users))
            for i, user in enumerate(users):
                self.user_table.setItem(i, 0, QTableWidgetItem(str(user[0])))
                self.user_table.setItem(i, 1, QTableWidgetItem(user[1]))
                self.user_table.setItem(i, 2, QTableWidgetItem(user[2]))
                self.user_table.setItem(i, 3, QTableWidgetItem(user[3] or ""))
                self.user_table.setItem(i, 4, QTableWidgetItem("启用" if user[4] else "禁用"))
        except Exception as e:
            print(f"加载用户列表错误: {e}")
            QMessageBox.warning(self, "错误", f"加载用户列表失败：{str(e)}")
    
    def load_logs(self):
        """加载操作日志"""
        try:
            conn = get_db_conn()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT l.timestamp, u.username, l.operation, l.details, l.id
                    FROM operation_logs l
                    LEFT JOIN users u ON l.user_id = u.id
                    ORDER BY l.timestamp DESC
                    LIMIT 100
                """)
                logs = cursor.fetchall()
            conn.close()
            
            self.log_table.setRowCount(len(logs))
            for i, log in enumerate(logs):
                self.log_table.setItem(i, 0, QTableWidgetItem(str(log[0])))
                self.log_table.setItem(i, 1, QTableWidgetItem(log[1] or "未知"))
                self.log_table.setItem(i, 2, QTableWidgetItem(log[2]))
                self.log_table.setItem(i, 3, QTableWidgetItem(log[3] or ""))
                self.log_table.setItem(i, 4, QTableWidgetItem(str(log[4])))
        except Exception as e:
            print(f"加载操作日志错误: {e}")
    
    def add_user(self):
        """添加用户"""
        dialog = UserEditDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            user_data = dialog.get_data()
            
            try:
                conn = get_db_conn()
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO users (username, password, role, email)
                        VALUES (%s, %s, %s, %s)
                    """, (user_data['username'], user_data['password'], 
                         user_data['role'], user_data['email']))
                    conn.commit()
                conn.close()
                
                if self.user_manager:
                    self.user_manager.log_operation("添加用户", f"添加用户: {user_data['username']}")
                
                self.load_users()
                QMessageBox.information(self, "成功", "用户添加成功！")
            except Exception as e:
                print(f"添加用户错误: {e}")
                QMessageBox.critical(self, "错误", f"添加用户失败：{str(e)}")
    
    def edit_user(self):
        """编辑用户"""
        current_row = self.user_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要编辑的用户！")
            return
        
        try:
            user_id = int(self.user_table.item(current_row, 0).text())
            username = self.user_table.item(current_row, 1).text()
            
            conn = get_db_conn()
            with conn.cursor() as cursor:
                cursor.execute("SELECT username, role, email FROM users WHERE id = %s", (user_id,))
                user_data = cursor.fetchone()
            conn.close()
            
            if not user_data:
                QMessageBox.warning(self, "错误", "用户数据不存在！")
                return
            
            dialog = UserEditDialog(self, {
                'username': user_data[0],
                'role': user_data[1],
                'email': user_data[2]
            })
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_data = dialog.get_data()
                
                conn = get_db_conn()
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE users SET role = %s, email = %s WHERE id = %s
                    """, (new_data['role'], new_data['email'], user_id))
                    conn.commit()
                conn.close()
                
                if self.user_manager:
                    self.user_manager.log_operation("编辑用户", f"编辑用户: {username}")
                self.load_users()
                QMessageBox.information(self, "成功", "用户信息更新成功！")
        except Exception as e:
            print(f"编辑用户错误: {e}")
            QMessageBox.critical(self, "错误", f"编辑用户失败：{str(e)}")
    
    def delete_user(self):
        """删除用户"""
        current_row = self.user_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要删除的用户！")
            return
        
        try:
            user_id = int(self.user_table.item(current_row, 0).text())
            username = self.user_table.item(current_row, 1).text()
            
            if username == 'admin':
                QMessageBox.warning(self, "警告", "不能删除管理员账户！")
                return
            
            reply = QMessageBox.question(self, "确认删除", 
                                       f"确定要删除用户 {username} 吗？",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                conn = get_db_conn()
                with conn.cursor() as cursor:
                    cursor.execute("UPDATE users SET is_active = FALSE WHERE id = %s", (user_id,))
                    conn.commit()
                conn.close()
                
                if self.user_manager:
                    self.user_manager.log_operation("删除用户", f"删除用户: {username}")
                self.load_users()
                QMessageBox.information(self, "成功", "用户已禁用！")
        except Exception as e:
            print(f"删除用户错误: {e}")
            QMessageBox.critical(self, "错误", f"删除用户失败：{str(e)}")
    
    def reset_password(self):
        """重置密码"""
        current_row = self.user_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要重置密码的用户！")
            return
        
        try:
            user_id = int(self.user_table.item(current_row, 0).text())
            username = self.user_table.item(current_row, 1).text()
            
            # 使用输入对话框
            from PyQt6.QtWidgets import QInputDialog
            new_password, ok = QInputDialog.getText(self, "重置密码", 
                                                   f"请输入用户 {username} 的新密码：",
                                                   QLineEdit.EchoMode.Password)
            
            if ok and new_password:
                conn = get_db_conn()
                with conn.cursor() as cursor:
                    cursor.execute("UPDATE users SET password = %s WHERE id = %s", 
                                 (new_password, user_id))
                    conn.commit()
                conn.close()
                
                if self.user_manager:
                    self.user_manager.log_operation("重置密码", f"重置用户密码: {username}")
                QMessageBox.information(self, "成功", "密码重置成功！")
        except Exception as e:
            print(f"重置密码错误: {e}")
            QMessageBox.critical(self, "错误", f"重置密码失败：{str(e)}")
    
    def create_backup(self):
        """创建数据备份"""
        try:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = QFileDialog.getExistingDirectory(self, "选择备份目录")
            
            if not backup_path:
                return
            
            # 创建备份文件
            backup_file = os.path.join(backup_path, f"{backup_name}.zip")
            
            with zipfile.ZipFile(backup_file, 'w') as zipf:
                # 备份数据库数据
                conn = get_db_conn()
                with conn.cursor() as cursor:
                    # 获取所有表数据
                    tables = ['users', 'wastes', 'product_standards', 'operation_logs', 'backup_logs']
                    
                    for table in tables:
                        try:
                            cursor.execute(f"SELECT * FROM {table}")
                            rows = cursor.fetchall()
                            
                            # 获取列名
                            cursor.execute(f"DESCRIBE {table}")
                            columns = [col[0] for col in cursor.fetchall()]
                            
                            # 保存表数据
                            table_data = {
                                'columns': columns,
                                'data': [list(row) for row in rows]
                            }
                            
                            zipf.writestr(f"{table}.json", json.dumps(table_data, default=str))
                        except Exception as e:
                            print(f"备份表 {table} 失败: {e}")
                            continue
                
                conn.close()
            
            # 记录备份日志
            backup_size = os.path.getsize(backup_file)
            if self.user_manager:
                conn = get_db_conn()
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO backup_logs (backup_name, backup_path, backup_size, created_by)
                        VALUES (%s, %s, %s, %s)
                    """, (backup_name, backup_file, backup_size, self.user_manager.current_user['id']))
                    conn.commit()
                conn.close()
                
                self.user_manager.log_operation("数据备份", f"创建备份: {backup_name}")
            
            QMessageBox.information(self, "成功", f"备份创建成功！\n文件位置: {backup_file}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"备份创建失败：{str(e)}")
    
    def restore_backup(self):
        """恢复数据备份"""
        backup_file, _ = QFileDialog.getOpenFileName(self, "选择备份文件", "", "ZIP files (*.zip)")
        
        if not backup_file:
            return
        
        reply = QMessageBox.question(self, "确认恢复", 
                                   "恢复备份将覆盖当前数据，确定要继续吗？",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    conn = get_db_conn()
                    with conn.cursor() as cursor:
                        # 恢复表数据
                        tables = ['users', 'wastes', 'product_standards', 'operation_logs', 'backup_logs']
                        
                        for table in tables:
                            if f"{table}.json" in zipf.namelist():
                                table_data = json.loads(zipf.read(f"{table}.json").decode())
                                
                                # 清空表
                                cursor.execute(f"DELETE FROM {table}")
                                
                                # 恢复数据
                                for row_data in table_data['data']:
                                    placeholders = ', '.join(['%s'] * len(row_data))
                                    cursor.execute(f"INSERT INTO {table} VALUES ({placeholders})", row_data)
                    
                    conn.commit()
                    conn.close()
                
                if self.user_manager:
                    self.user_manager.log_operation("数据恢复", f"恢复备份: {os.path.basename(backup_file)}")
                
                QMessageBox.information(self, "成功", "备份恢复成功！")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"备份恢复失败：{str(e)}")
    
    def setup_auto_backup(self):
        """设置自动备份"""
        QMessageBox.information(self, "自动备份", "自动备份功能开发中...")

class UserEditDialog(QDialog):
    """用户编辑对话框"""
    
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.user_data = user_data or {}
        self.setWindowTitle("编辑用户")
        self.resize(300, 200)
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QFormLayout(self)
        
        # 用户名
        self.username_edit = QLineEdit(self.user_data.get('username', ''))
        if self.user_data:
            self.username_edit.setReadOnly(True)
        layout.addRow("用户名", self.username_edit)
        
        # 密码
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        if not self.user_data:
            layout.addRow("密码", self.password_edit)
        
        # 角色
        self.role_combo = QComboBox()
        self.role_combo.addItems(['admin', 'operator', 'viewer'])
        self.role_combo.setCurrentText(self.user_data.get('role', 'viewer'))
        layout.addRow("角色", self.role_combo)
        
        # 邮箱
        self.email_edit = QLineEdit(self.user_data.get('email', ''))
        layout.addRow("邮箱", self.email_edit)
        
        # 按钮
        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton("确定")
        self.btn_cancel = QPushButton("取消")
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        layout.addRow(btn_layout)
        
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
    
    def get_data(self):
        """获取表单数据"""
        return {
            'username': self.username_edit.text(),
            'password': self.password_edit.text(),
            'role': self.role_combo.currentText(),
            'email': self.email_edit.text()
        } 