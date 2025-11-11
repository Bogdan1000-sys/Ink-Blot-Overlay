from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, QPoint, QTimer, pyqtSignal, QEvent
from PyQt6.QtGui import QPainter, QColor, QBrush, QPainterPath, QPixmap, QPen
import sys, keyboard, json, math

# -- Services --
from Services import CollectionService

# -- Functions --
from Functions import GetQTime, addDynamicStyle, GetAdaptedTextFromDictionary, GetUserSettings

# -- Variables --

# -- Resources --
mainIcon = 'Programm/Resources/Images/Ink Blot Icon.png'

# -- Constants --
with open("Programm/Data/Pathes.json", "r", encoding="utf-8") as pFile:
    Pathes = json.load(pFile)

# -- Data --
with open(Pathes["Constants"], "r", encoding="utf-8") as cFile:
    Constants = json.load(cFile)
with open(Pathes["Data"], "r", encoding="utf-8") as dataFile:
    Data = json.load(dataFile)
with open(Pathes["Dictionary"], "r", encoding="utf-8") as dFile:
    Dictionary = json.load(dFile)
with open(Pathes["SettingOptions"], "r", encoding="utf-8") as soFile:
    SettingOptions = json.load(soFile)

UserSettings = GetUserSettings()

def UpdateUserSettings():
    global UserSettings
    UserSettings = GetUserSettings()

# -- Common Styles --
menubarButtonStyle = '''
    QPushButton[class='menubarButton'] {
        width: 25 px;
        height: 25 px;
        padding: 0 0;
        font-size: 14px;
        font-family: 'Courier New', Courier, monospace;
        color: rgba(255, 106, 0, 255);
        background-color: rgba(100, 40, 0, 255);
        border-radius: 10px;
    }
                                        
    QPushButton[class='menubarButton']:hover {
        background-color: rgba(80, 30, 0, 255);
    }

    QPushButton[class='menubarButton']:pressed {
        background-color: rgba(50, 15, 0, 255);
    }
'''

menubarTextButtonStyle = '''
    QPushButton[class='menubarButton'] {
        min-width: 120px;
        max-width: 200px;
        height: 25 px;
        padding: 0 5px;
        font-size: 14px;
        font-family: 'Courier New', Courier, monospace;
        color: rgba(255, 106, 0, 255);
        background-color: rgba(100, 40, 0, 255);
        border-radius: 10px;
    }
                                        
    QPushButton[class='menubarButton']:hover {
        background-color: rgba(80, 30, 0, 255);
    }

    QPushButton[class='menubarButton']:pressed {
        background-color: rgba(50, 15, 0, 255);
    }
'''

# -------------- Classes --------------

class WidgetButton(QFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)

        self._data = kwargs or {}
        self._data["data"] = kwargs.get("data")
        self._data["size"] = kwargs.get("size", [100, 100])

        if self._data["data"] == None:
            self.hide()
            self.destroy()
            print("[Classes] Error: Data of Widget not found!")
            return
        
        self.setFixedSize(self._data["size"][0], self._data["size"][1])
        self.setProperty("class", "widgetButton")
        self.setStyleSheet("""
            QFrame[class='widgetButton'] {
                border: 1px solid rgba(255, 106, 0, 180);
                border-radius: 10px;
                background: qlineargradient(
                    x1: 0, y1: 1,
                    x2: 0, y2: 0,
                    stop: 0 #411c00,
                    stop: 1 #240f00);
            }
        """)

        pixmapScale = (self._data["size"][0] < self._data["size"][1] and self._data["size"][0] or self._data["size"][1])-5
        IconPixmap = QPixmap(self._data["data"]["Icon"]).scaled(pixmapScale, pixmapScale)

        self.Icon = QLabel(self)
        self.Icon.setStyleSheet("background: transparent; border: none; margin-top:1px; margin-left:1px")
        self.Icon.setPixmap(IconPixmap)

        self.nameLabel = QLabel(GetAdaptedTextFromDictionary(self._data["data"]["Name"]), parent=self)
        
        CollectionService.addTag(self.nameLabel, "adaptableTextWidget")
        self.nameLabel.setProperty("textKey", "widgetNames/"+self._data["data"]["Key"])

        self.nameLabel.resize(self._data["size"][0], 30)
        self.nameLabel.move(0, self._data["size"][1]-30)
        self.nameLabel.setStyleSheet("""
            border: none;
            font-family: 'Courier New', Courier, monospace;
            font-size: 15px;
            color: rgba(255, 106, 0, 255);
            background-color: rgba(0, 0, 0, 100);
                                     
            padding-left: 3px;
            padding-right: 3px;
            padding-top: 3px;
            padding-bottom: 3px;
        """)

        self.button = QPushButton(parent=self)
        self.button.resize(self._data["size"][0], self._data["size"][1])
        self.button.setStyleSheet("""
            background: rgba(0,0,0,0);
            border: none
        """)

