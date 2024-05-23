from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import Qt
from utils import center_window
from register import RegisterWindow
from network import login
from logged_in import Mainwindow_logged

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("GUI_main.ui", self)
        self.show()
        self.register_button.clicked.connect(self.open_register_window)
        self.login_button.clicked.connect(self.on_login)

    def open_register_window(self):
        self.register_window = RegisterWindow(self)
        self.register_window.show()
        self.hide()

    def on_login(self):
        username = self.username_fill.text()
        password = self.password_fill.text()
        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Username and password are required.")
            return
        if login(username, password):
            self.loggedInWindow = Mainwindow_logged(username=username, main_window=self)
            self.loggedInWindow.show()
            self.close()  # Use close() instead of hide() for better management

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.on_login()

def main():
    app = QApplication([])
    window = MainWindow()
    app.exec_()

if __name__ == "__main__":
    main()
