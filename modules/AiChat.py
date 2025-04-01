import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
                            QScrollArea, QLabel, QFrame, QSizePolicy, QMessageBox,
                            QProgressBar, QGraphicsOpacityEffect, QTextBrowser)
from PyQt6.QtCore import (Qt, QSize, pyqtSignal, QThread, QPropertyAnimation, 
                         QEasingCurve, QSequentialAnimationGroup, QTimer, QPoint, QRect)
from PyQt6.QtGui import QFont, QColor, QPalette, QKeyEvent, QIcon
from mistralai import Mistral
import markdown


API_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "api.json")


__all__ = ['AIChat', 'AIChatWindow', 'Worker', 'MessageWidget', 'ChatArea']

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

class LoadingIndicator(QProgressBar):

    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(False)
        self.setRange(0, 0)  
        self.setFixedHeight(4)
        self.setValue(0)
        self.setObjectName("loading_indicator")

class ExpandingTextBrowser(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.setWordWrapMode(self.document().defaultTextOption().wrapMode())
    
    def updateHeight(self):
        width = self.viewport().width() or 300
        self.document().setTextWidth(width)
        new_height = self.document().size().height() + 10
        self.setFixedHeight(int(new_height))
    
    def setHtml(self, html: str) -> None:
        super().setHtml(html)
        self.updateHeight()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateHeight()


class MessageWidget(QFrame):

    
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setObjectName("user_message" if is_user else "ai_message")
        
        layout = QVBoxLayout(self)
        
        sender = QLabel("Вы" if is_user else "ИИ")
        sender.setObjectName("sender_label")
        font = QFont()
        font.setBold(True)
        sender.setFont(font)
        layout.addWidget(sender)

        if is_user:
            self.message_widget = QLabel(text)
            self.message_widget.setWordWrap(True)
            self.message_widget.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        else:
          
            self.message_widget = ExpandingTextBrowser()
            self.message_widget.setHtml(text)
            self.message_widget.setFrameStyle(QFrame.Shape.NoFrame)
            self.message_widget.setReadOnly(True)
            self.message_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        layout.addWidget(self.message_widget)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
    
    def animate_appearance(self):
        """Анимирует появление сообщения через изменение прозрачности"""
        opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacity_effect)
        self.animation = QPropertyAnimation(opacity_effect, b"opacity")
        self.animation.setDuration(250)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()

