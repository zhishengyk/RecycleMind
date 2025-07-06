import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from login import LoginDialog
from waste import WasteManager

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        login = LoginDialog()
        if login.exec() == login.DialogCode.Accepted and login.login_success:
            window = WasteManager(login.user_manager)
            window.show()
            sys.exit(app.exec())
        else:
            sys.exit(0)
    except Exception as e:
        print(f"程序启动错误: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        
        # 显示错误对话框
        try:
            error_app = QApplication(sys.argv)
            QMessageBox.critical(None, "程序错误", 
                               f"程序启动时发生错误:\n{str(e)}\n\n请检查数据库连接配置。")
        except:
            pass
        sys.exit(1)