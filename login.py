from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from db import get_db_conn
from user_management import UserManager

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_manager = UserManager()
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
        self.btn_register = QPushButton("注册", self)
        btn_layout.addWidget(self.btn_login)
        btn_layout.addWidget(self.btn_register)
        layout.addLayout(btn_layout)
        
        self.btn_login.clicked.connect(self.try_login)
        self.btn_register.clicked.connect(self.try_register)
        self.login_success = False

    def try_login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        
        if not username or not password:
            QMessageBox.warning(self, "登录失败", "用户名和密码不能为空")
            return
        
        if self.user_manager.authenticate_user(username, password):
            self.login_success = True
            self.username_edit.clear()
            self.password_edit.clear()
            self.user_manager.log_operation("用户登录", f"用户 {username} 登录成功")
            self.accept()
        else:
            QMessageBox.warning(self, "登录失败", "用户名或密码错误")

    def try_register(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        if not username or not password:
            QMessageBox.warning(self, "注册失败", "用户名和密码不能为空")
            return
        try:
            conn = get_db_conn()
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM users WHERE username=%s", (username,))
                if cursor.fetchone():
                    QMessageBox.warning(self, "注册失败", "用户名已存在")
                    return
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                conn.commit()
                QMessageBox.information(self, "注册成功", "注册成功，请登录")
                self.username_edit.clear()
                self.password_edit.clear()
        except Exception as e:
            QMessageBox.critical(self, "数据库错误", f"数据库连接或写入失败：{e}")
        finally:
            if 'conn' in locals():
                conn.close()
