from PyQt6 import QtWidgets, QtCore  # Импортируем необходимые модули
from design import Ui_EduLab  # Импортируем интерфейс из сгенерированного файла
import func  # Импортируем файл с функциями


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
        self.ui.outputYandex.setReadOnly(True)  # outputYandex только для чтения
        self.ui.errorlog.setReadOnly(True)  # errorlog только для чтения

        # Привязка функций к кнопкам
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

        # Перемещение окна
        self.dragPos = None

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
