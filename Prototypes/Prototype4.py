from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QBrush, QPainterPath, QPen
import sys
import keyboard

# -- Variables --
Title = "Ink Blot Overlay"
Size = {"width": 1000, "height": 600}
WindowColor = [0, 0, 0, 255]
MainElementColor = [255, 106, 0, 255]
SecondaryElementColor = [255, 106, 0, 150]

class CustomWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(Title)
        self.resize(Size["width"], Size["height"])
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowOpacity(0.8)

        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())

        color = QColor(WindowColor[0], WindowColor[1], WindowColor[2], WindowColor[3])
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)

        radius = 20
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        painter.drawPath(path)

        border_pen = QPen(QColor(MainElementColor[0], MainElementColor[1], MainElementColor[2], MainElementColor[3]))
        border_pen
        border_pen.setWidth(1)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and keyboard.is_pressed('alt'):
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and keyboard.is_pressed('alt'):
            current_pos = event.globalPosition().toPoint()
            delta = current_pos - self._drag_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._drag_pos = current_pos
            event.accept()
    
    def closeEvent(self, event):
        event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomWindow()
    sys.exit(app.exec())
