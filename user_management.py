import os
import json
import shutil
import zipfile
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, 
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem, 
    QMessageBox, QLabel, QTextEdit, QFileDialog, QProgressBar,
    QGroupBox, QCheckBox, QSpinBox, QDateEdit, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from db import get_db_conn
import traceback # Added for traceback.print_exc()

# 角色权限定义
ROLES = {
    'admin': {
        'name': '管理员',
        'permissions': ['user_manage', 'waste_manage', 'standard_manage', 'optimization', 'backup', 'log_view']
    },
    'operator': {
        'name': '操作员', 
        'permissions': ['waste_manage', 'standard_manage', 'optimization']
    },
    'viewer': {
        'name': '查看者',
        'permissions': ['waste_view', 'standard_view', 'optimization_view']
    }
}

class UserManager:
    """用户管理类"""
    
    def __init__(self):
        self.current_user = None
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        try:
            conn = get_db_conn()
            with conn.cursor() as cursor:
                # 用户表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        role VARCHAR(20) NOT NULL DEFAULT 'viewer',
                        email VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP NULL,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """)
                
                # 操作日志表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS operation_logs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        username VARCHAR(50),
                        operation VARCHAR(100) NOT NULL,
                        details TEXT,
                        ip_address VARCHAR(45),
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """)
                
                # 数据备份记录表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS backup_logs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        backup_name VARCHAR(100) NOT NULL,
                        backup_path VARCHAR(255) NOT NULL,
                        backup_size BIGINT,
                        created_by INT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status VARCHAR(20) DEFAULT 'success',
                        FOREIGN KEY (created_by) REFERENCES users(id)
                    )
                """)
                
                # 创建默认管理员账户
                cursor.execute("SELECT 1 FROM users WHERE username = 'admin'")
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO users (username, password, role, email) 
                        VALUES ('admin', 'admin123', 'admin', 'admin@recyclemind.com')
                    """)
                
                conn.commit()
            conn.close()
        except Exception as e:
            print(f"数据库初始化错误: {e}")
            # 如果数据库初始化失败，创建一个简单的内存用户管理器
            self.current_user = None
    
    def authenticate_user(self, username, password):
        """用户认证"""
        try:
            print(f"尝试认证用户: {username}")  # 调试信息
            conn = get_db_conn()
            with conn.cursor() as cursor:
                query = """
                    SELECT id, username, role, email 
                    FROM users 
                    WHERE username = %s AND password = %s
                    AND (is_active IS NULL OR is_active = TRUE)
                """
                print(f"执行SQL查询: {query}")  # 调试信息
                cursor.execute(query, (username, password))
                user = cursor.fetchone()
                print(f"查询结果: {user}")  # 调试信息
                
                if user:
                    self.current_user = {
                        'id': user[0],
                        'username': user[1],
                        'role': user[2],
                        'email': user[3]
                    }
                    print(f"认证成功，用户信息: {self.current_user}")  # 调试信息
                    conn.close()
                    return True
            conn.close()
            print("认证失败：未找到匹配的用户记录")  # 调试信息
            return False
        except Exception as e:
            print(f"用户认证错误: {e}")
            traceback.print_exc()  # 打印详细错误信息
            return False
    
    def has_permission(self, permission):
        """检查用户权限"""
        if not self.current_user:
            return False
        role = self.current_user['role']
        return permission in ROLES.get(role, {}).get('permissions', [])
    
    def log_operation(self, operation, details=""):
        """记录操作日志"""
        if not self.current_user:
            return
            
        try:
            conn = get_db_conn()
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO operation_logs (user_id, username, operation, details)
                    VALUES (%s, %s, %s, %s)
                """, (
                    self.current_user['id'],
                    self.current_user['username'],
                    operation,
                    details
                ))
                conn.commit()
            conn.close()
        except Exception as e:
            print(f"日志记录错误: {e}")
            # 如果数据库连接失败，只打印日志到控制台
            print(f"操作日志: {self.current_user['username']} - {operation} - {details}")

class UserManagementDialog(QDialog):
    """用户管理对话框"""
    
    def __init__(self, user_manager=None, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.setWindowTitle("用户管理")
        self.setMinimumSize(800, 600)
        self.init_ui()
        self.load_users()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 创建标签页
        tabs = QTabWidget()
        
        # 用户管理标签页
        user_tab = QWidget()
        user_layout = QVBoxLayout(user_tab)
        
        # 用户列表
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(5)
        self.user_table.setHorizontalHeaderLabels([
            "ID", "用户名", "角色", "邮箱", "状态"
        ])
        user_layout.addWidget(self.user_table)
        
        # 用户操作按钮
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("添加用户")
        self.btn_edit = QPushButton("编辑用户")
        self.btn_delete = QPushButton("删除用户")
        self.btn_reset_pwd = QPushButton("重置密码")
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_reset_pwd)
        btn_layout.addStretch()
        
        user_layout.addLayout(btn_layout)
        
        # 连接信号
        self.btn_add.clicked.connect(self.add_user)
        self.btn_edit.clicked.connect(self.edit_user)
        self.btn_delete.clicked.connect(self.delete_user)
        self.btn_reset_pwd.clicked.connect(self.reset_password)
        
        tabs.addTab(user_tab, "用户管理")
        
        # 操作日志标签页
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        
        # 日志筛选
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("用户:"))
        self.user_filter = QComboBox()
        self.user_filter.addItem("全部用户")
        filter_layout.addWidget(self.user_filter)
        
        filter_layout.addWidget(QLabel("操作:"))
        self.operation_filter = QComboBox()
        self.operation_filter.addItem("全部操作")
        self.operation_filter.addItems([
            "登录", "添加废料", "编辑废料", "删除废料",
            "添加标准", "编辑标准", "删除标准", "计算优化",
            "数据备份", "用户管理"
        ])
        filter_layout.addWidget(self.operation_filter)
        
        self.btn_refresh_log = QPushButton("刷新")
        self.btn_refresh_log.clicked.connect(self.load_logs)
        filter_layout.addWidget(self.btn_refresh_log)
        filter_layout.addStretch()
        
        log_layout.addLayout(filter_layout)
        
        # 日志表格
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels([
            "时间", "用户", "操作", "详情", "IP地址"
        ])
        log_layout.addWidget(self.log_table)
        
        tabs.addTab(log_tab, "操作日志")
        
        # 数据备份标签页
        backup_tab = QWidget()
        backup_layout = QVBoxLayout(backup_tab)
        
        # 备份操作
        backup_group = QGroupBox("数据备份")
        backup_group_layout = QVBoxLayout(backup_group)
        
        backup_btn_layout = QHBoxLayout()
        self.btn_backup = QPushButton("创建备份")
        self.btn_restore = QPushButton("恢复备份")
        self.btn_auto_backup = QPushButton("设置自动备份")
        
        backup_btn_layout.addWidget(self.btn_backup)
        backup_btn_layout.addWidget(self.btn_restore)
        backup_btn_layout.addWidget(self.btn_auto_backup)
        backup_btn_layout.addStretch()
        
        backup_group_layout.addLayout(backup_btn_layout)
        
        # 自动备份设置
        auto_backup_layout = QHBoxLayout()
        auto_backup_layout.addWidget(QLabel("自动备份间隔:"))
        self.backup_interval = QSpinBox()
        self.backup_interval.setRange(1, 30)
        self.backup_interval.setValue(7)
        self.backup_interval.setSuffix(" 天")
        auto_backup_layout.addWidget(self.backup_interval)
        
        self.enable_auto_backup = QCheckBox("启用自动备份")
        auto_backup_layout.addWidget(self.enable_auto_backup)
        auto_backup_layout.addStretch()
        
        backup_group_layout.addLayout(auto_backup_layout)
        backup_layout.addWidget(backup_group)
        
        # 备份历史
        backup_history_group = QGroupBox("备份历史")
        backup_history_layout = QVBoxLayout(backup_history_group)
        
        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(5)
        self.backup_table.setHorizontalHeaderLabels([
            "备份名称", "创建时间", "大小", "状态", "创建者"
        ])
        backup_history_layout.addWidget(self.backup_table)
        
        backup_layout.addWidget(backup_history_group)
        
        # 连接信号
        self.btn_backup.clicked.connect(self.create_backup)
        self.btn_restore.clicked.connect(self.restore_backup)
        self.btn_auto_backup.clicked.connect(self.setup_auto_backup)
        
        tabs.addTab(backup_tab, "数据备份")
        
        layout.addWidget(tabs)
        
        # 保存标签页引用以便外部访问
        self.tab_widget = tabs
    
    def load_users(self):
        """加载用户列表"""
        try:
            conn = get_db_conn()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, username, role, email, is_active
                    FROM users ORDER BY id
                """)
                users = cursor.fetchall()
            
            self.user_table.setRowCount(len(users))
            for row, user in enumerate(users):
                self.user_table.setItem(row, 0, QTableWidgetItem(str(user[0])))
                self.user_table.setItem(row, 1, QTableWidgetItem(user[1]))
                self.user_table.setItem(row, 2, QTableWidgetItem(ROLES.get(user[2], {}).get('name', user[2])))
                self.user_table.setItem(row, 3, QTableWidgetItem(user[3] or ''))
                self.user_table.setItem(row, 4, QTableWidgetItem('启用' if user[4] else '禁用'))
            
            conn.close()
        except Exception as e:
            print(f"加载用户列表错误: {e}")
            QMessageBox.warning(self, "错误", f"加载用户列表失败：{str(e)}")
            # 显示默认管理员用户
            self.user_table.setRowCount(1)
            self.user_table.setItem(0, 0, QTableWidgetItem("1"))
            self.user_table.setItem(0, 1, QTableWidgetItem("admin"))
            self.user_table.setItem(0, 2, QTableWidgetItem("管理员"))
            self.user_table.setItem(0, 3, QTableWidgetItem("admin@recyclemind.com"))
            self.user_table.setItem(0, 4, QTableWidgetItem("启用"))
    
    def load_logs(self):
        """加载操作日志"""
        try:
            user_filter = self.user_filter.currentText()
            operation_filter = self.operation_filter.currentText()
            
            conn = get_db_conn()
            with conn.cursor() as cursor:
                query = """
                    SELECT timestamp, username, operation, details, ip_address
                    FROM operation_logs
                    WHERE 1=1
                """
                params = []
                
                if user_filter != "全部用户":
                    query += " AND username = %s"
                    params.append(user_filter)
                
                if operation_filter != "全部操作":
                    query += " AND operation = %s"
                    params.append(operation_filter)
                
                query += " ORDER BY timestamp DESC LIMIT 1000"
                
                cursor.execute(query, params)
                logs = cursor.fetchall()
            
            self.log_table.setRowCount(len(logs))
            for row, log in enumerate(logs):
                self.log_table.setItem(row, 0, QTableWidgetItem(str(log[0])))
                self.log_table.setItem(row, 1, QTableWidgetItem(log[1]))
                self.log_table.setItem(row, 2, QTableWidgetItem(log[2]))
                self.log_table.setItem(row, 3, QTableWidgetItem(log[3] or ''))
                self.log_table.setItem(row, 4, QTableWidgetItem(log[4] or ''))
            
            conn.close()
        except Exception as e:
            print(f"加载操作日志错误: {e}")
            QMessageBox.warning(self, "错误", f"加载操作日志失败：{str(e)}")
            # 显示空表格
            self.log_table.setRowCount(0)
    
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
                                if table_data['data']:
                                    columns = table_data['columns']
                                    placeholders = ', '.join(['%s'] * len(columns))
                                    query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
                                    
                                    for row in table_data['data']:
                                        cursor.execute(query, row)
                    
                    conn.commit()
                    conn.close()
                
                if self.user_manager:
                    self.user_manager.log_operation("数据恢复", f"恢复备份: {os.path.basename(backup_file)}")
                QMessageBox.information(self, "成功", "数据恢复成功！")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"数据恢复失败：{str(e)}")
    
    def setup_auto_backup(self):
        """设置自动备份"""
        interval = self.backup_interval.value()
        enabled = self.enable_auto_backup.isChecked()
        
        # 这里可以实现自动备份的定时任务
        # 可以使用 QTimer 或系统级的定时任务
        
        if self.user_manager:
            self.user_manager.log_operation("设置自动备份", 
                                           f"自动备份: {'启用' if enabled else '禁用'}, 间隔: {interval}天")
        QMessageBox.information(self, "成功", "自动备份设置已保存！")

