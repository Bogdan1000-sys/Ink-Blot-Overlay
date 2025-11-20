from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSlider
from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, QPoint, QTimer, pyqtSignal, QEvent
from PyQt6.QtGui import QPainter, QColor, QBrush, QPainterPath, QPixmap, QPen, QCursor, QRegion
import subprocess, keyboard, json, math

# -- Services --
from Services import CollectionService

# -- Functions --
from Functions import GetQTime, applyStyleClass, GetUserSettings, AppendUserSettings, CloneObject, initSound, playSound, RegisterAdaptableText

# -- Variables --

# -- Resources --
mainIcon = 'Programm/Resources/Images/Ink Blot Icon.png'

fadeSound = "Programm/Resources/SFX/CinematicWhoosh.wav"
buttonClickSound = "Programm/Resources/SFX/WidgetSelect.wav"

# -- Constants --
with open("Programm/Data/Pathes.json", "r", encoding="utf-8") as pFile:
    Pathes = json.load(pFile)

# -- Data --
with open(Pathes["Constants"], "r", encoding="utf-8") as cFile:
    Constants = json.load(cFile)
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

        self.setParent(parent)

        if self._data["data"] == None:
            self.hide()
            self.destroy()
            print("[Classes] Error: Data of Widget not found!")
            return
        
        self.setFixedSize(self._data["size"][0], self._data["size"][1])
        self.setProperty("class", "widgetButton:passive")
        self.setStyleSheet("""
            QFrame[class='widgetButton:passive'] {
                border: none;
                border-radius: 10px;
                background: qlineargradient(
                    x1: 0, y1: 1,
                    x2: 0, y2: 0,
                    stop: 0 #411c00,
                    stop: 1 #240f00);
            }
        """)

        self.Reference = self._data["data"]["Key"]
        CollectionService.addTag(self, "widgetButton")
        
        pixmapScale = (self._data["size"][0] < self._data["size"][1] and self._data["size"][0] or self._data["size"][1])-5
        IconPixmap = QPixmap(self._data["data"]["Icon"]).scaled(pixmapScale, pixmapScale)

        self.Icon = QLabel(self)
        self.Icon.setStyleSheet("background: transparent; border: none; margin-top:1px; margin-left:1px")
        self.Icon.setPixmap(IconPixmap)

        self.nameLabel = QLabel("Name", parent=self)
        RegisterAdaptableText(self.nameLabel, self._data["data"]["Name"])

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
        self.showAnim.setEndValue(UserSettings["opacity"])
        self.showAnim.setDuration(GetQTime(0.2))
        self.showAnim.start()

        self.hideAnim = QPropertyAnimation(self, b"windowOpacity")
        self.hideAnim.setEndValue(0)
        self.hideAnim.setDuration(GetQTime(0.2))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel("Q")
        RegisterAdaptableText(self.label, "labels/exitConfirmation/Q")
        
        self.label.setStyleSheet("color: white; font-size: 14px; font-family: 'Courier New', Courier, monospace;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        layout.addLayout(btn_layout)

        self.btn_yes = QPushButton("Y")
        RegisterAdaptableText(self.btn_yes, "labels/exitConfirmation/Y")

        self.btn_no = QPushButton("N")
        RegisterAdaptableText(self.btn_no, "labels/exitConfirmation/N")

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

class OptionsContainer(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.radius = 10

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect())

        painter.setBrush(QColor(0, 0, 0, 220))
        painter.setPen(QPen(QColor(255, 106, 0, 180), 2))

        path = QPainterPath()
        path.addRoundedRect(rect, self.radius, self.radius)
        painter.drawPath(path)

class SettingsWindow(QWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)

        UpdateUserSettings()
        CollectionService.addTag(self, "commonOpacityWindow")

        self.ClickSound = initSound(buttonClickSound, self)

        self._starterSettings = UserSettings
        self._finalSettings = CloneObject(UserSettings)

        self.setProperty("hidden", False)

        self._menuActive = True
        self._optionsContainer = None

        self._data = kwargs or {}
        self._data["Size"] = kwargs.get("Size", [125, 200])
        self._data["Position"] = kwargs.get("Position", QPoint(100, 100))
        self._data["language"] = UserSettings.get("language", "eng")
        
        self._settingButtons = {}

        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
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
        self.showAnim1.setEndValue(UserSettings["opacity"])
        self.showAnim1.setDuration(GetQTime(0.2))

        self.showAnim2 = QPropertyAnimation(self, b"pos")
        self.showAnim2.setStartValue(self._data["Position"] + QPoint(0, -5))
        self.showAnim2.setEndValue(self._data["Position"])
        self.showAnim2.setDuration(GetQTime(0.2))

        self.hideAnim1 = QPropertyAnimation(self, b"windowOpacity")
        self.hideAnim1.setEndValue(0)
        self.hideAnim1.setDuration(GetQTime(0.2))

        self.hideAnim2 = QPropertyAnimation(self, b"pos")
        self.hideAnim2.setStartValue(self._data["Position"])
        self.hideAnim2.setEndValue(self._data["Position"] + QPoint(0, -5))
        self.hideAnim2.setDuration(GetQTime(0.2))

        self._settingButtons["language"] = QPushButton("Language", parent=self)
        self._settingButtons["language"].setProperty("class", "settingButton")
        self.MainLayout.addWidget(self._settingButtons["language"])

        self._settingButtons["opacity"] = QPushButton("Opacity", parent=self)
        self._settingButtons["opacity"].setProperty("class", "settingButton")
        self.MainLayout.addWidget(self._settingButtons["opacity"])

        self._settingButtons["volume"] = QPushButton("Volume", parent=self)
        self._settingButtons["volume"].setProperty("class", "settingButton")
        self.MainLayout.addWidget(self._settingButtons["volume"])

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

            RegisterAdaptableText(button, "settings/"+key)
            
            def makeClickedFunction(sectionName):
                def onClicked():
                    if not self._menuActive:
                        return
                    
                    def CreateOptionsContainerBody():
                        playSound(self.ClickSound)

                        self._optionsContainer = OptionsContainer(parent=self.parent())
                        CollectionService.addTag(self._optionsContainer, "optionsContainer")
                        CollectionService.addTag(self._optionsContainer, "commonOpacityWindow")
                        self._optionsContainer.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)

                        self._optionsContainer.setProperty("class", "optionsContainer")
                        optionsLayout = QVBoxLayout()
                        optionsLayout.setContentsMargins(5, 5, 5, 5)
                        optionsLayout.setSpacing(5)
                        self._optionsContainer.setLayout(optionsLayout)

                        self._optionsContainer.Animations = {}
                        self._optionsContainer.Animations["showAnim"] = QPropertyAnimation(self._optionsContainer, b"windowOpacity")
                        self._optionsContainer.Animations["showAnim"].setStartValue(0)
                        self._optionsContainer.Animations["showAnim"].setEndValue(UserSettings["opacity"])
                        self._optionsContainer.Animations["showAnim"].setDuration(GetQTime(0.1))

                        self._optionsContainer.Animations["hideAnim"] = QPropertyAnimation(self._optionsContainer, b"windowOpacity")
                        self._optionsContainer.Animations["hideAnim"].setEndValue(0)
                        self._optionsContainer.Animations["hideAnim"].setDuration(GetQTime(0.1))
                        self._optionsContainer.Animations["hideAnim"].finished.connect(self._optionsContainer.deleteLater)

                        self._optionsContainer.resize(10, 10)

                        self._optionsContainer.move(
                            button.mapToGlobal(button.rect().topRight()).x() + 5,
                            QCursor.pos().y() - button.size().height() // 2
                        )

                        self._optionsContainer.setStyleSheet("""
                            QFrame[class='optionsContainer'] {
                                background-color: rgba(0, 0, 0, 220);
                                border: 1px solid rgba(255, 106, 0, 180);
                                border-radius: 10px;
                            }
                        """)

                        return optionsLayout

                    def createOptionsContainer():
                        optionsLayout = CreateOptionsContainerBody()

                        if SettingOptions[sectionName].get("Type") == "Options":
                            options = SettingOptions[sectionName].get("Options", [])

                            self._optionsContainer.resize(
                                math.floor(button.size().width() * 1.65),
                                len(options) * 30 + 10
                            )

                            for o in options:
                                o_button = QPushButton(o, parent=self._optionsContainer)
                                o_button.setProperty("class", "settingButton")
                                o_button.setStyleSheet("""
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
                                """)

                                def makeButtonClickHandler(optionName):
                                    def onClick():
                                        playSound(self.ClickSound)

                                        self._finalSettings[sectionName] = optionName

                                        if self._optionsContainer:
                                            self.clearSettingsUI()
                                            QTimer.singleShot(GetQTime(0.1), lambda: setattr(self, "_optionsContainer", None))
                                            
                                    return onClick

                                o_button.clicked.connect(makeButtonClickHandler(o))

                                optionsLayout.addWidget(o_button)
                        elif SettingOptions[sectionName].get("Type") == "Slider":
                            options = SettingOptions[sectionName].get("Options", {"min":0.25, "max":1})
                            
                            self._optionsContainer.resize(
                                math.floor(button.size().width() * 1.65),
                                40
                            )

                            UpdateUserSettings()

                            slider = QSlider(Qt.Orientation.Horizontal)
                            slider.setProperty("class", "slider")
                            slider.setStyleSheet("""
                                QSlider::handle:horizontal[class='slider'] {
                                    background: rgba(255, 106, 0, 255);
                                    border: 2px solid rgba(150, 60, 0, 255);
                                    width: 30px;
                                }
                                QSlider::groove:horizontal[class='slider'] {
                                    background: rgba(56, 22, 0, 255);
                                    border: 2px solid rgba(76, 42, 0, 255);
                                }
                            """)

                            def updateValue(value):
                                v = value/100
                                
                                if sectionName == 'opacity':
                                    for i, widget in enumerate(CollectionService.getTagged("commonOpacityWindow")):
                                        try: widget.setWindowOpacity(v)
                                        except: pass

                                self._finalSettings[sectionName] = v

                            slider.setMinimum( int(options["min"]*100) )
                            slider.setMaximum( int(options["max"]*100) )
                            slider.setValue( int(UserSettings[sectionName]*100) )

                            slider.valueChanged.connect(updateValue)

                            optionsLayout.addWidget(slider)

                        self._optionsContainer.Animations["showAnim"].start()
                        self._optionsContainer.show()

                    if self._optionsContainer is None:
                        createOptionsContainer()
                    else:
                        self.clearSettingsUI()
                    try:
                        self._optionsContainer.installEventFilter(self)
                        self._optionsContainer.buttonRef = button
                    except:
                        pass

                return onClicked
            
            def makeLeaveFunction(name):
                def leaveEvent(event):
                    return QPushButton.leaveEvent(button, event)
                return leaveEvent

            button.clicked.connect(makeClickedFunction(key))
            button.leaveEvent = makeLeaveFunction(key)

            

        self.showAnim1.start()
        self.showAnim2.start()

        QApplication.instance().installEventFilter(self)
        self._closing = False

    def clearSettingsUI(self):
        try:
            self._optionsContainer.Animations["hideAnim"].start() if self._optionsContainer is not None else None
            QTimer.singleShot(GetQTime(0.1), lambda: setattr(self, "_optionsContainer", None))
        except: pass
        AppendUserSettings({
            "language": self._finalSettings["language"],
            "opacity": self._finalSettings["opacity"],
            "volume": self._finalSettings["volume"],
        })

    def closeEvent(self, a0):
        self.clearSettingsUI()
        return super().closeEvent(a0)
    
    def eventFilter(self, obj, event):
        et = event.type()

        if et == QEvent.Type.MouseButtonPress and not self._closing:
            try:
                pos = event.globalPosition().toPoint()
            except AttributeError:
                pos = event.globalPos()

            widget = QApplication.widgetAt(pos)

            if not widget or (not self.isAncestorOf(widget) and not (self._optionsContainer and self._optionsContainer.isAncestorOf(widget))):
                self._closing = True
                self.hideAnim1.start()
                self.hideAnim2.start()

                self.setProperty("hidden", True)
                self._menuActive = False

                self.clearSettingsUI()
                return True
            
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

