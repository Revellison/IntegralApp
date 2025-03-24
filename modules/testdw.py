# main_gui.py
import sys
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QApplication
from apps_widget import FloatingButtonWidget

class MyMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.button = QPushButton("Показать/Скрыть виджет", self)
        self.button.clicked.connect(self.toggle_floating_widget)
        self.layout.addWidget(self.button)

        self.floating_widget = FloatingButtonWidget(self)
        self.layout.addWidget(self.floating_widget)
        self.floating_widget.setVisible(False) # Initially hidden


    def toggle_floating_widget(self):
        self.floating_widget.setVisible(not self.floating_widget.isVisible())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec())
