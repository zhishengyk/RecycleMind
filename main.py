import sys
from PyQt6.QtWidgets import QApplication
from login import LoginDialog
from waste import WasteManager

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginDialog()
    if login.exec() == login.DialogCode.Accepted and login.login_success:
        window = WasteManager()
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)