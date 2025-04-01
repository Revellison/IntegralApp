from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QScrollArea, QVBoxLayout, QLabel
from PyQt6.QtGui import QIcon,QFont, QFontDatabase
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QParallelAnimationGroup, QEasingCurve
from PyQt6.QtWidgets import QGraphicsOpacityEffect
import os

class FloatingButtonWidget(QtWidgets.QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.paddingLeft = 5
        self.paddingTop = 5

    def update_position(self):
        if hasattr(self.parent(), 'viewport'):
            parent_rect = self.parent().viewport().rect()
        else:
            parent_rect = self.parent().rect()

        if not parent_rect:
            return

        x = parent_rect.width() - self.width() - self.paddingLeft
        y = self.paddingTop
        self.setGeometry(x, y, self.width(), self.height())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_position()

    def mousePressEvent(self, event):
        self.parent().floatingButtonClicked.emit()

class OverlayedPlainTextEdit(QtWidgets.QPlainTextEdit):
    floatingButtonClicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.floating_button = FloatingButtonWidget(parent=self)

    def update_floating_button_text(self, txt):
        self.floating_button.setText(txt)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.floating_button.update_position()

class AppButton(QPushButton):
    def __init__(self, icon_path, app_name, parent=None):
        super().__init__(parent)
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QtCore.QSize(32, 32))
        self.setToolTip(app_name)
        self.setMinimumSize(50, 50)
        self.setMaximumSize(50, 50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class CategoryWidget(QWidget):
    def __init__(self, category_name, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 5, 0, 10)
        
        label = QLabel(category_name)
        label.setStyleSheet("color: #E8F5E9; font-size: 12px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.buttons_container = QWidget()
        self.buttons_container.setObjectName("buttons_container")
        self.buttons_layout = QHBoxLayout(self.buttons_container)
        self.buttons_layout.setSpacing(10)
        self.buttons_layout.setContentsMargins(8, 8, 8, 8)
        self.buttons_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        layout.addWidget(label)
        layout.addWidget(self.buttons_container)

class AppsWidget(QWidget):
    appClicked = pyqtSignal(str)
    focusLost = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(300)
        self.setup_ui()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.isAnimating = False
        self.original_pos = None
        
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(20, 10, 20, 10)
        
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.categories_widget = QWidget()
        self.categories_layout = QVBoxLayout(self.categories_widget)
        self.categories_layout.setSpacing(15)
        self.categories_layout.setContentsMargins(0, 0, 0, 0)
        self.categories_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(self.categories_widget)
        self.main_layout.addWidget(scroll_area)
        
        self.add_categories()
        
    def add_categories(self):
        categories = {
            "Общие": [
                ("mistralAi.png", "ИИ чат")
            ],
            "Текст": [
                ("text_rework.png", "Орфографический анализатор"), 
                ("text_analyze.png", "СЕО анализатор текста"),
                ("translator.png", "Переводчик")
            ],
            "Математика": [
                ("calculator.png", "Калькулятор"),
                ("function.png", "Построение функций")
            ]
        }

        icons_path = os.path.join("icons", "widget")
        QFontDatabase.addApplicationFont("resources/fonts/onest.ttf")

        font = QFont()
        font.setFamily("onest")
        font.setPointSize(26)
        font.setBold(False)
        
        for category_name, apps in categories.items():
            category_widget = CategoryWidget(category_name)
            
            label = category_widget.findChild(QLabel)
            if label:
                label.setFont(font)
            
            for icon_file, app_name in apps:
                icon_path = os.path.join(icons_path, icon_file)
                if os.path.exists(icon_path):
                    button = AppButton(icon_path, app_name)
                    button.clicked.connect(lambda checked, name=app_name: self.handle_app_click(name))
                    category_widget.buttons_layout.addWidget(button)
                else:
                    print(f"Иконка не найдена: {icon_path}")
            
            self.categories_layout.addWidget(category_widget)
    def handle_app_click(self, app_name):
        self.appClicked.emit(app_name)
        self.hide_with_animation()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if not self.geometry().contains(self.mapFromGlobal(QtCore.QCursor.pos())):
            self.focusLost.emit()

    def show_with_animation(self):
        if self.isAnimating:
            return
            
        self.isAnimating = True
        
        if self.original_pos is None:
            self.original_pos = self.geometry()
        else:
            self.setGeometry(self.original_pos)
        
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)
        
        duration = 200
        
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(duration)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.Type.InQuad)
        
        start_geometry = QtCore.QRect(
            self.original_pos.x(),
            self.original_pos.y() - 10, 
            self.original_pos.width(),
            self.original_pos.height()
        )
        
        self.slide_in = QPropertyAnimation(self, b"geometry")
        self.slide_in.setDuration(duration)
        self.slide_in.setStartValue(start_geometry)
        self.slide_in.setEndValue(self.original_pos)
        self.slide_in.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        self.animation_group = QParallelAnimationGroup()
        self.animation_group.addAnimation(self.fade_in)
        self.animation_group.addAnimation(self.slide_in)
        
        self.show()
        self.animation_group.finished.connect(self.finish_show_animation)
        self.animation_group.start()
        
    def hide_with_animation(self):
        if self.isAnimating:
            return
            
        self.isAnimating = True
        
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)
        
        duration = 200  
        
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(duration)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        end_geometry = QtCore.QRect(
            self.original_pos.x(),
            self.original_pos.y() + 10,  
            self.original_pos.width(),
            self.original_pos.height()
        )
        
        self.slide_out = QPropertyAnimation(self, b"geometry")
        self.slide_out.setDuration(duration)
        self.slide_out.setStartValue(self.original_pos)
        self.slide_out.setEndValue(end_geometry)
        self.slide_out.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        self.animation_group = QParallelAnimationGroup()
        self.animation_group.addAnimation(self.fade_out)
        self.animation_group.addAnimation(self.slide_out)
        
        self.animation_group.finished.connect(self.finish_hide_animation)
        self.animation_group.start()
        
    def finish_show_animation(self):
        self.setGraphicsEffect(None)
        self.isAnimating = False
        self.setGeometry(self.original_pos)
        
    def finish_hide_animation(self):
        self.hide()
        self.setGraphicsEffect(None)
        self.isAnimating = False
        self.setGeometry(self.original_pos)
