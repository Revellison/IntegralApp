
import json
import os
import re
import sys
from typing import Optional
from mistralai import Mistral
from PyQt6 import QtWidgets
from PyQt6.QtCore import (QThread,pyqtSignal)
import markdown
import subprocess

# Определение API_FILE как пути к файлу в корне проекта
API_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "api.json")

class Worker(QThread):
    result_signal = pyqtSignal(str, str)

    def __init__(self, api_key: str, user_input: str):
        super().__init__()
        self.api_key = api_key
        self.user_input = user_input

    def run(self):
        try:
            client = Mistral(api_key=self.api_key)
            response = client.chat.complete(
                model="mistral-small-latest",
                messages=[{"role": "user", "content": self.user_input}]
            )
            
            response_text = response.choices[0].message.content if response.choices else "Ошибка. Ответ не был сгенерирован."
            self.result_signal.emit(self.user_input, response_text)
            
        except Exception as e:
            self.result_signal.emit(self.user_input, f"Произошла ошибка: {str(e)}")

class ChatLogic:
    def __init__(self, ui):
        self.ui = ui
        # Получаем ссылку на главное окно
        self.main_window = self.ui.centralwidget.window()
        self.api_key = self._load_api_key()
        self._connect_signals()
        self._setup_markdown()
        
        # Устанавливаем API ключ в поле ввода при запуске, если он существует
        if self.api_key:
            self.ui.mistralAPI_input.setText(self.api_key)
    
    def _connect_signals(self):
        """Подключение сигналов к слотам"""
        self.ui.sendmessage_button.clicked.connect(self.send_request)
        self.ui.mistralAPIuseButton.clicked.connect(self.set_api_key)
    
    def _load_api_key(self) -> Optional[str]:
        """Загрузка API ключа из файла"""
        try:
            # Проверяем существование файла API_FILE
            if os.path.exists(API_FILE):
                with open(API_FILE, 'r') as file:
                    return json.load(file).get('api_key')
            
            # Проверяем альтернативный путь в директории data
            data_api_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "api.json")
            if os.path.exists(data_api_path):
                with open(data_api_path, 'r') as file:
                    return json.load(file).get('api_key')
            
            return None
        except Exception as e:
            print(f"Ошибка при загрузке API ключа: {str(e)}")
            return None
    
    def set_api_key(self):
        """Установка и сохранение API ключа"""
        try:
            new_key = self.ui.mistralAPI_input.text().strip()
            if not new_key:
                QtWidgets.QMessageBox.warning(
                    self.main_window,  # Используем главное окно вместо self.ui
                    "Ошибка",
                    "API ключ не может быть пустым."
                )
                return
                
            # Проверяем валидность ключа
            if not self._validate_api_key(new_key):
                QtWidgets.QMessageBox.warning(
                    self.main_window,  # Используем главное окно вместо self.ui
                    "Ошибка",
                    "Неверный формат API ключа."
                )
                return
                
            self.api_key = new_key
            self._save_api_key()
            
            QtWidgets.QMessageBox.information(
                self.main_window,  # Используем главное окно вместо self.ui
                "Успех",
                "API ключ успешно сохранен."
            )
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self.main_window,  # Используем главное окно вместо self.ui
                "Ошибка",
                f"Произошла ошибка при сохранении API ключа: {str(e)}"
            )
    
    def _validate_api_key(self, key: str) -> bool:
        """Проверка формата API ключа"""
        # Базовая проверка - ключ должен быть непустой строкой определенной длины
        # Можно добавить более сложную валидацию при необходимости
        return isinstance(key, str) and len(key) > 0
    
    def _save_api_key(self):
        """Сохранение API ключа в файл"""
        try:
            # Убедимся, что директория существует
            os.makedirs(os.path.dirname('data/api.json'), exist_ok=True)
            with open('data/api.json', 'w') as file:
                json.dump({'api_key': self.api_key}, file)
        except Exception as e:
            print(f"Ошибка при сохранении API ключа: {str(e)}")
            raise

    def send_request(self):
        """Отправка запроса к ИИ"""
        user_input = self.ui.response_input.text().strip()
        if not user_input:
            QtWidgets.QMessageBox.warning(
                self.main_window,
                "Ошибка",
                "Поле запроса не может быть пустым!"
            )
            return

        if not self.api_key:
            QtWidgets.QMessageBox.critical(
                self.main_window,
                "Ошибка",
                "API ключ не установлен."
            )
            return

        # Добавляем инструкцию про маркеры кода
        instruction = """
        """
        user_input += instruction

        # Создаем и запускаем фоновый поток
        self.worker = Worker(self.api_key, user_input)
        self.worker.result_signal.connect(self.update_response)
        self.worker.start()

    def _setup_markdown(self):
        """Настройка обработчика Markdown с улучшенными стилями"""
        self.md = markdown.Markdown(extensions=[
            'fenced_code',    # Поддержка блоков кода
            'tables',         # Поддержка таблиц
            'nl2br',          # Перевод строк
            'codehilite',     # Подсветка синтаксиса
            'sane_lists',     # Улучшенные списки
            'smarty',         # Умные кавычки и тире
            'meta'            # Метаданные
        ])
        
        # Улучшенные стили для markdown
        markdown_style = """
            <style>
                /* Основные стили текста */
                body {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    padding: 10px;
                }
                
                /* Блоки кода */
                pre {
                    background-color: #f8f9fa;
                    border: 1px solid #eaecef;
                    border-radius: 6px;
                    padding: 16px;
                    overflow-x: auto;
                    margin: 10px 0;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 0.9em;
                }
                
                code {
                    font-family: 'Consolas', 'Monaco', monospace;
                    background-color: rgba(27,31,35,0.05);
                    border-radius: 3px;
                    padding: 0.2em 0.4em;
                    font-size: 0.9em;
                }
                
                /* Таблицы */
                table {
                    border-collapse: collapse;
                    width: 100%;
                    margin: 16px 0;
                    background-color: #ffffff;
                }
                
                th, td {
                    border: 1px solid #e1e4e8;
                    padding: 8px 16px;
                    text-align: left;
                }
                
                th {
                    background-color: #f6f8fa;
                    font-weight: 600;
                }
                
                tr:nth-child(even) {
                    background-color: #f8f9fa;
                }
                
                /* Цитаты */
                blockquote {
                    border-left: 4px solid #0366d6;
                    color: #6a737d;
                    margin: 16px 0;
                    padding: 0 16px;
                    background-color: #f6f8fa;
                    border-radius: 0 3px 3px 0;
                }
                
                /* Заголовки */
                h1, h2, h3, h4, h5, h6 {
                    margin-top: 24px;
                    margin-bottom: 16px;
                    font-weight: 600;
                    line-height: 1.25;
                    color: #24292e;
                }
                
                /* Списки */
                ul, ol {
                    padding-left: 2em;
                    margin: 16px 0;
                }
                
                li {
                    margin: 4px 0;
                }
                
                /* Горизонтальная линия */
                hr {
                    height: 0px;
                    background-color: #e1e4e8;
                    border: none;
                    margin: 24px 0;
                }
                
                /* Сообщения пользователя и ИИ */
                .user-message {
                    background-color: #f1f8ff;
                    border-left: 4px solid #0366d6;
                    padding: 12px;
                    margin: 8px 0;
                    border-radius: 0 4px 4px 0;
                }
                
                .ai-message {
                    background-color: #f6f8fa;
                    border-left: 4px solid #28a745;
                    padding: 12px;
                    margin: 8px 0;
                    border-radius: 0 4px 4px 0;
                }
                
                /* Ссылки */
                a {
                    color: #0366d6;
                    text-decoration: none;
                }
                
                a:hover {
                    text-decoration: underline;
                }
                
                /* Выделение */
                mark {
                    background-color: #fff3b8;
                    padding: 0.2em;
                    border-radius: 2px;
                }
            </style>
        """
        self.ui.response_area.document().setDefaultStyleSheet(markdown_style)

    def update_response(self, user_input, response_text):
        """Обновление области вывода с улучшенным форматированием"""
        # Форматируем сообщение пользователя
        user_message = f'<div class="user-message"><b>Вы:</b> {user_input}</div>'
        
        # Преобразуем Markdown в HTML для ответа ИИ
        ai_response_html = self.md.convert(response_text)
        ai_message = f'<div class="ai-message"><b>ИИ:</b><br>{ai_response_html}</div>'
        
        # Добавляем сообщения в область вывода без разделителя
        self.ui.response_area.append(user_message)
        self.ui.response_area.append(ai_message)
        
        # Прокручиваем до последнего сообщения
        scrollbar = self.ui.response_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Очищаем поле ввода
        self.ui.response_input.clear()
        
        # Сбрасываем состояние Markdown конвертера
        self.md.reset()
