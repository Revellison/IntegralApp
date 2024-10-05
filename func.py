import requests
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtWidgets import QMessageBox, QMainWindow, QTextEdit, QVBoxLayout, QDialog


# Функция для проверки орфографии и пунктуации через Yandex Speller API
def check_spelling(text):
    params = {
        'text': text,
        'lang': 'ru'
    }
    response = requests.get('https://speller.yandex.net/services/spellservice.json/checkText', params=params)
    return response.json()


# Функция для обработки текста и вывода результата
def check_text(text_input, text_output, error_output):
    # Получаем текст из поля ввода
    input_text = text_input.toPlainText().strip()

    # Проверяем, что текст не пустой
    if not input_text:
        QMessageBox.warning(None, "Ошибка", "Поле ввода пустое!")
        return

    # Запрашиваем проверки орфографии через Yandex Speller API
    corrections = check_spelling(input_text)

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
        # Если ошибок не найдено
        QMessageBox.information(None, "Результат", "Ошибок не найдено.")
        text_output.setPlainText(input_text)
        error_output.clear()

# Функция для открытия отдельного окна с текстом из соответствующего поля
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


def clear_text(text_input):
    text_input.clear()  # Очищаем текстовое поле



def paste_text(text_input):
    clipboard_text = QtWidgets.QApplication.clipboard().text()  # Получаем текст из буфера обмена
    if clipboard_text:
        text_input.insertPlainText(clipboard_text)  # Вставляем текст в QTextEdit
    else:
        QtWidgets.QMessageBox.warning(None, "Ошибка", "Буфер обмена пуст!")  # Сообщение об ошибке



# Функция для создания контекстного меню
def create_context_menu(text_widget):
    context_menu = QtWidgets.QMenu()
    copy_action = context_menu.addAction("Копировать")
    cut_action = context_menu.addAction("Вырезать")
    paste_action = context_menu.addAction("Вставить")

    copy_action.triggered.connect(lambda: text_widget.copy())
    cut_action.triggered.connect(lambda: text_widget.cut())
    paste_action.triggered.connect(lambda: text_widget.paste())

    text_widget.setContextMenuPolicy(QtGui.Qt.ContextMenuPolicy.CustomContextMenu)
    text_widget.customContextMenuRequested.connect(lambda pos: context_menu.exec(text_widget.mapToGlobal(pos)))

def copy_text(text_input):
    text_to_copy = text_input.toPlainText()  # Получаем текст из QTextEdit
    if text_to_copy:
        QtWidgets.QApplication.clipboard().setText(text_to_copy)  # Копируем текст в буфер обмена

# Функция для копирования текста из поля ошибок
def copy_errors(error_output):
    clipboard = QtWidgets.QApplication.clipboard()
    clipboard.setText(error_output.toPlainText())

