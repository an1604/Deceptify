from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic

class Mainwindow_logged(QMainWindow):
    def __init__(self, username, main_window, parent=None):
        super(Mainwindow_logged, self).__init__(parent)
        uic.loadUi("GUI_main_logged.ui", self)
        self.username_logged_in.setText(username)
        self.main_window = main_window
        self.logout_button.clicked.connect(self.logout)
        self.show()

    def logout(self):
        self.main_window.show()
        self.close()
