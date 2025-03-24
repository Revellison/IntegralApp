from PyQt6.QtCore import Qt, QPoint, QRect, QSize
from PyQt6.QtGui import (QPainter, QPen, QBrush, QColor, QFont, QIcon, QPixmap,
                        QFontDatabase)
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
                           QComboBox, QDialog, QTextEdit, QPushButton, QLineEdit,
                           QFontDialog, QColorDialog, QInputDialog,
                           QApplication)
import math

__all__ = ['DrawPad', 'TextInputDialog']

class TextInputDialog(QDialog):
    def __init__(self, parent=None, existing_text=None, text_settings=None):
        super().__init__(parent)
        self.setWindowTitle("Ввод текста")
        self.resize(400, 300)
        
        self.text_settings = text_settings.copy() if text_settings else {
            "size": 12,
            "font": "Arial",
            "bold": False,
            "italic": False,
            "underline": False,
            "strikeout": False,
            "color": QColor(0, 0, 0),
        }
        
        layout = QVBoxLayout(self)
        
        self.text_input = QTextEdit()
        if existing_text:
            self.text_input.setText(existing_text)
        layout.addWidget(self.text_input)
        
        format_layout = QHBoxLayout()
        
        self.font_combo = QComboBox()
        self.font_combo.addItems(QFontDatabase.families())
        if self.text_settings["font"] in QFontDatabase.families():
            self.font_combo.setCurrentText(self.text_settings["font"])
        format_layout.addWidget(QLabel("Шрифт:"))
        format_layout.addWidget(self.font_combo)
        
        self.size_combo = QComboBox()
        self.size_combo.addItems([str(s) for s in [8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32, 36, 48, 72]])
        self.size_combo.setCurrentText(str(self.text_settings["size"]))
        format_layout.addWidget(QLabel("Размер:"))
        format_layout.addWidget(self.size_combo)
        
        self.color_button = QPushButton()
        self.color_button.setFixedSize(24, 24)
        self.update_color_button()
        self.color_button.clicked.connect(self.choose_color)
        format_layout.addWidget(QLabel("Цвет:"))
        format_layout.addWidget(self.color_button)
        
        layout.addLayout(format_layout)
        
        style_layout = QHBoxLayout()
        
        self.bold_check = QPushButton("Ж")
        self.bold_check.setCheckable(True)
        self.bold_check.setChecked(self.text_settings["bold"])
        self.bold_check.setFixedWidth(30)
        style_layout.addWidget(self.bold_check)
        
        self.italic_check = QPushButton("К")
        self.italic_check.setCheckable(True)
        self.italic_check.setChecked(self.text_settings["italic"])
        self.italic_check.setFixedWidth(30)
        style_layout.addWidget(self.italic_check)
        
        self.underline_check = QPushButton("П")
        self.underline_check.setCheckable(True)
        self.underline_check.setChecked(self.text_settings["underline"])
        self.underline_check.setFixedWidth(30)
        style_layout.addWidget(self.underline_check)
        
        self.strikeout_check = QPushButton("З")
        self.strikeout_check.setCheckable(True)
        self.strikeout_check.setChecked(self.text_settings["strikeout"])
        self.strikeout_check.setFixedWidth(30)
        style_layout.addWidget(self.strikeout_check)
        
        layout.addLayout(style_layout)
        
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("ОК")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
    
    def update_color_button(self):
        pixmap = QPixmap(self.color_button.size())
        pixmap.fill(self.text_settings["color"])
        self.color_button.setIcon(QIcon(pixmap))
    
    def choose_color(self):
        color = QColorDialog.getColor(self.text_settings["color"], self, "Выберите цвет текста")
        if color.isValid():
            self.text_settings["color"] = color
            self.update_color_button()
    
    def get_text(self):
        return self.text_input.toPlainText()
    
    def get_text_settings(self):
        self.text_settings["font"] = self.font_combo.currentText()
        self.text_settings["size"] = int(self.size_combo.currentText())
        self.text_settings["bold"] = self.bold_check.isChecked()
        self.text_settings["italic"] = self.italic_check.isChecked()
        self.text_settings["underline"] = self.underline_check.isChecked()
        self.text_settings["strikeout"] = self.strikeout_check.isChecked()
        return self.text_settings