class ConfirmExitWindow(QWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        
        UpdateUserSettings()
        
        self._data = kwargs or {}
        self._data["language"] = UserSettings.get("language", "eng")

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.resize(300, 100)
        self.setStyleSheet("background-color: black;")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        self.setWindowOpacity(0)

        self.showAnim = QPropertyAnimation(self, b"windowOpacity")
        self.showAnim.setEndValue(1)
        self.showAnim.setDuration(GetQTime(0.2))
        self.showAnim.start()

        self.hideAnim = QPropertyAnimation(self, b"windowOpacity")
        self.hideAnim.setEndValue(0)
        self.hideAnim.setDuration(GetQTime(0.2))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel(Dictionary[self._data["language"]]["labels"]["exitConfirmation"]["Q"])
        
        CollectionService.addTag(self.label, "adaptableTextWidget")
        self.label.setProperty("textKey", "labels/exitConfirmation/Q")

        self.label.setStyleSheet("color: white; font-size: 14px; font-family: 'Courier New', Courier, monospace;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        layout.addLayout(btn_layout)

        self.btn_yes = QPushButton(Dictionary[self._data["language"]]["labels"]["exitConfirmation"]["Y"])
        self.btn_yes.setProperty("textKey", "labels/exitConfirmation/Y")

        self.btn_no = QPushButton(Dictionary[self._data["language"]]["labels"]["exitConfirmation"]["N"])
        self.btn_no.setProperty("textKey", "labels/exitConfirmation/N")

        CollectionService.addTag(self.btn_yes, "adaptableTextWidget")
        CollectionService.addTag(self.btn_no, "adaptableTextWidget")

        for btn in (self.btn_yes, self.btn_no):
            btn.setFixedSize(80, 30)
            btn.setStyleSheet('''
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
            ''')
            btn_layout.addWidget(btn)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())

        painter.setBrush(QBrush(QColor(*Constants["WindowColor"])))
        painter.setPen(Qt.PenStyle.NoPen)
        path = QPainterPath()
        path.addRoundedRect(rect, 10, 10)
        painter.drawPath(path)

        border_pen = QPen(QColor(*Constants["MainElementColor"]))
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

class SettingsWindow(QWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)

        UpdateUserSettings()

        self._menuActive = True

        self._data = kwargs or {}
        self._data["Size"] = kwargs.get("Size", [125, 200])
        self._data["Position"] = kwargs.get("Position", QPoint(100, 100))
        self._data["language"] = UserSettings.get("language", "eng")
        
        self._settingButtons = {}

        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowOpacity(0)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")

        self.resize(*self._data["Size"])
        self.move(self._data["Position"])
        self.setProperty("class", "settingsWindow")

        self.setStyleSheet("""
            QPushButton[class='settingButton'] {
                text-align: left;
                min-width: 98%;
                max-width: 200px;
                height: 25 px;
                padding: 0 5px;
                font-size: 14px;
                font-family: 'Courier New', Courier, monospace;
                color: rgba(255, 106, 0, 255);
                background-color: rgba(100, 40, 0, 255);
                border-radius: 10px;
            }
                                        
            QPushButton[class='settingButton']:hover {
                background-color: rgba(80, 30, 0, 255);
            }

            QPushButton[class='settingButton']:pressed {
                background-color: rgba(50, 15, 0, 255);
            }
        """)

        self.MainLayout = QVBoxLayout()
        self.MainLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(self.MainLayout)

        self.showAnim1 = QPropertyAnimation(self, b"windowOpacity")
        self.showAnim1.setStartValue(0)
        self.showAnim1.setEndValue(1)
        self.showAnim1.setDuration(GetQTime(0.2))

        self.showAnim2 = QPropertyAnimation(self, b"pos")
        self.showAnim2.setStartValue(self._data["Position"] + QPoint(0, -5))
        self.showAnim2.setEndValue(self._data["Position"])
        self.showAnim2.setDuration(GetQTime(0.2))

        self.hideAnim1 = QPropertyAnimation(self, b"windowOpacity")
        self.hideAnim1.setStartValue(1)
        self.hideAnim1.setEndValue(0)
        self.hideAnim1.setDuration(GetQTime(0.2))

        self.hideAnim2 = QPropertyAnimation(self, b"pos")
        self.hideAnim2.setStartValue(self._data["Position"])
        self.hideAnim2.setEndValue(self._data["Position"] + QPoint(0, -5))
        self.hideAnim2.setDuration(GetQTime(0.2))

        self._settingButtons["language"] = QPushButton(Dictionary[self._data["language"]]["settings"]["language"], parent=self)
        self._settingButtons["language"].setProperty("class", "settingButton")
        self.MainLayout.addWidget(self._settingButtons["language"])

        for key, button in self._settingButtons.items():
            arrow = QLabel(">", parent=button)
            arrow.setProperty("class", "arrow")
            arrow.resize(15, button.size().height()//2 + button.size().height()//4)
            arrow.move(button.size().width()-arrow.size().width(), 0)
            arrow.setStyleSheet("""
                QLabel[class='arrow'] {
                    text-align: center;
                    font-size: 14px;
                    font-family: 'Courier New', Courier, monospace;
                    color: rgba(255, 106, 0, 255);
                }
            """)

            CollectionService.addTag(button, "adaptableTextWidget")
            button.setProperty("textKey", "settings/"+key)

            button.OptionsContainer = None

            def makeEnterFunction(name):
                def enterEvent(event):
                    if not self._menuActive: return

                    print("Cursor entered:", name)

                    if SettingOptions[name].get("Type") == "carousel":
                        options = SettingOptions[name].get("Options", [])
                        print(f"Current options for '{name}':")

                        if button.OptionsContainer is None: 
                            button.OptionsContainer = QFrame(parent=self.parent())
                            button.OptionsContainer.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
                            
                            button.OptionsContainer.setProperty("class", "button.OptionsContainer")
                            optionsLayout = QVBoxLayout()
                            optionsLayout.setContentsMargins(5, 5, 5, 5)
                            optionsLayout.setSpacing(5)
                            button.OptionsContainer.setLayout(optionsLayout)

                            button.OptionsContainer.Animations = {}
                            button.OptionsContainer.Animations["showAnim"] = QPropertyAnimation(button.OptionsContainer, b"windowOpacity")
                            button.OptionsContainer.Animations["showAnim"].setStartValue(0)
                            button.OptionsContainer.Animations["showAnim"].setEndValue(1)
                            button.OptionsContainer.Animations["showAnim"].setDuration(GetQTime(0.2))

                            button.OptionsContainer.Animations["hideAnim"] = QPropertyAnimation(button.OptionsContainer, b"windowOpacity")
                            button.OptionsContainer.Animations["hideAnim"].setStartValue(1)
                            button.OptionsContainer.Animations["hideAnim"].setEndValue(0)
                            button.OptionsContainer.Animations["hideAnim"].setDuration(GetQTime(0.2))
                            button.OptionsContainer.Animations["hideAnim"].finished.connect(button.OptionsContainer.deleteLater)

                            button.OptionsContainer.resize(math.floor(button.size().width() * 1.65), len(options) * 30 + 10)

                            button.OptionsContainer.move(button.mapToGlobal(button.rect().topRight()) + QPoint(15, 0))

                            button.OptionsContainer.setStyleSheet("""
                                QFrame[class='button.OptionsContainer'] {
                                    background-color: rgba(0, 0, 0, 220);
                                    border: 1px solid rgba(255, 106, 0, 180);
                                    border-radius: 10px;
                                }
                            """)

                            button.OptionsContainer.Animations["showAnim"].start()
                            button.OptionsContainer.show()
                        
                        button.OptionsContainer.installEventFilter(self)
                        button.OptionsContainer.buttonRef = button
                        
                        for o in options:
                            print(f" - {o}")

                    return QPushButton.enterEvent(button, event)
                return enterEvent

            
            def makeLeaveFunction(name):
                def leaveEvent(event):
                    return QPushButton.leaveEvent(button, event)
                return leaveEvent

            button.enterEvent = makeEnterFunction(key)
            button.leaveEvent = makeLeaveFunction(key)

            

        self.showAnim1.start()
        self.showAnim2.start()

        QApplication.instance().installEventFilter(self)
        self._closing = False
    
    def _finishClose(self):
        self._menuActive = False
        QApplication.instance().removeEventFilter(self)
        self.close()
    
    def eventFilter(self, obj, event):
        et = event.type()

        if et == QEvent.Type.MouseButtonPress and not self._closing:
            try:
                pos = event.globalPosition().toPoint()
            except AttributeError:
                pos = event.globalPos()

            widget = QApplication.widgetAt(pos)

            if not widget or not self.isAncestorOf(widget):
                self._closing = True
                self.hideAnim1.start()
                self.hideAnim2.start()
                return True


        if et == QEvent.Type.MouseMove:
            for btn in self.findChildren(QPushButton):
                cont = getattr(btn, "OptionsContainer", None)
                if not cont:
                    continue

                try:
                    cur = event.globalPosition().toPoint()
                except AttributeError:
                    cur = event.globalPos()

                inside_btn = btn.geometry().contains(btn.mapFromGlobal(cur))
                inside_cont = cont.geometry().contains(cont.mapFromGlobal(cur))

                if not inside_btn and not inside_cont:
                    anim = cont.Animations.get("hideAnim")
                    if anim and not anim.state():
                        anim.start()

        return super().eventFilter(obj, event)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())

        painter.setBrush(QBrush(QColor(*Constants["WindowColor"])))
        painter.setPen(Qt.PenStyle.NoPen)
        path = QPainterPath()
        path.addRoundedRect(rect, 10, 10)
        painter.drawPath(path)

        border_pen = QPen(QColor(*Constants["MainElementColor"]))
        border_pen.setWidth(1)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect.adjusted(1.5, 1.5, -1.5, -1.5), 10, 10)

