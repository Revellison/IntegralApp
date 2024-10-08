from PyQt6 import QtWidgets, QtCore  # Импортируем необходимые модули
from design import Ui_EduLab  # Импортируем интерфейс из сгенерированного файла
import func  # Импортируем файл с функциями
from googletrans import Translator
import time
import re
from collections import Counter
class MyApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_EduLab()  # Создаем объект интерфейса
        self.ui.setupUi(self)  # Инициализируем интерфейс
        self.setFixedSize(800, 600)  # Фиксируем размер окна
        self.ui.stackedWidget.setCurrentIndex(0)  # Устанавливаем начальную страницу

        # Убираем стандартный заголовок окна
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

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
        self.ui.open1_textreworker_pg3.clicked.connect(
            lambda: self.switch_page(2))  # Привязка кнопки к переключению на страницу 2
        self.ui.settings_pg2.clicked.connect(
            lambda: self.switch_page(1))  # Привязка кнопки к переключению на страницу 1
        self.ui.textanalyzer_open_page6.clicked.connect(
            lambda: self.switch_page(5))  # Привязка кнопки к переключению на страницу 6
        self.ui.translator_open_page4.clicked.connect(
            lambda: self.switch_page(3))  # Привязка кнопки к переключению на страницу 4
        self.ui.drygoe_open_page5.clicked.connect(
            lambda: self.switch_page(4))  # Привязка кнопки к переключению на страницу 4
        self.ui.home_pg1.clicked.connect(
            lambda: self.switch_page(0))  # Привязка кнопки к переключению на страницу 0

        # Перемещение окна
        self.dragPos = None

        # Привязка функций к кнопкам для переводчика
        self.translator = Translator()

        # Привязываем кнопки к функциям
        self.ui.translate_button.clicked.connect(self.translate_text)  # Кнопка "Перевести"
        self.ui.translate_paste.clicked.connect(lambda: func.paste_text(self.ui.translator_input))  # Кнопка вставки1
        self.ui.translatecopy.clicked.connect(lambda: func.copy_text(self.ui.translator_input))  # Кнопка копирования1
        self.ui.translate_delete.clicked.connect(lambda: func.clear_text(self.ui.translator_input))  # Кнопка удаления1
        #второе поле
        self.ui.translatecopy_2.clicked.connect(lambda: func.copy_text(self.ui.translate_output))  # Кнопка копирования2
        self.ui.translate_delete2.clicked.connect(lambda: func.clear_text(self.ui.translate_output))  # Кнопка удаления2

        #анализатор текста
        self.ui.analyze_text_button.clicked.connect(self.analyze_text)
        self.ui.analysed_text_paste.clicked.connect(lambda: func.paste_text(self.ui.analyze_input))  # Кнопка вставки1
        self.ui.analyzed_text_copy.clicked.connect(lambda: func.copy_text(self.ui.analyze_input))  # Кнопка копирования1
        self.ui.analyxed_text_clear.clicked.connect(lambda: func.clear_text(self.ui.analyze_input))  # Кнопка удаления1
    def analyze_text(self):
        """Функция анализа текста и вывода результатов."""
        text = self.ui.analyze_input.toPlainText()  # Получаем текст из поля ввода

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
        notebook_pages = total_words / 100

        # Подсчет "воды" через стоп-слова
        stop_words = set(["и", "в", "на", "с", "по", "а", "но", "или", "для", "что"])  # Список стоп-слов
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
                translated = self.translator.translate(input_text, dest=target_language)
                self.ui.translate_output.setPlainText(translated.text)

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
        """Переключить страницы в stackedWidget."""
        if 0 <= index < self.ui.stackedWidget.count():  # Проверяем, существует ли индекс
            self.ui.stackedWidget.setCurrentIndex(index)
        else:
            print(f"Index {index} is out of range.")

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