class DrawPad(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(30000, 30000)
        self.current_tool = "pen"
        self.shapes = []
        self.pen_color = QColor(0, 0, 0)
        self.pen_size = 2
        self.eraser_size = 20
        self.shape_border_size = 2
        self.show_slider = False
        self.start_point = None
        self.temp_shape = None
        self.undo_stack = []
        self.redo_stack = []
        self.moving_object = None
        self.moving_object_offset = QPoint(0, 0)
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
        self.is_dragging = False
        self.last_pos = None
        
        self.scale_factor = 1.0
        self.offset = QPoint(0, 0)
        self.cursor_pos = QPoint(0, 0)
        self.is_eraser_tool_active = False
        self.fill_color = QColor(0, 0, 0)

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

        self.size_slider.valueChanged.connect(self.update_tool_settings)
        
        self.setMouseTracking(True)
        
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
        self.update()

    def set_tool(self, tool):
        self.current_tool = tool
        self.update_slider_visibility()
        
        self.is_eraser_tool_active = (tool == "eraser")
        
        if tool == "eraser":
            self.setCursor(Qt.CursorShape.BlankCursor)
        else:
            self.setCursor(Qt.CursorShape.CrossCursor)
            
        self.update()

    def open_color_picker(self):
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
                self.fill_color = color_dialog.selectedColor()
            self.color_picker_open = False

    def set_text_settings(self):
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
        transformed_pos = self.transform_point(event.pos())
        
        if event.button() == Qt.MouseButton.LeftButton:
            if self.current_tool in {"line", "rect", "circle"}:
                self.start_point = transformed_pos
                self.temp_shape = (self.current_tool, transformed_pos, transformed_pos, self.pen_color, self.pen_size)
            elif self.current_tool == "pen":
                self.shapes.append(("pen", [transformed_pos], self.pen_color, self.pen_size))
            elif self.current_tool == "eraser":
                self.erase(transformed_pos)
            elif self.current_tool == "text":
                dialog = TextInputDialog(self, text_settings=self.text_settings)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    text = dialog.get_text()
                    self.text_settings = dialog.get_text_settings()
                    if text:
                        self.shapes.append(("text", transformed_pos, text, self.text_settings.copy()))
            elif self.current_tool == "move_object":
                found_shape = self.find_shape(transformed_pos)
                
                if found_shape and found_shape[0] == "text" and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    self.edit_text(found_shape)
                else:
                    self.moving_object = found_shape
                    if self.moving_object:
                        self.last_pos = transformed_pos
            elif self.current_tool == "fill":
                shape = self.find_shape(transformed_pos)
                if shape:
                    self.apply_fill(shape)
                
            self.save_state()
            
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_slider = not self.show_slider
            self.update_slider_visibility()
            
        self.update()
    
    def mouseMoveEvent(self, event):
        self.cursor_pos = event.pos()
        
        transformed_pos = self.transform_point(event.pos())
        
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self.current_tool == "pen":
                self.shapes[-1][1].append(transformed_pos)
            elif self.current_tool in {"line", "rect", "circle"} and self.temp_shape:
                self.temp_shape = (self.temp_shape[0], self.temp_shape[1], transformed_pos, self.temp_shape[3], self.temp_shape[4])
            elif self.current_tool == "eraser":
                self.erase(transformed_pos)
            elif self.current_tool == "move_object" and self.moving_object:
                delta = transformed_pos - self.last_pos
                self.move_shape_by_delta(self.moving_object, delta)
                self.last_pos = transformed_pos
            
        self.update()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.temp_shape and self.current_tool in {"line", "rect", "circle"}:
                self.shapes.append(self.temp_shape)
                self.temp_shape = None
            elif self.current_tool == "move_object" and self.moving_object:
                self.moving_object = None
                self.moving_object_offset = QPoint(0, 0)
        
        self.update()
    
    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            cursor_pos = event.position().toPoint()
            canvas_pos = self.transform_point(cursor_pos)
            
            zoom_in = event.angleDelta().y() > 0
            old_factor = self.scale_factor
            
            if zoom_in:
                self.scale_factor *= 1.15
            else:
                self.scale_factor /= 1.15
                
            self.scale_factor = max(0.1, min(self.scale_factor, 5.0))
            
            new_screen_pos = QPoint(
                int(canvas_pos.x() * self.scale_factor + self.offset.x()),
                int(canvas_pos.y() * self.scale_factor + self.offset.y())
            )
            
            self.offset += cursor_pos - new_screen_pos
            
        else:
            delta_y = event.angleDelta().y()
            delta_x = event.angleDelta().x()
            
            dx = int(delta_x / 8)
            dy = int(delta_y / 8)
            
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                dx, dy = dy, dx
                
            self.offset += QPoint(dx, dy)
        
        self.update()
        event.accept()
    
    def transform_point(self, point):
        x = (point.x() - self.offset.x()) / self.scale_factor
        y = (point.y() - self.offset.y()) / self.scale_factor
        return QPoint(int(x), int(y))
    
    def inverse_transform_point(self, point):
        x = point.x() * self.scale_factor + self.offset.x()
        y = point.y() * self.scale_factor + self.offset.y()
        return QPoint(int(x), int(y))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        painter.translate(self.offset)
        painter.scale(self.scale_factor, self.scale_factor)
        
        for shape in self.shapes:
            self.draw_shape(painter, shape)
        
        if self.temp_shape:
            self.draw_shape(painter, self.temp_shape)
        
        painter.resetTransform()
        
        if self.is_eraser_tool_active:
            eraser_rect = QRect(
                self.cursor_pos.x() - self.eraser_size // 2,
                self.cursor_pos.y() - self.eraser_size // 2,
                self.eraser_size,
                self.eraser_size
            )
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.PenStyle.DashLine))
            painter.drawRect(eraser_rect)

    def draw_shape(self, painter, shape):
        try:
            if shape[0] == "pen":
                pen = QPen(shape[2], shape[3])
                painter.setPen(pen)
                points = shape[1]
                if not points or len(points) < 2:
                    return
                for i in range(1, len(points)):
                    painter.drawLine(points[i - 1], points[i])
                painter.setPen(QPen(shape[2], shape[3], Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                for point in points:
                    painter.drawPoint(point)

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
                if len(shape) > 5 and shape[5]:
                    painter.setBrush(QBrush(shape[3]))
                else:
                    painter.setBrush(QColor(255, 255, 255) if shape[4] == 0 else QBrush(Qt.BrushStyle.NoBrush))
                
                if isinstance(shape[1], QPoint) and isinstance(shape[2], QPoint):
                    painter.drawRect(QRect(shape[1], shape[2]))
                else:
                    print("Invalid rect data:", shape)
                    return

            elif shape[0] == "circle":
                pen = QPen(shape[3], shape[4])
                painter.setPen(pen)
                if len(shape) > 5 and shape[5]:
                    painter.setBrush(QBrush(shape[3]))
                else:
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
        self.undo_stack.append([s.copy() if isinstance(s, list) else s for s in self.shapes])
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.shapes.copy())
            self.shapes = self.undo_stack.pop()
            self.update()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.shapes.copy())
            self.shapes = self.redo_stack.pop()
            self.update()

    def erase(self, pos):
        eraser_rect = QRect(
            pos.x() - self.eraser_size // 2,
            pos.y() - self.eraser_size // 2,
            self.eraser_size,
            self.eraser_size
        )
        
        eraser_color = QColor(255, 255, 255)
        self.shapes.append(("rect", eraser_rect.topLeft(), eraser_rect.bottomRight(), eraser_color, 0))
        self.update()

    def find_shape(self, pos):
        for shape in reversed(self.shapes):
            if shape[0] == "text":
                text_rect = QRect(shape[1], QSize(100, 50))
                if text_rect.contains(pos):
                    return shape
            elif shape[0] == "pen":
                points = shape[1]
                for i in range(1, len(points)):
                    line_width = shape[3] + 5
                    line_rect = QRect(
                        min(points[i-1].x(), points[i].x()) - line_width,
                        min(points[i-1].y(), points[i].y()) - line_width,
                        abs(points[i].x() - points[i-1].x()) + 2 * line_width,
                        abs(points[i].y() - points[i-1].y()) + 2 * line_width
                    )
                    if line_rect.contains(pos):
                        return shape
            elif shape[0] in {"rect", "circle", "line"}:
                shape_rect = QRect(
                    min(shape[1].x(), shape[2].x()),
                    min(shape[1].y(), shape[2].y()),
                    abs(shape[2].x() - shape[1].x()),
                    abs(shape[2].y() - shape[1].y())
                )
                shape_rect = shape_rect.adjusted(-5, -5, 5, 5)
                if shape_rect.contains(pos):
                    return shape
                    
        return None

    def move_shape_by_delta(self, shape, delta):
        if not shape:
            return
            
        try:
            index = self.shapes.index(shape)
        except ValueError:
            return
            
        shape_list = list(shape)
            
        if shape[0] == "pen":
            shape_list[1] = [p + delta for p in shape[1]]
            
        elif shape[0] in {"line", "rect", "circle"}:
            shape_list[1] = shape[1] + delta
            shape_list[2] = shape[2] + delta
            
        elif shape[0] == "text":
            shape_list[1] = shape[1] + delta
            
        self.shapes[index] = tuple(shape_list)
        self.moving_object = self.shapes[index]

    def apply_fill(self, shape):
        if not shape:
            return
            
        try:
            index = self.shapes.index(shape)
        except ValueError:
            return
            
        shape_list = list(shape)
        
        if shape[0] == "rect" or shape[0] == "circle":
            shape_list[3] = self.pen_color
            
            if len(shape_list) <= 5:
                shape_list.append(True)
            else:
                shape_list[5] = True
                
            self.shapes[index] = tuple(shape_list)
            self.update()

    def edit_text(self, text_shape):
        if not text_shape or text_shape[0] != "text":
            return
            
        try:
            index = self.shapes.index(text_shape)
        except ValueError:
            return
        
        pos = text_shape[1]
        existing_text = text_shape[2]
        text_settings = text_shape[3]
        
        dialog = TextInputDialog(self, existing_text=existing_text, text_settings=text_settings)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_text = dialog.get_text()
            updated_settings = dialog.get_text_settings()
            
            if new_text:
                updated_text = ("text", pos, new_text, updated_settings)
                self.shapes[index] = updated_text
                self.update()
    
    def get_font(self, text_settings):
        font = QFont(text_settings["font"], text_settings["size"])
        font.setBold(text_settings["bold"])
        font.setItalic(text_settings["italic"])
        font.setUnderline(text_settings["underline"])
        font.setStrikeOut(text_settings["strikeout"])
        return font
    
    def reset_view(self):
        self.scale_factor = 1.0
        self.offset = QPoint(0, 0)
        self.update()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_E and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if self.moving_object and self.moving_object[0] == "text":
                self.edit_text(self.moving_object)
        elif event.key() == Qt.Key.Key_Home:
            self.reset_view()
        elif event.key() == Qt.Key.Key_Z and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.undo()
        elif event.key() == Qt.Key.Key_Y and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.redo()
        elif event.key() == Qt.Key.Key_Left:
            self.offset += QPoint(20, 0)
            self.update()
        elif event.key() == Qt.Key.Key_Right:
            self.offset += QPoint(-20, 0)
            self.update()
        elif event.key() == Qt.Key.Key_Up:
            self.offset += QPoint(0, 20)
            self.update()
        elif event.key() == Qt.Key.Key_Down:
            self.offset += QPoint(0, -20)
            self.update()
        else:
            super().keyPressEvent(event)