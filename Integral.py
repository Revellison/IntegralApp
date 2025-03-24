# Оптимизируем импорты, группируем их логически
from collections import Counter
import json
import os
import re
import sys
import time
from typing import Dict
from modules.chat import ChatLogic
from modules.calc import *
from modules.apps_widget import OverlayedPlainTextEdit, FloatingButtonWidget, AppsWidget
import numpy as np
import requests
import sympy as sp
from deep_translator import GoogleTranslator
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mistralai import Mistral
from PyQt6 import QtCore, QtWidgets
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
from design.design import Ui_EduLab


SETTINGS_FILE = "settings.json"
API_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "api.json")
DEFAULT_THEME = "light"
with open('data/water_words.json', 'r', encoding='utf-8') as file:
    data = json.load(file)



def load_fonts():
    font1_id = QFontDatabase.addApplicationFont("resources/fonts/NotoSans.ttf")
    if font1_id == -1:
        print("error")
    else:
        font1_family = QFontDatabase.applicationFontFamilies(font1_id)[0]

    font2_id = QFontDatabase.addApplicationFont("resources/fonts/Rubik-VariableFont_wght.ttf")
    if font2_id == -1:
        print("error")
    else:
        font2_family = QFontDatabase.applicationFontFamilies(font2_id)[0]

class Animated:
    def __init__(self, button):
        self.button = button
        self.default_icon_size = button.iconSize()  # Запоминаем стандартный размер иконки
        
        # Определяем немного уменьшенный размер иконки для анимации
        self.animated_icon_size = QSize(
            int(self.default_icon_size.width() * 0.95),
            int(self.default_icon_size.height() * 0.95)
        )
        
        # Создаем анимации
        self._setup_animations()
        
        # Подключаем анимацию к нажатию
        button.pressed.connect(self.start_animation)
        
        # Флаг для предотвращения наложения анимаций
        self.is_animating = False

    def _setup_animations(self):
        # Анимация уменьшения иконки
        self.grow_animation = QPropertyAnimation(self.button, b"iconSize")
        self.grow_animation.setDuration(100)  # Короткая длительность
        self.grow_animation.setStartValue(self.default_icon_size)
        self.grow_animation.setEndValue(self.animated_icon_size)
        self.grow_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # Анимация возврата размера иконки
        self.shrink_animation = QPropertyAnimation(self.button, b"iconSize")
        self.shrink_animation.setDuration(150)  # Немного дольше для плавного возврата
        self.shrink_animation.setStartValue(self.animated_icon_size)
        self.shrink_animation.setEndValue(self.default_icon_size)
        self.shrink_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Соединяем сигналы завершения
        self.grow_animation.finished.connect(self.shrink_animation.start)
        self.shrink_animation.finished.connect(self._reset_animation_state)

    def start_animation(self):
        # Предотвращаем запуск новой анимации, если предыдущая еще не завершена
        if self.is_animating:
            return
            
        self.is_animating = True
        self.grow_animation.start()
        
    def _reset_animation_state(self):
        # Сбрасываем флаг анимации
        self.is_animating = False


