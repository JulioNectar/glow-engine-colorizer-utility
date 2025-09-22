from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import pyqtSignal

class ColorOptionWidget(QWidget):
    colorSelected = pyqtSignal(str)

    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = color
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.color_label = QLabel()
        self.color_label.setFixedSize(30, 30)
        self.color_label.setStyleSheet(f"background-color: {self.color}; border: 1px solid #ccc;")

        self.select_btn = QPushButton(self.color)
        self.select_btn.clicked.connect(self.on_color_selected)

        layout.addWidget(self.color_label)
        layout.addWidget(self.select_btn)

    def on_color_selected(self):
        self.colorSelected.emit(self.color)