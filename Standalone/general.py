from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from utils import center_window

class GeneralWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("General")
        center_window(self, 500, 400)
        self.setStyleSheet("background-color: #e6e6fa;")

        layout = QVBoxLayout()

        self.label_welcome = QLabel("Welcome to the General Window")
        layout.addWidget(self.label_welcome)

        self.btn_logout = QPushButton("Logout")
        self.btn_logout.clicked.connect(self.on_logout)
        layout.addWidget(self.btn_logout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_logout(self):
        self.close()