class DrawPad(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(30000, 30000)
        self.current_tool = "pen"  # Текущий инструмент
        self.shapes = []  # Список нарисованных объектов
        self.pen_color = QColor(0, 0, 0)
        self.pen_color = QColor(0, 0, 0)
        self.pen_size = 2
        self.eraser_size = 20
        self.shape_border_size = 2
        self.show_slider = False  # Флаг для показа слайдера
        self.start_point = None
        self.temp_shape = None
        self.undo_stack = []  # Стек для отмены
        self.redo_stack = []  # Стек для повторов
        self.moving_object = None
        self.text_settings = {
            "size": 12,
            "font": "Arial",
            "bold": False,
            "italic": False,
            "underline": False,
            "strikeout": False,
            "color": QColor(0, 0, 0),
        }
        self.color_picker_open = False
        self.is_dragging = False  # Флаг для отслеживания перетаскивания холста
        self.last_pos = None  # Переменная для хранения последней позиции мыши

        # Создание слайдеров и других виджетов
        self.slider_layout = QVBoxLayout()
        self.slider_layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(1, 50)
        self.size_slider.setValue(self.pen_size)
        self.size_slider.setVisible(False)

        self.size_label = QLabel("Size: 2")
        self.size_label.setVisible(False)

        self.form_selector = QComboBox()
        self.form_selector.addItems(["Round", "Square"])
        self.form_selector.setVisible(False)

        self.slider_layout.addWidget(self.size_label)
        self.slider_layout.addWidget(self.size_slider)
        self.slider_layout.addWidget(self.form_selector)

        self.setLayout(self.slider_layout)

        # Сигналы от слайдера
        self.size_slider.valueChanged.connect(self.update_tool_settings)

    def update_slider_visibility(self):
        if self.show_slider:
            self.size_slider.setVisible(True)
            self.size_label.setVisible(True)
            if self.current_tool in {"pen", "eraser"}:
                self.form_selector.setVisible(True)
            else:
                self.form_selector.setVisible(False)
        else:
            self.size_slider.setVisible(False)
            self.size_label.setVisible(False)
            self.form_selector.setVisible(False)

    def update_tool_settings(self):
        size = self.size_slider.value()
        self.size_label.setText(f"Size: {size}")
        if self.current_tool == "pen":
            self.pen_size = size
        elif self.current_tool == "eraser":
            self.eraser_size = size
        elif self.current_tool in {"line", "rect", "circle"}:
            self.shape_border_size = size

    def set_tool(self, tool):
        """Устанавливаем текущий инструмент."""
        self.current_tool = tool
        self.update_slider_visibility()
        if tool == "move":
            QApplication.setOverrideCursor(Qt.CursorShape.OpenHandCursor)
        else:
            QApplication.restoreOverrideCursor()

    def open_color_picker(self):
        """Стилизация цветового диалога."""
        if not self.color_picker_open:
            self.color_picker_open = True

            color_dialog = QColorDialog(self)
            color_dialog.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog)
            color_dialog.show()

            color_dialog.setOptions(
                QColorDialog.ColorDialogOption.ShowAlphaChannel | QColorDialog.ColorDialogOption.DontUseNativeDialog
            )
            if color_dialog.exec():
                self.pen_color = color_dialog.selectedColor()
            self.color_picker_open = False

    def set_text_settings(self):
        """Меню настройки текста."""
        font, ok = QFontDialog.getFont()
        if ok:
            self.text_settings.update({
                "size": font.pointSize(),
                "font": font.family(),
                "bold": font.bold(),
                "italic": font.italic(),
                "underline": font.underline(),
                "strikeout": font.strikeOut(),
                "color": self.pen_color,
            })

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.current_tool in {"line", "rect", "circle"}:
                self.start_point = event.pos()
            elif self.current_tool == "pen":
                self.shapes.append(("pen", [event.pos()], self.pen_color, self.pen_size))
            elif self.current_tool == "eraser":
                self.erase(event.pos())
            elif self.current_tool == "text":
                text, ok = QInputDialog.getText(self, "Добавить текст", "Введите текст:")
                if ok and text:
                    self.shapes.append(("text", event.pos(), text, self.text_settings.copy()))
            elif self.current_tool == "move_object":
                self.moving_object = self.find_shape(event.pos())
            self.save_state()

            if event.button() == Qt.MouseButton.RightButton and self.current_tool == "move":
                self.is_dragging = True
                self.last_pos = event.globalPos()
            else:
                super().mousePressEvent(event)
            if event.button() == Qt.MouseButton.RightButton:
                self.show_slider = not self.show_slider
                self.update_slider_visibility()
            else:
                super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self.current_tool == "pen":
                self.shapes[-1][1].append(event.pos())
            elif self.current_tool in {"line", "rect", "circle"}:
                self.temp_shape = (self.current_tool, self.start_point, event.pos(), self.pen_color, self.pen_size)
            elif self.current_tool == "eraser":
                self.erase(event.pos())
            elif self.current_tool == "move_object" and self.moving_object:
                self.move_shape(self.moving_object, event.pos())
            self.update()

        if self.is_dragging:
            delta = event.globalPos() - self.last_pos
            self.last_pos = event.globalPos()
            self.move(self.x() + delta.x(), self.y() + delta.y())
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.temp_shape and self.current_tool in {"line", "rect", "circle"}:
            self.shapes.append(self.temp_shape)
            self.temp_shape = None
        elif self.current_tool == "move_object":
            self.moving_object = None
        self.update()

        if event.button() == Qt.MouseButton.RightButton and self.is_dragging:
            self.is_dragging = False
        else:
            super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        for shape in self.shapes:
            self.draw_shape(painter, shape)
        if self.temp_shape:
            self.draw_shape(painter, self.temp_shape)

    def draw_shape(self, painter, shape):
        """Рисует фигуры с корректным использованием заливки."""
        try:
            if shape[0] == "pen":
                pen = QPen(shape[2], shape[3])
                painter.setPen(pen)
                points = shape[1]
                if not points or len(points) < 2:
                    return  # Пропускаем, если недостаточно точек
                for i in range(1, len(points)):
                    painter.drawLine(points[i - 1], points[i])

            elif shape[0] == "line":
                pen = QPen(shape[3], shape[4])
                painter.setPen(pen)
                if isinstance(shape[1], QPoint) and isinstance(shape[2], QPoint):
                    painter.drawLine(shape[1], shape[2])
                else:
                    print("Invalid line data:", shape)
                    return

            elif shape[0] == "rect":
                pen = QPen(shape[3], shape[4])
                painter.setPen(pen)
                # Ластик рисует белый фон, остальные - без заливки
                painter.setBrush(QColor(255, 255, 255) if shape[4] == 0 else QBrush(Qt.BrushStyle.NoBrush))
                if isinstance(shape[1], QPoint) and isinstance(shape[2], QPoint):
                    painter.drawRect(QRect(shape[1], shape[2]))
                else:
                    print("Invalid rect data:", shape)
                    return

            elif shape[0] == "circle":
                pen = QPen(shape[3], shape[4])
                painter.setPen(pen)
                # Ластик рисует белый круг, остальные - без заливки
                painter.setBrush(QColor(255, 255, 255) if shape[4] == 0 else QBrush(Qt.BrushStyle.NoBrush))
                if isinstance(shape[1], QPoint) and isinstance(shape[2], QPoint):
                    painter.drawEllipse(QRect(shape[1], shape[2]))
                else:
                    print("Invalid circle data:", shape)
                    return

            elif shape[0] == "text":
                painter.setFont(self.get_font(shape[3]))
                painter.setPen(QPen(shape[3]["color"]))
                if isinstance(shape[1], QPoint) and isinstance(shape[2], str):
                    painter.drawText(shape[1], shape[2])
                else:
                    print("Invalid text data:", shape)
                    return

        except Exception as e:
            print(f"Error drawing shape {shape}: {e}")

    def save_state(self):
        """Сохраняем состояние для отмены."""
        self.undo_stack.append([s.copy() if isinstance(s, list) else s for s in self.shapes])
        self.redo_stack.clear()

    def undo(self):
        """Отмена последнего действия."""
        if self.undo_stack:
            self.redo_stack.append(self.shapes)
            self.shapes = self.undo_stack.pop()
            self.update()

    def redo(self):
        """Повтор последнего отменённого действия."""
        if self.redo_stack:
            self.undo_stack.append(self.shapes)
            self.shapes = self.redo_stack.pop()
            self.update()

    def erase(self, pos):
        """Добавляет область стирания в shapes."""
        eraser_size = 20  # Размер ластика
        eraser_color = QColor(255, 255, 255)  # Белый цвет
        eraser_rect = QRect(pos - QPoint(eraser_size // 2, eraser_size // 2), QSize(eraser_size, eraser_size))

        # Добавляем стирающую фигуру (белый прямоугольник) в список
        self.shapes.append(("rect", eraser_rect.topLeft(), eraser_rect.bottomRight(), eraser_color, 0))
        self.update()

    def shape_intersects(self, shape, rect):
        if shape[0] == "pen":
            return any(rect.contains(p) for p in shape[1])
        elif shape[0] in {"line", "rect", "circle"}:
            return rect.intersects(QRect(shape[1], shape[2]))
        return False

    def find_shape(self, pos):
        """Находит объект по позиции."""
        for shape in reversed(self.shapes):
            if shape[0] == "text" and QRect(shape[1], QSize(50, 20)).contains(pos):
                return shape
        return None

    def move_shape(self, shape, new_pos):
        """Перемещает объект."""
        if shape[0] in {"line", "rect", "circle"}:
            offset = new_pos - shape[1]
            shape[1] += offset
            shape[2] += offset
        elif shape[0] == "text":
            shape[1] = new_pos

    def get_font(self, text_settings):
        """Создаёт шрифт на основе настроек."""
        font = QFont(text_settings["font"], text_settings["size"])
        font.setBold(text_settings["bold"])
        font.setItalic(text_settings["italic"])
        font.setUnderline(text_settings["underline"])
        font.setStrikeOut(text_settings["strikeout"])
        return font

class TextProcessor:



    @staticmethod
    def clear_text(text_input):
        text_input.clear()

    @staticmethod
    def paste_text(text_input):
        clipboard_text = QtWidgets.QApplication.clipboard().text() 
        if clipboard_text:
            cleaned_text = TextProcessor.clean_text(clipboard_text)  
            text_input.insertPlainText(cleaned_text)
        else:
            QMessageBox.warning(None, "Ошибка", "Буфер обмена пуст!") 

    @staticmethod
    def copy_text(text_input):
        text_to_copy = text_input.toPlainText()  
        if text_to_copy:
            QtWidgets.QApplication.clipboard().setText(text_to_copy) 
    @staticmethod
    def copy_errors(error_output):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(error_output.toPlainText())

    @staticmethod
    def check_spelling(text):
        params = {
            'text': text,
            'lang': 'ru'
        }
        response = requests.get('https://speller.yandex.net/services/spellservice.json/checkText', params=params)
        return response.json()

    @staticmethod
    def check_text(text_input, text_output, error_output):
        """Функция для обработки текста и вывода результата."""
        input_text = text_input.toPlainText().strip()

        corrections = TextProcessor.check_spelling(input_text)

        # Проверяем, есть ли ошибки
        if corrections:
            corrected_text = input_text
            error_messages = []

            # Обрабатываем каждую найденную ошибку
            for correction in corrections:
                word = correction['word']
                suggestions = correction['s']
                if suggestions:
                    # Заменяем слово на первое предложение
                    corrected_text = corrected_text.replace(word, suggestions[0])
                error_messages.append(f"Ошибка в слове '{word}': {suggestions}")

            # Устанавливаем исправленный текст и вывод ошибок
            text_output.setPlainText(corrected_text)
            error_output.setPlainText("\n".join(error_messages))
        else:
            text_output.setPlainText(input_text)
            error_output.clear()

    @staticmethod
    def open_window_from_text(text):
        """Открывает отдельное окно с текстом."""
        new_window = QDialog()
        new_window.setWindowTitle("Текст")
        new_window.resize(400, 300)

        layout = QVBoxLayout()
        text_display = QTextEdit(new_window)
        text_display.setPlainText(text)
        text_display.setReadOnly(True)

        layout.addWidget(text_display)
        new_window.setLayout(layout)
        new_window.exec()

class MyApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_background = None  # Переменная для хранения пути к текущему изображению
        self.isAnimating = False
        self.ui = Ui_EduLab()  # Создаем объект интерфейса
        self.ui.setupUi(self)  # Инициализируем интерфейс
        self.chat_logic = ChatLogic(self.ui)
        self.ui.stackedWidget.setCurrentIndex(8)  # Устанавливаем начальную страницу
        self.current_theme = "dark"  # По умолчанию светлая тема

        self.buttons = [self.ui.settings_pg2, self.ui.opisanye_pg1, self.ui.drawpad_pg8]
        self.animated_buttons = [Animated(button) for button in self.buttons]

        # Создаем виджет с приложениями
        self.apps_widget = AppsWidget(self)
        self.apps_widget.setFixedHeight(300)
        self.apps_widget.setGeometry(65, 20, 420, 300)
        self.apps_widget.appClicked.connect(self.handle_app_click)
        self.apps_widget.focusLost.connect(self.hide_apps_widget)  # Подключаем новый сигнал
        self.apps_widget.hide()

        #hide
        self.ui.progressBar.hide()
        self.ui.lineEdit_3.hide()
        self.ui.lineEdit_4.hide()
        self.ui.lineEdit_2.hide()

        # Подключаем DrawPad к существующему QWidget
        self.ui.draw_pad.setLayout(QVBoxLayout())  # Устанавливаем макет для виджета
        self.draw_pad_area = DrawPad()  # Создаем область рисования из импортированного модуля
        scroll_area = QScrollArea()  # Обертываем в прокручиваемую область
        scroll_area.setWidget(self.draw_pad_area)
        self.ui.draw_pad.layout().addWidget(scroll_area)  # Добавляем прокручиваемую область

        self.math = Math()
        #self.ui.opencalculatorbutton.clicked.connect(self.math.open_calculator)
        #drawpad_binds
        self.ui.pen_1.clicked.connect(lambda: self.draw_pad_area.set_tool("pen"))  # Перо
        self.ui.line_1.clicked.connect(lambda: self.draw_pad_area.set_tool("line"))  # Линия
        self.ui.circle.clicked.connect(lambda: self.draw_pad_area.set_tool("circle"))  # Круг
        self.ui.rect.clicked.connect(lambda: self.draw_pad_area.set_tool("rect"))  # Прямоугольник
        self.ui.clear.clicked.connect(lambda: self.clear_draw_pad())  #
        self.ui.palette.clicked.connect(self.draw_pad_area.open_color_picker)
        self.ui.pouring.clicked.connect(lambda: self.draw_pad_area.set_tool("fill"))  # Заливка
        self.ui.text.clicked.connect(lambda: self.draw_pad_area.set_tool("text"))  # Инструмент "текст"
        self.ui.move_object.clicked.connect(lambda: self.draw_pad_area.set_tool("move_object"))  # Перемещение объектов
        self.ui.eraser.clicked.connect(lambda: self.draw_pad_area.set_tool("eraser"))  # Ластик
        self.ui.undo_button.clicked.connect(self.draw_pad_area.undo)  # Отмена действия

        self.load_settings()  # Загружаем и применяем сохранённые настройки

        # Добавление графика в functions_widget
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        # Настройка виджета для графика
        layout = QtWidgets.QVBoxLayout(self.ui.functions_widget)
        layout.addWidget(self.canvas)

        # Устанавливаем поля только для чтения
        self.ui.outputYandex.setReadOnly(True)
        self.ui.errorlog.setReadOnly(True)
        self.ui.simvols_output_probels.setReadOnly(True)
        self.ui.simvols_output_bezprobelov.setReadOnly(True)
        self.ui.slova_output_vsego.setReadOnly(True)
        self.ui.slova_output_Achetyre.setReadOnly(True)
        self.ui.slova_output_tetradnyxlistov.setReadOnly(True)
        self.ui.voda_output.setReadOnly(True)
        self.ui.toshnota_output.setReadOnly(True)
        self.ui.simvols_output_vsego.setReadOnly(True)
        self.ui.translate_output.setReadOnly(True)
        self.ui.translator_otladka_output.setReadOnly(True)

        # Привязка функций к кнопкам для проверки текста
        self.ui.paste1.clicked.connect(lambda: TextProcessor.paste_text(self.ui.inputYandex))
        self.ui.copy1.clicked.connect(lambda: TextProcessor.copy_text(self.ui.inputYandex))  # Кнопка копирования
        self.ui.copy2.clicked.connect(lambda: TextProcessor.copy_text(self.ui.outputYandex))  # Кнопка копирования
        self.ui.errorcopy.clicked.connect(lambda: TextProcessor.copy_text(self.ui.errorlog))  # Кнопка копирования ошибок
        self.ui.delete1.clicked.connect(lambda: TextProcessor.clear_text(self.ui.inputYandex))  # Кнопка удаления
        self.ui.delete2.clicked.connect(lambda: TextProcessor.clear_text(self.ui.outputYandex))  # Кнопка удаления
        self.ui.deleteerrors.clicked.connect(lambda: TextProcessor.clear_text(self.ui.errorlog))  # Кнопка удаления ошибок
        self.ui.delete1.clicked.connect(lambda: TextProcessor.clear_text(self.ui.outputYandex))  # Кнопка удаления
        self.ui.delete1.clicked.connect(lambda: TextProcessor.clear_text(self.ui.errorlog))  # Кнопка удаления
        self.ui.checktext.clicked.connect(lambda: TextProcessor.check_text(  # Кнопка проверки текста
            self.ui.inputYandex,
            self.ui.outputYandex,
            self.ui.errorlog
        ))

        # Переключение страниц
        self.ui.opisanye_pg1.clicked.connect(lambda: self.switch_page(0))  # Привязка кнопки к переключению на страницу 0
        self.ui.settings_pg2.clicked.connect(lambda: self.switch_page(1))  # Привязка кнопки к переключению на страницу 1
        #self.ui.open1_textreworker_pg3.clicked.connect(lambda: self.switch_page(2))  # Привязка кнопки к переключению на страницу 2
        #self.ui.translator_open_page4.clicked.connect(lambda: self.switch_page(3))  # Привязка кнопки к переключению на страницу 4
        #self.ui.drygoe_open_page5.clicked.connect(lambda: self.switch_page(4))  # Привязка кнопки к переключению на страницу 5
        #self.ui.textanalyzer_open_page6.clicked.connect(lambda: self.switch_page(5))  # Привязка кнопки к переключению на страницу 6
        #self.ui.functions_page7.clicked.connect(lambda: self.switch_page(7))  # Привязка кнопки к переключению на страницу 7
        self.ui.drawpad_pg8.clicked.connect(lambda: self.switch_page(8))  # Привязка кнопки к переключению на страницу 8
        #self.ui.calc_page10.clicked.connect(lambda: self.switch_page(9))  # Привязка кнопки к переключению на страницу 9
        #self.ui.aichat_pg10.clicked.connect(lambda: self.switch_page(10))  # Привязка кнопки к переключению на страницу 8

        # Перемещение окна
        self.dragPos = None

        # Привязка функций к кнопкам для переводчика
        self.translator = GoogleTranslator()  # Исправлено: инициализация переводчика
        self.ui.translate_button.clicked.connect(self.translate_text)

        # Привязываем кнопки к функциям
        self.ui.translate_button.clicked.connect(self.translate_text)  # Кнопка "Перевести"
        self.ui.translate_paste.clicked.connect(lambda: TextProcessor.paste_text(self.ui.translator_input))  # Кнопка вставки1
        self.ui.translatecopy.clicked.connect(lambda: TextProcessor.copy_text(self.ui.translator_input))  # Кнопка копирования1
        self.ui.translate_delete.clicked.connect(lambda: TextProcessor.clear_text(self.ui.translator_input))  # Кнопка удаления1
        # второе поле
        self.ui.translatecopy_2.clicked.connect(lambda: TextProcessor.copy_text(self.ui.translate_output))  # Кнопка копирования2
        self.ui.translate_delete2.clicked.connect(lambda: TextProcessor.clear_text(self.ui.translate_output))  # Кнопка удаления2
        self.ui.translate_delete.clicked.connect(lambda: TextProcessor.clear_text(self.ui.translator_input))
        self.ui.translate_delete.clicked.connect(lambda: TextProcessor.clear_text(self.ui.translate_output)) # Кнопка удаления

        # анализатор текста
        self.ui.analyze_text_button.clicked.connect(self.analyze_text)
        self.ui.analysed_text_paste.clicked.connect(lambda: TextProcessor.paste_text(self.ui.analyze_input))  # Кнопка вставки1
        self.ui.analyzed_text_copy.clicked.connect(lambda: TextProcessor.copy_text(self.ui.analyze_input))  # Кнопка копирования1
        self.ui.analyxed_text_clear.clicked.connect(lambda: TextProcessor.clear_text(self.ui.analyze_input))  # Кнопка удаления1
        self.ui.analyxed_text_clear.clicked.connect(lambda: TextProcessor.clear_text(self.ui.simvols_output_vsego))  # Кнопка удаления
        self.ui.analyxed_text_clear.clicked.connect(lambda: TextProcessor.clear_text(self.ui.simvols_output_probels))  # Кнопка удаления
        self.ui.analyxed_text_clear.clicked.connect(lambda: TextProcessor.clear_text(self.ui.simvols_output_bezprobelov))  # Кнопка удаления
        self.ui.analyxed_text_clear.clicked.connect(lambda: TextProcessor.clear_text(self.ui.voda_output))  # Кнопка удаления
        self.ui.analyxed_text_clear.clicked.connect(lambda: TextProcessor.clear_text(self.ui.toshnota_output))  # Кнопка удаления
        self.ui.analyxed_text_clear.clicked.connect(lambda: TextProcessor.clear_text(self.ui.slova_output_vsego))  # Кнопка удаления
        self.ui.analyxed_text_clear.clicked.connect(lambda: TextProcessor.clear_text(self.ui.slova_output_Achetyre))  # Кнопка удаления
        self.ui.analyxed_text_clear.clicked.connect(lambda: TextProcessor.clear_text(self.ui.slova_output_tetradnyxlistov))  # Кнопка удаления
        
        #SETTINGS
        #темы
        self.ui.set_white_theme_4.clicked.connect(self.set_white_theme)
        self.ui.set_black_theme_4.clicked.connect(self.set_black_theme)
        self.ui.set_custom_theme_4.clicked.connect(self.set_custom_theme)

        # Привязываем кнопки для установки и сброса фона
        self.ui.background_set_file_open.clicked.connect(self.set_background_image)
        self.ui.background_reset.clicked.connect(self.reset_background)

        # Подключение кнопки для построения графика
        self.ui.function_create.clicked.connect(self.plot_function)
        self.ui.function_clear.clicked.connect(lambda: TextProcessor.clear_text(self.ui.function_lineEdit))  # Кнопка удаления

        self.ui.apps_widget_start.clicked.connect(self.toggle_apps_widget)

        self.floating_widget = OverlayedPlainTextEdit(self) 
        self.floating_widget.setGeometry(65, 10, 420, 270)  #(x=a, y=b, ширина=c, высота=d)
        self.floating_widget.update_floating_button_text("Открыть")  
        self.floating_widget.hide()  
    
    def handle_app_click(self, app_name):
        """Обработчик клика по приложению"""
        page_mapping = {
            "Калькулятор": lambda: self.math.open_calculator(),
            "Блокнот": lambda: self.switch_page(2),
            "Рисование": lambda: self.switch_page(8),  
            "Орфографический анализатор": lambda: self.switch_page(2),
            "СЕО анализатор текста": lambda: self.switch_page(5),
            "Переводчик": lambda: self.switch_page(3),
            "Построение функций": lambda: self.switch_page(7),
            "ИИ чат": lambda: self.switch_page(10),
        }
        
        if action := page_mapping.get(app_name):
            action()
            self.apps_widget.hide_with_animation()

    def toggle_apps_widget(self):
        """Показать/скрыть панель приложений"""
        if self.apps_widget.isHidden():
            self.apps_widget.show_with_animation()
        else:
            self.apps_widget.hide_with_animation()

    def clear_draw_pad(self):
        self.draw_pad_area.shapes = []
        self.draw_pad_area.update()

    def plot_function(self):
        """Обработка построения графика"""
        function_str = self.ui.function_lineEdit.text().strip()

        try:
            # Преобразование строки функции в символьное выражение
            x = sp.symbols('x')
            func = sp.sympify(function_str)
            func_lambdified = sp.lambdify(x, func, "numpy")

            # Генерация значений
            x_vals = np.linspace(-10, 10, 1000)
            y_vals = func_lambdified(x_vals)

            # Построение графика
            self.ax.clear()
            self.ax.plot(x_vals, y_vals, label=f"y = {sp.pretty(func)}", color="blue", linewidth=2.0)
            self.ax.set_title("Function graph", fontsize=14, fontweight="bold")
            self.ax.set_xlabel("x")
            self.ax.set_ylabel("y")
            self.ax.grid(True, linestyle=':')
            self.ax.axhline(0, color="black", linewidth=0.5, linestyle="--")
            self.ax.axvline(0, color="black", linewidth=0.5, linestyle="--")
            self.ax.legend()
            self.canvas.draw()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось построить график: {e}")

    def save_settings(self):
        """Сохранить настройки в файл"""
        settings = {
            "theme": self.current_theme,  # Сохраняем текущую тему
            "background_image": self.current_background,  # Полный путь к изображению
            "background_image_name": os.path.basename(self.current_background) if self.current_background else ""
        }
        # Создаем путь к файлу настроек в папке data
        settings_path = os.path.join("data", "settings.json")
        # Убедимся, что директория существует
        os.makedirs(os.path.dirname(settings_path), exist_ok=True)
        # Сохраняем настройки
        with open(settings_path, "w") as settings_file:
            json.dump(settings, settings_file)
        print(f"Настройки сохранены: {settings}")  # Отладочная информация

    # Переопределение метода закрытия окна
    def closeEvent(self, event):
        """Обработчик события закрытия окна, сохраняющий настройки"""
        self.save_settings()  # Сохраняем настройки при закрытии
        event.accept()  # Закрываем окно

    def load_settings(self):
        """Загрузить настройки из файла"""
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as settings_file:
                settings = json.load(settings_file)
                self.current_theme = settings.get("theme", "light")  # Загрузить текущую тему
                self.current_background = settings.get("background_image", None)  # Загрузить путь к изображению фона

                print(f"Loaded theme: {self.current_theme}")  # Отладочная информация

                # Применяем загруженную тему
                self.apply_current_theme()

                # Если путь к изображению фона существует, применяем его
                if self.current_background:
                    self.apply_background(self.current_background)  # Устанавливаем изображение как фон
                    # Устанавливаем только имя файла в lineEdit
                    file_name = os.path.basename(self.current_background)
                    self.ui.lineEdit.setText(file_name)
        else:
            # Если файл настроек не существует, устанавливаем тему по умолчанию
            self.apply_current_theme()

    def load_setting(self, key, default=None):
        """Загрузить конкретный параметр из файла настроек."""
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as settings_file:
                settings = json.load(settings_file)
                return settings.get(key, default)
        return default

    def set_background_image(self):
        # Определяем путь к папке с изображениями
        project_dir = os.path.dirname(os.path.abspath(__file__))  # Корневая папка проекта
        images_dir = os.path.join(project_dir, "resources", "backgrounds")  # Папка с изображениями

        # Открываем файловый диалог с указанием начальной директории
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбрать изображение",
            images_dir,  # Указываем начальную директорию
            "Images (*.png *.jpg *.jpeg);;All Files (*)"
        )

        # Проверяем, был ли выбран файл
        if file_path:
            print(f"Выбрано изображение: {file_path}")
            self.current_background = file_path
            # Отображаем только имя файла в lineEdit
            file_name = os.path.basename(file_path)
            self.ui.lineEdit.setText(file_name)
            self.apply_background(file_path)
        else:
            print("Файл не выбран.")

    def apply_background(self, image_path):
        if not os.path.exists(image_path):
            print("Файл не найден")
            return

        # Создаем стиль для фона только для QMainWindow
        background_style = f"""
        QMainWindow {{
            background-image: url({image_path});
            background-repeat: no-repeat;
            background-position: center;
            background-size: cover;
        }}
        """

        # Получаем текущий стиль и добавляем к нему стиль для QMainWindow
        existing_style = self.styleSheet()
        new_style = existing_style + background_style
        self.setStyleSheet(new_style)

    def reset_background(self):
        """Сбросить фон до исходного состояния и применить соответствующую тему."""
        self.current_background = None  # Удаляем путь к изображению
        self.ui.lineEdit.clear()  # Очищаем lineEdit

        # Получаем текущий стиль и удаляем из него фон QMainWindow, если он был установлен
        existing_style = self.styleSheet()

        # Удаляем стиль, относящийся к QMainWindow, чтобы сбросить только фон
        new_style = re.sub(r"QMainWindow\s*{[^}]*background-image[^}]*}", "", existing_style)
        self.setStyleSheet(new_style.strip())

        # Загружаем конкретный параметр (например, тему)
        theme = self.load_setting("theme", "light")  # По умолчанию светлая тема
        self.apply_current_theme()

    def apply_theme(self, theme_path):
        """
        Загрузить и применить тему из файла .qss.
        """
        try:
            with open(theme_path, "r") as file:
                theme_style = file.read()
                # Устанавливаем стиль для всего приложения
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
        
    def set_custom_theme(self):
        """Установить кислотную черно-зеленую тему."""
        self.apply_theme("resources/styles/custom_theme.qss")
        self.current_theme = "custom"

    def apply_current_theme(self):
        """Применить текущую тему при запуске."""
        if self.current_theme == "light":
            self.set_white_theme()
        elif self.current_theme == "dark":
            self.set_black_theme()
        elif self.current_theme == "custom":
            self.set_custom_theme()
        else:
            self.set_white_theme()  # По умолчанию светлая тема

    def analyze_text(self):
        """Функция анализа текста и вывода результатов."""
        text = self.ui.analyze_input.toPlainText()  # Получаем текст из поля ввода и удаляем лишние пробелы

        # Выполняем анализ текста
        results = self.calculate_text_metrics(text)

        # Отображаем результаты в полях
        self.ui.simvols_output_vsego.setText(str(results['total_characters']))
        self.ui.simvols_output_probels.setText(str(results['total_spaces']))
        self.ui.simvols_output_bezprobelov.setText(str(results['non_space_characters']))
        self.ui.slova_output_vsego.setText(str(results['total_words']))
        self.ui.slova_output_Achetyre.setText(f"{results['a4_pages']:.2f}")
        self.ui.slova_output_tetradnyxlistov.setText(f"{results['notebook_pages']:.2f}")
        self.ui.voda_output.setText(f"{results['water_percentage']:.2f}%")
        self.ui.toshnota_output.setText(f"{results['nausea_percentage']:.2f}%")

    def calculate_text_metrics(self, text):

        total_characters = len(text)
        total_spaces = text.count(' ')
        non_space_characters = total_characters - total_spaces

        # Подсчет слов
        words = re.findall(r'\b\w+\b', text) 
        total_words = len(words)

        # Подсчет страниц A4 и тетрадных страниц
        a4_pages = total_words / 250
        notebook_pages = total_words / 80

        # Подсчет "воды" через стоп-слова
        stop_words = set(data['stop_words'])
        water_words = [word for word in words if word.lower() in stop_words]
        water_percentage = len(water_words) / total_words * 100 if total_words > 0 else 0

        # Подсчет "тошноты"
        word_frequencies = Counter(words)
        most_frequent_word_count = word_frequencies.most_common(1)[0][1] if word_frequencies else 0
        nausea_percentage = most_frequent_word_count / total_words * 100 if total_words > 0 else 0

        return {
            "total_characters": total_characters,
            "total_spaces": total_spaces,
            "non_space_characters": non_space_characters,
            "total_words": total_words,
            "a4_pages": a4_pages,
            "notebook_pages": notebook_pages,
            "water_percentage": water_percentage,
            "nausea_percentage": nausea_percentage
        }

    def translate_text(self):
        input_text = self.ui.translator_input.toPlainText()
        target_language = self.get_selected_language()

        if input_text:
            try:
                # Старт замера времени
                start_time = time.time()

                # Перевод текста
                translated = GoogleTranslator(target=target_language).translate(input_text)
                self.ui.translate_output.setPlainText(translated)

                # Время выполнения операции
                end_time = time.time()
                elapsed_time = end_time - start_time

                # Вывод отладочной информации
                self.ui.translator_otladka_output.setPlainText(
                    f"language: {target_language}\n"
                    f"time: {elapsed_time:.2f} "
                )
            except Exception as e:
                self.ui.translator_otladka_output.setPlainText(f"Translate error: {str(e)}")
        else:
            self.ui.translator_otladka_output.setPlainText("popa")

    def get_selected_language(self):
        languages = {
            "Русский": "ru",
            "Английский": "en",
            "Немецкий": "de",
            "Французский": "fr",
            "Японский": "ja",
            "Китайский": "zh-cn",
            "Турецкий": "tr",
            "Белорусский": "be",
            "Казахский": "kk"
        }
        current_language = self.ui.translator_languages_comboBox.currentText()
        return languages.get(current_language, "en")


    def switch_page(self, index):
        """Переключение страниц с анимацией сверху вниз."""
        if self.isAnimating or index == self.ui.stackedWidget.currentIndex():
            return  

        self.isAnimating = True  

        current_widget = self.ui.stackedWidget.currentWidget()
        next_widget = self.ui.stackedWidget.widget(index)


        next_widget.setGeometry(current_widget.geometry())  
        next_widget.show()  


        self.animation_out = QtCore.QPropertyAnimation(current_widget, b"geometry")
        self.animation_out.setDuration(500)
        self.animation_out.setStartValue(current_widget.geometry())
        self.animation_out.setEndValue(QtCore.QRect(
            current_widget.x(),
            current_widget.y() + current_widget.height(), 
            current_widget.width(),
            current_widget.height()
        ))


        self.animation_in = QtCore.QPropertyAnimation(next_widget, b"geometry")
        self.animation_in.setDuration(500)
        self.animation_in.setStartValue(QtCore.QRect(
            next_widget.x(),
            next_widget.y() - next_widget.height(),  
            next_widget.width(),
            next_widget.height()
        ))
        self.animation_in.setEndValue(current_widget.geometry())  


        self.animation_out.setEasingCurve(QtCore.QEasingCurve.Type.InOutCirc)
        self.animation_in.setEasingCurve(QtCore.QEasingCurve.Type.InOutCirc)


        self.animation_out.finished.connect(lambda: self.finalize_switch_page(index, current_widget))

        # Запуск анимаций
        self.animation_out.start()
        self.animation_in.start()

    def finalize_switch_page(self, index, current_widget):
        """Завершение переключения страницы."""
        self.ui.stackedWidget.setCurrentIndex(index)
        current_widget.hide()  # Скрываем текущий виджет после анимации
        self.isAnimating = False  # Сбрасываем флаг анимации

    def show_with_animation(self):
        """Анимация открытия окна."""
        self.setWindowOpacity(0)
        self.show()
        self.animation = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def hide_apps_widget(self):
        """Скрыть виджет приложений"""
        if self.apps_widget.isVisible() and not self.apps_widget.isAnimating:
            self.apps_widget.hide_with_animation()


class SettingsManager:
    @staticmethod
    def load_settings() -> Dict:
        """Загрузка настроек из файла"""
        try:
            with open(SETTINGS_FILE, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {"theme": DEFAULT_THEME, "background_image": None}
    
    @staticmethod
    def save_settings(settings: Dict):
        """Сохранение настроек в файл"""
        with open(SETTINGS_FILE, 'w') as file:
            json.dump(settings, file)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()  
    window.show()
    sys.exit(app.exec())