class InteractableWindow(QMainWindow):
    valueChanged = pyqtSignal(str, object)
    
    Windows = []

    def AddWindow(self, win):
        def onDestroy():
            self.Windows.remove(win) if win in self.Windows else None

        if win is None:
            return

        self.Windows.append(win)
        win.destroyed.connect(onDestroy)

    def __init__(self, **kwargs):
        super().__init__()
        
        UpdateUserSettings()

        self._data = kwargs or {}
        
        self._data["titleKey"] = kwargs.get("titleKey", "titles/widgetSelection")
        self._data["language"] = UserSettings.get("language", "eng")

        self._data["title"] = GetAdaptedTextFromDictionary(self._data["titleKey"])

        self._data["_drag_pos"] = None
        self._data["exitConfirmationShowed"] = False
        self._data["exitState"] = None
        self._activeExitDialog = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.mainLayout = QVBoxLayout(central_widget)
        self.mainLayout.setContentsMargins(2, 2, 2, 2)
        self.mainLayout.setSpacing(5)
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        headerLayout = QHBoxLayout()
        headerLayout.setSpacing(5)
        headerLayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.mainLayout.addLayout(headerLayout)

        self.iconsLayout = QHBoxLayout()
        self.iconsLayout.setSpacing(5)
        self.iconsLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        headerLayout.addLayout(self.iconsLayout, 0)

        headerLayout.addStretch()

        self.menuBarLayout = QHBoxLayout()
        self.menuBarLayout.setSpacing(5)
        self.menuBarLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        headerLayout.addLayout(self.menuBarLayout, 0)

        self.icons = {}
        self.buttons = {}
        self.uis = {}

        mainIconPixmap = QPixmap(mainIcon).scaled(30, 30)

        self.icons["mainIcon"] = QLabel(self)
        self.icons["mainIcon"].setPixmap(mainIconPixmap)
        self.iconsLayout.addWidget(self.icons["mainIcon"])

        self.uis["holdAlt"] = QLabel(Dictionary[self._data["language"]]["labels"]["HoldAlt"], parent=self)

        CollectionService.addTag(self.uis["holdAlt"], "adaptableTextWidget")
        self.uis["holdAlt"].setProperty("textKey", "labels/HoldAlt")

        self.uis["holdAlt"].setProperty("class", "passive")
        addDynamicStyle(self.uis["holdAlt"], '''
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
        ''')
        self.menuBarLayout.addWidget(self.uis["holdAlt"], 0, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        
        self.buttons["settingsButton"] = QPushButton(Dictionary[self._data["language"]]["labels"]["Settings"])
        CollectionService.addTag(self.buttons["settingsButton"], "adaptableTextWidget")
        self.buttons["settingsButton"].setProperty("textKey", "labels/Settings")
        self.buttons["settingsButton"].setProperty("class", "menubarButton")
        self.buttons["settingsButton"].setStyleSheet(menubarTextButtonStyle)

        def Settings():
            button = self.buttons["settingsButton"]

            settingsWindow = SettingsWindow(self, Size = [self.buttons["settingsButton"].width(), len(SettingOptions) * 30], Position = (button.mapToGlobal(button.rect().bottomLeft()) + QPoint(0, 2)) )
            self.AddWindow(settingsWindow)

            settingsWindow.show()

        self.buttons["settingsButton"].clicked.connect(lambda: Settings())
        self.menuBarLayout.addWidget(self.buttons["settingsButton"])

        self.buttons["minimizeButton"] = QPushButton("_")
        self.buttons["minimizeButton"].setProperty("class", "menubarButton")
        self.buttons["minimizeButton"].setStyleSheet(menubarButtonStyle)
        self.buttons["minimizeButton"].clicked.connect(lambda: self.showMinimized())
        self.menuBarLayout.addWidget(self.buttons["minimizeButton"])

        self.buttons["closeButton"] = QPushButton("X")
        self.buttons["closeButton"].setProperty("class", "menubarButton")
        self.buttons["closeButton"].setStyleSheet(menubarButtonStyle)
        self.buttons["closeButton"].clicked.connect(lambda: self.close())
        self.menuBarLayout.addWidget(self.buttons["closeButton"])

        self.uis["mainTitle"] = QLabel(self._data["title"])
        
        CollectionService.addTag(self.uis["mainTitle"], "adaptableTextWidget")
        self.uis["mainTitle"].setProperty("textKey", "titles/widgetSelection")

        self.uis["mainTitle"].setProperty("class", "mainTitle")
        self.uis["mainTitle"].setStyleSheet('''
            QLabel[class="mainTitle"] {
                width: 200px;
                height: 25px;
                padding: 5 0;
                font-size: 14px;
                font-family: 'Courier New', Courier, monospace;
                color: rgba(255, 106, 0, 255);
                background-color: rgba(0, 0, 0, 0);
            }
        ''')
        self.iconsLayout.addWidget(self.uis["mainTitle"])

        self.valueChanged.connect(self.OnChangedValue)

    # ---------------- Value handling -----------------
    def setValue(self, key, newValue):
        if self._data.get(key) != newValue:
            self._data[key] = newValue
            self.valueChanged.emit(key, newValue)

    def getValue(self, key, default=None):
        return self._data.get(key, default)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self.setValue(key, value)

    def __contains__(self, key):
        return key in self._data

    def items(self):
        return self._data.items()

    # ---------------- Event filter -------------------
    def eventFilter(self, obj, event):
        if event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Alt:
                if self.uis["holdAlt"].property("class") != "active":
                    self.uis["holdAlt"].setProperty("class", "active")
                    self.uis["holdAlt"].style().unpolish(self.uis["holdAlt"])
                    self.uis["holdAlt"].style().polish(self.uis["holdAlt"])
                    self.uis["holdAlt"].update()

            elif self._activeExitDialog is not None:
                if event.key() == Qt.Key.Key_Enter:
                    self.setValue("exitState", "Enter")
                elif event.key() == Qt.Key.Key_Escape:
                    self.setValue("exitState", "Esc")

        elif event.type() == event.Type.KeyRelease:
            if event.key() == Qt.Key.Key_Alt:
                if self.uis["holdAlt"].property("class") != "passive":
                    self.uis["holdAlt"].setProperty("class", "passive")
                    self.uis["holdAlt"].style().unpolish(self.uis["holdAlt"])
                    self.uis["holdAlt"].style().polish(self.uis["holdAlt"])
                    self.uis["holdAlt"].update()

        return super().eventFilter(obj, event)
    
    # ---------------- Paint & drag -------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())

        painter.setBrush(QBrush(QColor(*Constants["WindowColor"])))
        painter.setPen(Qt.PenStyle.NoPen)
        path = QPainterPath()
        path.addRoundedRect(rect, 15, 15)
        painter.drawPath(path)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and keyboard.is_pressed('alt'):
            self._data["_drag_pos"] = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if (event.buttons() == Qt.MouseButton.LeftButton
            and keyboard.is_pressed('alt')
            and self._data["_drag_pos"] is not None):
            current_pos = event.globalPosition().toPoint()
            delta = current_pos - self._data["_drag_pos"]
            self.move(self.x() + int(delta.x()), self.y() + int(delta.y()))
            self._data["_drag_pos"] = current_pos
            event.accept()

    # ---------------- Close dialog -------------------
    def closeEvent(self, event):
        event.ignore()
        if self._data["exitConfirmationShowed"]:
            return
        self._data["exitConfirmationShowed"] = True

        shade = QFrame(parent=self)
        shade.setProperty("class", "shade")
        shade.setStyleSheet('''
            QFrame[class="shade"] {
                background-color: rgba(0,0,0,0.5);
                border-radius: 15px
            }
        ''')
        shade.resize(Constants["Size"]["width"], Constants["Size"]["height"])
        shade.show()

        shade.showAnim = QPropertyAnimation(shade, b"windowOpacity")
        shade.showAnim.setEndValue(1)
        shade.showAnim.setDuration(GetQTime(0.2))
        shade.showAnim.start()

        dialog = ConfirmExitWindow(self, language=self._data["language"])

        self.AddWindow(dialog)
        self._activeExitDialog = dialog

        dialog.move(
            self.x() + (self.width() - dialog.width()) // 2,
            self.y() + (self.height() - dialog.height()) // 2
        )
        dialog.show()

        # ---------------- Destroy dialog ----------------
        def destroy_dialog():
            if self._activeExitDialog is not None:
                dlg = self._activeExitDialog
                self._activeExitDialog = None

                dlg.canClose = True
                dlg.hideAnim.finished.connect(dlg.close)
                dlg.hideAnim.start()

                currentPos = dlg.pos()
                dlg.hideAnimMove = QPropertyAnimation(dlg, b"pos")
                dlg.hideAnimMove.setStartValue(currentPos)
                dlg.hideAnimMove.setEndValue(QPoint(currentPos.x(), currentPos.y() + 30))
                dlg.hideAnimMove.start()

                shade.hideAnim = QPropertyAnimation(shade, b"windowOpacity")
                shade.hideAnim.setEndValue(0)
                shade.hideAnim.setDuration(GetQTime(0.2))
                shade.hideAnim.finished.connect(shade.close)
                shade.hideAnim.start()

        # ---------------- Button actions ----------------
        def no_clicked():
            self._data["exitConfirmationShowed"] = False
            destroy_dialog()

        def yes_clicked():
            def exit_app():
                sys.exit(0)

            destroy_dialog()

            self.HideAnim = QPropertyAnimation(self, b"windowOpacity")
            self.HideAnim.setEndValue(0)
            self.HideAnim.setDuration(GetQTime(0.2))
            self.HideAnim.finished.connect(exit_app)

            currentPos = self.pos()
            self.HideAnimMove = QPropertyAnimation(self, b"pos")
            self.HideAnimMove.setStartValue(currentPos)
            self.HideAnimMove.setEndValue(QPoint(currentPos.x(), currentPos.y() + 30))

            self.HideAnimMove.start()
            self.HideAnim.start()

        dialog.btn_no.clicked.connect(no_clicked)
        dialog.btn_yes.clicked.connect(yes_clicked)

    # ---------------- Value change handler ----------------
    def OnChangedValue(self, name, value):
        if name == "exitState" and self._activeExitDialog is not None:
            if value == "Enter":
                self._activeExitDialog.btn_yes.click()
            else:
                self._activeExitDialog.btn_no.click()

            self.setValue("exitState", None)

    # ---------------- Animations -------------------
    def showMinimized(self):
        self.HideAnim = QPropertyAnimation(self, b"windowOpacity")
        self.HideAnim.setEndValue(0)
        self.HideAnim.setDuration(GetQTime(0.2))

        currentPos = self.pos()
        self.HideAnimMove = QPropertyAnimation(self, b"pos")
        self.HideAnimMove.setStartValue(currentPos)
        self.HideAnimMove.setEndValue(QPoint(currentPos.x(), currentPos.y() + 30))

        QTimer.singleShot(GetQTime(0.3), lambda: QMainWindow.showMinimized(self))

        self.HideAnimMove.start()
        self.HideAnim.start()

    def showEvent(self, a0):
        self.ShowAnim = QPropertyAnimation(self, b"windowOpacity")
        self.ShowAnim.setStartValue(0)
        self.ShowAnim.setEndValue(Constants["MainOpacity"])
        self.ShowAnim.setDuration(GetQTime(0.2))

        currentPos = self.pos()
        self.ShowAnimMove = QPropertyAnimation(self, b"pos")
        self.ShowAnimMove.setStartValue(currentPos)
        self.ShowAnimMove.setEndValue(QPoint(currentPos.x(), currentPos.y() - 30))

        self.ShowAnimMove.start()
        self.ShowAnim.start()

        return super().showEvent(a0)
