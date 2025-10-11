from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, QPoint, QObject, QTimer
from PyQt6.QtGui import QPainter, QColor, QBrush, QPainterPath, QPixmap, QPen
import sys, keyboard

# -- Functions --
def GetAnimTime(n:float):
    return int(n*1000)

def getHex(rgb):
    if isinstance(rgb, (list, tuple)) and len(rgb) >= 3:
        r, g, b = rgb[:3]
        return f"#{r:02X}{g:02X}{b:02X}"
    elif isinstance(rgb, str):
        parts = [int(x) for x in rgb.replace(' ', '').split(',')]
        return f"#{parts[0]:02X}{parts[1]:02X}{parts[2]:02X}"
    else:
        raise ValueError("Error: Unknonw format RGB")
    
def addDynamicStyle(obj, style: str):
    obj.setStyleSheet(style)

    class _StyleWatcher(QObject):
        def eventFilter(self, watched, event):
            if watched == obj and event.type() == 105:
                if event.propertyName().data().decode() == "class":
                    obj.style().unpolish(obj)
                    obj.style().polish(obj)
                    obj.update()
            return False

    watcher = _StyleWatcher()
    obj.installEventFilter(watcher)
    obj._styleWatcher = watcher
    

# -- Variables --
Title = "Ink Blot Overlay"
Size = {"width": 1000, "height": 600}
BlobsOnScreen = 12
BorderRadius = 15
MainWindowOpacity = 0.9

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
menubarTitleStyle = '''
    QLabel {
        width: 200px;
        height: 25px;
        padding: 5 0;
        font-size: 14px;
        font-family: 'Courier New', Courier, monospace;
        color: rgba(255, 106, 0, 255);
        background-color: rgba(0, 0, 0, 0);
    }
'''

buttonStyle = '''
    QPushButton {
        color: rgba(255, 106, 0, 255);
        background-color: qlineargradient(
            x1: 0, y1: 0,
            x2: 0, y2: 1,
            stop: 0 rgba(50, 25, 0, 255),
            stop: 1 rgba(30, 15, 0, 255)
        );
        border: 1px solid rgba(255, 106, 0, 255);
        border-radius: 10px;
        font-family: 'Courier New', Courier, monospace;
    }
    QPushButton:hover {
        background-color: qlineargradient(
            x1: 0, y1: 0,
            x2: 0, y2: 1,
            stop: 0 rgba(70, 35, 0, 255),
            stop: 1 rgba(40, 20, 0, 255)
        );
    }
    QPushButton:pressed {
        background-color: qlineargradient(
            x1: 0, y1: 0,
            x2: 0, y2: 1,
            stop: 0 rgba(25, 10, 0, 255),
            stop: 1 rgba(15, 5, 0, 255)
        );
    }
'''

dinamicTitleStyle = '''
    QLabel[class='passive'] {
        width: 200px;
        height: 25px;
        padding: 5 0;
        font-size: 14px;
        font-family: 'Courier New', Courier, monospace;
        color: rgb(150, 60, 0);
        background-color: rgba(0, 0, 0, 0);
    }

    QLabel[class='active'] {
        width: 200px;
        height: 25px;
        padding: 5 0;
        font-size: 14px;
        font-family: 'Courier New', Courier, monospace;
        color: rgba(255, 106, 0, 255);
        background-color: rgba(0, 0, 0, 0);
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
            btn.setStyleSheet(buttonStyle)
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
        mainLayout.setContentsMargins(2, 2, 2, 2)
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
        self.uis = {}

        mainIconPixmap = QPixmap(mainIcon).scaled(30, 30)

        self.icons["mainIcon"] = QLabel(self)
        self.icons["mainIcon"].setPixmap(mainIconPixmap)
        self.iconsLayout.addWidget(self.icons["mainIcon"])

        self.uis["holdAlt"] = QLabel("Hold Alt to drag", parent=self)
        self.uis["holdAlt"].setProperty("class", "passive")

        addDynamicStyle(self.uis["holdAlt"], dinamicTitleStyle)

        self.menuBarLayout.addWidget(self.uis["holdAlt"], 0, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)

        self.buttons["minimizeButton"] = QPushButton("_")
        self.buttons["minimizeButton"].setStyleSheet(menubarStyle)
        self.buttons["minimizeButton"].clicked.connect(lambda: self.showMinimized())
        self.menuBarLayout.addWidget(self.buttons["minimizeButton"])

        self.buttons["closeButton"] = QPushButton("X")
        self.buttons["closeButton"].setStyleSheet(menubarStyle)
        self.buttons["closeButton"].clicked.connect(lambda: self.close())
        self.menuBarLayout.addWidget(self.buttons["closeButton"])

        self.uis["mainTitle"] = QLabel("Ink Blot Overlay - Select Widgets")
        self.uis["mainTitle"].setStyleSheet(menubarTitleStyle)
        self.iconsLayout.addWidget(self.uis["mainTitle"])

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(Title)
        self.resize(Size["width"], Size["height"])
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowOpacity(MainWindowOpacity)

        QApplication.instance().installEventFilter(self)

        self.show()

    def eventFilter(self, obj, event):
        if event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Alt:
                if self.uis["holdAlt"].property("class") != "active":
                    self.uis["holdAlt"].setProperty("class", "active")
                    self.uis["holdAlt"].style().unpolish(self.uis["holdAlt"])
                    self.uis["holdAlt"].style().polish(self.uis["holdAlt"])
                    self.uis["holdAlt"].update()

        elif event.type() == event.Type.KeyRelease:
            if event.key() == Qt.Key.Key_Alt:
                if self.uis["holdAlt"].property("class") != "passive":
                    self.uis["holdAlt"].setProperty("class", "passive")
                    self.uis["holdAlt"].style().unpolish(self.uis["holdAlt"])
                    self.uis["holdAlt"].style().polish(self.uis["holdAlt"])
                    self.uis["holdAlt"].update()

        return super().eventFilter(obj, event)

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
        self.HideAnim = QPropertyAnimation(self, b"windowOpacity")
        self.HideAnim.setEndValue(0)
        self.HideAnim.setDuration(GetAnimTime(0.2))

        currentPos = self.pos()
        self.HideAnimMove = QPropertyAnimation(self, b"pos")
        self.HideAnimMove.setStartValue(currentPos)
        self.HideAnimMove.setEndValue(QPoint(currentPos.x(), currentPos.y()+30))
    
        QTimer.singleShot(300, lambda: QMainWindow.showMinimized(self))

        self.HideAnimMove.start()
        self.HideAnim.start()

        
    def showEvent(self, a0):
        self.ShowAnim = QPropertyAnimation(self, b"windowOpacity")
        self.ShowAnim.setStartValue(0)
        self.ShowAnim.setEndValue(MainWindowOpacity)
        self.ShowAnim.setDuration(GetAnimTime(0.2))

        currentPos = self.pos()
        self.ShowAnimMove = QPropertyAnimation(self, b"pos")
        self.ShowAnimMove.setStartValue(currentPos)
        self.ShowAnimMove.setEndValue(QPoint(currentPos.x(), currentPos.y()-30))

        self.ShowAnimMove.start()
        self.ShowAnim.start()

        return super().showEvent(a0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    settingWindow = WidgetSettingWindow()
    
    # def toggle_window():
    #     if len(settingWindow.Windows) > 0:
    #         return
        
    #     if settingWindow.isVisible():
    #         settingWindow.hide()
    #     else:
    #         settingWindow.show()

    # keyboard.add_hotkey("ctrl+alt+\\", toggle_window)

    sys.exit(app.exec())