class UIApplication(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.processes: dict[str, subprocess.Popen] = {}

    def addProcess(self, key: str, process: subprocess.Popen):
        """Добавляет процесс по ключу"""
        self.processes[key] = process

    def removeProcess(self, key: str):
        """Завершает и удаляет процесс из словаря, если он существует"""
        proc = self.processes.get(key)

        if proc is not None:
            try:
                if proc.poll() is None:
                    print(f"Terminating process '{key}'...")
                    proc.terminate()
            except Exception as e:
                print(f"Error terminating process '{key}': {e}")

            del self.processes[key]

    def getProcess(self, key: str):
        """Получить процесс по ключу"""
        return self.processes.get(key, None)

    def terminateProcesses(self):
        """Завершает все процессы и очищает словарь"""
        for key, p in list(self.processes.items()):
            if p is not None:
                try:
                    print("Terminating:", key, p)
                    p.terminate()
                except Exception as e:
                    print("Error terminating process:", e)

        print("Subprocesses terminated!")
        self.processes.clear()

class MPushButton(QPushButton):
    def __init__(self, text="", size=None, miniTitleKey=None, parent=None):
        super().__init__(text, parent)

        CollectionService.addTag(self, "commonOpacityWindow")

        self.resize(size[0], size[1])

        self.setProperty("class", "minimizeWindowButton")
        self.setStyleSheet("""
            QPushButton[class='minimizeWindowButton'] {
                font-size: 14px;
                font-family: 'Courier New', Courier, monospace;
                padding: 4px 8px; 
                color: rgba(255, 106, 0, 255);

                background-color: qlineargradient(
                    x1: 0, y1: 0,
                    x2: 0, y2: 1,
                    stop: 0 rgba(50, 25, 0, 255),
                    stop: 1 rgba(30, 15, 0, 255)
                );

                border: 1px solid rgba(255, 106, 0, 255);
                border-radius: 10px;
            }
            QPushButton[class='minimizeWindowButton']:hover {
                background-color: qlineargradient(
                    x1: 0, y1: 0,
                    x2: 0, y2: 1,
                    stop: 0 rgba(40, 15, 0, 255),
                    stop: 1 rgba(20, 5, 0, 255)
                );
            }
            QPushButton[class='minimizeWindowButton']:pressed {
                background-color: qlineargradient(
                    x1: 0, y1: 0,
                    x2: 0, y2: 1,
                    stop: 0 rgba(30, 5, 0, 255),
                    stop: 1 rgba(10, 0, 0, 255)
                );
            }
        """)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.DragFrame = QFrame(self)
        CollectionService.addTag(self.DragFrame, "dragger")
        CollectionService.addTag(self.DragFrame, "commonOpacityWindow")
        self.DragFrame.setProperty("class", "dragFrame")
        self.DragFrame.setStyleSheet("""
            QFrame[class='dragFrame'] {
                background: black;
                border: 1px solid rgba(255, 106, 0, 255);
            }
        """)
        self.DragFrame.resize(math.floor(self.width() / 2.5), math.floor(self.height() * 0.5))
        self.DragFrame.setAttribute(Qt.WidgetAttribute.WA_SetStyle, True)
        self.DragFrame.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.DragFrame.rect()), 5, 5)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.DragFrame.setMask(region)

        self.DragFrame.show()

        self._dragging = False
        self._drag_offset = QPoint()

    def updateDragFramePosition(self):
        self.DragFrame.move(
            self.x() + self.width() + 3,
            self.y() + self.height() // 2 - self.DragFrame.height() // 2
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_offset = event.globalPosition().toPoint() - self.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging:
            new_pos = event.globalPosition().toPoint() - self._drag_offset
            self.move(new_pos)
            self.updateDragFramePosition()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._dragging = False
        super().mouseReleaseEvent(event)

    def moveEvent(self, event):
        self.updateDragFramePosition()
        super().moveEvent(event)

class InteractableWindow(QMainWindow):
    valueChanged = pyqtSignal(str, object)    
    settingsWindow = None
    
    def __init__(self, **kwargs):
        super().__init__()
        
        self.FadeSound = initSound(fadeSound, self)
        self.ClickSound = initSound(buttonClickSound, self)

        UpdateUserSettings()
        CollectionService.addTag(self, "commonOpacityWindow")
        CollectionService.addTag(self, "dragger")

        self._data = kwargs or {}
        
        self._data["titleKey"] = kwargs.get("titleKey", "titles/widgetSelection")
        self._data["miniTitleKey"] = kwargs.get("miniTitleKey", "miniTitles/widgetSelection")
        self._data["language"] = UserSettings.get("language", "eng")

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

        self.uis["holdAlt"] = QLabel("Hold Alt", parent=self)
        RegisterAdaptableText(self.uis["holdAlt"], "labels/HoldAlt")
        
        self.uis["holdAlt"].setProperty("class", "passive")
        self.uis["holdAlt"].setStyleSheet('''
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
        
        self.buttons["settingsButton"] = QPushButton("Settings")
        RegisterAdaptableText(self.buttons["settingsButton"], "labels/Settings")
        
        self.buttons["settingsButton"].setProperty("class", "menubarButton")
        self.buttons["settingsButton"].setStyleSheet(menubarTextButtonStyle)

        def Settings():
            button = self.buttons["settingsButton"]
            
            if self.settingsWindow:
                try:
                    self.settingsWindow.hide()
                    self.settingsWindow.destroy()
                    self.settingsWindow = None
                except: pass

            playSound(self.ClickSound)

            self.settingsWindow = SettingsWindow(parent=self, Size = [self.buttons["settingsButton"].width(), len(SettingOptions) * 30], Position = (button.mapToGlobal(button.rect().bottomLeft()) + QPoint(0, 2)) )
            self.settingsWindow.show()

        self.buttons["settingsButton"].clicked.connect(lambda: Settings())
        self.menuBarLayout.addWidget(self.buttons["settingsButton"])

        # self.buttons["minimizeButton"] = QPushButton("_")
        # self.buttons["minimizeButton"].setProperty("class", "menubarButton")
        # self.buttons["minimizeButton"].setStyleSheet(menubarButtonStyle)
        # self.buttons["minimizeButton"].clicked.connect(lambda: self.showMinimized())
        # self.menuBarLayout.addWidget(self.buttons["minimizeButton"])

        self.buttons["closeButton"] = QPushButton("X")
        self.buttons["closeButton"].setProperty("class", "menubarButton")
        self.buttons["closeButton"].setStyleSheet(menubarButtonStyle)
        self.buttons["closeButton"].clicked.connect(lambda: self.close())
        self.menuBarLayout.addWidget(self.buttons["closeButton"])

        self.uis["mainTitle"] = QLabel("Ink Blot Overlay")
        RegisterAdaptableText(self.uis["mainTitle"], self._data["titleKey"])
        
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

        self.minimizeButton = MPushButton("<", parent=self, size=[25,Constants["Size"]["height"]//5], miniTitleKey=self._data["miniTitleKey"])
        self.minimizeButton.move(self.width()+5, self.height()//2 - self.minimizeButton.height()//2)
        self.minimizeButton.show()

        self.valueChanged.connect(self.OnChangedValue)

        UIApplication.instance().installEventFilter(self)
        self.updateMinimizeButtonPosition()


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

    def eventFilter(self, obj, event):
        if event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Alt:
                if self.uis["holdAlt"].property("class") != "active":
                    applyStyleClass(self.uis["holdAlt"], "active")

            elif self._activeExitDialog is not None:
                if event.key() == Qt.Key.Key_Enter:
                    self.setValue("exitState", "Enter")
                elif event.key() == Qt.Key.Key_Escape:
                    self.setValue("exitState", "Esc")

        elif event.type() == event.Type.KeyRelease:
            if event.key() == Qt.Key.Key_Alt:
                if self.uis["holdAlt"].property("class") != "passive":
                    applyStyleClass(self.uis["holdAlt"], "passive")

        if obj == self and event.type() == QEvent.Type.Move:
            self.updateMinimizeButtonPosition()

        return super().eventFilter(obj, event)
    
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

        self._activeExitDialog = dialog

        dialog.move(
            self.x() + (self.width() - dialog.width()) // 2,
            self.y() + (self.height() - dialog.height()) // 2
        )
        dialog.show()


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


        def no_clicked():
            self._data["exitConfirmationShowed"] = False
            destroy_dialog()

        def yes_clicked():
            self.exitCollection = 0

            def exit_app():
                self.exitCollection += 1
                if self.exitCollection == 2:
                    UIApplication.instance().terminateProcesses()
                    UIApplication.instance().exit()

            destroy_dialog()
            
            hideAnims = []
            for i, widget in enumerate(CollectionService.getTagged("commonOpacityWindow")):
                if widget == self: continue
                try: 
                    widget.HideAnim = QPropertyAnimation(widget, b"windowOpacity")
                    widget.HideAnim.setEndValue(0)
                    widget.HideAnim.setDuration(GetQTime(0.2))

                    currentPos = widget.pos()
                    widget.HideAnimMove = QPropertyAnimation(widget, b"pos")
                    widget.HideAnimMove.setStartValue(currentPos)
                    widget.HideAnimMove.setEndValue(QPoint(currentPos.x(), currentPos.y() + 30))

                    hideAnims.append(widget.HideAnim)
                    hideAnims.append(widget.HideAnimMove)
                except: pass

            self.HideAnim = QPropertyAnimation(self, b"windowOpacity")
            self.HideAnim.setEndValue(0)
            self.HideAnim.setDuration(GetQTime(0.2))
            self.HideAnim.finished.connect(exit_app)

            currentPos = self.pos()
            self.HideAnimMove = QPropertyAnimation(self, b"pos")
            self.HideAnimMove.setStartValue(currentPos)
            self.HideAnimMove.setEndValue(QPoint(currentPos.x(), currentPos.y() + 30))

            def soundHandler():
                if self.FadeSound.isPlaying() == False:
                    exit_app()
                else:
                    QTimer.singleShot(GetQTime(0.5), soundHandler)

            playSound(self.FadeSound)
            soundHandler()

            for anim in hideAnims:
                anim.start()

            self.HideAnimMove.start()
            self.HideAnim.start()

        dialog.btn_no.clicked.connect(no_clicked)
        dialog.btn_yes.clicked.connect(yes_clicked)

    def OnChangedValue(self, name, value):
        if name == "exitState" and self._activeExitDialog is not None:
            if value == "Enter":
                self._activeExitDialog.btn_yes.click()
            else:
                self._activeExitDialog.btn_no.click()

            self.setValue("exitState", None)

    def showMinimized(self):
        hideAnims = []
        for i, widget in enumerate(CollectionService.getTagged("commonOpacityWindow")):
            if widget == self: continue
            try: 
                widget.HideAnim = QPropertyAnimation(widget, b"windowOpacity")
                widget.HideAnim.setEndValue(0)
                widget.HideAnim.setDuration(GetQTime(0.2))

                currentPos = widget.pos()
                widget.HideAnimMove = QPropertyAnimation(widget, b"pos")
                widget.HideAnimMove.setStartValue(currentPos)
                widget.HideAnimMove.setEndValue(QPoint(currentPos.x(), currentPos.y() + 30))

                hideAnims.append(widget.HideAnim)
                hideAnims.append(widget.HideAnimMove)
            except: pass

        self.HideAnim = QPropertyAnimation(self, b"windowOpacity")
        self.HideAnim.setEndValue(0)
        self.HideAnim.setDuration(GetQTime(0.2))

        currentPos = self.pos()
        self.HideAnimMove = QPropertyAnimation(self, b"pos")
        self.HideAnimMove.setStartValue(currentPos)
        self.HideAnimMove.setEndValue(QPoint(currentPos.x(), currentPos.y() + 30))

        QTimer.singleShot(GetQTime(0.3), lambda: QMainWindow.showMinimized(self))

        playSound(self.FadeSound)

        for anim in hideAnims:
            anim.start()

        self.HideAnimMove.start()
        self.HideAnim.start()

    def showEvent(self, a0):
        showAnims = []
        for i, widget in enumerate(CollectionService.getTagged("commonOpacityWindow")):
            if widget == self: continue
            if widget.property("hidden"): continue
            try: 
                widget.ShowAnim = QPropertyAnimation(widget, b"windowOpacity")
                widget.ShowAnim.setStartValue(0)
                widget.ShowAnim.setEndValue(UserSettings["opacity"])
                widget.ShowAnim.setDuration(GetQTime(0.2))

                currentPos = widget.pos()
                widget.ShowAnimMove = QPropertyAnimation(widget, b"pos")
                widget.ShowAnimMove.setStartValue(currentPos)
                widget.ShowAnimMove.setEndValue(QPoint(currentPos.x(), currentPos.y() - 30))

                showAnims.append(widget.ShowAnim)
                showAnims.append(widget.ShowAnimMove)
            except: pass

        self.ShowAnim = QPropertyAnimation(self, b"windowOpacity")
        self.ShowAnim.setStartValue(0)
        self.ShowAnim.setEndValue(UserSettings["opacity"])
        self.ShowAnim.setDuration(GetQTime(0.2))

        currentPos = self.pos()
        self.ShowAnimMove = QPropertyAnimation(self, b"pos")
        self.ShowAnimMove.setStartValue(currentPos)
        self.ShowAnimMove.setEndValue(QPoint(currentPos.x(), currentPos.y() - 30))
        
        playSound(self.FadeSound)

        for anim in showAnims:
            anim.start()

        self.ShowAnimMove.start()
        self.ShowAnim.start()

        return super().showEvent(a0)
    
    def updateMinimizeButtonPosition(self):
        screen = self.screen().availableGeometry()

        x = self.x() + self.width() + Constants["MinimizeButtonMargins"]
        y = self.y() + self.height() // 2 - self.minimizeButton.height() // 2

        btn_w = self.minimizeButton.width()
        btn_h = self.minimizeButton.height()

        if x + btn_w > screen.right() - Constants["MinimizeButtonMargins"] * 3:
            x = screen.right() - btn_w - Constants["MinimizeButtonMargins"] * 3
        if x < screen.left() + Constants["MinimizeButtonMargins"]:
            x = screen.left() + Constants["MinimizeButtonMargins"]

        if y + btn_h > screen.bottom() - Constants["MinimizeButtonMargins"]:
            y = screen.bottom() - btn_h - Constants["MinimizeButtonMargins"]
        if y < screen.top() + Constants["MinimizeButtonMargins"]:
            y = screen.top() + Constants["MinimizeButtonMargins"]

        self.minimizeButton.move(x, y)