class UserEditDialog(QDialog):
    """用户编辑对话框"""
    
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.user_data = user_data
        self.setWindowTitle("用户信息")
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout(self)
        
        # 用户名
        self.username_edit = QLineEdit(self)
        if self.user_data:
            self.username_edit.setText(self.user_data.get('username', ''))
            self.username_edit.setReadOnly(True)  # 编辑模式下不允许修改用户名
        layout.addRow("用户名:", self.username_edit)
        
        # 密码
        self.password_edit = QLineEdit(self)
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        if not self.user_data:  # 新建用户时才显示密码输入
            layout.addRow("密码:", self.password_edit)
        
        # 角色
        self.role_combo = QComboBox(self)
        for role_key, role_info in ROLES.items():
            self.role_combo.addItem(role_info['name'], role_key)
        
        if self.user_data:
            role_index = self.role_combo.findData(self.user_data.get('role', 'viewer'))
            if role_index >= 0:
                self.role_combo.setCurrentIndex(role_index)
        
        layout.addRow("角色:", self.role_combo)
        
        # 邮箱
        self.email_edit = QLineEdit(self)
        if self.user_data:
            self.email_edit.setText(self.user_data.get('email', ''))
        layout.addRow("邮箱:", self.email_edit)
        
        # 按钮
        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton("确定")
        self.btn_cancel = QPushButton("取消")
        
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addRow(btn_layout)
        
        # 连接信号
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
    
    def get_data(self):
        return {
            'username': self.username_edit.text(),
            'password': self.password_edit.text() if not self.user_data else '',
            'role': self.role_combo.currentData(),
            'email': self.email_edit.text()
        } 