#auto-py-to-exe
# pyuic6 -x qtdesign3.ui -o design2.py
from PyQt6.QtWidgets import QMessageBox, QMainWindow, QTextEdit, QVBoxLayout, QDialog
import re
from PyQt6 import QtWidgets, QtGui
from tqdm import tqdm
import requests



def clean_text(text):
    clean = re.sub(r'<.*?>', '', text)
    # Удаляем лишние пробелы
    clean = ' '.join(clean.split())
    return clean


def clear_text(text_input):

    text_input.clear()  # Очищаем текстовое поле


def paste_text(text_input):

    clipboard_text = QtWidgets.QApplication.clipboard().text()  # Получаем текст из буфера обмена
    if clipboard_text:
        cleaned_text = clean_text(clipboard_text)  # Очищаем текст
        text_input.insertPlainText(cleaned_text)  # Вставляем очищенный текст в QTextEdit
    else:
        QtWidgets.QMessageBox.warning(None, "Ошибка", "Буфер обмена пуст!")  # Сообщение об ошибке

def copy_text(text_input):

    text_to_copy = text_input.toPlainText()  # Получаем текст из QTextEdit
    if text_to_copy:
        QtWidgets.QApplication.clipboard().setText(text_to_copy)  # Копируем текст в буфер обмена

# Функция для копирования текста из поля ошибок
def copy_errors(error_output):

    clipboard = QtWidgets.QApplication.clipboard()
    clipboard.setText(error_output.toPlainText())


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






