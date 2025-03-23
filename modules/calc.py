from collections import Counter
import json
import math
import os
import re
import sys
import time
from typing import Dict, List, Optional, Tuple

import numpy as np
import requests
import sympy as sp
from deep_translator import GoogleTranslator
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mistralai import Mistral
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import (QEasingCurve, QPoint, QPropertyAnimation, QRect, QSize,
                         QThread, QTimer, Qt, pyqtSignal)
from PyQt6.QtGui import (QBrush, QColor, QFont, QFontDatabase, QIcon, QPainter,
                        QPen, QPixmap)
from PyQt6.QtWidgets import (QApplication, QColorDialog, QComboBox, QDialog,
                           QFileDialog, QFontDialog, QGraphicsDropShadowEffect,
                           QGraphicsOpacityEffect, QGridLayout, QHBoxLayout,
                           QInputDialog, QLabel, QLineEdit, QMainWindow,
                           QMessageBox, QPushButton, QScrollArea, QSlider,
                           QSplashScreen, QTextEdit, QVBoxLayout, QWidget)


import markdown
from markdown.extensions import fenced_code, tables, nl2br
import subprocess

class MiniCalculatorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_settings()  # Загружаем настройки при старте
        self.setWindowTitle("Mini Calculator")
        self.setFixedSize(250, 350)  # Устанавливаем фиксированные размеры окна
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icons", "icon.ico")))  # Указываем абсолютный путь к файлу с иконкой в корневой директории
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.entry = QLineEdit()
        self.entry.setReadOnly(True)
        self.layout.addWidget(self.entry)

        self.create_buttons()
        self.apply_current_theme()  # Применяем текущую тему



    def load_settings(self):
        """Загрузить настройки из файла"""
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as settings_file:
                settings = json.load(settings_file)
                self.current_theme = settings.get("theme", "light")  # Загрузить текущую тему
                self.current_background = settings.get("background_image", None)  # Загрузить путь к изображению фона

                print(f"Mini calc loaded theme: {self.current_theme}")  # Отладочная информация

                # Применяем загруженную тему
                if self.current_theme == "dark":
                    self.set_black_theme()  # Применяем тёмную тему
                else:
                    self.set_white_theme()  # Применяем светлую тему

                # Если путь к изображению фона существует, применяем его
                if self.current_background:
                    self.apply_background(self.current_background)  # Устанавливаем изображение как фон
        else:
            # Если файл настроек не существует, устанавливаем тему по умолчанию
            self.set_white_theme()

    def apply_background(self, background_path):
        """Применить фоновое изображение"""
        if os.path.exists(background_path):
            self.setStyleSheet(f"QWidget {{ background-image: url({background_path}); }}")
        else:
            print(f"Фон не найден по пути: {background_path}")

    def create_buttons(self):
        buttons = [
            ('(', ')', 'C', 'AC'),
            ('7', '8', '9', '/'),
            ('4', '5', '6', '*'),
            ('1', '2', '3', '-'),
            ('0', '.', '=', '+'),
        ]

        for row in buttons:
            button_row = QHBoxLayout()
            for button_text in row:
                button = QPushButton(button_text)
                button.clicked.connect(self.on_button_click)
                button_row.addWidget(button)
            self.layout.addLayout(button_row)

    def on_button_click(self):
        button = self.sender()
        button_text = button.text()

        if button_text == '=':
            try:
                result = str(eval(self.entry.text()))  # Вычисляем результат
                self.entry.setText(result)
            except Exception as e:
                self.error_message()  # Показываем сообщение об ошибке

        elif button_text == 'C':
            current_text = self.entry.text()
            self.entry.setText(current_text[:-1])

        elif button_text == 'AC':
            self.entry.clear()

        elif button_text == 'sqrt':
            try:
                result = math.sqrt(float(self.entry.text()))
                self.entry.setText(str(result))
            except ValueError:
                self.error_message()  # Показываем сообщение об ошибке

        elif button_text == 'pow':
            try:
                result = str(eval(self.entry.text()))
                self.entry.setText(result)
            except Exception as e:
                self.error_message()  # Показываем сообщение об ошибке

        elif button_text == 'pi':
            self.entry.setText(str(math.pi))

        elif button_text == 'e':
            self.entry.setText(str(math.e))

        else:
            current_text = self.entry.text()
            new_text = current_text + button_text
            self.entry.setText(new_text)

    def error_message(self):
        msg = QMessageBox(self)

        custom_icon = QPixmap("../icons/integral-icon.ico")  
        msg.setIconPixmap(custom_icon)

        msg.setText("Произошла ошибка при вычислении!")
        msg.setWindowTitle("Ошибка")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.clear_text(self.entry)
        # Отображаем сообщение
        msg.exec()

    def clear_text(self, text_input):
        """Очищает текстовое поле."""
        text_input.clear()

    def calcanimation(self):
        """Анимация открытия окна."""
        self.setWindowOpacity(0)
        self.show()
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(200)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def apply_theme(self, theme_path):
        """Загрузить и применить тему из файла .qss."""
        try:
            with open(theme_path, "r") as file:
                theme_style = file.read()
                self.setStyleSheet(theme_style)
        except FileNotFoundError:
            print(f"Тема {theme_path} не найдена.")
        except Exception as e:
            print(f"Ошибка при загрузке темы: {e}")

    def set_white_theme(self):
        """Установить светлую тему."""
        self.apply_theme("resources/styles/light_theme.qss")
        self.current_theme = "light"

    def set_black_theme(self):
        """Установить темную тему."""
        self.apply_theme("resources/styles/dark_theme.qss")
        self.current_theme = "dark"

    def apply_current_theme(self):
        """Применить текущую тему при запуске."""
        if self.current_theme == "light":
            self.set_white_theme()
        else:
            self.set_black_theme()

class Math:
    def __init__(self):
        self.mini_calculator = None  # Placeholder for the calculator instance

    def open_calculator(self):
        if not self.mini_calculator:
            self.mini_calculator = MiniCalculatorUI()
        self.mini_calculator.calcanimation()