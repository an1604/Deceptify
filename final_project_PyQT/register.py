from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
from utils import center_window
from network import create_user

class RegisterWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Register")
        center_window(self, 400, 300)
        self.setStyleSheet("background-color: #e6e6fa;")

        layout = QVBoxLayout()

        self.label_username = QLabel("Username:")
        layout.addWidget(self.label_username)
        self.entry_username = QLineEdit()
        layout.addWidget(self.entry_username)

        self.label_password = QLabel("Password:")
        layout.addWidget(self.label_password)
        self.entry_password = QLineEdit()
        self.entry_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.entry_password)

        self.btn_create_user = QPushButton("Create User")
        self.btn_create_user.clicked.connect(self.on_create_user)
        layout.addWidget(self.btn_create_user)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_create_user(self):
        username = self.entry_username.text()
        password = self.entry_password.text()
        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Username and password are required.")
            return
        if create_user(username, password):
            self.parent.show()
            self.close()
