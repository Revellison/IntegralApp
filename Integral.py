from collections import Counter
import json
import os
import re
import sys
import time
from typing import Dict
from modules.chat import ChatLogic
from modules.calc import *
from modules.apps_widget import OverlayedPlainTextEdit, AppsWidget
from modules.DrawPad import DrawPad
import numpy as np
import requests
import sympy as sp
from deep_translator import GoogleTranslator
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import (QEasingCurve, QPropertyAnimation, QSize)
from PyQt6.QtGui import (QFontDatabase)
from PyQt6.QtWidgets import (QApplication, QDialog,
                           QFileDialog, QMessageBox, QScrollArea, QTextEdit, QVBoxLayout)
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
        self.default_icon_size = button.iconSize()
        self.animated_icon_size = QSize(
            int(self.default_icon_size.width() * 0.95),
            int(self.default_icon_size.height() * 0.95)
        )
        
        self._setup_animations()
        button.pressed.connect(self.start_animation)
        self.is_animating = False

    def _setup_animations(self):
        self.grow_animation = QPropertyAnimation(self.button, b"iconSize")
        self.grow_animation.setDuration(100)
        self.grow_animation.setStartValue(self.default_icon_size)
        self.grow_animation.setEndValue(self.animated_icon_size)
        self.grow_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.shrink_animation = QPropertyAnimation(self.button, b"iconSize")
        self.shrink_animation.setDuration(150)
        self.shrink_animation.setStartValue(self.animated_icon_size)
        self.shrink_animation.setEndValue(self.default_icon_size)
        self.shrink_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.grow_animation.finished.connect(self.shrink_animation.start)
        self.shrink_animation.finished.connect(self._reset_animation_state)

    def start_animation(self):
        if self.is_animating:
                return
                
        self.is_animating = True
        self.grow_animation.start()
        
    def _reset_animation_state(self):
        self.is_animating = False


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
        input_text = text_input.toPlainText().strip()

        corrections = TextProcessor.check_spelling(input_text)

        if corrections:
            corrected_text = input_text
            error_messages = []

            for correction in corrections:
                word = correction['word']
                suggestions = correction['s']
                if suggestions:
                    corrected_text = corrected_text.replace(word, suggestions[0])
                error_messages.append(f"Ошибка в слове '{word}': {suggestions}")

            text_output.setPlainText(corrected_text)
            error_output.setPlainText("\n".join(error_messages))
        else:
            text_output.setPlainText(input_text)
            error_output.clear()

    @staticmethod
    def open_window_from_text(text):
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
        self.current_background = None
        self.isAnimating = False
        self.ui = Ui_EduLab()
        self.ui.setupUi(self)
        self.chat_logic = ChatLogic(self.ui)
        self.ui.stackedWidget.setCurrentIndex(8)
        self.current_theme = "dark"

        self.buttons = [self.ui.settings_pg2, self.ui.opisanye_pg1, self.ui.drawpad_pg8]  
        self.animated_buttons = [Animated(button) for button in self.buttons]

        self.apps_widget = AppsWidget(self)
        self.apps_widget.setFixedHeight(300)
        self.apps_widget.setGeometry(65, 20, 420, 300)
        self.apps_widget.appClicked.connect(self.handle_app_click)
        self.apps_widget.focusLost.connect(self.hide_apps_widget)
        self.apps_widget.hide()

        self.ui.progressBar.hide()
        self.ui.lineEdit_3.hide()
        self.ui.lineEdit_4.hide()
        self.ui.lineEdit_2.hide()

        self.ui.draw_pad.setLayout(QVBoxLayout())
        self.draw_pad_area = DrawPad()
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.draw_pad_area)
        self.ui.draw_pad.layout().addWidget(scroll_area)

        self.math = Math()
        
        self.ui.pen_1.clicked.connect(lambda: self.draw_pad_area.set_tool("pen"))
        self.ui.line_1.clicked.connect(lambda: self.draw_pad_area.set_tool("line"))
        self.ui.circle.clicked.connect(lambda: self.draw_pad_area.set_tool("circle"))
        self.ui.rect.clicked.connect(lambda: self.draw_pad_area.set_tool("rect"))
        self.ui.clear.clicked.connect(lambda: self.clear_draw_pad())
        self.ui.palette.clicked.connect(self.draw_pad_area.open_color_picker)
        self.ui.pouring.clicked.connect(lambda: self.draw_pad_area.set_tool("fill"))
        self.ui.text.clicked.connect(lambda: self.draw_pad_area.set_tool("text"))
        self.ui.move_object.clicked.connect(lambda: self.draw_pad_area.set_tool("move_object"))
        self.ui.eraser.clicked.connect(lambda: self.draw_pad_area.set_tool("eraser"))
        self.ui.undo_button.clicked.connect(self.draw_pad_area.undo)

        self.load_settings()

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        layout = QtWidgets.QVBoxLayout(self.ui.functions_widget)
        layout.addWidget(self.canvas)

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

        self.ui.paste1.clicked.connect(lambda: TextProcessor.paste_text(self.ui.inputYandex))
        self.ui.copy1.clicked.connect(lambda: TextProcessor.copy_text(self.ui.inputYandex))
        self.ui.copy2.clicked.connect(lambda: TextProcessor.copy_text(self.ui.outputYandex))
        self.ui.errorcopy.clicked.connect(lambda: TextProcessor.copy_text(self.ui.errorlog))
        self.ui.delete1.clicked.connect(lambda: TextProcessor.clear_text(self.ui.inputYandex))
        self.ui.delete2.clicked.connect(lambda: TextProcessor.clear_text(self.ui.outputYandex))
        self.ui.deleteerrors.clicked.connect(lambda: TextProcessor.clear_text(self.ui.errorlog))
        self.ui.delete1.clicked.connect(lambda: TextProcessor.clear_text(self.ui.outputYandex))
        self.ui.delete1.clicked.connect(lambda: TextProcessor.clear_text(self.ui.errorlog))
        self.ui.checktext.clicked.connect(lambda: TextProcessor.check_text(
            self.ui.inputYandex,
            self.ui.outputYandex,
            self.ui.errorlog
        ))

        self.ui.opisanye_pg1.clicked.connect(lambda: self.switch_page(0))
        self.ui.settings_pg2.clicked.connect(lambda: self.switch_page(1))
        self.ui.drawpad_pg8.clicked.connect(lambda: self.switch_page(8))

        self.dragPos = None

        self.translator = GoogleTranslator()
        self.ui.translate_button.clicked.connect(self.translate_text)

        self.ui.translate_button.clicked.connect(self.translate_text)
        self.ui.translate_paste.clicked.connect(lambda: TextProcessor.paste_text(self.ui.translator_input))
        self.ui.translatecopy.clicked.connect(lambda: TextProcessor.copy_text(self.ui.translator_input))
        self.ui.translate_delete.clicked.connect(lambda: TextProcessor.clear_text(self.ui.translator_input))
        self.ui.translatecopy_2.clicked.connect(lambda: TextProcessor.copy_text(self.ui.translate_output))
        self.ui.translate_delete2.clicked.connect(lambda: TextProcessor.clear_text(self.ui.translate_output))
        self.ui.translate_delete.clicked.connect(lambda: TextProcessor.clear_text(self.ui.translator_input))
        self.ui.translate_delete.clicked.connect(lambda: TextProcessor.clear_text(self.ui.translate_output))

        self.ui.analyze_text_button.clicked.connect(self.analyze_text)
        self.ui.analysed_text_paste.clicked.connect(lambda: TextProcessor.paste_text(self.ui.analyze_input))
        self.ui.analyzed_text_copy.clicked.connect(lambda: TextProcessor.copy_text(self.ui.analyze_input))
        self.ui.analyxed_text_clear.clicked.connect(lambda: TextProcessor.clear_text(self.ui.analyze_input))
        self.ui.analyxed_text_clear.clicked.connect(lambda: TextProcessor.clear_text(self.ui.simvols_output_vsego))
        self.ui.analyxed_text_clear.clicked.connect(lambda: TextProcessor.clear_text(self.ui.simvols_output_probels))
        self.ui.analyxed_text_clear.clicked.connect(lambda: TextProcessor.clear_text(self.ui.simvols_output_bezprobelov))
        self.ui.analyxed_text_clear.clicked.connect(lambda: TextProcessor.clear_text(self.ui.voda_output))
        self.ui.analyxed_text_clear.clicked.connect(lambda: TextProcessor.clear_text(self.ui.toshnota_output))
        self.ui.analyxed_text_clear.clicked.connect(lambda: TextProcessor.clear_text(self.ui.slova_output_vsego))
        self.ui.analyxed_text_clear.clicked.connect(lambda: TextProcessor.clear_text(self.ui.slova_output_Achetyre))
        self.ui.analyxed_text_clear.clicked.connect(lambda: TextProcessor.clear_text(self.ui.slova_output_tetradnyxlistov))
        
        self.ui.set_white_theme_4.clicked.connect(self.set_white_theme)
        self.ui.set_black_theme_4.clicked.connect(self.set_black_theme)
        self.ui.set_custom_theme_4.clicked.connect(self.set_custom_theme)

        self.ui.background_set_file_open.clicked.connect(self.set_background_image)
        self.ui.background_reset.clicked.connect(self.reset_background)

        self.ui.function_create.clicked.connect(self.plot_function)
        self.ui.function_clear.clicked.connect(lambda: TextProcessor.clear_text(self.ui.function_lineEdit))

        self.ui.apps_widget_start.clicked.connect(self.toggle_apps_widget)

        self.floating_widget = OverlayedPlainTextEdit(self) 
        self.floating_widget.setGeometry(65, 10, 420, 270)
        self.floating_widget.update_floating_button_text("Открыть")  
        self.floating_widget.hide()  
    
    def handle_app_click(self, app_name):
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
        if self.apps_widget.isHidden():
            self.apps_widget.show_with_animation()
        else:
            self.apps_widget.hide_with_animation()

    def clear_draw_pad(self):
        self.draw_pad_area.shapes = []
        self.draw_pad_area.update()

    def plot_function(self):
        function_str = self.ui.function_lineEdit.text().strip()

        try:
            x = sp.symbols('x')
            func = sp.sympify(function_str)
            func_lambdified = sp.lambdify(x, func, "numpy")

            x_vals = np.linspace(-10, 10, 1000)
            y_vals = func_lambdified(x_vals)

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
        settings = {
            "theme": self.current_theme,
            "background_image": self.current_background,
            "background_image_name": os.path.basename(self.current_background) if self.current_background else ""
        }
        settings_path = os.path.join("data", "settings.json")
        os.makedirs(os.path.dirname(settings_path), exist_ok=True)
        with open(settings_path, "w") as settings_file:
            json.dump(settings, settings_file)
        print(f"Настройки сохранены: {settings}")

    def closeEvent(self, event):
        self.save_settings()
        event.accept()

    def load_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as settings_file:
                settings = json.load(settings_file)
                self.current_theme = settings.get("theme", "light")
                self.current_background = settings.get("background_image", None)

                print(f"Loaded theme: {self.current_theme}")

                self.apply_current_theme()

                if self.current_background:
                    self.apply_background(self.current_background)
                    file_name = os.path.basename(self.current_background)
                    self.ui.lineEdit.setText(file_name)
        else:
            self.apply_current_theme()

    def load_setting(self, key, default=None):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as settings_file:
                settings = json.load(settings_file)
                return settings.get(key, default)
        return default

    def set_background_image(self):
        project_dir = os.path.dirname(os.path.abspath(__file__))
        images_dir = os.path.join(project_dir, "resources", "backgrounds")

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбрать изображение",
            images_dir,
            "Images (*.png *.jpg *.jpeg);;All Files (*)"
        )

        if file_path:
            print(f"Выбрано изображение: {file_path}")
            self.current_background = file_path
            file_name = os.path.basename(file_path)
            self.ui.lineEdit.setText(file_name)
            self.apply_background(file_path)
        else:
            print("Файл не выбран.")

    def apply_background(self, image_path):
        if not os.path.exists(image_path):
            print("Файл не найден")
            return

        background_style = f"""
        QMainWindow {{
            background-image: url({image_path});
            background-repeat: no-repeat;
            background-position: center;
            background-size: cover;
        }}
        """

        existing_style = self.styleSheet()
        new_style = existing_style + background_style
        self.setStyleSheet(new_style)

    def reset_background(self):
        self.current_background = None
        self.ui.lineEdit.clear()

        existing_style = self.styleSheet()

        new_style = re.sub(r"QMainWindow\s*{[^}]*background-image[^}]*}", "", existing_style)
        self.setStyleSheet(new_style.strip())

        theme = self.load_setting("theme", "light")
        self.apply_current_theme()

    def apply_theme(self, theme_path):
        try:
            with open(theme_path, "r") as file:
                theme_style = file.read()
                self.setStyleSheet(theme_style)
        except FileNotFoundError:
            print(f"Тема {theme_path} не найдена.")
        except Exception as e:
            print(f"Ошибка при загрузке темы: {e}")

    def set_white_theme(self):
        self.apply_theme("resources/styles/light_theme.qss")
        self.current_theme = "light"

    def set_black_theme(self):
        self.apply_theme("resources/styles/dark_theme.qss")
        self.current_theme = "dark"
        
    def set_custom_theme(self):
        self.apply_theme("resources/styles/custom_theme.qss")
        self.current_theme = "custom"

    def apply_current_theme(self):
        if self.current_theme == "light":
            self.set_white_theme()
        elif self.current_theme == "dark":
            self.set_black_theme()
        elif self.current_theme == "custom":
            self.set_custom_theme()
        else:
            self.set_white_theme()

    def analyze_text(self):
        text = self.ui.analyze_input.toPlainText()

        results = self.calculate_text_metrics(text)

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

        words = re.findall(r'\b\w+\b', text) 
        total_words = len(words)

        a4_pages = total_words / 250
        notebook_pages = total_words / 80

        stop_words = set(data['stop_words'])
        water_words = [word for word in words if word.lower() in stop_words]
        water_percentage = len(water_words) / total_words * 100 if total_words > 0 else 0

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
                start_time = time.time()

                translated = GoogleTranslator(target=target_language).translate(input_text)
                self.ui.translate_output.setPlainText(translated)

                end_time = time.time()
                elapsed_time = end_time - start_time

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
            "Испанский": "es",
            "Итальянский": "it", 
            "Португальский": "pt",
            "Японский": "ja",
            "Китайский": "zh-cn",
            "Корейский": "ko",
            "Турецкий": "tr",
            "Арабский": "ar",
            "Хинди": "hi",
            "Вьетнамский": "vi",
            "Тайский": "th",
            "Белорусский": "be",
            "Казахский": "kk",
            "Украинский": "uk",
            "Польский": "pl",
            "Чешский": "cs",
            "Венгерский": "hu",
            "Греческий": "el",
            "Иврит": "he",
            "Персидский": "fa"
        }
        current_language = self.ui.translator_languages_comboBox.currentText()
        return languages.get(current_language, "en")


    def switch_page(self, index):
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

        self.animation_out.start()
        self.animation_in.start()

    def finalize_switch_page(self, index, current_widget):
        self.ui.stackedWidget.setCurrentIndex(index)
        current_widget.hide()  
        self.isAnimating = False  

    def show_with_animation(self):
        self.setWindowOpacity(0)
        self.show()
        self.animation = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def hide_apps_widget(self):
        if self.apps_widget.isVisible() and not self.apps_widget.isAnimating:
            self.apps_widget.hide_with_animation()


class SettingsManager:
    @staticmethod
    def load_settings() -> Dict:
        try:
            with open(SETTINGS_FILE, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {"theme": DEFAULT_THEME, "background_image": None}
    
    @staticmethod
    def save_settings(settings: Dict):
        with open(SETTINGS_FILE, 'w') as file:
            json.dump(settings, file)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()  
    window.show()
    sys.exit(app.exec())

