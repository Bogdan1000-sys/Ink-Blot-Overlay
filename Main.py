from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, QPoint, QParallelAnimationGroup
from PyQt6.QtGui import QPainter, QColor, QBrush, QPainterPath, QPixmap, QPen
import sys, keyboard, threading, time

# -- Functions --
def GetAnimTime(n:float):
    return int(n*1000)

# -- Variables --
Title = "Ink Blot Overlay"
Size = {"width": 1000, "height": 600}
BlobsOnScreen = 12
BorderRadius = 15

# -- Colors --
WindowColor = [0, 0, 0, 255]
MainElementColor = [255, 106, 0, 255]
DarkElementColor = [150, 60, 0]
SecondaryElementColor = [255, 106, 0, 100]

# -- Resources --
mainIcon = 'Resources/Images/Ink Blot Icon.png'

# -- Stylesheets --
menubarStyle = '''
    QPushButton {
        width: 25 px;
        height: 25 px;
        padding: 0 0;
        font-size: 14px;
        font-family: Arial;
        font-weight: bolder;
        color: rgba(255, 106, 0, 255);
        background-color: rgba(100, 40, 0, 255);
        border-radius: 10px;
    }
                                        
    QPushButton:hover {
        background-color: rgba(80, 30, 0, 255);
    }

    QPushButton:pressed {
        background-color: rgba(50, 15, 0, 255);
    }
'''

class ConfirmExitWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.resize(300, 100)
        self.setStyleSheet("background-color: black;")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        self.setWindowOpacity(0)

        self.showAnim = QPropertyAnimation(self, b"windowOpacity")
        self.showAnim.setEndValue(1)
        self.showAnim.setDuration(GetAnimTime(0.2))
        self.showAnim.start()

        self.hideAnim = QPropertyAnimation(self, b"windowOpacity")
        self.hideAnim.setEndValue(0)
        self.hideAnim.setDuration(GetAnimTime(0.2))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel("Are you sure you want to exit?")
        self.label.setStyleSheet("color: white; font-size: 14px; font-family: 'Courier New', Courier, monospace;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        layout.addLayout(btn_layout)

        self.btn_yes = QPushButton("Yes")
        self.btn_no = QPushButton("No")

        for btn in (self.btn_yes, self.btn_no):
            btn.setFixedSize(80, 30)
            btn.setStyleSheet("""
                QPushButton {
                    color: rgba(255, 106, 0, 255);
                    background-color: rgba(30, 30, 30, 255);
                    border: 1px solid rgba(255, 106, 0, 255);
                    border-radius: 10px;
                    font-family: 'Courier New', Courier, monospace;
                }
                QPushButton:hover {
                    background-color: rgba(50, 25, 0, 255);
                }
            """)
            btn_layout.addWidget(btn)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())

        painter.setBrush(QBrush(QColor(*WindowColor)))
        painter.setPen(Qt.PenStyle.NoPen)
        path = QPainterPath()
        path.addRoundedRect(rect, 10, 10)
        painter.drawPath(path)

        border_pen = QPen(QColor(*MainElementColor))
        border_pen.setWidth(1)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect.adjusted(1.5, 1.5, -1.5, -1.5), 10, 10)
    
    canClose = False
    def closeEvent(self, event):
        if self.canClose:
            self.deleteLater()
            event.accept()
        else:
            event.ignore()
        