class ChatArea(QScrollArea):
    """Область чата с прокруткой"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setObjectName("chat_area")
        self.setFrameShape(QFrame.Shape.NoFrame)  
        

        self.container = QWidget()
        self.container.setObjectName("chat_container")
        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(15, 15, 15, 15)  
        self.setWidget(self.container)
    
    def add_message(self, text, is_user=True):
        """Добавляет новое сообщение в чат с анимацией"""
        message_widget = MessageWidget(text, is_user)
        self.layout.addWidget(message_widget)
        

        message_widget.adjustSize()
        message_widget.setMinimumHeight(message_widget.sizeHint().height())
        message_widget.setMaximumHeight(message_widget.sizeHint().height())
        

        QTimer.singleShot(10, lambda: self.verticalScrollBar().setValue(self.verticalScrollBar().maximum()))
        
        QTimer.singleShot(0, message_widget.animate_appearance)
        
        return message_widget

    def add_message(self, text, is_user=True):
        """Добавляет новое сообщение в чат с анимацией"""
        message_widget = MessageWidget(text, is_user)
        self.layout.addWidget(message_widget)
    
    
        QTimer.singleShot(10, lambda: self.verticalScrollBar().setValue(self.verticalScrollBar().maximum()))
        QTimer.singleShot(0, message_widget.animate_appearance)
    
        return message_widget


class EnhancedTextEdit(QTextEdit):

    
    enterPressed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def keyPressEvent(self, event: QKeyEvent):
        """Обработка нажатия клавиш"""
        if event.key() == Qt.Key.Key_Return and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:

            self.enterPressed.emit()
        elif event.key() == Qt.Key.Key_Return and event.modifiers() & Qt.KeyboardModifier.ShiftModifier:

            super().keyPressEvent(event)
        else:

            super().keyPressEvent(event)

class AIChat(QWidget):

    processing_changed = pyqtSignal(bool)
    
    def __init__(self, parent=None, use_default_api_key=True, custom_api_key=None):
        super().__init__(parent)
        if use_default_api_key:
            self.api_key = self._load_api_key()
        else:
            self.api_key = custom_api_key
            
        self.md = self._setup_markdown()
        self.is_processing = False
        self.setup_ui()
        
    def _load_api_key(self):
        try:
            if os.path.exists(API_FILE):
                with open(API_FILE, 'r') as file:
                    return json.load(file).get('api_key')
            return None
        except Exception as e:
            print(f"Ошибка при загрузке API ключа: {str(e)}")
            return None
    
    def _setup_markdown(self):
        """Настройка обработчика Markdown"""
        return markdown.Markdown(extensions=[
            'fenced_code',
            'tables',
            'nl2br',
            'codehilite',
            'sane_lists',
            'smarty',
            'meta'
        ])
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0) 
        self.setObjectName("ai_chat_widget")  

        self.chat_area = ChatArea()
        self.chat_area.setObjectName("chat_area")
        main_layout.addWidget(self.chat_area)

        self.loading_indicator = LoadingIndicator()
        self.loading_indicator.hide()
        main_layout.addWidget(self.loading_indicator)

        input_layout = QHBoxLayout()
        
        self.message_input = EnhancedTextEdit()
        self.message_input.setPlaceholderText("Введите ваше сообщение... (Shift+Enter для новой строки)")
        self.message_input.setMaximumHeight(100)
        self.message_input.textChanged.connect(self.adjust_input_height)
        self.message_input.enterPressed.connect(self.send_message)
        
        self.send_button = QPushButton()
        self.send_button.setObjectName("send_button")
        self.send_button.setToolTip("Отправить сообщение")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setMinimumWidth(50)
        self.send_button.setMinimumHeight(50)
        self.send_button_icon_path = "icons/dark/send.png"
        self.send_button.setIcon(QIcon(self.send_button_icon_path))
        self.send_button.setIconSize(QSize(36, 36))
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        
        main_layout.addLayout(input_layout)
        
        self.chat_area.add_message("Привет! Я ИИ-ассистент. Чем я могу вам помочь сегодня?", False)
    
    def adjust_input_height(self):
        document_height = self.message_input.document().size().height()
        new_height = min(max(50, document_height + 10), 100)
        self.message_input.setMinimumHeight(int(new_height))
    
    def set_api_key(self, api_key):

        self.api_key = api_key
    
    def clear_chat(self):

        for i in reversed(range(self.chat_area.layout.count())): 
            widget = self.chat_area.layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        

        self.chat_area.add_message("Привет! Я ИИ-ассистент. Чем я могу вам помочь сегодня?", False)
    
    def send_message(self):

        if self.is_processing:
            return
            
        message_text = self.message_input.toPlainText().strip()
        if not message_text:
            return
            
        if not self.api_key:
            QMessageBox.critical(
                self,
                "Ошибка",
                "API ключ не установлен. Пожалуйста, установите API ключ в настройках."
            )
            return
        

        self.is_processing = True
        self.processing_changed.emit(True)
        

        self.message_input.setReadOnly(True)
        self.send_button.setEnabled(False)
        
        self.loading_indicator.show()
            

        self.chat_area.add_message(message_text, True)
        

        self.message_input.clear()
        

        self.worker = Worker(self.api_key, message_text)
        self.worker.result_signal.connect(self.handle_ai_response)
        self.worker.start()
    
    def handle_ai_response(self, user_input, response_text):

        self.loading_indicator.hide()

        ai_response_html = self.md.convert(response_text)
        self.chat_area.add_message(ai_response_html, False)

        self.md.reset()
        

        self.message_input.setReadOnly(False)
        self.send_button.setEnabled(True)
        self.message_input.setFocus()
        

        self.is_processing = False
        self.processing_changed.emit(False)

class AIChatWindow(QMainWindow):

    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Чат с ИИ")
        self.resize(800, 600)
        

        self.chat_widget = AIChat()
        self.setCentralWidget(self.chat_widget)
        

        self.apply_styles()
    
    def apply_styles(self):
        """Применяет стили к элементам интерфейса"""
        self.setStyleSheet("""
            #user_message {
                background-color: #161616;
                border: 1px solid #2e2e2e;
                border-radius: 10px;
                padding: 10px;
                margin-left: 50px;
            }
            
            #ai_message {
                background-color: #212121;
                border: 1px solid #2e2e2e;
                border-radius: 10px;
                padding: 10px;
                margin-right: 50px;
            }
            
            #sender_label {
                color: #cccccc;
                font-weight: bold;
            }
            
            QTextEdit, QLineEdit {
                background-color: #161616;
                color: white;
                border: 1px solid #2e2e2e;
                border-radius: 6px;
                padding: 5px;
            }
            
            QPushButton {
                background-color: #161616;
                color: white;
                border: 0px solid transparent;
                border-radius: 6px;
                padding: 8px;
            }
            
            QPushButton:hover {
                background-color: #252525;
            }
            
            QPushButton:pressed {
                background-color: #323232;
            }
            
            QPushButton:disabled {
                background-color: #0f0f0f;
                color: #444444;
            }
            
            QScrollArea {
                border: none;
                background-color: #0f0f0f;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #161616;
                width: 10px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background: #323232;
                min-height: 20px;
                border-radius: 5px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            
            #loading_indicator {
                background-color: #212121;
                border-radius: 2px;
                text-align: center;
            }
            
            #loading_indicator::chunk {
                background-color: #1e88e5;
                border-radius: 2px;
            }
        """)


def get_chat_styles():
    return """
        #user_message {
            background-color: #161616;
            border: 1px solid #2e2e2e;
            border-radius: 10px;
            padding: 10px;
            margin-left: 50px;
        }
        
        #ai_message {
            background-color: #212121;
            border: 1px solid #2e2e2e;
            border-radius: 10px;
            padding: 10px;
            margin-right: 50px;
        }
        
        #sender_label {
            color: #cccccc;
            font-weight: bold;
        }
        
        #loading_indicator {
            background-color: #212121;
            border-radius: 2px;
            text-align: center;
        }
        
        #loading_indicator::chunk {
            background-color: #1e88e5;
            border-radius: 2px;
        }
    """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AIChatWindow()
    window.show()
    sys.exit(app.exec())
