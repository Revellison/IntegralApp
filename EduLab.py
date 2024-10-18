#pyinstaller --noconfirm --onedir --windowed --clean --log-level=DEBUG --hidden-import=scipy.special._cdflib --hidden-import=setuptools.msvc --exclude-module=tzdata your_script.py
#(old)pyinstaller --noconfirm --onedir --windowed --clean --log-level=DEBUG --hidden-import=scipy.special._cdflib --hidden-import=setuptools.msvc your_script.py
#pyinstaller --noconfirm --onedir --windowed --clean --hidden-import=func --hidden-import=googletrans --hidden-import=googlesearch --hidden-import=tqdm --hidden-import=requests --hidden-import=bs4 --hidden-import=sklearn.feature_extraction.text.TfidfVectorizer --hidden-import=sklearn.metrics.pairwise.cosine_similarity --exclude-module=tkinter your_script.py
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QFileDialog
from design2 import Ui_EduLab  # Импортируем интерфейс из сгенерированного файла
from collections import Counter
from deep_translator import GoogleTranslator
import func  # Импортируем файл с функциями
import time
import re
import json
import os


class MyApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_background = None  # Переменная для хранения пути к текущему изображению
        self.isAnimating = False
        self.ui = Ui_EduLab()  # Создаем объект интерфейса
        self.ui.setupUi(self)  # Инициализируем интерфейс
        self.setFixedSize(800, 600)  # Фиксируем размер окна
        self.ui.stackedWidget.setCurrentIndex(0)  # Устанавливаем начальную страницу
        #self.apply_theme("styles/light_theme.qss")
        self.current_theme = "light"  # По умолчанию светлая тема
        self.load_settings()  # Загружаем и применяем сохранённые настройки
        # Убираем стандартный заголовок окна
        #self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        #ytdn

            
        # Привязка пользовательских кнопок к действиям
        self.ui.close.clicked.connect(self.animate_close)  # Кнопка закрытия с анимацией
        self.ui.rollup.clicked.connect(self.animate_minimize)  # Кнопка сворачивания с анимацией

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
        self.ui.ynikalnost_output.setReadOnly(True)

        # Привязка функций к кнопкам для проверки текста
        self.ui.paste1.clicked.connect(lambda: func.paste_text(self.ui.inputYandex))  # Кнопка вставки
        self.ui.copy1.clicked.connect(lambda: func.copy_text(self.ui.inputYandex))  # Кнопка копирования
        self.ui.copy2.clicked.connect(lambda: func.copy_text(self.ui.outputYandex))  # Кнопка копирования
        self.ui.errorcopy.clicked.connect(lambda: func.copy_text(self.ui.errorlog))  # Кнопка копирования ошибок
        self.ui.delete1.clicked.connect(lambda: func.clear_text(self.ui.inputYandex))  # Кнопка удаления
        self.ui.delete2.clicked.connect(lambda: func.clear_text(self.ui.outputYandex))  # Кнопка удаления
        self.ui.deleteerrors.clicked.connect(lambda: func.clear_text(self.ui.errorlog))  # Кнопка удаления ошибок
        self.ui.checktext.clicked.connect(lambda: func.check_text(  # Кнопка проверки текста
            self.ui.inputYandex,
            self.ui.outputYandex,
            self.ui.errorlog
        ))



        # Переключение страниц
        self.ui.open1_textreworker_pg3.clicked.connect(lambda: self.switch_page(2))  # Привязка кнопки к переключению на страницу 2
        self.ui.settings_pg2.clicked.connect(lambda: self.switch_page(1))  # Привязка кнопки к переключению на страницу 1
        self.ui.textanalyzer_open_page6.clicked.connect(lambda: self.switch_page(5))  # Привязка кнопки к переключению на страницу 6
        self.ui.translator_open_page4.clicked.connect(lambda: self.switch_page(3))  # Привязка кнопки к переключению на страницу 4
        self.ui.drygoe_open_page5.clicked.connect(lambda: self.switch_page(4))  # Привязка кнопки к переключению на страницу 4
        self.ui.home_pg1.clicked.connect(lambda: self.switch_page(0))  # Привязка кнопки к переключению на страницу 0        #self.ui.ynikalnost_button_pg7.clicked.connect(lambda: self.switch_page(6))  # Привязка кнопки к переключению на страницу 6

        # Перемещение окна
        self.dragPos = None

        # Привязка функций к кнопкам для переводчика
        self.translator = GoogleTranslator()  # Исправлено: инициализация переводчика
        self.ui.translate_button.clicked.connect(self.translate_text)

        # Привязываем кнопки к функциям
        self.ui.translate_button.clicked.connect(self.translate_text)  # Кнопка "Перевести"
        self.ui.translate_paste.clicked.connect(lambda: func.paste_text(self.ui.translator_input))  # Кнопка вставки1
        self.ui.translatecopy.clicked.connect(lambda: func.copy_text(self.ui.translator_input))  # Кнопка копирования1
        self.ui.translate_delete.clicked.connect(lambda: func.clear_text(self.ui.translator_input))  # Кнопка удаления1
        # второе поле
        self.ui.translatecopy_2.clicked.connect(lambda: func.copy_text(self.ui.translate_output))  # Кнопка копирования2
        self.ui.translate_delete2.clicked.connect(lambda: func.clear_text(self.ui.translate_output))  # Кнопка удаления2

        # анализатор текста
        self.ui.analyze_text_button.clicked.connect(self.analyze_text)
        self.ui.analysed_text_paste.clicked.connect(lambda: func.paste_text(self.ui.analyze_input))  # Кнопка вставки1
        self.ui.analyzed_text_copy.clicked.connect(lambda: func.copy_text(self.ui.analyze_input))  # Кнопка копирования1
        self.ui.analyxed_text_clear.clicked.connect(lambda: func.clear_text(self.ui.analyze_input))  # Кнопка удаления1
        #SETTINGS
        #темы
        self.ui.set_white_theme.clicked.connect(self.set_white_theme)
        self.ui.set_black_theme.clicked.connect(self.set_black_theme)
        #savebutton
        self.ui.save_settings.clicked.connect(self.save_settings)
        # Привязываем кнопки для установки и сброса фона
        self.ui.background_set_file_open.clicked.connect(self.set_background_image)
        self.ui.background_reset.clicked.connect(self.reset_background)


    def save_settings(self):
        #Сохранить настройки в файл
        settings = {
            "theme": self.current_theme,  # Сохраняем текущую тему
            "background_image": self.current_background  # Сохраняем текущий путь к изображению фона
        }
        with open("settings.json", "w") as settings_file:
            json.dump(settings, settings_file)
        print(f"Settings saved: {settings}")  # Отладочная информация

    def load_settings(self):
        #Загрузить настройки из файла
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as settings_file:
                settings = json.load(settings_file)
                self.current_theme = settings.get("theme", "light")  # Загрузить текущую тему
                self.current_background = settings.get("background_image", None)  # Загрузить путь к изображению фона

                print(f"Loaded theme: {self.current_theme}")  # Отладочная информация

                # Применяем загруженную тему
                if self.current_theme == "dark":
                    self.set_black_theme()  # Применяем тёмную тему
                else:
                    self.set_white_theme()  # Применяем светлую тему

                # Если путь к изображению фона существует, применяем его
                if self.current_background:
                    self.apply_background(self.current_background)  # Устанавливаем изображение как фон
                    self.ui.lineEdit.setText(self.current_background)  # Устанавливаем текст в lineEdit
        else:
            # Если файл настроек не существует, устанавливаем тему по умолчанию
            self.set_white_theme()

    def load_setting(self, key, default=None):
        """Загрузить конкретный параметр из файла настроек."""
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as settings_file:
                settings = json.load(settings_file)
                return settings.get(key, default)
        return default

    def set_background_image(self):
        #Выбор изображения и установка его как фон.
        try:
            # Вызываем диалог выбора файла
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Выбрать изображение", "", "Images (*.png *.jpg *.jpeg);;All Files (*)"
            )

            # Проверяем, выбран ли файл
            if file_path:
                self.current_background = file_path  # Сохраняем путь к изображению
                self.ui.lineEdit.setText(file_path)  # Выводим путь к изображению в lineEdit
                self.apply_background(file_path)  # Устанавливаем изображение как фон
            else:
                print("Файл не выбран.")

        except Exception as e:
            print(f"Ошибка при выборе или установке фона: {e}")  # Печатаем ошибку для отладки

    def apply_background(self, image_path):
        if not os.path.exists(image_path):
            print("Файл не найден")
            return

        # Сохраняем текущие стили
        current_style = self.styleSheet()

        # Создаем стиль для фона
        background_style = f"""
        QMainWindow {{
            background-image: url({image_path});
            background-repeat: no-repeat;
            background-position: center;
        }}
        """

        # Применяем новый стиль фона поверх существующих стилей
        self.setStyleSheet(current_style + background_style)

    def reset_background(self):
        """Сбросить фон до исходного состояния и применить соответствующую тему."""
        self.current_background = None  # Удаляем путь к изображению
        self.ui.lineEdit.clear()  # Очищаем lineEdit
        self.setStyleSheet("")  # Сбрасываем все стили, возвращая фон по умолчанию

        # Загружаем конкретный параметр (например, тему)
        theme = self.load_setting("theme", "light")  # По умолчанию светлая тема
        if theme == "dark":
            self.set_black_theme()  # Применяем тёмную тему
        else:
            self.set_white_theme()  # Применяем светлую тему

    def apply_theme(self, theme_file):
        """Загрузить и применить тему из QSS файла."""
        with open(theme_file, "r") as f:
            style = f.read()
            self.setStyleSheet(style)

    def set_white_theme(self):
        """Установить светлую тему."""
        print("Applying white theme")  # Отладочная информация
        self.apply_theme("styles/light_theme.qss")
        self.current_theme = "light"

    def set_black_theme(self):
        """Установить темную тему."""
        print("Applying black theme")  # Отладочная информация
        self.apply_theme("styles/dark_theme.qss")
        self.current_theme = "dark"

    def analyze_text(self):
        """Функция анализа текста и вывода результатов."""
        text = self.ui.analyze_input.toPlainText()  # Получаем текст из поля ввода и удаляем лишние пробелы

        # Проверка: если поле ввода пустое, выводим сообщение и завершаем функцию
        if not text:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Поле ввода пустое! Пожалуйста, введите текст для анализа.")

            return

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
        """Вычисляем метрики текста."""
        total_characters = len(text)
        total_spaces = text.count(' ')
        non_space_characters = total_characters - total_spaces

        # Подсчет слов
        words = re.findall(r'\b\w+\b', text)  # Поиск всех слов
        total_words = len(words)

        # Подсчет страниц A4 и тетрадных страниц
        a4_pages = total_words / 250
        notebook_pages = total_words / 80

        # Подсчет "воды" через стоп-слова
        stop_words = {
            "и", "в", "на", "с", "по", "а", "но", "или", "для", "что", "к", "от", "из", "у", "же",
            "так", "как", "о", "за", "это", "он", "она", "оно", "мы", "вы", "они", "ты", "уже",
            "этот", "то", "все", "когда", "если", "бы", "тот", "также", "было", "будет",
            "был", "быть", "во", "при", "об", "из-за", "под", "без", "да", "нет", "ли", "тем",
            "чем", "что-то", "кто", "где", "там", "сюда", "здесь", "поэтому", "однако", "например",
            "тем не менее", "впрочем", "в общем", "короче говоря", "таким образом", "кроме того",
            "и т.д.", "и т.п.", "и др.", "в частности", "уважаемые", "дорогие", "клиенты",
            "посетители", "гарантия качества", "команда профессионалов", "большой опыт",
            "гибкая ценовая политика", "восхитительно", "невероятно", "красивые", "просто",
            "очень", "совершенно", "прекрасно", "превосходно", "абсолютно"
        }
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
        """Функция перевода текста без определения языка и вывода отладочной информации."""
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
                self.ui.translator_otladka_output.setPlainText(f"Ошибка перевода: {str(e)}")
        else:
            self.ui.translator_otladka_output.setPlainText("Введите текст для перевода.")

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
            return  # Если анимация уже выполняется или нажата та же кнопка, ничего не делаем

        self.isAnimating = True  # Устанавливаем флаг анимации

        current_widget = self.ui.stackedWidget.currentWidget()
        next_widget = self.ui.stackedWidget.widget(index)

        # Устанавливаем начальные параметры для следующего виджета
        next_widget.setGeometry(current_widget.geometry())  # Совпадение геометрии текущего виджета
        next_widget.show()  # Показываем следующий виджет

        # Анимация для текущего виджета (выход вниз)
        self.animation_out = QtCore.QPropertyAnimation(current_widget, b"geometry")
        self.animation_out.setDuration(500)
        self.animation_out.setStartValue(current_widget.geometry())
        self.animation_out.setEndValue(QtCore.QRect(
            current_widget.x(),
            current_widget.y() + current_widget.height(),  # Двигаем вниз
            current_widget.width(),
            current_widget.height()
        ))

        # Анимация для следующего виджета (вход сверху)
        self.animation_in = QtCore.QPropertyAnimation(next_widget, b"geometry")
        self.animation_in.setDuration(500)
        self.animation_in.setStartValue(QtCore.QRect(
            next_widget.x(),
            next_widget.y() - next_widget.height(),  # Начальная позиция сверху
            next_widget.width(),
            next_widget.height()
        ))
        self.animation_in.setEndValue(current_widget.geometry())  # Конечная позиция

        # Устанавливаем эффект ease in-out
        self.animation_out.setEasingCurve(QtCore.QEasingCurve.Type.InOutCirc)
        self.animation_in.setEasingCurve(QtCore.QEasingCurve.Type.InOutCirc)

        # Переключение страниц после завершения анимации выхода
        self.animation_out.finished.connect(lambda: self.finalize_switch_page(index, current_widget))

        # Запуск анимаций
        self.animation_out.start()
        self.animation_in.start()

    def finalize_switch_page(self, index, current_widget):
        """Завершение переключения страницы."""
        self.ui.stackedWidget.setCurrentIndex(index)
        current_widget.hide()  # Скрываем текущий виджет после анимации
        self.isAnimating = False  # Сбрасываем флаг анимации

    def mousePressEvent(self, event):
        """Отслеживаем нажатие мыши для перемещения окна."""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.dragPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        """Отслеживаем перемещение мыши для перемещения окна."""
        if self.dragPos is not None:
            delta = event.globalPosition().toPoint() - self.dragPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.dragPos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        """Сбрасываем перемещение окна при отпускании кнопки мыши."""
        self.dragPos = None

    def animate_close(self):
        """Анимация закрытия окна."""
        self.animation = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)  # Длительность анимации в миллисекундах
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.finished.connect(self.close_application)
        self.animation.start()

    def close_application(self):
        """Закрыть приложение."""
        self.close()

    def animate_minimize(self):
        """Анимация сворачивания окна."""
        # Получаем текущие размеры окна
        start_geometry = self.geometry()
        # Определяем конечные размеры — минимальная высота (например, свернуть в верхнюю панель)
        end_geometry = QtCore.QRect(start_geometry.x(), start_geometry.y(), start_geometry.width(), 0)

        # Настраиваем анимацию геометрии
        self.animation = QtCore.QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)  # Длительность анимации в миллисекундах
        self.animation.setStartValue(start_geometry)
        self.animation.setEndValue(end_geometry)
        self.animation.finished.connect(self.showMinimized)  # Сворачиваем окно после анимации
        self.animation.start()

    def show_with_animation(self):
        """Анимация открытия окна."""
        self.setWindowOpacity(0)
        self.show()
        self.animation = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show_with_animation()  # Запуск с анимацией
    sys.exit(app.exec())