class WidgetSettingWindow(QMainWindow):
    Windows = []
    def AddWindow(self, win):
        def onDestroy():
            self.Windows.remove(win) if win in self.Windows else None
            print(self.Windows)

        if win == None:
            return
        
        self.Windows.append(win)
        win.destroyed.connect(onDestroy)

    def __init__(self):
        super().__init__()

        self._drag_pos = None
        self.exitConfirmationShowed = False
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        mainLayout = QHBoxLayout(central_widget)
        mainLayout.setContentsMargins(3, 2, 5, 5)
        mainLayout.setSpacing(5)
        mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self.iconsLayout = QHBoxLayout()
        self.iconsLayout.setSpacing(5)
        self.iconsLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        mainLayout.addLayout(self.iconsLayout, 0)

        mainLayout.addStretch()

        self.menuBarLayout = QHBoxLayout()
        self.menuBarLayout.setSpacing(5)
        self.menuBarLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        mainLayout.addLayout(self.menuBarLayout, 0)

        self.icons = {}
        self.buttons = {}

        mainIconPixmap = QPixmap(mainIcon).scaled(30, 30)

        self.icons["mainIcon"] = QLabel(self)
        self.icons["mainIcon"].setPixmap(mainIconPixmap)
        self.iconsLayout.addWidget(self.icons["mainIcon"])

        self.buttons["minimizeButton"] = QPushButton("_")
        self.buttons["minimizeButton"].setStyleSheet(menubarStyle)
        self.buttons["minimizeButton"].clicked.connect(lambda: self.showMinimized())
        self.menuBarLayout.addWidget(self.buttons["minimizeButton"])

        self.buttons["closeButton"] = QPushButton("X")
        self.buttons["closeButton"].setStyleSheet(menubarStyle)
        self.buttons["closeButton"].clicked.connect(lambda: self.close())
        self.menuBarLayout.addWidget(self.buttons["closeButton"])

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(Title)
        self.resize(Size["width"], Size["height"])
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowOpacity(0.85)

        self.show()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())

        painter.setBrush(QBrush(QColor(*WindowColor)))
        painter.setPen(Qt.PenStyle.NoPen)
        path = QPainterPath()
        path.addRoundedRect(rect, BorderRadius, BorderRadius)
        painter.drawPath(path)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and keyboard.is_pressed('alt'):
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if (
            event.buttons() == Qt.MouseButton.LeftButton
            and keyboard.is_pressed('alt')
            and self._drag_pos is not None
        ):
            current_pos = event.globalPosition().toPoint()
            delta = current_pos - self._drag_pos
            self.move(self.x() + int(delta.x()), self.y() + int(delta.y()))
            self._drag_pos = current_pos
            event.accept()

    def closeEvent(self, event):
        event.ignore()
        if self.exitConfirmationShowed:
            return
        self.exitConfirmationShowed = True
    
        shade = QFrame(parent=self)
        shade.setStyleSheet('background-color: rgba(0,0,0,0.5); border-radius: 15px')
        shade.resize(Size["width"], Size["height"])
        shade.show()

        shade.showAnim = QPropertyAnimation(shade, b"windowOpacity")
        shade.showAnim.setEndValue(1)
        shade.showAnim.setDuration(GetAnimTime(0.2))
        shade.showAnim.start()

        dialog = ConfirmExitWindow(self)
        self.AddWindow(dialog)

        dialog.move(
            self.x() + (self.width() - dialog.width()) // 2,
            self.y() + (self.height() - dialog.height()) // 2
        )
        dialog.show()

        def destroy_dialog():
            dialog.canClose = True
            dialog.hideAnim.finished.connect(dialog.close)
            dialog.hideAnim.start()

            currentPos = dialog.pos()
            dialog.hideAnimMove = QPropertyAnimation(dialog, b"pos")
            dialog.hideAnimMove.setStartValue(currentPos)
            dialog.hideAnimMove.setEndValue(QPoint(currentPos.x(), currentPos.y()+30))
            dialog.hideAnimMove.start()

            shade.hideAnim = QPropertyAnimation(shade, b"windowOpacity")
            shade.hideAnim.setEndValue(0)
            shade.hideAnim.setDuration(GetAnimTime(0.2))
            shade.hideAnim.finished.connect(shade.close)
            shade.hideAnim.start()

        def no_clicked():
            self.exitConfirmationShowed = False
            destroy_dialog()

        def yes_clicked():
            def exit():
                sys.exit(0)
            
            destroy_dialog()

            self.HideAnim = QPropertyAnimation(self, b"windowOpacity")
            self.HideAnim.setEndValue(0)
            self.HideAnim.setDuration(GetAnimTime(0.2))
            self.HideAnim.finished.connect(exit)

            currentPos = self.pos()
            self.HideAnimMove = QPropertyAnimation(self, b"pos")
            self.HideAnimMove.setStartValue(currentPos)
            self.HideAnimMove.setEndValue(QPoint(currentPos.x(), currentPos.y()+30))

            self.HideAnimMove.start()
            self.HideAnim.start()


        dialog.btn_no.clicked.connect(no_clicked)
        dialog.btn_yes.clicked.connect(yes_clicked)

    def showMinimized(self):
        return super().showMinimized()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    settingWindow = WidgetSettingWindow()
    
    def toggle_window():
        if len(settingWindow.Windows) > 0:
            return
        
        if settingWindow.isVisible():
            settingWindow.hide()
        else:
            settingWindow.show()

    keyboard.add_hotkey("ctrl+alt+\\", toggle_window)

    sys.exit(app.exec())
